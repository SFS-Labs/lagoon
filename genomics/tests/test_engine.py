"""Isolated synthetic tests; NO personal genomics in the repository."""
import os
import tempfile
import unittest
from pathlib import Path

from genomics.engine import analyze, parse_calls, check_alleles, EVIDENCE
from genomics.mcp import execute, TOOLS

class CoreTests(unittest.TestCase):
    def setUp(self):
        self.folder = tempfile.TemporaryDirectory()
        self.path = Path(self.folder.name) / "synthetic.txt"
    def tearDown(self):
        self.folder.cleanup()
        os.environ.pop("GENOMICS_RAW_FILE", None)
    def write(self, content):
        self.path.write_text(content, encoding="utf-8")
        return self.path
    def test_parse_qc_and_build(self):
        self.write("# MyHeritage Build 37\nrsid\tchromosome\tposition\tgenotype\nrs601338\t19\t49206674\tAA\nrs855791\t22\t37462936\tCT\n")
        p = parse_calls(self.path)
        self.assertEqual(p["qc"]["build"], "GRCh37")
        self.assertEqual(p["calls"]["rs601338"]["genotype"], "AA")
        self.assertEqual(p["qc"]["valid"], 2)
    def test_absent_is_unknown(self):
        x = analyze({})
        self.assertEqual(x["matched_loci"], 0)
        self.assertTrue(all(r["status"] == "NOT_GENOTYPED" for r in x["results"]))
    def test_strand_conflict_fail_closed(self):
        a, b = check_alleles("GT", "AC")
        self.assertEqual(a, "reverse_complement_candidate_UNVERIFIED")
        self.assertIsNone(b)
        a, b = check_alleles("AC", "AG")
        self.assertEqual(a, "ALLELE_MISMATCH")
        self.assertIsNone(b)
    def test_researched_effect_not_scaled_into_absolute_risk(self):
        x = analyze({"rs601338": {"genotype": "AA", "chromosome": "19", "position": "1"}})
        b12 = next(r for r in x["results"] if r["rsid"] == "rs601338")
        self.assertEqual(b12["effect_allele_count"], 2)
        self.assertEqual(b12["status"], "matching_reported_strand")
        self.assertNotIn("personal_risk", b12)
    def test_skip_no_calls_and_refuse_conflicting_duplicates(self):
        self.write("# build 37\nrs601338\t19\t1\t--\nrs601338\t19\t1\tAA\nrs601338\t19\t1\tGG\n")
        d = parse_calls(self.path)
        self.assertNotIn("rs601338", d["calls"])
        self.assertIn("conflicting_call:rs601338", d["qc"]["issues"])
    def test_mcp_no_file_no_leak(self):
        os.environ.pop("GENOMICS_RAW_FILE", None)
        self.assertEqual(execute("analyze_micronutrient_genetics", {})["status"], "NO_PRIVATE_RAW_FILE")
        self.assertEqual(len(TOOLS), 3)
    def test_csv_not_tsv(self):
        self.write("rsid,chromosome,position,genotype\nrs855791,22,10,TT\n")
        self.assertEqual(parse_calls(self.path)["calls"]["rs855791"]["genotype"], "TT")
    def test_no_personal_genotypes_in_registry(self):
        self.assertTrue(all("study" in e and e["study"].startswith("https://") for e in EVIDENCE))

if __name__ == "__main__":
    unittest.main()
