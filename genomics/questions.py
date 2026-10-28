"""Phenotype-oriented, evidence-aware micronutrient question answering.

No diagnostic 'risk score' is produced from consumer array variants.
Each observed marker is classified by physiological mechanism and limitations.
"""
from __future__ import annotations
from .engine import analyze, EVIDENCE

NUTRIENT = {
    "b12": {"traits": ("B12",), "lab": "Vitamin B12; methylmalonic acid if clinically indicated",
            "differential": "Diet, pernicious anaemia, gastric/ileal disease, medication effects, transport proteins"},
    "iron": {"traits": ("iron", "Ferritin"), "lab": "Complete blood count, ferritin, transferrin saturation, CRP",
             "differential": "Blood loss, diet, inflammation/hepcidin, gastrointestinal disease, iron transport"},
    "vitamin_d": {"traits": ("vitamin D", "25(OH)"), "lab": "Serum 25-hydroxyvitamin D",
                  "differential": "Skin synthesis, season, adiposity, liver and kidney handling, binding protein"},
    "folate": {"traits": ("Folate",), "lab": "Folate with vitamin B12 and, where indicated, homocysteine",
               "differential": "Intake, medications, intestinal disease, processing and utilization"},
    "lactose": {"traits": ("Lactase",), "lab": "Dietary correlation; hydrogen breath test when indicated",
                "differential": "Lactose-specific enzyme capacity; not generalized micronutrient malabsorption"},
}
EXCLUSIONS = [
    {"hypothesis": "Celiac disease and HLA-DQ2/DQ8", "reason": "Complete HLA haplotypes cannot be inferred from this selected consumer SNP panel.",
     "follow_up": "tTG-IgA + total IgA in a person consuming gluten if clinically indicated; validated HLA typing only for relevant questions"},
    {"hypothesis": "Rare hereditary B12 malabsorption (CUBN/AMN and related genes)", "reason": "Unmeasured pathogenic variants and structural variants are not excluded by common array SNPs.",
     "follow_up": "Phenotype-driven clinical testing and, when appropriate, germline sequencing"},
    {"hypothesis": "Rare hereditary folate, thiamine, riboflavin or metal transporter disorders", "reason": "No validated negative screening from a handful of markers.",
     "follow_up": "Biochemical and genetic testing guided by symptoms and biochemical phenotype"},
    {"hypothesis": "Acquired intestinal malabsorption", "reason": "Cannot be reliably confirmed or excluded by SNP data alone.",
     "follow_up": "Targeted gastroenterological differential diagnosis if clinically indicated"},
]

def answer_question(calls: dict, *, nutrient: str = "all", build: str = "unknown") -> dict:
    if nutrient not in (*NUTRIENT.keys(), "all"):
        raise ValueError("Unknown nutrient filter")
    base = analyze(calls, build)
    selected = []
    for item in base["results"]:
        if nutrient != "all" and not any(t.lower() in item["trait"].lower() for t in NUTRIENT[nutrient]["traits"]):
            continue
        status = item["status"]
        # Each candidate gets the true status of genotype observation and
        # of the still-unverified external coordinate/strand harmonization.
        selected.append({
            "rsid": item["rsid"], "gene": item["gene"], "genotype": item.get("genotype"),
            "array_call_status": status, "mechanism": item["domain"],
            "effect_as_reported_in_literature": item["effect"],
            "study_population": item["population"], "genetic_model": item["model"],
            "study_url": item["study"],
            "study_curation_level": item["evidence_level"],
            "interpretation_gate": ("UNMEASURED" if status == "NOT_GENOTYPED" else
                                    "UNRESOLVED_STRAND" if status != "matching_reported_strand" else
                                    "ARRAY_CALL_ONLY_NOT_CLINICALLY_VALIDATED"),
        })
    focus = NUTRIENT if nutrient == "all" else {nutrient: NUTRIENT[nutrient]}
    return {
        "question": "Which SNP patterns could contribute to micronutrient status or malabsorption?",
        "filter": nutrient,
        "genome_build": build,
        "clinical_conclusion": "UNDETERMINED; NO VALIDATED PERSONALISED MALABSORPTION RISK",
        "candidate_snps": selected,
        "number_of_associations_reviewed": len(selected),
        "lab_and_differential": {
            key: {"labs": value["lab"], "differential": value["differential"]}
            for key, value in focus.items()
        },
        "not_excluded": EXCLUSIONS,
        "analytical_guardrails": [
            "A GWAS biomarker change is NOT the same outcome as intestinal malabsorption or clinically significant deficiency.",
            "Missing loci and variant classes are unknown, not negative.",
            "Individual penetrance and absolute probability require externally validated population-calibrated models.",
            "Do not add linked allelic effects or use a SNP panel as proof of a diagnosis.",
            "Reported strand is not independently reference-verified until the dedicated Ensembl check passes.",
        ],
        "evidence_policy": "Primary study effect is retained verbatim as population evidence; no new numerical estimates invented.",
    }
