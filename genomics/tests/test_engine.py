"""Isolated synthetic tests; NO personal genomics in the repository."""
import os
import tempfile
import unittest
from pathlib import Path

from genomics.engine import analyze, parse_calls, check_alleles, EVIDENCE
from genomics.mcp import execute, TOOLS
from genomics.research import verify_reported_locus
from genomics.discovery import scan_trait_calls
from unittest.mock import patch

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
        self.assertEqual(len(TOOLS), 12)
    def test_csv_not_tsv(self):
        self.write("rsid,chromosome,position,genotype\nrs855791,22,10,TT\n")
        self.assertEqual(parse_calls(self.path)["calls"]["rs855791"]["genotype"], "TT")

    def test_reference_coordinate_and_strand_fail_closed(self):
        data = {"mappings": [{"assembly_name": "GRCh37",
                              "seq_region_name": "4",
                              "start": 1234, "allele_string": "A/C"}]}
        with patch("genomics.research.get_json", return_value=data) as remote:
            same = verify_reported_locus("rs2282679", "4", "1234", "AC")
            flipped = verify_reported_locus("rs2282679", "4", "1234", "GT")
            wrong = verify_reported_locus("rs2282679", "4", "9876", "AC")
            self.assertEqual(remote.call_count, 3)
        self.assertEqual(same["status"], "GRCH37_COORDINATE_ALLELES_MATCH")
        self.assertFalse(same["clinical_call_confirmed"])
        self.assertEqual(flipped["status"], "STRAND_FLIP_CANDIDATE_UNRESOLVED")
        self.assertEqual(wrong["status"], "REFERENCE_MAPPING_MISMATCH_OR_UNAVAILABLE")

    def test_palindromic_reference_keeps_strand_unresolved(self):
        data = {"mappings": [{"assembly_name": "GRCh37",
                              "seq_region_name": "1",
                              "start": 7, "allele_string": "A/T"}]}
        with patch("genomics.research.get_json", return_value=data):
            result = verify_reported_locus("rs100", "1", "7", "AT")
        self.assertEqual(result["status"], "PALINDROMIC_STRAND_UNRESOLVED")

    def test_trait_scan_intersects_only_locally(self):
        pages = [{"content": [
            {"rsId": "rs601338", "id": "GCST-test-1"},
            {"rsId": "rs999999", "id": "GCST-test-2"}]}, {"content": []}]
        personal_calls = {"rs601338": {"genotype": "AA", "chromosome": "19",
                                     "position": "1"}}
        with patch("genomics.discovery.get_json", side_effect=pages) as remote:
            output = scan_trait_calls(personal_calls, "b12", pages=2)
        self.assertEqual(len(output["matched_candidates"]), 1)
        self.assertEqual(output["matched_candidates"][0]["rsid"], "rs601338")
        self.assertEqual(output["matched_candidates"][0]["effect"], "NOT_HARMONIZED")
        for call in remote.call_args_list:
            self.assertNotIn("AA", str(call))
            self.assertNotIn("rs601338", str(call))
        self.assertFalse(output["page_budget_exhausted"])

    def test_trait_scan_fails_closed_on_unknown_upstream_shape(self):
        with patch("genomics.discovery.get_json", return_value={"new_shape": {}}):
            with self.assertRaises(RuntimeError):
                scan_trait_calls({}, "iron")

    def test_new_tools_respect_absent_private_data(self):
        self.assertEqual(execute("inspect_private_genomic_input", {})["status"], "NO_PRIVATE_RAW_FILE")
        self.assertEqual(execute("audit_quantitative_gwas_record", {"record": {"rsid": "rs100"}})["status"],
                         "NO_PRIVATE_RAW_FILE")

    def test_real_gwas_v2_nested_snp_allele_schema(self):
        # Mirrors verified live API response keys from Oct 27 2026.
        response = {"_embedded": {"associations": [
            {"association_id": 1001, "snp_allele": [{"rs_id": "rs855791",
                                                      "effect_allele": "G"}],
             "snp_effect_allele": ["rs855791-G"], "pubmed_id": "12345678",
             "accession_id": "GCST901", "multi_snp_haplotype": False,
             "snp_interaction": False},
            {"association_id": 1002, "snp_allele": [{"rs_id": "rs99999",
                                                      "effect_allele": "A"}],
             "snp_effect_allele": ["rs99999-A"]},
            {"association_id": 1003, "snp_allele": [{"rs_id": "rs855791",
                                                      "effect_allele": "C"}],
             "multi_snp_haplotype": True}
        ]}}
        calls = {"rs855791": {"genotype": "CT", "chromosome": "22", "position": "10"}}
        with patch("genomics.discovery.get_json", return_value=response):
            out = scan_trait_calls(calls, "iron", pages=1)
        self.assertEqual(len(out["matched_candidates"]), 1)
        found = out["matched_candidates"][0]
        self.assertEqual(found["rsid"], "rs855791")
        self.assertEqual(found["source_pmids"], ["12345678"])
        self.assertEqual(found["study_accessions"], ["GCST901"])
        self.assertEqual(found["association_ids"], ["1001"])
        self.assertEqual(found["effect"], "NOT_HARMONIZED")

    def test_no_personal_genotypes_in_registry(self):
        self.assertTrue(all("study" in e and e["study"].startswith("https://") for e in EVIDENCE))

if __name__ == "__main__":
    unittest.main()
