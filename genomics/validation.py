"""SFS Genomics: deterministic, non-diagnostic GRCh37 genotype and evidence gates.

Only public reference loci are embedded. No private genotypes, clinical records or
owner credentials are committed. All genotype inputs must remain in private runtime.
These checks are NOT laboratory confirmation or comprehensive medical validation.
"""
from __future__ import annotations
import re

RS = re.compile(r"^rs[0-9]{1,15}$", re.I)
BASES = frozenset("ACGT")
COMPLEMENT = str.maketrans("ACGT", "TGCA")

# GRCh37 forward genomic alleles, drawn from the linked primary registries.
# This is deliberately a SMALL auditable reference snapshot, not a genome build.
# For all remaining loci, defer to a live, versioned GRCh37 reference source.
LOCI = {
    "rs855791": {
        "gene": "TMPRSS6", "chr": "22", "pos": 37462936, "ref": "A", "alt": "G",
        "source": "https://www.ncbi.nlm.nih.gov/clinvar/314922001/",
        "endpoint": "circulating_iron_biomarker",
    },
    "rs1801133": {
        "gene": "MTHFR", "chr": "1", "pos": 11856378, "ref": "G", "alt": "A",
        "source": "https://www.ncbi.nlm.nih.gov/clinvar/variation/VCV000003520.60/",
        "endpoint": "folate_metabolism",
    },
    "rs1801131": {
        "gene": "MTHFR", "chr": "1", "pos": 11854476, "ref": "T", "alt": "G",
        "source": "https://www.ncbi.nlm.nih.gov/clinvar/variation/VCV000003521.123/",
        "endpoint": "folate_metabolism",
    },
    "rs1799945": {
        "gene": "HFE", "chr": "6", "pos": 26091179, "ref": "C", "alt": "G",
        "source": "https://www.ncbi.nlm.nih.gov/clinvar/RCV000394716/",
        "endpoint": "iron_homeostasis",
    },
    "rs4988235": {
        "gene": "MCM6/LCT", "chr": "2", "pos": 136608646, "ref": "G", "alt": "A",
        "source": "https://pmc.ncbi.nlm.nih.gov/articles/PMC7615474/",
        "endpoint": "lactase_persistence",
    },
}

def _ret(status: str, rsid: str, *, reasons=(), record=None, alt_dosage=None):
    return {
        "rsid": rsid,
        "status": status,
        "reasons": list(reasons),
        "reference": record,
        "forward_alt_allele_dosage": alt_dosage,
        "is_clinically_validated": False,
    }


def validate_call(
    rsid: str, chromosome, position, genotype,
    *, build: str = "GRCh37", reference: dict | None = None
) -> dict:
    """Compare an array genotype with a pinned GRCh37 forward-strand locus.

    Passing this quality gate establishes logical concordance, not that the
    laboratory call or DNA chip orientation was independently confirmed.
    """
    if not isinstance(rsid, str) or not RS.fullmatch(rsid):
        return _ret("INVALID_RSID", str(rsid))
    rid = rsid.lower()
    locus = reference if reference is not None else LOCI.get(rid)
    if genotype is None or genotype == "":
        return _ret("NO_CALL_OR_NOT_ON_ARRAY", rid, reasons=("absence is not a reference genotype",))
    if build != "GRCh37":
        return _ret("BUILD_UNVERIFIED", rid, reasons=("coordinate assembly requires explicit liftover",))
    if locus is None:
        return _ret("REFERENCE_NOT_YET_VERIFIED", rid, reasons=("no pinned forward reference; no allele inference",))
    public = {k: locus[k] for k in ("gene", "chr", "pos", "ref", "alt", "source", "endpoint") if k in locus}
    if str(chromosome) != str(locus.get("chr")) or position != locus.get("pos"):
        return _ret("GRCH37_COORDINATE_MISMATCH", rid, record=public)
    ref, alt = str(locus.get("ref", "")).upper(), str(locus.get("alt", "")).upper()
    if len(ref) != 1 or len(alt) != 1 or ref not in BASES or alt not in BASES or ref == alt:
        return _ret("REFERENCE_ALLELES_UNVERIFIED", rid, record=public)
    g = str(genotype).upper()
    if len(g) != 2 or any(x not in BASES for x in g):
        return _ret("INVALID_DIPLOID_BASES", rid, record=public)
    forward = set(g) <= {ref, alt}
    reverse = set(g.translate(COMPLEMENT)) <= {ref, alt}
    if forward and reverse:
        # Palindromic sites: C/G or A/T. Even with a coherent call,
        # reference-strand orientation cannot be inferred from letters alone.
        return _ret("PALINDROMIC_STRAND_UNRESOLVED", rid, record=public,
                    reasons=("complement-compatible alleles; no effect-direction claim",))
    if forward:
        return _ret("GRCH37_FORWARD_ALLELES_CONCORDANT", rid, record=public,
                    reasons=("array call is unconfirmed and research-only",),
                    alt_dosage=g.count(alt))
    if reverse:
        return _ret("REVERSE_COMPLEMENT_CANDIDATE_UNVERIFIED", rid, record=public,
                    reasons=("strand annotation required; do not auto-flip",))
    return _ret("ALLELES_NOT_IN_REFERENCE_SET", rid, record=public,
                reasons=("rsID or coordinate or platform call may disagree",))


