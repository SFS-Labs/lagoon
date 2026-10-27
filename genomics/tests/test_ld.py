import unittest
from unittest.mock import patch
from genomics.ld import reference_pairwise_ld,identify_ld_blocks
class LDTests(unittest.TestCase):
 def test_high_reference_ld_stops_double_counting(self):
  with patch("genomics.ld.get_json",return_value=[{"r2":0.94,"d_prime":0.99,
       "population_name":"1000GENOMES:phase_3:EUR"}]) as q:
   out=reference_pairwise_ld("rs1801133","rs1801131",population="EUR")
  self.assertEqual(out["status"],"HIGH_LD")
  self.assertTrue(out["avoid_independent_sum"])
  self.assertIsNone(out["effect_direction"])
  self.assertNotIn("genotype",str(q.call_args))
 def test_no_data_is_unknown_not_independent(self):
  with patch("genomics.ld.get_json",return_value=[]):
   result=reference_pairwise_ld("rs10","rs11")
  self.assertEqual(result["status"],"LD_NOT_AVAILABLE")
  self.assertIsNone(result["r2"])
 def test_population_restricted(self):
  with self.assertRaises(ValueError):
   reference_pairwise_ld("rs1","rs2",population="PERSONAL")
 def test_conflicting_reference_data_refused(self):
  with patch("genomics.ld.get_json",return_value=[{"r2":0.09},{"r2":0.92}]):
   self.assertEqual(reference_pairwise_ld("rs1","rs2")["status"],"CONFLICTING_LD_RECORDS")
 def test_chain_of_high_LD_candidates_block(self):
  edges=[0.9,0.02,0.91]
  with patch("genomics.ld.get_json",side_effect=[[{"r2":v}] for v in edges]):
   result=identify_ld_blocks(["rs1","rs2","rs3"])
  self.assertEqual(result["queries"],3)
  self.assertEqual(len(result["high_ld_clusters"]),1)
  self.assertEqual(result["score_policy"][:6],"NO_SUM")
 def test_missing_service_refuses_assuming_no_ld(self):
  with patch("genomics.ld.get_json",side_effect=RuntimeError("timeout")):
   result=identify_ld_blocks(["rs1","rs2"])
  self.assertEqual(result["pairs"][0]["status"],"UPSTREAM_UNAVAILABLE")
  self.assertEqual(len(result["unknown_pairs"]),1)
 def test_bounded_queries(self):
  with self.assertRaises(ValueError):
   identify_ld_blocks(["rs"+str(i) for i in range(7)])
if __name__=="__main__":unittest.main()
