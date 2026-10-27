"""Bounded GWAS v2 trait-first candidate scan against a private array.

Returns candidates for HUMAN REVIEW, not personal effect estimates.
Only public trait labels leave the local machine; genotypes never do.
"""
import re
from .research import get_json, URLS

_ALLOWED = {
    "b12": "vitamin B12 measurement",
    "folate": "folate measurement",
    "vitamin_d": "vitamin D measurement",
    "iron": "iron measurement",
    "ferritin": "ferritin measurement",
    "zinc": "zinc measurement",
    "calcium": "calcium measurement",
    "magnesium": "magnesium measurement",
    "selenium": "selenium measurement",
}
_RS = re.compile(r"\brs[0-9]+\b", re.I)

def _items(document):
    if isinstance(document, list):
        return document
    if not isinstance(document, dict):
        return None
    for key in ("content", "data", "results", "items", "associations"):
        if isinstance(document.get(key), list):
            return document[key]
    embedded = document.get("_embedded")
    if isinstance(embedded, dict):
        for value in embedded.values():
            if isinstance(value, list):
                return value
    return None

def scan_trait_calls(calls: dict, trait: str, pages: int = 2) -> dict:
    """Short discovery window; explicitly bounded, incomplete genome coverage.

    No source effect allele, OR, beta, CI or ancestry is harmonized here.
    """
    if trait not in _ALLOWED:
        raise ValueError("Unsupported ontology trait alias")
    if not isinstance(pages, int) or isinstance(pages, bool) or not (1 <= pages <= 5):
        raise ValueError("Page limit must be 1 through 5")
    found = {}
    inspected = 0
    completed = 0
    for page in range(pages):
        params = {"efo_trait": _ALLOWED[trait], "page": page, "size": 100,
                  "show_child_traits": "false"}
        raw = get_json(URLS["gwas_catalog_v2"], params)
        associations = _items(raw)
        if associations is None:
            raise RuntimeError("Unknown GWAS Catalog v2 response shape: no candidate claims permitted")
        completed += 1
        if not associations:
            break
        for association in associations:
            inspected += 1
            if not isinstance(association, dict):
                continue
            # Limit selection to explicit rsID-bearing fields, not generic prose.
            identifier_fields = [v for k, v in association.items()
                                 if isinstance(v, str) and ("rs" in k.lower() or "snp" in k.lower()
                                                            or "variant" in k.lower()
                                                            or "strongest" in k.lower())]
            for v in identifier_fields:
                for rsid in set(match.lower() for match in _RS.findall(v)):
                    if rsid in calls:
                        found.setdefault(rsid, {
                            "rsid": rsid, "observed_genotype": calls[rsid]["genotype"],
                            "chromosome": calls[rsid]["chromosome"],
                            "position": calls[rsid]["position"],
                            "effect": "NOT_HARMONIZED",
                            "candidate_status": "EXPLORATORY_ONLY_REQUIRES_STUDY_REVIEW",
                            "association_ids": []})
                        aid = association.get("id") or association.get("accessionId")
                        if aid and len(found[rsid]["association_ids"]) < 8:
                            found[rsid]["association_ids"].append(str(aid)[:120])
    return {
        "requested_trait": trait, "query": _ALLOWED[trait],
        "provider": "GWAS Catalog v2, curated top associations only",
        "inspected_association_records": inspected, "completed_pages": completed,
        "page_budget_exhausted": completed == pages,
        "raw_input_not_uploaded": True,
        "no_match_means": "No match in the retrieved subset, NOT no genetic association",
        "statistical_limit": "Effect allele, study population, p value, CI, LD and ancestry unverified",
        "matched_candidates": list(found.values())[:100],
    }
