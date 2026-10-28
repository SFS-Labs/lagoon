"""Assay-aware input preflight: a genotyping microarray is not NGS.

Identify common variants-file and sequencing signatures without uploading
their contents. No automatic cloud execution, conversion, imputation or calling.
"""
from __future__ import annotations
from pathlib import Path

MAX_PEEK = 8192

def inspect_input(path: str | Path) -> dict:
    p = Path(path)
    if not p.is_file():
        return {"status": "MISSING_FILE", "type": "unknown", "callable_as_array": False}
    with p.open("rb") as f:
        header = f.read(MAX_PEEK)
    suffix = p.name.lower()
    kind = "unknown"
    route = "manual_file_validation"
    if header.startswith(b"CRAM"):
        kind, route = "cram_alignment", "ngs_dna_germline_variants"
    elif header.startswith(b"BAM\x01"):
        kind, route = "bam_alignment", "ngs_dna_germline_variants"
    elif header.startswith(b"\x1f\x8b"):
        # BAM and BGZF are gzip-container streams; cannot infer assay
        # from magic bytes alone. Treat as untrusted until decompressed.
        kind, route = "gzip_container_undetermined", "decompress_then_reinspect"
    elif header.lstrip().startswith(b"##fileformat=VCF"):
        kind, route = "variant_call_format", "ngs_dna_germline_variant_review"
    elif header.lstrip().startswith(b"@") and b"\n+\n" in header:
        kind, route = "fastq_sequencing", "ngs_analysis_router"
    elif header.lstrip().startswith(b">"):
        kind, route = "fasta_reference_sequence", "reference_context_not_personal_genotyping"
    else:
        lines = header.decode("utf-8-sig", errors="replace").splitlines()
        meaningful = [line.strip() for line in lines if line.strip() and not line.lstrip().startswith("#")]
        if meaningful:
            head = meaningful[0].lower()
            if ("rsid" in head or head.startswith("rs")) and (
                    "\t" in meaningful[0] or "," in meaningful[0]):
                kind, route = "consumer_snp_array", "local_array_interpretation"
            elif len(meaningful) > 1 and meaningful[0].startswith("@") and meaningful[2].startswith("+"):
                kind, route = "fastq_sequencing", "ngs_analysis_router"
    return {"status": "IDENTIFIED" if kind != "unknown" else "UNKNOWN_FORMAT",
            "type": kind, "route": route, "callable_as_array": kind == "consumer_snp_array",
            "source_kept_private": True,
            "file_size_bytes": p.stat().st_size,
            "note": ("VCF/FASTQ/BAM/CRAM are different evidence modalities. "
                     "NGS requires reference and QC; arrays do not support de novo calls.")}

def require_array(path: str | Path) -> dict:
    record = inspect_input(path)
    if not record["callable_as_array"]:
        raise ValueError("Wrong or unconfirmed genomic assay: " + record["type"] +
                         "; do not parse as consumer rsID array")
    return record
