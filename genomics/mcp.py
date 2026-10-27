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
    from .engine import analyze, parse_calls, research_summary, GenotypeError
    from .research import query_rsid
except ImportError:
    from engine import analyze, parse_calls, research_summary, GenotypeError
    from research import query_rsid

PROTOCOL = "2025-06-18"
TOOLS = [
    {"name": "genomic_dataset_status",
     "description": "Check whether a privately configured MyHeritage/23andMe genotype file is available and report coverage. No genotype is uploaded.",
     "inputSchema": {"type": "object", "properties": {}, "additionalProperties": False}},
    {"name": "analyze_micronutrient_genetics",
     "description": "Analyze cited SNP associations for B12, iron, vitamin D, folate, lactose, and unresolved malabsorption possibilities. Distinguishes biomarkers from absorption; no individual probability without calibrated model.",
     "inputSchema": {"type": "object", "properties": {"format": {"type": "string", "enum": ["json", "markdown"]}},
                     "additionalProperties": False}},
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
        try:
            message = json.loads(line)
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
            if "id_" in locals():
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
