# SFS Genomics | Scientific Validation Protocol v0.1

**Date:** 2026-10-28 · **Scope:** GRCh37 chip-SNP research, not clinical diagnostics.
**Source control:** public reference identifiers and synthetic fixtures ONLY. Never commit personal genotypes, raw arrays, biometric data or access tokens.

## Validation sequence (do not skip gates)

1. **Array / genome-build QC:** One exact rsID, chromosome, GRCh37 1-based position and call; a no-call or absent marker stays `NO_CALL_OR_NOT_ON_ARRAY`. Genome counts or a successful database query do not certify assay accuracy.
2. **Genomic reference:** Match rsID, GRCh37 coordinate and reference/alternative alleles to a source with identifiable version. Distinguish chromosome-forward genomic alleles from coding-transcript alleles; do not conflate MTHFR 677C>T with genomic G>A.
3. **Strand and ambiguity:** Never silently complement a mismatch. A/T and C/G palindromic sites can remain strand-ambiguous; do not guess the signed effect or alternate dosage from letters alone.
4. **Study proof:** Record PMID, original phenotype, ancestry/sample size, build, *forward-aligned* effect/other allele, beta/OR/HR, confidence interval or standard error, statistical adjustment and replication. GWAS Catalog's association list alone does not certify harmonisation. When available use GWAS-SSF harmonised summary statistics with audit metadata.
5. **LD / haplotypes:** Compare population reference LD only within a matching build and cohort; r² has no signed phase. Never add two correlated tag-SNP effects as independent evidence without proper covariance/haplotype model.
6. **Endpoint ontology:** A circulating vitamin level is not intestinal absorption; hepcidin ratio is not iron-overload disease; LCT expression is not patient-reported symptoms; in vitro function is not a calibrated clinical outcome. Keep causal hypotheses separate from testable endpoints.
7. **Calibration/abstention:** Individual probability, clinical pathogenicity, treatment or dosage conclusions require a validated, appropriately calibrated model and relevant confirmatory phenotype. The research pipeline must abstain otherwise.

## Audited forward GRCh37 loci (versioned, non-personal)

| rsID | Locus | Forward GRCh37 | REF > ALT | Public source |
|---|---|---|---|---|
| rs855791 | TMPRSS6 | chr22:37462936 | A>G | [ClinVar GRCh37 HGVS](https://www.ncbi.nlm.nih.gov/clinvar/314922001/) |
| rs1801133 | MTHFR | chr1:11856378 | G>A | [ClinVar Variation 3520](https://www.ncbi.nlm.nih.gov/clinvar/variation/VCV000003520.60/) |
| rs1801131 | MTHFR | chr1:11854476 | T>G | [ClinVar Variation 3521](https://www.ncbi.nlm.nih.gov/clinvar/variation/VCV000003521.123/) |
| rs1799945 | HFE | chr6:26091179 | C>G | [ClinVar H63D](https://www.ncbi.nlm.nih.gov/clinvar/RCV000394716/) |
| rs4988235 | MCM6/LCT regulatory locus | chr2:136608646 | G>A | [Nature, LCT persistence allele](https://pmc.ncbi.nlm.nih.gov/articles/PMC7615474/) |

**These are genomic allele-reference records, not proven medical effect directions.** The remainder of the original 10-marker panel is explicitly not yet in the pinned manifest. Ensembl live reference fetch and fresh curation are necessary before adding more.

## Primary research and clinical-context anchors

- [GWAS Catalog SSF format and forward-strand harmonisation](https://www.ebi.ac.uk/gwas/docs/methods/summary-statistics/): full study-aligned summary statistics, not bare association API records.
- [Lactase genotype and ileal expression; CEDAR, n=196 (2021)](https://pubmed.ncbi.nlm.nih.gov/33920682/): genotype ↔ measured mucosal LCT RNA; expression != symptoms.
- [TMPRSS6 functional rs855791 and hepcidin (2011)](https://pubmed.ncbi.nlm.nih.gov/21873547/): an in-vitro and human biomarker signal, no patient diagnosis.
- [HFE + TMPRSS6 iron-parameter replication (2013)](https://jmg.bmj.com/content/50/9/593): biomarker associations; questions a single hepcidin-mediated causal explanation.
- [HFE-related hemochromatosis, GeneReviews](https://www.ncbi.nlm.nih.gov/books/NBK1440/): clinical penetrance and biochemical measures differ from individual SNP carriage.
- [CDC folic acid / common MTHFR variants](https://www.cdc.gov/folic-acid/hcp/clinical-overview/): common MTHFR genotype alone is not an indication for genotype-tailored dose.

## Reproducible commands

```bash
python -m unittest discover -s genomics/tests -v
node --test genomics/cloud/tests/*.test.mjs
node --check genomics/cloud/worker.mjs
```

Deterministic code: [Python gates](validation.py), [Python synthetic regression tests](tests/test_validation.py), [Cloud Worker](cloud/worker.mjs), [Cloud Worker synthetic regression tests](cloud/tests/reference-qc.test.mjs).

## Known unresolved scientific limitations

- The original SNP-array genotype calls are not independently confirmed in a clinical laboratory. Reference concordance is not assay validation.
- Liftover to GRCh38, rare variant detection, copy-number variants, structural variants, HLA phasing and sample-level ancestry inference are outside this phase.
- Five pinned GRCh37 loci are a *bounded pilot*, not validation of all 607,051 SNPs.
- No multi-marker ancestry-calibrated clinical-risk model, causal demonstration, confidence intervals for an individual's outcome, or true genetic phase is available.
- Daily Cloudflare D1 free-tier row-read quota is account-wide and may interrupt authenticated queries. The data remain stored; quota failure must be reported rather than silently interpreted as absence.

## Acceptance criteria

- Full stored dataset: verified independently by 256 shards summing to 607,051 records, not medically validated.
- Private MCP reference marker: green only if reference IDs, GRCh37 coordinates and alleles agree; otherwise explicit abstention.
- Study effects: not green until reference strand, summary-statistics metadata, actual phenotype, cohort applicability, LD adjustment and independent replication all satisfy the evidence gates.
- Clinical effect claim: no inferred personalized diagnosis or probability from this pilot.
