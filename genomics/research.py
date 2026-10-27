"""External public research adapters. Never transmit personal genotypes."""
import json
import re
import time
from urllib.parse import urlencode
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError

RSID = re.compile(r"^rs[0-9]{1,15}$", re.I)
HEADERS = {"User-Agent": "SFS-Labs-GenomicResearch/0.1 (nonclinical; public rsIDs only)",
           "Accept": "application/json"}
URLS = {
    "gwas_catalog_v2": "https://www.ebi.ac.uk/gwas/rest/api/v2/associations",
    "ensembl_grch37": "https://grch37.rest.ensembl.org/variation/human/",
    "ensembl_ld_pairwise": "https://grch37.rest.ensembl.org/ld/human/pairwise/",
    "europe_pmc": "https://www.ebi.ac.uk/europepmc/webservices/rest/search",
}
def get_json(url: str, params: dict | None = None, retries: int = 2) -> dict:
    if not any(url.startswith(prefix) for prefix in URLS.values()):
        raise ValueError("External destination not allowed")
    if params:
        url += ("&" if "?" in url else "?") + urlencode(params)
    for attempt in range(retries + 1):
        try:
            with urlopen(Request(url, headers=HEADERS), timeout=12) as response:
                if int(response.headers.get("Content-Length", "0")) > 1_500_000:
                    raise ValueError("Upstream response too large")
                body = response.read(1_500_001)
                if len(body) > 1_500_000:
                    raise ValueError("Upstream body too large")
                return json.loads(body)
        except (HTTPError, URLError, TimeoutError, ValueError) as e:
            if attempt == retries or (isinstance(e, HTTPError) and e.code not in (429, 500, 502, 503)):
                raise RuntimeError(f"Upstream unavailable ({type(e).__name__})") from None
            time.sleep(0.5 * (2 ** attempt))
    raise RuntimeError("Upstream unavailable")

def query_rsid(rsid: str) -> dict:
    """Raw, explicitly non-harmonized annotations; do not extract ORs without allele alignment."""
    if not RSID.fullmatch(rsid):
        raise ValueError("Invalid rsID")
    rsid = rsid.lower()
    targets = [
        ("gwas_catalog_v2", URLS["gwas_catalog_v2"], {"rs_id": rsid, "page": 0, "size": 10}),
        ("ensembl_grch37", URLS["ensembl_grch37"] + rsid, {"content-type": "application/json"}),
        ("europe_pmc", URLS["europe_pmc"], {"query": rsid, "format": "json", "pageSize": 5}),
    ]
    sources = {}
    for name, endpoint, params in targets:
        try:
            result = get_json(endpoint, params)
            # Bound returned data so MCP cannot inadvertently flood context.
            payload = json.dumps(result, ensure_ascii=False)
            sources[name] = {"status": "ok", "url": endpoint, "query": params,
                             "record_excerpt": payload[:10000],
                             "truncated": len(payload) > 10000}
        except RuntimeError as e:
            sources[name] = {"status": "unavailable", "reason": str(e), "url": endpoint}
    return {"rsid": rsid, "privacy": "Only this public rsID was transmitted; no genotype",
            "interpretation_status": "RAW_SOURCE_DATA_NOT_ALLELE_HARMONISED",
            "sources": sources}


def verify_reported_locus(rsid: str, chromosome: str, position: str,
                          genotype: str, build: str = "GRCh37") -> dict:
    """Check public reference coordinates and allele spelling, NOT chip accuracy.

    External requests contain rsID only. Chromosome, coordinates and the
    personal genotype are compared locally after the reference response.
    """
    if build != "GRCh37":
        return {"rsid": rsid, "status": "UNSUPPORTED_OR_UNKNOWN_BUILD"}
    if not RSID.fullmatch(rsid):
        raise ValueError("Invalid rsID")
    if not re.fullmatch(r"[ACGT]{1,2}", genotype):
        return {"rsid": rsid, "status": "INVALID_GENOTYPE"}
    source_url = URLS["ensembl_grch37"] + rsid.lower()
    record = get_json(source_url, {"content-type": "application/json"})
    candidates = []
    for mapping in record.get("mappings", []):
        assembly = str(mapping.get("assembly_name", "")).upper()
        if assembly not in ("GRCH37", "HG19"):
            continue
        chrom = str(mapping.get("seq_region_name", "")).upper().removeprefix("CHR")
        pos = str(mapping.get("start", ""))
        candidates.append(chrom + ":" + pos)
        if chrom != str(chromosome).upper().removeprefix("CHR") or pos != str(position):
            continue
        allele_list = str(mapping.get("allele_string", "")).upper().split("/")
        allowed = set(x for x in allele_list if len(x) == 1 and x in "ACGT")
        if not allowed:
            return {"rsid": rsid, "status": "REFERENCE_ALLELES_UNSUPPORTED",
                    "clinical_call_confirmed": False}
        gt = set(genotype)
        flipped = set(genotype.translate(str.maketrans("ACGT", "TGCA")))
        if allowed == {"A", "T"} or allowed == {"C", "G"}:
            if gt <= allowed or flipped <= allowed:
                return {"rsid": rsid, "status": "PALINDROMIC_STRAND_UNRESOLVED",
                        "coordinates_verified": True, "clinical_call_confirmed": False}
        if gt <= allowed:
            return {"rsid": rsid, "status": "GRCH37_COORDINATE_ALLELES_MATCH",
                    "coordinates_verified": True, "clinical_call_confirmed": False,
                    "source": source_url}
        if flipped <= allowed:
            return {"rsid": rsid, "status": "STRAND_FLIP_CANDIDATE_UNRESOLVED",
                    "coordinates_verified": True, "clinical_call_confirmed": False,
                    "source": source_url}
        return {"rsid": rsid, "status": "REFERENCE_ALLELES_MISMATCH",
                "coordinates_verified": True, "clinical_call_confirmed": False}
    return {"rsid": rsid, "status": "REFERENCE_MAPPING_MISMATCH_OR_UNAVAILABLE",
            "reference_loci": candidates[:8], "clinical_call_confirmed": False}
