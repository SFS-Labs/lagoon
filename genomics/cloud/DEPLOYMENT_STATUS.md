# SFS Genomics — Cloud Database & Remote MCP

> Public product identity: **SFS Genomics**. The Worker, D1 database and website retain legacy `lagoon` technical identifiers to preserve existing URLs. See [portfolio overview](../PORTFOLIO.md).

## Actual deployment status (2026-10-28)

- Cloudflare D1 database `lagoon-genomics` created in the **EU** with structured `genome_shards`, staging transactions, metadata, OAuth clients/codes/tokens. Database UUID is held in Worker binding, not hardcoded in browser.
- Remote Worker `lagoon-genomics-mcp` deployed to `https://lagoon-genomics-mcp.sfs-labs.workers.dev/mcp`, OAuth 2.1 PKCE/DCR, discoverable under `/.well-known/oauth-authorization-server`. Public live health/OAuth discovery checked in GitHub CI.
- GitHub Pages v1.0 adds one-off upload from the previously opened 607k SNP dataset, 256 stable shards (by numeric rsID mod 256), no additional genomics API credits, with staged commit after all 256 were stored.
- Current iPhone browser vault only supplies source data for initial cloud migration; once imported, the **database is the source of truth** for ChatGPT SNP lookups.
- Six callable tools: `genome_status`, `lookup_snp`, `lookup_snps`, `micronutrient_panel`, `public_gwas_evidence`, `public_pairwise_ld`.
- Local Python MCP retains additional study-orientation, ancestry, clinical and reference LD gates, but these do **not** magically turn common biomarker SNPs into clinical malabsorption diagnoses.

## Independently verified operational state

- **Authenticated ChatGPT-MCP working**: successful calls to `genome_status`, `micronutrient_panel`, `lookup_snp`, `lookup_snps` and external public LD/GWAS queries.
- **Actual complete personal array import verified** with a direct EU D1 query: **256/256 distinct genome shards**, their `call_count` sums to **607,051**. The original CSV is not needed on subsequent authenticated reads.
- **Cloudflare Access interception fixed** by app-scoped bypass for this Worker's own OAuth checks. PKCE/DCR live verified from GitHub runner.
- **Owner hash configured**; do not expose setup token in documentation or public issue comments. Rotate owner token if past exposure warrants it.
- **Scientific checks:** five pinned public GRCh37 allelic reference loci, deterministic abstention gates and synthetic Python/Node tests. See [protocol](../SCIENTIFIC_VALIDATION_PROTOCOL.md).
- **Current quota issue:** D1 Free has an account-wide daily read limit enforced since September 2026. At least one subsequent authenticated tool call returned that quota error. Stored data are unaffected; error is not an absent-genotype result. A paid plan was **not** selected.

## Scientific evidence contract

- GWAS Catalog: marker association + study metadata, not auto-harmonized effect direction.
- Ensembl GRCh37: must separately match personal rsID coordinate/alleles, then verify the primary **study's** forward-strand effect allele.
- LD: `public_pairwise_ld` retrieves ancestry-specific reference r², which is unsigned and cannot simply be treated as genetic effect covariance; no naive additive scores.
- Clinical: measured blood biomarkers, absorption disorders, iron overload and micronutrient deficiencies are different phenotypes. No individual numerical penetrance or malabsorption diagnosis without independent primary-study, ancestry and clinical validation.
- Unmeasured SNPs, chip no-calls, rare disorders/CNVs, HLA haplotypes are not negative results.

## No-extra-credit operation

- D1 stores ~256 payload rows, not 607,000 individual SQL writes.
- Upload has bounded 3 concurrent requests and at most 256 segments plus metadata operations.
- Cloudflare provider limits and subscribed plan still apply. No new subscriptions have been changed.
- No external paid genomics APIs or commercial inference model is used. Public GWAS and Ensembl API calls are on a best-effort basis.

## Exact verification gates

| Gate | Evidence | Status |
|---|---|---|
| Cloud D1 provisioned EU | Cloudflare API creation and schema query | DONE |
| Worker deployed with named D1 binding | Cloudflare API worker deployment | DONE |
| Public OAuth metadata / Worker health | GitHub runner public HTTP smoke | DONE |
| Website cloud upload UI | Live GitHub Pages + synthetic Node test | DONE |
| Real complete cloud import of actual MyHeritage data | Direct EU D1 query confirmed 256 distinct shards / 607,051 calls | DONE |
| OAuth ChatGPT mobile installation and full tool round trip | Authenticated tool calls verified in ChatGPT | DONE |
| Effect allele primary study proof and LD-adjusted personal calibrated model | Five public reference loci pinned; full harmonisation, individual risk calibration and clinical endpoint validation remain open | PARTIAL / OPEN |
