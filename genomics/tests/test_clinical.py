import unittest
from genomics.clinical import assess_locus_claim,claim_scope
VALID={
 "rsid":"rs999001","study_id":"TESTONLY","trait":"serum iron",
 "endpoint":"serum_iron","effect_allele":"T","other_allele":"C",
 "genome_build":"GRCh37","study_orientation":"documented_GRCh37_forward",
 "effect_type":"beta","effect_size":-0.12,"standard_error":0.02,
 "unit":"SD of serum iron","population":"independent synthetic population",
 "model":"per_allele_additive","sample_size":10000,"replicated":True,
 "source_url":"https://pubmed.ncbi.nlm.nih.gov/12345678"
}
REFERENCE={"status":"GRCH37_COORDINATE_ALLELES_MATCH"}
class ClinicalTests(unittest.TestCase):
 def valid(self,record=None,gt="CT",ref=REFERENCE,ancestry=True):
  return assess_locus_claim(record or VALID,genotype=gt,reference=ref,
                             ancestry_matching_evidence=ancestry)
 def test_population_only_after_all_validated_metadata(self):
  r=self.valid()
  self.assertEqual(r["status"],"POPULATION_EFFECT_ELIGIBLE_FOR_HUMAN_REVIEW")
  self.assertEqual(r["effect_allele_dosage"],1)
  self.assertIsNone(r["absolute_personal_risk"])
  self.assertFalse(r["malabsorption_mechanism_inferred"])
 def test_undocumented_study_forward_strand_refused(self):
  r=self.valid({**VALID,"study_orientation":"unknown"})
  self.assertIn("STUDY_EFFECT_ALLELE_ORIENTATION_UNVERIFIED",r["blocking_reasons"])
  self.assertIsNone(r["effect_allele_dosage"])
 def test_ancestry_replication_refused(self):
  r=self.valid({**VALID,"replicated":False},ancestry=False)
  self.assertIn("INDEPENDENT_REPLICATION_NOT_ESTABLISHED",r["blocking_reasons"])
  self.assertIn("ANCESTRY_MATCH_NOT_ESTABLISHED",r["blocking_reasons"])
 def test_palindromic_refused_even_if_other_metadata_valid(self):
  r=self.valid({**VALID,"effect_allele":"A","other_allele":"T"},gt="AT")
  self.assertIn("PALINDROMIC_STUDY_ALLELE_FREQUENCY_REQUIRED",r["blocking_reasons"])
 def test_unsupported_genotype_is_not_harmonized(self):
  r=self.valid(gt="GG")
  self.assertIn("PERSONAL_CALL_NOT_ORIENTED_TO_PUBLISHED_ALLELE_PAIR",r["blocking_reasons"])
 def test_reference_missing_blocks(self):
  r=self.valid(ref={"status":"STRAND_FLIP_CANDIDATE_UNRESOLVED"})
  self.assertIsNone(r["effect_allele_dosage"])
 def test_beta_without_unit_and_se_refused(self):
  r=self.valid({**VALID,"unit":None,"standard_error":None})
  self.assertIn("BETA_UNIT_OR_SE_MISSING",r["blocking_reasons"])
 def test_serum_B12_not_direct_malabsorption(self):
  r=claim_scope("serum_b12")
  self.assertEqual(r["domain"],"CIRCULATING_BIOMARKER")
  self.assertFalse(r["supports_intestinal_malabsorption_diagnosis"])
 def test_iron_overload_not_iron_deficiency(self):
  r=claim_scope("iron_overload")
  self.assertEqual(r["domain"],"IRON_STORAGE_DISEASE_CANDIDATE")
  self.assertFalse(r["supports_intestinal_malabsorption_diagnosis"])
if __name__=="__main__":unittest.main()
