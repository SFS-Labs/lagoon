"""Local MCP stdio server and CLI. Zero third-party Python dependencies.

Set GENOMICS_RAW_FILE to an ABSOLUTE local private path before starting.
Never expose this stdin/stdout process on an unauthenticated public port.
"""
import argparse
import json
import os
import sys
from pathlib import Path

try:
    from .engine import analyze, parse_calls, research_summary, GenotypeError, EVIDENCE
    from .research import query_rsid, verify_reported_locus
    from .discovery import scan_trait_calls
    from .intake import inspect_input, require_array
    from .statistics import assess_study_effect
    from .questions import answer_question
except ImportError:
    from engine import analyze, parse_calls, research_summary, GenotypeError, EVIDENCE
    from research import query_rsid, verify_reported_locus
    from discovery import scan_trait_calls
    from intake import inspect_input, require_array
    from statistics import assess_study_effect
    from questions import answer_question

PROTOCOL = "2025-06-18"
TOOLS = [
    {"name": "genomic_dataset_status",
     "description": "Check whether a privately configured MyHeritage/23andMe genotype file is available and report coverage. No genotype is uploaded.",
     "inputSchema": {"type": "object", "properties": {}, "additionalProperties": False}},
    {"name": "analyze_micronutrient_genetics",
     "description": "Analyze cited SNP associations for B12, iron, vitamin D, folate, lactose, and unresolved malabsorption possibilities. Distinguishes biomarkers from absorption; no individual probability without calibrated model.",
     "inputSchema": {"type": "object", "properties": {"format": {"type": "string", "enum": ["json", "markdown"]}},
                     "additionalProperties": False}},
    {"name": "verify_micronutrient_variant_coordinates",
     "description": "Verify GRCh37 position and allele correspondence. ONLY rsID sent externally. Research-only.",
     "inputSchema": {"type": "object", "properties": {"rsids": {"type": "array", "items": {"type": "string", "pattern": "^rs[0-9]+$"}, "maxItems": 12}}, "additionalProperties": False}},
    {"name": "scan_private_genome_against_gwas_trait",
     "description": "Discover candidate associations for nutrient traits from public GWAS v2 and intersect with private genotypes LOCALLY. Bounded 1-5 pages; NO individual risk scores.",
     "inputSchema": {"type": "object", "properties": {"trait": {"type": "string", "enum": ["b12", "folate", "vitamin_d", "iron", "ferritin", "zinc", "calcium", "magnesium", "selenium"]}, "pages": {"type": "integer", "minimum": 1, "maximum": 5}}, "required": ["trait"], "additionalProperties": False}},
    {"name": "inspect_private_genomic_input",
     "description": "Determine private genotype format (SNP array versus FASTQ/VCF/BAM/CRAM) and safe local/NGS route without uploading contents.",
     "inputSchema": {"type": "object", "properties": {}, "additionalProperties": False}},
    {"name": "audit_quantitative_gwas_record",
     "description": "Statistically audit a caller-supplied literature effect with full fields, personal array call, external GRCh37 coordinate check and explicitly confirmed ancestry compatibility. Does NOT verify paper content or calculate individual risk.",
     "inputSchema": {"type": "object", "properties": {"record": {"type": "object"}, "ancestry_match": {"type": "boolean"}}, "required": ["record"], "additionalProperties": False}},
    {"name": "answer_micronutrient_genetic_question",
     "description": "Generate source-linked personal genotype candidate table for malabsorption and vitamin B12/iron/D/folate/lactose while preserving unknown genotypes, mechanism distinctions and diagnostics that SNP arrays cannot resolve.",
     "inputSchema": {"type": "object", "properties": {"nutrient": {"type": "string", "enum": ["all", "b12", "iron", "vitamin_d", "folate", "lactose"]}}, "additionalProperties": False}},
    {"name": "lookup_public_variant_evidence",
     "description": "Retrieve live raw annotation snippets for a public rsID from GWAS Catalog v2, Ensembl GRCh37 and Europe PMC. Does not transmit DNA data; raw results are NOT effect allele-harmonised.",
     "inputSchema": {"type": "object", "properties": {"rsid": {"type": "string", "pattern": "^rs[0-9]+$"}},
                     "required": ["rsid"], "additionalProperties": False}},
]
def source():
    path = os.environ.get("GENOMICS_RAW_FILE", "").strip()
    if not path:
        return None
    p = Path(path)
    if not p.is_absolute():
        raise GenotypeError("GENOMICS_RAW_FILE must be an absolute path")
    require_array(p)
    return parse_calls(p)

