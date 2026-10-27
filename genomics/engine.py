"""Privacy-preserving, deterministic consumer-genotype interpretation core.

No medical diagnoses. Only explicitly sourced population associations are reported.
Only raw SNP identifiers (never genotypes) may be sent to external databases.
"""
from __future__ import annotations

import csv
import json
import re
from pathlib import Path
from typing import Any

RSID = re.compile(r"^rs[0-9]+$", re.I)
COMPLEMENT = str.maketrans("ACGT", "TGCA")
TOPIC_SYNONYMS = {
    "micronutrients": "micronutrients", "vitamins": "micronutrients",
    "malabsorption": "micronutrients", "mangel": "micronutrients",
    "mikronährstoffe": "micronutrients", "nutrient": "micronutrients",
}
# Only effect directions supported by the cited primary study or meta-analysis.
# Do not infer any individual penetrance, absolute risk, treatment or doses.
EVIDENCE: list[dict[str, Any]] = [
    dict(rsid="rs601338", gene="FUT2", trait="Serum-Vitamin-B12",
         domain="circulating_biomarker", allele_set="AG", effect_allele="A",
         model="AA versus GA/GG", detail="AA (non-secretor) showed 16–18% higher total serum B12; not evidence of superior intestinal absorption or cellular B12 sufficiency.",
         effect="16–18% higher mean serum B12 for AA vs GA/GG", population="Irish young adults; n=2,232",
         study="https://academic.oup.com/hmg/article/26/24/4975/4460048",
         evidence_level="replicated_association", clinical_test="B12 plus methylmalonic acid when indicated"),
    dict(rsid="rs855791", gene="TMPRSS6", trait="Serum iron / transferrin saturation",
         domain="circulating_biomarker", allele_set="CT", effect_allele="T",
         model="per T allele", detail="Iron decreased 0.18 SD and transferrin saturation 0.20 SD per T allele in research cohorts. This does not establish malabsorption.",
         effect="−0.18 SD serum iron; −0.20 SD transferrin saturation per T allele",
         population="Australian and Dutch cohorts; findings not universal",
         study="https://pmc.ncbi.nlm.nih.gov/articles/PMC3135421/",
         evidence_level="replicated_association", clinical_test="CBC, ferritin, transferrin saturation and CRP as appropriate"),
    dict(rsid="rs10741657", gene="CYP2R1", trait="25(OH)-vitamin D",
         domain="circulating_biomarker", allele_set="AG", effect_allele="G",
         model="per G allele; meta-analysis", detail="G allele is associated with lower vitamin D levels; effect is small and context-dependent, not evidence of gut malabsorption.",
         effect="OR 1.09 (95% CI 1.03–1.15) for vitamin-D deficiency per G allele in studied cohorts",
         population="Meta-analysis across studied populations, variable heterogeneity",
         study="https://pubmed.ncbi.nlm.nih.gov/30120973/",
         evidence_level="meta_analysis_association", clinical_test="Serum 25(OH)D, interpretation in clinical context"),
    dict(rsid="rs2282679", gene="GC", trait="Total circulating 25(OH)-vitamin D",
         domain="circulating_biomarker", allele_set="AC", effect_allele=None,
         model="genome-wide association", detail="Association with vitamin-D-binding protein and total 25(OH)D; potential ancestry/assay effects. Effect allele needs strand harmonisation before individual classification.",
         effect="GWAS P=1.9×10⁻¹⁰⁹; not an individual absolute risk estimate",
         population="GWAS discovery + replication cohorts, chiefly European ancestry",
         study="https://pmc.ncbi.nlm.nih.gov/articles/PMC3086761/",
         evidence_level="replicated_association", clinical_test="Serum 25(OH)D, not inferred absorption"),
    dict(rsid="rs12785878", gene="DHCR7/NADSYN1", trait="25(OH)-vitamin D",
         domain="circulating_biomarker", allele_set="GT", effect_allele=None,
         model="genome-wide association", detail="Associated with vitamin-D synthesis pathway; cannot infer an individual's deficiency probability from this marker alone.",
         effect="GWAS locus P=2.1×10⁻²⁷",
         population="GWAS discovery and replication cohorts",
         study="https://pubmed.ncbi.nlm.nih.gov/20541252/",
         evidence_level="replicated_association", clinical_test="Serum 25(OH)D"),
    dict(rsid="rs4988235", gene="MCM6/LCT", trait="Lactase persistence",
         domain="substrate_specific_digestion", allele_set="AG", effect_allele=None,
         model="adult lactase-persistence tagging in European ancestry", detail="GG commonly indicates lactase non-persistence in relevant populations; lactose digestion is not generalized micronutrient malabsorption. Allelic patterns differ across ancestries.",
         effect="Qualitative genotype–phenotype association; no calibrated absolute probability",
         population="Predominantly European ancestry; not universal",
         study="https://www.ncbi.nlm.nih.gov/books/NBK534631/",
         evidence_level="established_functional_association", clinical_test="If symptomatic: dietary history, hydrogen breath test as indicated"),
    dict(rsid="rs1801133", gene="MTHFR", trait="Folate / homocysteine handling",
         domain="metabolic_processing", allele_set="AG", effect_allele=None,
         model="C677T common variant", detail="Common genotype cannot diagnose folate deficiency or impaired intestinal absorption; homocysteine and measured folate are more informative.",
         effect="No calibrated malabsorption effect estimate",
         population="Populations vary", study="https://www.ncbi.nlm.nih.gov/books/NBK66131/",
         evidence_level="mechanistic_context_only", clinical_test="Serum folate, B12 and homocysteine when indicated"),
    dict(rsid="rs1801131", gene="MTHFR", trait="Folate / homocysteine handling",
         domain="metabolic_processing", allele_set="GT", effect_allele=None,
         model="A1298C common variant", detail="Isolated heterozygosity is not evidence of clinically significant folate deficiency or malabsorption.",
         effect="No calibrated deficiency risk for isolated heterozygosity",
         population="Populations vary", study="https://pubmed.ncbi.nlm.nih.gov/36662122/",
         evidence_level="insufficient_clinical_utility", clinical_test="Measured folate and B12 if clinical indication"),
    dict(rsid="rs1799945", gene="HFE", trait="Iron overload predisposition",
         domain="differential_diagnosis", allele_set="CG", effect_allele=None,
         model="H63D", detail="H63D carrier status alone is not evidence of iron deficiency or intestinal malabsorption. C282Y genotype and iron studies may be relevant for overload.",
         effect="Cannot estimate iron-deficiency risk from H63D alone",
         population="Ancestry-dependent", study="https://pmc.ncbi.nlm.nih.gov/articles/PMC10224841/",
         evidence_level="established_genetic_context", clinical_test="Ferritin + transferrin saturation"),
    dict(rsid="rs1800562", gene="HFE", trait="Iron overload predisposition",
         domain="differential_diagnosis", allele_set="AG", effect_allele=None,
         model="C282Y", detail="Relevant to iron-overload differential diagnosis, particularly combined with H63D. Missing data must not be interpreted as reference genotype.",
         effect="Risk depends on complete genotype, sex, clinical phenotype",
         population="Ancestry-dependent", study="https://easl.eu/publication/easl-clinical-practice-guidelines-on-haemochromatosis/",
         evidence_level="established_genetic_context", clinical_test="Transferrin saturation, ferritin, clinician confirmation"),
]
CLINICAL_CATEGORIES = {
    "intestinal_malabsorption": "Gut malabsorption cannot be diagnosed by these consumer SNPs; evaluate celiac disease, pancreatic disease, inflammation and medicines when appropriate.",
    "status_vs_absorption": "Circulating concentrations, synthesis, transport and intracellular utilization are distinct mechanisms.",
    "hla": "Accurate celiac HLA-DQ2/DQ8 haplotype determination cannot be inferred from an arbitrary short SNP list.",
    "missing": "Not genotyped means UNKNOWN, never wild-type.",
    "calibration": "No personal absolute risk, additive OR or polygenic risk score without a validated ancestry-matched model.",
}
MAX_BYTES = 80 * 1024 * 1024
MAX_ROWS = 2_000_000

