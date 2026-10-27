"""Synthetic NGS/microarray intake checks."""
import tempfile
import unittest
from pathlib import Path
from genomics.intake import inspect_input, require_array

class IntakeTests(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.TemporaryDirectory()
        self.path = Path(self.dir.name)/"input.txt"
    def tearDown(self):
        self.dir.cleanup()
    def put(self, x):
        self.path.write_bytes(x)
        return inspect_input(self.path)
    def test_myheritage_array_routes_locally(self):
        self.assertEqual(self.put(b"# Build 37\nrsid\tchromosome\tposition\tgenotype\nrs1\t1\t123\tAA\n")["type"],
                         "consumer_snp_array")
        self.assertTrue(require_array(self.path)["callable_as_array"])
    def test_vcf_is_not_array(self):
        self.assertEqual(self.put(b"##fileformat=VCFv4.2\n#CHROM\tPOS\tID\tREF\tALT\tQUAL\tFILTER\tINFO\n")["type"],
                         "variant_call_format")
        with self.assertRaises(ValueError):
            require_array(self.path)
    def test_cram_and_gzip_not_snp_array(self):
        self.assertEqual(self.put(b"CRAM\x03\x00" + b"\0"*20)["type"], "cram_alignment")
        self.assertEqual(self.put(b"\x1f\x8b\x08" + b"\0"*20)["type"], "gzip_container_undetermined")
    def test_fastq_and_fasta_not_snp_array(self):
        self.assertEqual(self.put(b"@r1\nACGT\n+\nIIII\n")["type"], "fastq_sequencing")
        self.assertEqual(self.put(b">chr1\nACGT\n")["type"], "fasta_reference_sequence")
    def test_unknown_rejected(self):
        self.assertFalse(self.put(b"not a genotype file")["callable_as_array"])

if __name__ == "__main__":
    unittest.main()
