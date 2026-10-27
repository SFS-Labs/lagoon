"""Claim-specific clinical validity gates for common chip-array variants.

Marker -> published trait association != inherited disease != malabsorption
!= laboratory-confirmed deficiency. This module reports *why* a requested
inference is/ is not justified. Never gives genotype-guided treatment doses.
"""
from __future__ import annotations
from math import isfinite
from .statistics import or_ci_to_log_effect, EvidenceValidationError

MICRONUTRIENT_ENDPOINTS={
  "serum_b12":{"domain":"CIRCULATING_BIOMARKER","clinical_deficiency_equivalent":False,
               "requires":["B12 assay","consider MMA or homocysteine when clinically indicated"],
               "differential":["diet and supplementation","metformin/other medications",
                               "pernicious anemia","gastric/ileal disease"]},
  "serum_iron":{"domain":"CIRCULATING_BIOMARKER","clinical_deficiency_equivalent":False,
                "requires":["CBC","ferritin","transferrin saturation","CRP where indicated"],
                "differential":["blood loss","inflammation/hepcidin","diet",
                                "intestinal disorders"]},
  "serum_vitamin_d":{"domain":"CIRCULATING_BIOMARKER","clinical_deficiency_equivalent":False,
                 "requires":["serum 25(OH)D"],"differential":["season/sunlight","adiposity",
                           "vitamin D binding protein","kidney/liver metabolism"]},
  "serum_folate":{"domain":"CIRCULATING_BIOMARKER","clinical_deficiency_equivalent":False,
                 "requires":["serum folate and B12 when indicated"],
                 "differential":["diet","medications","intestinal disease","utilization"]},
  "lactase_persistence":{"domain":"ENZYME_PHENOTYPE","clinical_deficiency_equivalent":False,
                 "requires":["food response or clinical breath test where appropriate"],
                 "differential":["ancestry","lactose-specific intestinal enzyme activity"]},
  "iron_overload":{"domain":"IRON_STORAGE_DISEASE_CANDIDATE","clinical_deficiency_equivalent":False,
                 "requires":["ferritin","transferrin saturation","confirm clinically significant HFE variants"],
                 "differential":["penetrance and family history","liver disease","secondary iron overload"]},
  "malabsorption":{"domain":"CLINICAL_SYNDROME","clinical_deficiency_equivalent":False,
                 "requires":["specific symptoms","biochemical deficiencies",
                             "validated gastroenterological evaluation where appropriate"],
                 "differential":["celiac disease","pernicious anemia",
                         "pancreatic exocrine insufficiency","bowel disease","diet","medications"]},
}
REQUIRE=["rsid","study_id","trait","endpoint","effect_allele","other_allele",
         "genome_build","study_orientation","effect_type","effect_size",
         "population","model","sample_size","replicated","source_url"]

