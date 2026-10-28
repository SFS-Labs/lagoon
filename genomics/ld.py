"""LD quality control using free Ensembl GRCh37 pairwise 1000 Genomes data.

References are *public rsIDs only*: neither chip genotypes nor clinical
history are transmitted. r² alone has no direction/sign and must never be
inserted as covariance in a polygenic risk model.
"""
from __future__ import annotations
import itertools
import math
import re
from .research import get_json, URLS

RS = re.compile(r"^rs[0-9]{1,15}$", re.I)
POPULATIONS = {
    "EUR": "1000GENOMES:phase_3:EUR",
    "AFR": "1000GENOMES:phase_3:AFR",
    "AMR": "1000GENOMES:phase_3:AMR",
    "EAS": "1000GENOMES:phase_3:EAS",
    "SAS": "1000GENOMES:phase_3:SAS",
}
MAX_VARIANTS=5
MAX_QUERIES=10

def _number(v):
    try:
        x=float(v)
        if math.isfinite(x) and 0<=x<=1:return x
    except (ValueError,TypeError,OverflowError):pass
    return None

def _rows(doc):
    if isinstance(doc,list):return doc
    if isinstance(doc,dict):
        if "r2" in doc:return [doc]
        for key in ("data","results","ld","values"):
            if isinstance(doc.get(key),list):return doc[key]
    raise ValueError("Unrecognised Ensembl LD response; cannot declare independence")

def reference_pairwise_ld(rsid_a:str,rsid_b:str,*,population:str="EUR")->dict:
    if not all(isinstance(r,str) and RS.fullmatch(r) for r in (rsid_a,rsid_b)):
        raise ValueError("Use two valid public rsIDs only")
    if rsid_a.lower()==rsid_b.lower():
        raise ValueError("Pairwise LD requires distinct rsIDs")
    if population not in POPULATIONS:raise ValueError("Unrecognised reference population")
    a,b=sorted((rsid_a.lower(),rsid_b.lower()))
    source=URLS["ensembl_ld_pairwise"]+a+"/"+b
    response=get_json(source,{"population_name":POPULATIONS[population],"content-type":"application/json"})
    parsed=[]
    for row in _rows(response):
        if not isinstance(row,dict):continue
        pop=row.get("population_name",row.get("population"))
        if pop is not None and pop!=POPULATIONS[population]:continue
        r2=_number(row.get("r2"))
        dp=_number(row.get("d_prime"))
        if r2 is not None:
            parsed.append((r2,dp))
    if not parsed:
        return {"rsids":[a,b],"status":"LD_NOT_AVAILABLE","r2":None,
                "population":POPULATIONS[population],"source":source,
                "avoid_independent_sum":True}
    # Multiple values for the *same* pair/population without a unique
    # definition must not be cherry-picked as low LD.
    if len({round(x[0],6) for x in parsed})>1:
        return {"rsids":[a,b],"status":"CONFLICTING_LD_RECORDS","r2":None,
                "population":POPULATIONS[population],"source":source,
                "avoid_independent_sum":True}
    value=parsed[0][0]
    return {"rsids":[a,b],"status":("HIGH_LD" if value>=0.8 else
                       "MODERATE_LD" if value>=0.2 else "LOW_LD_REFERENCE"),
            "r2":value,"d_prime":parsed[0][1],
            "population":POPULATIONS[population],"source":source,
            "avoid_independent_sum":value>=0.2,
            "effect_direction":None,
            "warning":"Population reference r² is not a signed GWAS effect-estimator covariance."}

def identify_ld_blocks(rsids:list[str], *,population="EUR")->dict:
    if not isinstance(rsids,list) or not 2<=len(rsids)<=MAX_VARIANTS:
        raise ValueError("2–5 distinct public rsIDs required; maximum 10 external pair calls")
    if not all(isinstance(x,str) and RS.fullmatch(x) for x in rsids):
        raise ValueError("Only public rsIDs accepted")
    uniq=list(dict.fromkeys(x.lower() for x in rsids))
    if len(uniq)!=len(rsids):raise ValueError("Repeated rsID")
    if population not in POPULATIONS:raise ValueError("Reference population unknown")
    edges=[]
    parent={x:x for x in uniq}
    def find(x):
        while parent[x]!=x:
            x=parent[x]
        return x
    def union(a,b):
        parent[find(b)]=find(a)
    for a,b in itertools.combinations(uniq,2):
        try:
            pair=reference_pairwise_ld(a,b,population=population)
        except RuntimeError:
            pair={"rsids":[a,b],"status":"UPSTREAM_UNAVAILABLE","r2":None,
                  "population":POPULATIONS[population],"avoid_independent_sum":True}
        edges.append(pair)
        if pair["status"]=="HIGH_LD":union(a,b)
    blocks={}
    for x in uniq:blocks.setdefault(find(x),[]).append(x)
    return {"population":POPULATIONS[population],"reference":"Ensembl GRCh37 / 1000 Genomes phase 3",
            "pairs":edges,"high_ld_clusters":list(blocks.values()),
            "unknown_pairs":[p["rsids"] for p in edges if p["r2"] is None],
            "score_policy":"NO_SUM: no effect-score combination until study allele orientation, model, LD signs and independent replication validated",
            "population_is_reference_not_inferred_personal_ancestry":True,
            "queries":len(edges)}
