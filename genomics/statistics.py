"""Quantitative GWAS effect gates; no unsourced clinical risk predictions.

An odds ratio in a paper is not a patient's absolute disease probability.
Allele identity, endpoint, ancestry, model, reference build, and data quality
must all be validated before interpreting a population estimate.
No LD-adjusted PRS is built here.
"""
from __future__ import annotations
from math import exp, isfinite, log, sqrt
from typing import Any

Z95 = 1.959963984540054

class EvidenceValidationError(ValueError):
    pass

def _positive(name: str, value: Any) -> float:
    try:
        x = float(value)
    except (ValueError, TypeError, OverflowError):
        raise EvidenceValidationError(name + " must be a finite positive number") from None
    if not isfinite(x) or x <= 0:
        raise EvidenceValidationError(name + " must be a finite positive number")
    return x

def or_ci_to_log_effect(odds_ratio: float, ci_lower: float, ci_upper: float) -> dict:
    """Two-sided 95% CI log-scale approximation; asymmetry flagged.

    Assumes estimates and CI share the same OR contrast. Intervals from exact
    methods, penalised models or other confidence levels need their own method.
    """
    odds_ratio = _positive("odds_ratio", odds_ratio)
    lower = _positive("ci_lower", ci_lower)
    upper = _positive("ci_upper", ci_upper)
    if not lower < odds_ratio < upper:
        raise EvidenceValidationError("CI must strictly bracket the OR")
    beta = log(odds_ratio)
    se = (log(upper) - log(lower)) / (2 * Z95)
    return {"beta_log_odds": beta, "se_log_odds": se,
            "variance_log_odds": se * se, "or": odds_ratio,
            "ci_lower": lower, "ci_upper": upper,
            "log_ci_asymmetry": abs((beta - log(lower)) - (log(upper) - beta)),
            "method": "asymptotic 95%-CI log-OR approximation",
            "not_individual_risk": True}

_REQUIRED = ("rsid", "effect_allele", "other_allele", "build",
             "trait", "outcome_definition", "study_id", "source_url",
             "population", "genetic_model", "effect_measure",
             "effect_value", "ci_lower", "ci_upper", "sample_size")

def assess_study_effect(record: dict, *, personal_genotype: str | None,
                        coordinate_status: str, ancestry_match: bool | None) -> dict:
    """Fail closed on everything needed for a defensible population association.

    Never return a personal probability or combine independent/correlated SNPs.
    """
    rsid = str(record.get("rsid", ""))
    result = {"rsid": rsid, "classification": "NOT_INTERPRETABLE",
              "individual_absolute_risk": None, "population_effect": None,
              "blocking_reasons": []}
    reasons = result["blocking_reasons"]
    missing = [k for k in _REQUIRED if k not in record or record[k] in ("", None)]
    if missing:
        reasons.append("missing_fields:" + ",".join(missing))
    if personal_genotype is None:
        reasons.append("NOT_GENOTYPED")
    if coordinate_status != "GRCH37_COORDINATE_ALLELES_MATCH":
        reasons.append("NO_REFERENCE_ALLELE_HARMONIZATION")
    if ancestry_match is not True:
        reasons.append("NO_MATCHED_ANCESTRY_EVIDENCE")
    if missing:
        return result
    if record["build"] != "GRCh37":
        reasons.append("WRONG_OR_UNKNOWN_GENOME_BUILD")
    if record["effect_measure"] != "OR":
        reasons.append("UNSUPPORTED_MEASURE_NO_ODDS_RATIO_INFERENCE")
    if record["genetic_model"] not in ("additive_per_allele", "dominant", "recessive"):
        reasons.append("UNVERIFIED_GENETIC_MODEL")
    effect_allele = str(record["effect_allele"]).upper()
    other_allele = str(record["other_allele"]).upper()
    if effect_allele not in "ACGT" or other_allele not in "ACGT" or effect_allele == other_allele:
        reasons.append("INVALID_EFFECT_AND_OTHER_ALLELES")
    try:
        n = int(record["sample_size"])
        if n < 30:
            reasons.append("INADEQUATE_SAMPLE_SIZE_FOR_AUTOMATED_USE")
    except (ValueError, TypeError, OverflowError):
        reasons.append("INVALID_SAMPLE_SIZE")
    if not str(record["source_url"]).startswith(("https://doi.org/", "https://pubmed.ncbi.nlm.nih.gov/", "https://www.ebi.ac.uk/gwas/")):
        reasons.append("UNVERIFIED_PRIMARY_SOURCE_URL")
    gt = str(personal_genotype or "").upper()
    if len(gt) != 2 or set(gt) - {effect_allele, other_allele}:
        reasons.append("PERSONAL_GENOTYPE_NOT_EFFECT_ALLELE_MATCHED")
    if record["effect_measure"] == "OR":
        try:
            effect = or_ci_to_log_effect(record["effect_value"], record["ci_lower"], record["ci_upper"])
        except EvidenceValidationError:
            reasons.append("INVALID_OR_OR_CONFIDENCE_INTERVAL")
            effect = None
    else:
        effect = None
    if reasons:
        return result
    result["classification"] = "POPULATION_ASSOCIATION_ONLY"
    result["effect_allele_dosage"] = gt.count(effect_allele)
    result["population_effect"] = effect
    result["disclaimer"] = ("Published effect for a defined ancestry/study endpoint; "
                             "not a measured micronutrient deficiency, malabsorption diagnosis, "
                             "or validated individual risk. Do not multiply associated loci.")
    return result

