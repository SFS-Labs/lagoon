# Integration audit — Elicit, Wolfram, Life Sciences NGS Analysis, Plasmole

Date: 2026-10-27. Repository: SFS-Labs/lagoon, PR #1. Research-only, no personal genotype file committed.

## Scope and proof

| Service | Verified activity | Role | Operational status | Cost / gate |
|---|---|---|---|---|
| Elicit MCP | `get_usage` and `search_papers` returned `api_access_denied` | Systematic literature extraction | BLOCKED | Pro required. Not integrated as a mandatory or paid dependency. |
| Wolfram Language | Evaluated natural log OR, confidence-interval SE and correlated variance | Statistical independent cross-check | VERIFIED in this development session | No new subscription or billing initiated |
| Life Sciences NGS Analysis | Read router, germline and runtime skills | Input-specific assay selection; FASTQ/BAM/CRAM/VCF needs NGS path | ROUTING IMPLEMENTED, NO PERSONAL NGS INPUT | Public pipeline nf-core/sarek requires sequencing inputs/references and resource preflight |
| Plasmole | Queried NCBI for human FUT2; loaded `NM_000511.6` | Public sequence and CDS reference workbench | REFERENCE FETCH VERIFIED | No DNA user input transmitted |
| GWAS Catalog v2 | Live GitHub Actions retrieved `rs855791` association; detected actual `_embedded.associations[].snp_allele[].rs_id` | Association discovery/metadata | LIVE SCHEMA VERIFIED + PARSER CORRECTED | Free public API with usage limits |
| Ensembl GRCh37 and Europe PMC | Both public rsID API smoke probes returned success | Reference coordinates / literature | LIVE API VERIFIED | Free public APIs; outcomes must be checked |

## Wolfram independent numerical benchmarks

- `log(1.38)` = `0.3220834991691132`.
- `SE = (log(1.60) − log(1.19)) / (2 × 1.95996398454)` = `0.0755244291368395`.
- `Var(X+Y)` for `SE(X)=0.2`, `SE(Y)=0.3` and correlation `0.8` = `0.226`.
- Code + synthetic regressions: `genomics/statistics.py`, `genomics/tests/test_statistics.py`.
- **Do not substitute genotype LD r² for a signed covariance of GWAS effect estimators.** Effect directions, ethnicity, phenotype and study overlap matter.
- Even a statistically valid OR is not a personal absolute probability without an appropriately calibrated baseline and externally validated risk model.

## Bioinformatics intake and no mis-routing

- A consumer genotyping SNP array is not NGS and cannot discover rare unmeasured variants by sequencing or predict reliable HLA-DQ2/DQ8 haplotypes from a short list.
- The assay router in `genomics/intake.py` distinguishes simple array text, VCF, FASTQ, BAM, CRAM, FASTA and compressed containers; wrong inputs are rejected.
- Real germline WGS/WES/panel input would route to nf-core/sarek or a clinically governed GATK/DeepVariant workflow after explicit reference/resource and cloud-permission checks.
- NGS sequencing tools have NOT been installed or executed because no FASTQ/BAM/CRAM/VCF was supplied.

## Plasmole provenance

- The public transcript `NM_000511.6` was fetched by accession after a gene-name search; length 3,116 bp and a coding feature annotated positions 122–1153 on that transcript.
- This demonstrates gene/transcript annotation utility. It does **not** validate any personal FUT2 rs601338 genotype or a transcript-coordinate mapping for that SNP. Plasmole is not a VCF annotator or SNP-array genotyper.
- Future sequence-based variant checks must first map an rsID to a validated reference genome and transcript HGVS change, then align known-reference and alternate sequences. No synthetic plasmid alignment can substitute for this.

## Remaining hard blockers

1. No private original consumer genotype file has been reprocessed in this PR; previous public static report calls are not authoritative.
2. GWAS Catalog returns curated association summaries, not automatically harmonized ancestry-matched OR and SE values.
3. Study authenticity is not independently validated merely by a DOI-form URL or user's uploaded effect record; `audit_quantitative_gwas_record` returns a provisional calculation, not proof.
4. Celiac HLA, low-frequency monogenic causes, CNVs and structural variants can remain entirely outside array coverage.
5. Elicit requires a paid plan in this account; the zero-cost project must not depend on it.
6. Authenticated remote iPhone-friendly access to a **private** dataset remains undeployed. A public unsecured MCP is prohibited.

## Quality gates for the exact user query

Given 'Which SNP constellations increase my risk of micronutrient deficiencies or malabsorption?', `answer_micronutrient_genetic_question` returns only observed/missing candidates with genotype, mechanism, study link, population, model and uncertainty. Quantitative study-effect interpretation is separately refused unless source metadata, matched ancestry and public reference-coordinate consistency pass. It will NOT invent a personal absolute risk, diagnose malabsorption from serum biomarker associations, or call untyped HLA haplotypes negative.