class GenotypeError(ValueError):
    pass

def parse_calls(path: str | Path) -> dict[str, Any]:
    p = Path(path)
    if not p.is_file() or p.stat().st_size > MAX_BYTES:
        raise GenotypeError("Raw-data file missing or exceeds 80 MiB")
    calls: dict[str, dict[str, str]] = {}
    problems: list[str] = []
    skipped = 0
    seen_rows = 0
    build_text = ""
    with p.open("r", encoding="utf-8-sig", errors="replace", newline="") as stream:
        for line in stream:
            if line.lstrip().startswith("#"):
                if len(build_text) < 4000:
                    build_text += line[:250] + " "
                continue
            if not line.strip():
                continue
            seen_rows += 1
            if seen_rows > MAX_ROWS:
                raise GenotypeError("Too many variant rows")
            try:
                row = next(csv.reader([line], delimiter="\t" if "\t" in line else ","))
                row = [v.strip().strip('"') for v in row]
                if row and row[0].lower() in ("rsid", "rs_id", "snp"):
                    continue
                if len(row) < 4 or not RSID.fullmatch(row[0]):
                    skipped += 1
                    continue
                rsid, chromosome, pos, allele = row[:4]
                gt = allele.upper().replace(" ", "").replace("/", "").replace("|", "")
                if gt in ("--", "NN", "N", "00", "-"):
                    skipped += 1
                    continue
                if not re.fullmatch(r"[ACGT]{1,2}", gt):
                    skipped += 1
                    continue
                if not re.fullmatch("[0-9]+", pos):
                    skipped += 1
                    continue
                candidate = dict(genotype=gt, chromosome=chromosome, position=pos)
                prior = calls.get(rsid.lower())
                if prior and prior != candidate:
                    problems.append(f"conflicting_call:{rsid}")
                    calls.pop(rsid.lower(), None)
                elif f"conflicting_call:{rsid}" not in problems:
                    calls[rsid.lower()] = candidate
            except (csv.Error, ValueError):
                skipped += 1
    b = build_text.lower()
    build = "GRCh37" if "build 37" in b or "grch37" in b or "hg19" in b else "GRCh38" if "build 38" in b or "grch38" in b or "hg38" in b else "unknown"
    return dict(calls=calls, qc=dict(rows=seen_rows, valid=len(calls), skipped=skipped,
                                    build=build, issues=problems[:50],
                                    raw_file_hash_published=False))