def assess_locus_claim(study:dict, *, genotype:str|None, reference:dict,
                       ancestry_matching_evidence:bool=False)->dict:
    """Permit genotype dosage only with documented *study* orientation.

    Catalog rsID/risk allele alone never proves forward strand. Passing a
    record here validates explicit typed assertions, NOT their authenticity.
    Evidence URLs require independent comparison to the primary publication.
    """
    result={"rsid":study.get("rsid"),"status":"BLOCKED",
            "effect_allele_dosage":None,"absolute_personal_risk":None,
            "personal_deficiency_diagnosis":False,"blocking_reasons":[]}
    bad=result["blocking_reasons"]
    missing=[f for f in REQUIRE if study.get(f) in (None,"")]
    if missing:
        bad.append("missing_metadata:"+",".join(missing))
        return result
    phenotype=MICRONUTRIENT_ENDPOINTS.get(study.get("endpoint"))
    if not phenotype:
        bad.append("UNCLASSIFIED_CLINICAL_ENDPOINT")
    else:
        result["endpoint_interpretation"]=phenotype
    if study["genome_build"]!="GRCh37":
        bad.append("GENOME_BUILD_NOT_ALIGNED")
    if study["study_orientation"]!="documented_GRCh37_forward":
        bad.append("STUDY_EFFECT_ALLELE_ORIENTATION_UNVERIFIED")
    if reference.get("status")!="GRCH37_COORDINATE_ALLELES_MATCH":
        bad.append("PERSONAL_GENOTYPE_REFERENCE_NOT_ALIGNED")
    if ancestry_matching_evidence is not True:
        bad.append("ANCESTRY_MATCH_NOT_ESTABLISHED")
    if study["replicated"] is not True:
        bad.append("INDEPENDENT_REPLICATION_NOT_ESTABLISHED")
    if study["model"]!="per_allele_additive":
        bad.append("UNSUPPORTED_OR_UNVERIFIED_GENETIC_MODEL")
    allele=str(study["effect_allele"]).upper()
    other=str(study["other_allele"]).upper()
    if (allele not in ("A","C","G","T") or other not in ("A","C","G","T") or allele==other):
        bad.append("INVALID_EFFECT_OR_OTHER_ALLELE")
    elif {allele,other} in ({"A","T"},{"C","G"}):
        bad.append("PALINDROMIC_STUDY_ALLELE_FREQUENCY_REQUIRED")
    gt=(genotype or "").upper()
    if not genotype:
        bad.append("NO_PERSONAL_CALL")
    elif len(gt)!=2 or set(gt)-{allele,other}:
        bad.append("PERSONAL_CALL_NOT_ORIENTED_TO_PUBLISHED_ALLELE_PAIR")
    try:
        sample_size=int(study["sample_size"])
        if sample_size<100:
            bad.append("INSUFFICIENT_SAMPLE_INFORMATION")
    except (TypeError,ValueError,OverflowError):
        bad.append("BAD_SAMPLE_SIZE")
    et=study["effect_type"]
    try:
        eff=float(study["effect_size"])
        if not isfinite(eff):raise ValueError()
        if et=="odds_ratio":
            ci=study.get("confidence_interval")
            if not isinstance(ci,(list,tuple)) or len(ci)!=2:
                bad.append("OR_95_PERCENT_CI_MISSING")
            else:
                or_ci_to_log_effect(eff,ci[0],ci[1])
        elif et=="beta":
            unit=study.get("unit")
            se=study.get("standard_error")
            if not unit or se is None or not isfinite(float(se)) or float(se)<=0:
                bad.append("BETA_UNIT_OR_SE_MISSING")
        else:bad.append("UNSUPPORTED_EFFECT_MEASURE")
    except (ValueError,TypeError,OverflowError,EvidenceValidationError):
        bad.append("INVALID_QUANTITATIVE_EFFECT")
    # IMPORTANT: HFE iron overload and B12 biomarker changes should not be
    # reported as evidence of *intestinal micronutrient malabsorption*.
    result["malabsorption_mechanism_inferred"]=False
    result["study_authenticity_checked"]=False
    if bad:return result
    result["status"]="POPULATION_EFFECT_ELIGIBLE_FOR_HUMAN_REVIEW"
    result["effect_allele_dosage"]=gt.count(allele)
    result["effect_allele"]=allele
    result["model_unit"]=study.get("unit")
    result["effect_type"]=et
    result["effect_size_as_reported"]=eff
    result["publication_verification_required"]=True
    return result

def claim_scope(endpoint:str, asked_for:str="malabsorption")->dict:
    e=MICRONUTRIENT_ENDPOINTS.get(endpoint)
    if e is None:return {"status":"UNKNOWN_TRAIT_CANNOT_CLASSIFY"}
    return {"endpoint":endpoint,"domain":e["domain"],"question":asked_for,
           "supports_intestinal_malabsorption_diagnosis":False,
           "minimum_evidence_for_clinical_followup":e["requires"],
           "differential":e["differential"],
           "explanation":"A population-level SNP association cannot substitute for an individual's biochemical and clinical phenotype."}