def evaluate_study_claim(allele_check: dict, study: dict, requested_endpoint: str) -> dict:
    """Abstention-first gates for interpreting a published genetic effect.

    The function deliberately computes no individual probability or risk score.
    Harmonised sumstats metadata is essential: GWAS Catalog association API
    summaries alone do not establish forward effect-allele orientation.
    """
    reasons = []
    if allele_check.get("status") != "GRCH37_FORWARD_ALLELES_CONCORDANT":
        reasons.append("GENOTYPE_NOT_UNAMBIGUOUSLY_REFERENCE_ALIGNED")
    if study.get("harmonised") is not True:
        reasons.append("GWAS_EFFECT_ALLELES_NOT_PROVEN_HARMONISED")
    if study.get("build") != "GRCh37":
        reasons.append("STUDY_BUILD_NOT_MATCHED_TO_GRCH37")
    ref = allele_check.get("reference") or {}
    study_alleles = (study.get("effect_allele"), study.get("other_allele"))
    if any(not isinstance(x, str) or len(x) != 1 for x in study_alleles):
        reasons.append("STUDY_EFFECT_AND_OTHER_ALLELE_REQUIRED")
    elif {x.upper() for x in study_alleles} != {ref.get("ref"), ref.get("alt")}:
        reasons.append("STUDY_ALLELE_SET_MISMATCH")
    if study.get("effect_type") not in ("beta", "odds_ratio", "hazard_ratio"):
        reasons.append("STUDY_EFFECT_TYPE_UNSUPPORTED")
    if not isinstance(study.get("effect_value"), (float, int)) or isinstance(study.get("effect_value"), bool):
        reasons.append("STUDY_EFFECT_VALUE_MISSING")
    if study.get("endpoint") != requested_endpoint:
        reasons.append("BIOMARKER_OR_PROXY_IS_NOT_REQUESTED_CLINICAL_ENDPOINT")
    if not study.get("ancestry_matched"):
        reasons.append("ANCESTRY_APPLICABILITY_UNVERIFIED")
    if not study.get("independent_replication"):
        reasons.append("INDEPENDENT_REPLICATION_UNVERIFIED")
    if not study.get("ld_adjusted"):
        reasons.append("LD_DEPENDENCE_UNRESOLVED")
    if study.get("endpoint_kind") == "clinical" and not study.get("clinically_calibrated"):
        reasons.append("CLINICAL_RISK_CALIBRATION_MISSING")
    return {
        "status": "RESEARCH_EFFECT_GATES_PASSED" if not reasons else "ABSTAIN_FROM_EFFECT_OR_RISK",
        "blockers": reasons,
        "can_report_individual_disease_probability": False,
        "reported_outcome": requested_endpoint,
        "study_identifier": study.get("id"),
    }


def assess_ld_double_counting(r2, *, same_population: bool, same_build: bool) -> dict:
    if not same_population or not same_build or r2 is None:
        return {"status": "LD_CONTEXT_UNVERIFIED", "safe_to_sum_independently": False}
    if not isinstance(r2, (int, float)) or isinstance(r2, bool) or not (0 <= r2 <= 1):
        return {"status": "INVALID_LD_R2", "safe_to_sum_independently": False}
    # r² lacks phase/direction; low r² alone also does not validate a score.
    return {"status": "LD_DEPENDENCE_PRESENT" if r2 >= 0.1 else "LD_LOW_NOT_SUFFICIENT",
            "r2": r2, "safe_to_sum_independently": False,
            "note": "r² is unsigned; haplotype phase and model covariance unknown"}