def check_alleles(genotype: str, allele_set: str) -> tuple[str, str | None]:
    """Never silently complement/misclassify ambiguous or mismatched genotype calls."""
    alleles = set(allele_set)
    got = set(genotype)
    if got <= alleles:
        return "matching_reported_strand", "".join(sorted(genotype))
    if set(genotype.translate(COMPLEMENT)) <= alleles:
        return "reverse_complement_candidate_UNVERIFIED", None
    return "ALLELE_MISMATCH", None

def analyze(calls: dict[str, dict[str, str]], build: str = "unknown") -> dict[str, Any]:
    results = []
    for item in EVIDENCE:
        record = calls.get(item["rsid"])
        entry = {k: v for k, v in item.items()}
        if record is None:
            entry.update(status="NOT_GENOTYPED", genotype=None, effect_allele_count=None)
        else:
            status, normalized = check_alleles(record["genotype"], item["allele_set"])
            # Coordinates must be validated against an authoritative GRCh37 lookup
            # before this becomes a verified genetic finding.
            entry.update(status=status, genotype=record["genotype"],
                         chromosome=record["chromosome"], position=record["position"],
                         effect_allele_count=(normalized.count(item["effect_allele"])
                                              if normalized and item["effect_allele"] else None))
        results.append(entry)
    matched = [r for r in results if r["status"] == "matching_reported_strand"]
    return dict(schema_version="1.0", status="RESEARCH_ONLY_NOT_CLINICALLY_VALIDATED",
                raw_build=build, build_requirement="GRCh37 coordinate confirmation and variant normalization required",
                analyzed_loci=len(EVIDENCE), matched_loci=len(matched),
                results=results, limitations=CLINICAL_CATEGORIES,
                conclusions=[
                    "No calibrated individual absolute risk of idiopathic deficiency or malabsorption is available from this panel.",
                    "Markers of biomarker concentrations are not equivalent to intestinal malabsorption.",
                    "Do not combine correlated vitamin-D GWAS variants as independent odds ratios.",
                    "Clinically significant hereditary absorption disorders or celiac HLA haplotypes require appropriate clinical assessment.",
                ],
                relevant_labs=["Blood count and ferritin/transferrin saturation for iron concern",
                               "Serum B12 with methylmalonic acid when indicated",
                               "Serum 25(OH)D for vitamin D concern",
                               "Folate with B12 and homocysteine when clinically relevant",
                               "tTG-IgA plus total IgA if celiac disease is suspected while eating gluten"])

def research_summary(report: dict[str, Any]) -> str:
    lines = ["# Micronutrient genetics — research summary", "",
             "Interpretation: research-only consumer array data; not a diagnosis.", ""]
    for r in report["results"]:
        gt = r.get("genotype") or "not measured"
        lines.append(f"## {r['gene']} {r['rsid']} — {gt}")
        lines.append(f"Variant status: {r['status']}. Outcome class: {r['domain']}.")
        lines.append(f"Evidence: {r['effect']} ({r['model']}). Population: {r['population']}.")
        lines.append(f"Interpretation: {r['detail']}")
        lines.append(f"Primary source: {r['study']}")
        if r.get("effect_allele_count") is not None:
            lines.append(f"Effect-allele copies in reported strand: {r['effect_allele_count']}; NOT a personalised risk score.")
        lines.append("")
    lines.extend(["## Limits", *[f"- {v}" for v in report["limitations"].values()],
                  "", "## Clinically useful follow-up", *[f"- {x}" for x in report["relevant_labs"]]])
    return "\n".join(lines)
