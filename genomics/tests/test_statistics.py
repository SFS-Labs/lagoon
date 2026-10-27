"""Statistical correctness and refusal invariants; all inputs synthetic."""
import math
import unittest
from genomics.statistics import (
    EvidenceValidationError, or_ci_to_log_effect,
    assess_study_effect, correlated_estimate_variance, odds_ratio_to_risk,
)

VALID = dict(rsid="rs111", effect_allele="T", other_allele="C",
             build="GRCh37", trait="synthetic serum nutrient",
             outcome_definition="case versus control by validated threshold",
             study_id="synthetic-only", source_url="https://doi.org/10.1000/example",
             population="synthetic cohort", genetic_model="additive_per_allele",
             effect_measure="OR", effect_value=1.38,
             ci_lower=1.19, ci_upper=1.60, sample_size=10000)

class StatisticsTests(unittest.TestCase):
    def verify(self, record=None, genotype="CT", status="GRCH37_COORDINATE_ALLELES_MATCH", ancestry=True):
        return assess_study_effect(record or VALID, personal_genotype=genotype,
                                   coordinate_status=status, ancestry_match=ancestry)

    def test_wolfram_or_to_beta_and_se(self):
        value = or_ci_to_log_effect(1.38, 1.19, 1.60)
        self.assertAlmostEqual(value["beta_log_odds"], 0.3220834991691132, places=12)
        self.assertAlmostEqual(value["se_log_odds"], 0.0755244291368395, places=12)

    def test_effect_not_individual_risk(self):
        r = self.verify()
        self.assertEqual(r["classification"], "POPULATION_ASSOCIATION_ONLY")
        self.assertEqual(r["effect_allele_dosage"], 1)
        self.assertIsNone(r["individual_absolute_risk"])

    def test_required_metadata_and_ancestry(self):
        short = {k:v for k,v in VALID.items() if k != "population"}
        self.assertIn("missing_fields:population", self.verify(short)["blocking_reasons"])
        self.assertIn("NO_MATCHED_ANCESTRY_EVIDENCE", self.verify(ancestry=None)["blocking_reasons"])

    def test_unverified_coordinate_refuses(self):
        self.assertIn("NO_REFERENCE_ALLELE_HARMONIZATION",
                      self.verify(status="STRAND_FLIP_CANDIDATE_UNRESOLVED")["blocking_reasons"])

    def test_mismatched_effect_allele_refuses(self):
        self.assertIn("PERSONAL_GENOTYPE_NOT_EFFECT_ALLELE_MATCHED",
                      self.verify(genotype="AA")["blocking_reasons"])

    def test_missing_calls_do_not_become_wildtype(self):
        self.assertIn("NOT_GENOTYPED", self.verify(genotype=None)["blocking_reasons"])

    def test_non_odds_ratios_cannot_be_converted_to_odds(self):
        r = dict(VALID, effect_measure="beta_standard_deviation", effect_value=-0.2)
        self.assertIn("UNSUPPORTED_MEASURE_NO_ODDS_RATIO_INFERENCE", self.verify(r)["blocking_reasons"])

    def test_invalid_numeric_or_confidence_interval(self):
        for row in ((0, 0.8, 1.4), (1.38, 1.4, 1.6), (float("nan"), 1, 2)):
            with self.assertRaises(EvidenceValidationError):
                or_ci_to_log_effect(*row)

    def test_wolfram_covariance_example(self):
        self.assertAlmostEqual(correlated_estimate_variance([0.2,0.3], [[1,0.8],[0.8,1]]),
                               0.226, places=12)

    def test_covariance_rejects_impossible_matrix(self):
        with self.assertRaises(EvidenceValidationError):
            correlated_estimate_variance([0.1,0.1,0.1], [[1,0.9,0.9],[0.9,1,-0.9],[0.9,-0.9,1]])

    def test_uncalibrated_baseline_blocks_absolute_risk(self):
        self.assertEqual(odds_ratio_to_risk(1.5,0.1)["status"],
                         "BLOCKED_NO_CALIBRATED_BASELINE")
        self.assertAlmostEqual(odds_ratio_to_risk(2,0.1, calibrated_baseline=True)["conditional_risk"],
                               2/11, places=12)

if __name__ == "__main__":
    unittest.main()
