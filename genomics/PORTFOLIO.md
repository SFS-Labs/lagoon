# SFS Genomics — Engineering Evidence Profile

**AI-Native Genomic Intelligence Platform** · SFS Labs · 28 October 2026

**[Human-readable technical case study](https://sfs-labs.gitbook.io/sfs-labs-docs/ai-docs/featured-engineering-project-sfs-genomics/sfs-genomics)** · [Mobile interface](https://sfs-labs.github.io/lagoon/) · [Research validation protocol](SCIENTIFIC_VALIDATION_PROTOCOL.md) · [CI](https://github.com/SFS-Labs/lagoon/actions/workflows/genomics-ci.yml)

## Technical problem

Turn a large consumer SNP-array export into an interactive AI-accessible research system under three hard constraints: **iPhone-only initial ingestion**, **persistent private storage**, and **scientifically defensible outputs** despite incomplete genotype and study harmonization.

## Engineering achievements supported by observable evidence

| Engineering domain | Delivered system | Proof |
| --- | --- | --- |
| Data engineering | Mobile parser, explicit malformed/no-call handling, 256-shard staged import | 609,346 raw lines processed; 607,051 accepted calls |
| Cloud backend | EU D1 persistent genotype partitions and OAuth state | Direct 256-shard count reconciliation equals 607,051 |
| Applied AI / agent integration | JSON-RPC MCP over HTTP with typed tools, PKCE/DCR | ChatGPT authenticated status/lookup; external OAuth CI |
| Scientific API federation | GWAS Catalog v2 study associations and Ensembl population LD | Observed public results carrying study IDs/PMIDs and reference r² |
| Biomedical evidence engineering | GRCh37, allele-set, strand, study and endpoint abstention gates | Five pinned loci and Python/Node synthetic tests |
| Reliability | Error taxonomy for D1 quota, explicit service state and testable incident resolution | Real quota error reproduced; 401 discovery/DCR CI regressions |
| Product documentation | Nine linked public GitBook chapters and project overview | Git Sync source: `SFS-Labs/ai-docs/docs/projects/sfs-genomics/` |

## Demonstration narrative (recruiter / technical reviewer)

1. **System constraint:** no laptop or repeated chat-file upload; a phone imports the dataset once.
2. **Working data path:** accepted calls are staged and committed to D1; aggregate reconciliation verifies completeness.
3. **AI interoperability:** ChatGPT obtains OAuth access, invokes bounded MCP tools and reads the stored dataset.
4. **Research quality:** study and reference queries augment results, but unharmonized effect alleles and clinical proxies trigger abstention.
5. **Engineering scrutiny:** CI, design decisions, live incidents, known limits and source code are linked and independently inspectable.

## Verified versus incomplete

**Verified:** cloud import, D1 persistence, OAuth DCR interoperability, authenticated MCP calls, selected external research tools, CI and synthetic scientific reference gates.

**Not verified:** all personal SNPs against orthogonal reference sequencing; full primary-study allele harmonization; ancestry-phased clinical polygenic scores; clinical penetrance calibration; multi-tenant operations. The seventh remote QC tool has been deployed and synthetically validated but post-quota private-data acceptance remains open.

**Repository note:** implementation remains on an open feature branch of the unrelated older `SFS-Labs/lagoon` repository. The public product is **SFS Genomics**; a separate repository migration remains desirable to eliminate this portfolio-clarity defect. Technical Worker and Pages identifiers are retained for compatibility.

## Résumé-ready description

**SFS Genomics — AI-Native Genomic Intelligence Platform**
Designed and implemented a mobile-first genomics research platform processing 607k accepted SNP calls into 256 persistent EU Cloudflare D1 partitions. Integrated OAuth PKCE/DCR-protected MCP tools with ChatGPT, federated public GWAS/Ensembl research and built Python/JavaScript regression and reference-validation gates that explicitly distinguish genomic associations from unverified clinical inference.

**Evidence link:** https://sfs-labs.gitbook.io/sfs-labs-docs/ai-docs/featured-engineering-project-sfs-genomics/sfs-genomics
