"""Synthetic-only regression cases; never include personal genotype fixtures."""
import unittest
from genomics.validation import LOCI, validate_call, evaluate_study_claim, assess_ld_double_counting


class TestReferenceGates(unittest.TestCase):
    def test_five_pinned_loci(self):
        self.assertEqual(len(LOCI), 5)
        for rsid, ref in LOCI.items():
            v = validate_call(rsid, ref["chr"], ref["pos"], ref["ref"] * 2)
            self.assertIn(v["status"], ("GRCH37_FORWARD_ALLELES_CONCORDANT", "PALINDROMIC_STRAND_UNRESOLVED"))
            self.assertFalse(v["is_clinically_validated"])

    def test_normalised_id_and_forward_dosage(self):
        v = validate_call("RS1801133", "1", 11856378, "GA")
        self.assertEqual(v["status"], "GRCH37_FORWARD_ALLELES_CONCORDANT")
        self.assertEqual(v["forward_alt_allele_dosage"], 1)

    def test_build_mismatch(self):
        self.assertEqual(validate_call("rs855791", "22", 37462936, "AG", build="GRCh38")["status"], "BUILD_UNVERIFIED")

    def test_coordinate_mismatch(self):
        self.assertEqual(validate_call("rs855791", "22", 37462937, "GG")["status"], "GRCH37_COORDINATE_MISMATCH")

    def test_silent_flip_prohibited(self):
        self.assertEqual(validate_call("rs855791", "22", 37462936, "CT")["status"], "REVERSE_COMPLEMENT_CANDIDATE_UNVERIFIED")

    def test_mismatched_alleles(self):
        self.assertEqual(validate_call("rs855791", "22", 37462936, "AT")["status"], "ALLELES_NOT_IN_REFERENCE_SET")

    def test_unknown_reference(self):
        self.assertEqual(validate_call("rs123456789", "2", 50, "AA")["status"], "REFERENCE_NOT_YET_VERIFIED")

    def test_missing_not_wildtype(self):
        self.assertEqual(validate_call("rs1801133", None, None, None)["status"], "NO_CALL_OR_NOT_ON_ARRAY")

    def test_palindromic_alleles_cannot_orient(self):
        v=validate_call("rs1799945", "6", 26091179, "CG")
        self.assertEqual(v["status"], "PALINDROMIC_STRAND_UNRESOLVED")
        self.assertIsNone(v["forward_alt_allele_dosage"])

    def test_invalid_diploid_bases(self):
        self.assertEqual(validate_call("rs855791", "22", 37462936, "GGG")["status"], "INVALID_DIPLOID_BASES")

    def test_invalid_id(self):
        self.assertEqual(validate_call("nope", "22", 37462936, "GG")["status"], "INVALID_RSID")


class TestStudyAndLdGates(unittest.TestCase):
    def setUp(self):
        self.check = validate_call("rs1801133", "1", 11856378, "GA")
        self.study = {"id": "SYNTHETIC_ONLY", "harmonised": True, "build": "GRCh37",
                      "effect_allele": "A", "other_allele": "G",
                      "effect_type": "beta", "effect_value": 0.2, "endpoint": "folate_metabolism",
                      "endpoint_kind": "biomarker", "ancestry_matched": True,
                      "independent_replication": True, "ld_adjusted": True}
    def test_eligible_research_effect_only(self):
        r = evaluate_study_claim(self.check, self.study, "folate_metabolism")
        self.assertEqual(r["status"], "RESEARCH_EFFECT_GATES_PASSED")
        self.assertFalse(r["can_report_individual_disease_probability"])
    def test_unharmonised_blocks(self):
        s={**self.study, "harmonised": False}
        self.assertIn("GWAS_EFFECT_ALLELES_NOT_PROVEN_HARMONISED",
                      evaluate_study_claim(self.check, s, "folate_metabolism")["blockers"])
    def test_absorption_not_iron_serum(self):
        s={**self.study, "endpoint": "iron_concentration"}
        self.assertIn("BIOMARKER_OR_PROXY_IS_NOT_REQUESTED_CLINICAL_ENDPOINT",
                      evaluate_study_claim(self.check, s, "gut_iron_absorption")["blockers"])
    def test_study_allele_mismatch(self):
        s={**self.study, "effect_allele": "T"}
        self.assertIn("STUDY_ALLELE_SET_MISMATCH",
                      evaluate_study_claim(self.check, s, "folate_metabolism")["blockers"])
    def test_missing_ancestry_and_replication(self):
        s={**self.study, "ancestry_matched": False, "independent_replication": False}
        r=evaluate_study_claim(self.check, s, "folate_metabolism")
        self.assertIn("ANCESTRY_APPLICABILITY_UNVERIFIED", r["blockers"])
        self.assertIn("INDEPENDENT_REPLICATION_UNVERIFIED", r["blockers"])
    def test_clinical_calibration_gate(self):
        s={**self.study, "endpoint_kind": "clinical"}
        self.assertIn("CLINICAL_RISK_CALIBRATION_MISSING",
                      evaluate_study_claim(self.check, s, "folate_metabolism")["blockers"])
    def test_ld_r2_cannot_be_added(self):
        r=assess_ld_double_counting(0.261793, same_population=True, same_build=True)
        self.assertEqual(r["status"], "LD_DEPENDENCE_PRESENT")
        self.assertFalse(r["safe_to_sum_independently"])
    def test_low_ld_not_license(self):
        self.assertFalse(assess_ld_double_counting(0.01, same_population=True, same_build=True)["safe_to_sum_independently"])
    def test_missing_ld_context(self):
        self.assertEqual(assess_ld_double_counting(None, same_population=False, same_build=True)["status"], "LD_CONTEXT_UNVERIFIED")
    def test_bad_ld_context(self):
        self.assertEqual(assess_ld_double_counting(1.2, same_population=True, same_build=True)["status"], "INVALID_LD_R2")


if __name__ == "__main__":
    unittest.main()