def correlated_estimate_variance(standard_errors: list[float], correlations: list[list[float]]) -> float:
    """Variance of a sum of ESTIMATORS with a supplied estimate-correlation matrix.

    A genotype LD r^2 is NOT interchangeable with the correlation of GWAS
    effect estimators; r^2 also discards sign. No inference if unknown.
    """
    n = len(standard_errors)
    if n == 0 or n > 100 or len(correlations) != n or any(len(row) != n for row in correlations):
        raise EvidenceValidationError("Consistent, nonempty square correlation matrix required")
    se = [_positive("standard error", s) for s in standard_errors]
    for i in range(n):
        for j in range(n):
            try:
                c = float(correlations[i][j])
                mirror = float(correlations[j][i])
            except (ValueError, TypeError, OverflowError):
                raise EvidenceValidationError("Invalid correlation coefficient") from None
            if not isfinite(c) or not (-1 <= c <= 1) or abs(c - mirror) > 1e-10:
                raise EvidenceValidationError("Correlation matrix must be finite and symmetric")
        if abs(float(correlations[i][i]) - 1) > 1e-10:
            raise EvidenceValidationError("Correlation matrix diagonal must equal 1")
    # Reject impossible input correlation matrices, including 3x3 pairwise
    # values that cannot coexist. Cholesky factorisation for PSD matrices.
    a = [[float(correlations[i][j]) for j in range(n)] for i in range(n)]
    L = [[0.0] * n for _ in range(n)]
    for i in range(n):
        for j in range(i + 1):
            residual = a[i][j] - sum(L[i][k] * L[j][k] for k in range(j))
            if i == j:
                if residual < -1e-9:
                    raise EvidenceValidationError("Correlation matrix must be PSD")
                L[i][j] = sqrt(max(0.0, residual))
            else:
                if L[j][j] > 1e-10:
                    L[i][j] = residual / L[j][j]
                elif abs(residual) > 1e-8:
                    raise EvidenceValidationError("Correlation matrix must be PSD")
    v = sum(se[i] * se[j] * a[i][j] for i in range(n) for j in range(n))
    if v < -1e-10:
        raise EvidenceValidationError("Negative variance")
    return max(0.0, v)

def odds_ratio_to_risk(odds_ratio: float, baseline_risk: float,
                       *, calibrated_baseline: bool = False) -> dict:
    """Algebraic demonstration only; blocked without explicitly calibrated baseline.

    Mathematical formula: OR*p0 / (1-p0 + OR*p0).
    """
    OR = _positive("odds ratio", odds_ratio)
    if not calibrated_baseline:
        return {"status": "BLOCKED_NO_CALIBRATED_BASELINE", "individual_risk": None}
    if not isinstance(baseline_risk, (int, float)) or not isfinite(float(baseline_risk)) or not 0 < baseline_risk < 1:
        raise EvidenceValidationError("Baseline must be a probability strictly between 0 and 1")
    return {"status": "MATHEMATICAL_ONLY_NOT_CLINICALLY_VALIDATED",
            "conditional_risk": OR * baseline_risk / (1 - baseline_risk + OR * baseline_risk),
            "individual_risk": None}
