"""GWAS Catalog v2 association audit for local, nonclinical research.

Every remote request contains only one public rsID. Genotype/chromosome/
coordinate remain local. Never infer clinical penetrance from biomarker GWAS.
"""
from __future__ import annotations
from math import isfinite
import re
from typing import Any
from .research import URLS, get_json, verify_reported_locus

_RE = re.compile(r"^rs[0-9]{1,15}$", re.I)
_ONE = re.compile(r"^[ACGT]$")
_COMP = str.maketrans("ACGT","TGCA")
def _association_rows(root):
    if not isinstance(root, dict):
        raise ValueError("Unexpected GWAS provider shape")
    rows=root.get("_embedded",{}).get("associations")
    if not isinstance(rows, list):
        raise ValueError("Missing _embedded.associations in GWAS v2 response")
    return rows
def _published_allele_set(record,rsid):
    declared=set()
    for obj in record.get("snp_allele",[]):
        if not isinstance(obj,dict) or obj.get("rs_id","").lower()!=rsid:continue
        allele=str(obj.get("effect_allele","")).upper()
        if _ONE.fullmatch(allele):declared.add(allele)
    for x in record.get("snp_effect_allele",[]):
        if isinstance(x,str) and x.lower().startswith(rsid+"-"):
            a=x.split("-",1)[-1].upper()
            if _ONE.fullmatch(a):declared.add(a)
    return declared

def public_evidence_snapshot(rsid: str, limit: int = 15)->dict:
    if not isinstance(rsid,str) or not _RE.fullmatch(rsid):
        raise ValueError("Valid public rsID required")
    if not isinstance(limit,int) or isinstance(limit,bool) or not 1<=limit<=30:
        raise ValueError("limit must be in [1, 30]")
    rsid=rsid.lower()
    raw=get_json(URLS["gwas_catalog_v2"], {"rs_id":rsid,"page":0,"size":limit})
    parsed=[]
    for row in _association_rows(raw):
        if not isinstance(row,dict) or row.get("multi_snp_haplotype") or row.get("snp_interaction"):
            continue
        effect_set=_published_allele_set(row,rsid)
        if not effect_set:continue
        p=row.get("p_value")
        try:pval=float(p)
        except (ValueError,TypeError,OverflowError):pval=None
        if pval is not None and (not isfinite(pval) or pval<0 or pval>1):pval=None
        parsed.append({"association_id":str(row.get("association_id","")),
           "study_accession":str(row.get("accession_id","")),
           "pubmed_id":str(row.get("pubmed_id","")),
           "author":str(row.get("first_author",""))[:120],
           "reported_trait":row.get("reported_trait",[])[:4] if isinstance(row.get("reported_trait"),list) else [],
           "efo_traits":row.get("efo_traits",[])[:4] if isinstance(row.get("efo_traits"),list) else [],
           "effect_allele_as_reported":sorted(effect_set),
           "reported_beta":str(row.get("beta",""))[:100],
           "reported_ci_lower":row.get("ci_lower"),
           "reported_ci_upper":row.get("ci_upper"),
           "reported_p_value":pval,
           "association_url":"https://www.ebi.ac.uk/gwas/associations/"+str(row.get("association_id","")),
           "interpretation_state":"SOURCE_METADATA_NOT_EFFECT_ALLELE_HARMONIZED"})
    return {"rsid":rsid,"provider":"GWAS Catalog v2",
       "privacy":"public rsID only; no person-specific data passed to external APIs",
       "scope":"first page only; not all studies or LD-corrected independent signals",
       "associations":parsed,"record_count":len(parsed)}

def orientation_gate(rsid, reported_effect_allele:str, chromosome:str,position:str,
                     genotype:str, build:str="GRCh37", *,
                     reference_verification:dict|None=None)->dict:
    """No signed effect or dosage without a verified study-to-reference strand.

    The GWAS REST v2 study allele's strand is not proven by simply seeing
    that it is in the Ensembl GRCh37 allele string.
    """
    if not isinstance(reported_effect_allele,str) or not _ONE.fullmatch(reported_effect_allele.upper()):
        return {"status":"INVALID_PUBLISHED_ALLELE","effect_allele_dosage":None}
    ref=reference_verification
    if ref is None:
        ref=verify_reported_locus(rsid,chromosome,position,genotype,build)
    status=ref.get("status","UNVERIFIED")
    if status!="GRCH37_COORDINATE_ALLELES_MATCH":
        return {"status":"PERSONAL_COORDINATE_OR_STRAND_UNVERIFIED",
                "reference_check":status,"effect_allele_dosage":None}
    return {"status":"STUDY_EFFECT_ALLELE_STRAND_NOT_INDEPENDENTLY_VERIFIED",
            "personal_locus":rsid,"reference_check":status,
            "effect_allele_as_reported":reported_effect_allele.upper(),
            "effect_allele_dosage":None,
            "note":"An Ensembl coordinate match is necessary but not sufficient to orient the published effect allele. Do not calculate dosage yet."}

def explore_public_study_locus(rsid:str, local_call:dict|None=None, build="unknown")->dict:
    """Use for data discovery; local genotypes are never submitted."""
    snapshot=public_evidence_snapshot(rsid)
    if not local_call:
        snapshot["local_call_status"]="NOT_GENOTYPED"
        return snapshot
    verification=verify_reported_locus(rsid,local_call["chromosome"],local_call["position"],
                                        local_call["genotype"],build)
    snapshot["reference_check"]=verification
    snapshot["local_call_status"]="ARRAY_CALL_NOT_CLINICALLY_CONFIRMED"
    snapshot["interpretation"]=[
       {"association_id":a["association_id"],
        "orientation":orientation_gate(rsid,a["effect_allele_as_reported"][0],
           local_call["chromosome"],local_call["position"],local_call["genotype"],build,
           reference_verification=verification)}
       for a in snapshot["associations"] if len(a["effect_allele_as_reported"])==1]
    return snapshot
