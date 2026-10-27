"""Test real-structure GWAS metadata extraction and fail-closed orientation."""
import unittest
from unittest.mock import patch
from genomics.harmonization import public_evidence_snapshot,orientation_gate,explore_public_study_locus

MOCK={"_embedded":{"associations":[{
 "association_id":123,"accession_id":"GCST01234","pubmed_id":"12345678",
 "first_author":"Study Author","snp_allele":[{"rs_id":"rs855791","effect_allele":"G"}],
 "snp_effect_allele":["rs855791-G"],"multi_snp_haplotype":False,
 "snp_interaction":False,"reported_trait":["serum iron"],"efo_traits":["iron measurement"],
 "beta":"-0.12","ci_lower":0.2,"ci_upper":0.4,"p_value":1.2e-6
}]}}

class HarmonizationTest(unittest.TestCase):
 def test_gwas_snapshot_extracts_actual_nested_schema(self):
  with patch("genomics.harmonization.get_json",return_value=MOCK) as get:
   out=public_evidence_snapshot("rs855791")
  self.assertEqual(out["record_count"],1)
  self.assertEqual(out["associations"][0]["effect_allele_as_reported"],["G"])
  self.assertEqual(out["associations"][0]["pubmed_id"],"12345678")
  self.assertNotIn("genotype",str(get.call_args))
 def test_status_does_not_turn_beta_into_risk(self):
  with patch("genomics.harmonization.get_json",return_value=MOCK),\
       patch("genomics.harmonization.verify_reported_locus",return_value={"status":"GRCH37_COORDINATE_ALLELES_MATCH"}):
   out=explore_public_study_locus("rs855791",{"genotype":"CT","chromosome":"22","position":"100"},"GRCh37")
  a=out["interpretation"][0]["orientation"]
  self.assertEqual(a["status"],"STUDY_EFFECT_ALLELE_STRAND_NOT_INDEPENDENTLY_VERIFIED")
  self.assertIsNone(a["effect_allele_dosage"])
 def test_palindromic_or_ambiguous_reference_rejected(self):
  out=orientation_gate("rs1","A","1","123","AT",reference_verification={"status":"PALINDROMIC_STRAND_UNRESOLVED"})
  self.assertEqual(out["status"],"PERSONAL_COORDINATE_OR_STRAND_UNVERIFIED")
 def test_missing_source_records_fail(self):
  with patch("genomics.harmonization.get_json",return_value={"content":[]}):
   with self.assertRaises(ValueError):public_evidence_snapshot("rs1")
 def test_several_conflicting_reported_effect_alleles_not_counted(self):
  doc={"_embedded":{"associations":[dict(MOCK["_embedded"]["associations"][0],
    snp_effect_allele=["rs855791-C"])]}}
  with patch("genomics.harmonization.get_json",return_value=doc),\
       patch("genomics.harmonization.verify_reported_locus",return_value={"status":"GRCH37_COORDINATE_ALLELES_MATCH"}):
   o=explore_public_study_locus("rs855791",{"genotype":"CT","chromosome":"22","position":"100"},"GRCh37")
  self.assertEqual(len(o["interpretation"]),0)
  self.assertEqual(o["associations"][0]["effect_allele_as_reported"],["C","G"])
if __name__=="__main__":unittest.main()
