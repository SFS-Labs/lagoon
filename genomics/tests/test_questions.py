"""Synthetic phenotype-oriented answer contract."""
import unittest
from genomics.questions import answer_question

class QuestionsTests(unittest.TestCase):
    def test_unknown_genotype_does_not_become_normal(self):
        output = answer_question({}, nutrient="b12")
        self.assertTrue(output["candidate_snps"])
        self.assertTrue(all(x["interpretation_gate"] == "UNMEASURED" for x in output["candidate_snps"]))
        self.assertIn("UNDETERMINED", output["clinical_conclusion"])
    def test_observed_variant_is_not_diagnosed(self):
        calls={"rs601338": {"genotype": "AA", "chromosome": "19", "position": "1"}}
        output = answer_question(calls, nutrient="b12", build="GRCh37")
        variant = next(x for x in output["candidate_snps"] if x["rsid"] == "rs601338")
        self.assertEqual(variant["genotype"], "AA")
        self.assertEqual(variant["interpretation_gate"], "ARRAY_CALL_ONLY_NOT_CLINICALLY_VALIDATED")
        self.assertTrue(variant["study_url"].startswith("https://"))
        self.assertNotIn("personal_absolute_risk", output)
    def test_hla_and_rare_disorders_not_excluded(self):
        output=answer_question({}, nutrient="folate")
        self.assertTrue(any("HLA" in x["hypothesis"] for x in output["not_excluded"]))
        self.assertTrue(any("transport" in x["reason"].lower() or "variant" in x["reason"].lower() for x in output["not_excluded"]))
    def test_invalid_nutrient_refused(self):
        with self.assertRaises(ValueError):
            answer_question({}, nutrient="celiac_verified")

if __name__ == "__main__":
    unittest.main()