def execute(name, args):
    if name == "genomic_dataset_status":
        data = source()
        return {"configured": data is not None,
                "qc": data["qc"] if data else None, "private": True}
    if name == "analyze_micronutrient_genetics":
        data = source()
        if data is None:
            return {"status": "NO_PRIVATE_RAW_FILE",
                    "message": "Set GENOMICS_RAW_FILE to an absolute private export path. Cannot infer unseen genotypes from the public PR."}
        output = analyze(data["calls"], data["qc"]["build"])
        output["input_qc"] = data["qc"]
        if args.get("format") == "markdown":
            return research_summary(output)
        return output
    if name == "verify_micronutrient_variant_coordinates":
        data = source()
        if data is None:
            return {"status": "NO_PRIVATE_RAW_FILE"}
        known = {item["rsid"] for item in EVIDENCE}
        requested = args.get("rsids") or sorted(known.intersection(data["calls"]))
        if not isinstance(requested, list) or len(requested) > 12:
            raise ValueError("Maximum 12 rsIDs")
        output = {}
        for rsid in requested:
            if rsid not in known:
                output[rsid] = {"status": "NOT_IN_CURATED_PANEL"}
            elif rsid not in data["calls"]:
                output[rsid] = {"status": "NOT_GENOTYPED"}
            else:
                record = data["calls"][rsid]
                try:
                    output[rsid] = verify_reported_locus(
                        rsid, record["chromosome"], record["position"],
                        record["genotype"], data["qc"]["build"])
                except (RuntimeError, ValueError) as exc:
                    output[rsid] = {"status": "UPSTREAM_ERROR", "error_type": type(exc).__name__}
        return {"reference_validation": output, "interpretation": "research-only"}
    if name == "scan_private_genome_against_gwas_trait":
        data = source()
        if data is None:
            return {"status": "NO_PRIVATE_RAW_FILE"}
        return scan_trait_calls(data["calls"], args["trait"], args.get("pages", 2))
    if name == "inspect_private_genomic_input":
        p = os.environ.get("GENOMICS_RAW_FILE", "").strip()
        if not p:
            return {"status": "NO_PRIVATE_RAW_FILE", "configured": False}
        if not Path(p).is_absolute():
            raise GenotypeError("Expected absolute path for private input")
        return inspect_input(p)
    if name == "audit_quantitative_gwas_record":
        data = source()
        if data is None:
            return {"status": "NO_PRIVATE_RAW_FILE"}
        record = args.get("record")
        if not isinstance(record, dict):
            raise ValueError("Missing study-effect record object")
        rsid = record.get("rsid")
        if not isinstance(rsid, str) or not rsid.startswith("rs") or not rsid[2:].isdigit():
            raise ValueError("Valid public rsID required")
        personal = data["calls"].get(rsid)
        reference = {"status": "NOT_GENOTYPED"} if personal is None else {"status": "UNVERIFIED_REFERENCE"}
        if personal is not None:
            try:
                reference = verify_reported_locus(
                    rsid, personal["chromosome"], personal["position"],
                    personal["genotype"], data["qc"]["build"])
            except (RuntimeError, ValueError) as exc:
                reference = {"status": "UPSTREAM_ERROR", "error_type": type(exc).__name__}
        evaluated = assess_study_effect(
            record, personal_genotype=personal["genotype"] if personal else None,
            coordinate_status=reference["status"],
            ancestry_match=args.get("ancestry_match"))
        evaluated["reference_check"] = reference
        evaluated["literature_authenticity"] = "NOT_VERIFIED_USER_SUPPLIED_METADATA"
        evaluated["clinical_validation"] = False
        return evaluated
    if name == "answer_micronutrient_genetic_question":
        data = source()
        if data is None:
            return {"status": "NO_PRIVATE_RAW_FILE",
                    "message": "No private genotype file configured; no personal SNPs can be inferred."}
        return answer_question(data["calls"], nutrient=args.get("nutrient", "all"),
                               build=data["qc"]["build"])
    if name == "lookup_public_variant_evidence":
        return query_rsid(args["rsid"])
    raise ValueError("Unknown tool")

def response(id_, result=None, error=None):
    out = {"jsonrpc": "2.0", "id": id_}
    if error is not None:
        out["error"] = {"code": -32603, "message": str(error)}
    else:
        out["result"] = result
    sys.stdout.write(json.dumps(out, ensure_ascii=False) + "\n")
    sys.stdout.flush()

def serve():
    for line in sys.stdin:
        id_ = None
        try:
            message = json.loads(line)
            if not isinstance(message, dict):
                continue
            method = message.get("method")
            if "id" not in message:
                continue
            id_ = message["id"]
            if method == "initialize":
                response(id_, {"protocolVersion": PROTOCOL,
                               "capabilities": {"tools": {"listChanged": False}},
                               "serverInfo": {"name": "lagoon-genomics-research", "version": "0.1.0"}})
            elif method == "ping":
                response(id_, {})
            elif method == "tools/list":
                response(id_, {"tools": TOOLS})
            elif method == "tools/call":
                params = message.get("params", {})
                result = execute(params.get("name"), params.get("arguments") or {})
                text = result if isinstance(result, str) else json.dumps(result, ensure_ascii=False)
                response(id_, {"content": [{"type": "text", "text": text}], "isError": False})
            else:
                response(id_, error=f"Unsupported method: {method}")
        except Exception as exc:
            if id_ is not None:
                response(id_, error=f"{type(exc).__name__}: {exc}")
            # Never log genotypes, raw input, or call contents.
def main():
    p = argparse.ArgumentParser()
    p.add_argument("command", choices=["mcp", "status", "analyze", "research"])
    p.add_argument("--raw", help="Local MyHeritage/23andMe text export path; not uploaded")
    p.add_argument("--rsid", help="Public rsID for research")
    p.add_argument("--format", choices=["json", "markdown"], default="markdown")
    args = p.parse_args()
    if args.raw:
        os.environ["GENOMICS_RAW_FILE"] = str(Path(args.raw).resolve())
    if args.command == "mcp":
        serve()
    else:
        name = {"status": "genomic_dataset_status",
                "analyze": "analyze_micronutrient_genetics",
                "research": "lookup_public_variant_evidence"}[args.command]
        result = execute(name, {"rsid": args.rsid, "format": args.format})
        print(result if isinstance(result, str) else json.dumps(result, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    main()
