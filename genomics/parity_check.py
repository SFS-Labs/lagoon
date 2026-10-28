"""Compare two independent implementations on exactly the same synthetic SNP array.

Only aggregates and two boolean membership statuses are printed. No real
genotype information, external credentials, HTTP, or persistent storage.
"""
import json
import subprocess
import tempfile
from pathlib import Path
from .engine import parse_calls

SAMPLE = ("""# MyHeritage Build 37
RSID\tCHROMOSOME\tPOSITION\tRESULT
rs601338\t19\t49206674\tAA
rs855791\t22\t37462936\tCT
rs855791\t22\t37462936\tCT
rs200001\t1\t1000\t--
rs200002\t1\t1001\tAA
rs200002\t1\t1001\tCC
rs200003\t1\t1002\t??\n""")

def run():
    web_js = Path(__file__).parent / "web" / "parity-cli.mjs"
    with tempfile.TemporaryDirectory() as name:
        fixture = Path(name) / "synthetic.txt"
        fixture.write_text(SAMPLE, encoding="utf-8")
        p = parse_calls(fixture)
        raw = subprocess.check_output(["node", str(web_js), str(fixture)],
                                      text=True, timeout=30)
        js = json.loads(raw)
        qc = p["qc"]
        expected = {
            "build": qc["build"],
            "valid": qc["valid"],
            "no_calls": qc["no_calls"],
            "duplicates": qc["duplicate_rows"],
            "conflicts": qc["conflicts"],
            "rejected": qc["skipped"],
            "typed_status": {r: r in p["calls"] for r in ("rs601338","rs855791")},
        }
        if js != expected:
            raise RuntimeError("Python/iPhone JS parser disagreement (aggregates only)")
        return {"parity": "PASS", "checked_fields": list(expected),
                "raw_data": "SYNTHETIC_ONLY"}
if __name__ == "__main__":
    print(json.dumps(run()))
