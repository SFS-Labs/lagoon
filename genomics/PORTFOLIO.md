# SFS Genomics
### AI-Native Genomic Intelligence Platform

**SFS Labs · Genomic data engineering × AI interoperability × population genetics × biomedical evidence validation**

[Live project](https://sfs-labs.github.io/lagoon/) · [Public implementation](https://github.com/SFS-Labs/lagoon/pull/1) · [Cloud deployment](cloud/DEPLOYMENT_STATUS.md)

An AI-accessible genomic intelligence stack connecting large consumer SNP-array datasets to queryable cloud infrastructure, independently sourced biomedical research and transparent evidence gates. Scientific uncertainty is represented as a first-class status, not converted into unsupported medical predictions.

## Architecture

1. **Genomic data layer:** MyHeritage/23andMe GRCh37 intake, 609k-row scale, rsID indexing, valid calls, no-calls, rejected records and conflict QC.
2. **Cloud-native infrastructure:** Cloudflare Workers, EU D1, staged 256-shard data ingestion and authenticated SNP-query interfaces.
3. **AI interoperability:** Model Context Protocol (MCP), tool schemas, JSON-RPC and OAuth PKCE; remote tools for status, private SNP lookups, micronutrient panels, public GWAS and ancestry-specific LD.
4. **Evidence intelligence:** GWAS Catalog v2, Ensembl GRCh37, Europe PMC, variant build and effect-allele verification gates, LD-aware population reference data.
5. **Biomedical reasoning safeguards:** Separate circulating biomarkers, enzyme activity, iron-loading genetics and clinically diagnosed malabsorption; no uncalibrated individual risk scores.
6. **Reliability and verification:** Independent Python/JavaScript parsers, stress testing, provider live smoke probes and automated CI.

## Demonstrated engineering competencies

| Discipline | Implementation |
|---|---|
| Data engineering | Large-array ingestion, streaming validation, deduplication, rejection accounting and indexed lookup |
| Cloud and database | Cloudflare D1/Workers, staged batch ingestion, bounded shard writes, stateful schema |
| Agentic-AI integration | MCP tools, machine-readable contracts, JSON-RPC, OAuth PKCE for ChatGPT-facing workflows |
| Scientific source federation | GWAS Catalog, Ensembl GRCh37 and Europe PMC adapter layer |
| Quantitative methods | GWAS effect metadata, model/ancestry gates, population LD analysis, abstention on unverified risk |
| Production-oriented testing | Python/Node regression tests, 609,346-row synthetic benchmark, parity and HTTP discovery checks |

## Measured and confirmed

- A real iPhone browser import of a 609,346-row consumer SNP file produced 607,051 valid calls, 1,516 no-calls and 779 rejected rows. These numbers confirm ingestion, **not** clinical genotype validation.
- Independent parsers and representative large synthetic files were tested.
- The EU Cloudflare D1 database and remote Worker were provisioned; public Worker health and OAuth discovery succeeded.
- The public source and portfolio interface can be inspected independently.

## Explicit acceptance gates

| Capability | Current position |
|---|---|
| Public engineering implementation and mobile SNP browser | Implemented |
| Cloud database and remotely reachable MCP / OAuth metadata | Provisioned; public HTTP discovery verified |
| Complete original SNP dataset persisted in cloud | **Not independently confirmed** |
| User-authorized authenticated ChatGPT iPhone tool call | **Not independently confirmed** |
| Source-verified effect-allele strand, study provenance, ancestry, LD and phenotype across all loci | Partial; evidence gates and manual review still needed |
| Clinical-grade diagnosis or calibrated genetic penetrance | Not implemented or validated |

**Why AI-native?** The platform uses machine-addressable, source-aware research and genomics tools intended for AI reasoning workflows. This does **not** claim that a production autonomous multi-agent diagnostic engine already exists.

## Résumé-ready project description

**SFS Genomics — AI-Native Genomic Intelligence Platform** · SFS Labs

Designed and implemented a cloud-native genomics stack combining high-volume SNP-array data processing, searchable EU Cloudflare D1 storage, OAuth-enabled Model Context Protocol tooling and integrations with GWAS Catalog, Ensembl and Europe PMC. Built cross-language QC tests, population-sensitive linkage-disequilibrium safeguards and primary-study/effect-allele validation gates to avoid unsupported personal clinical-risk claims.

## Public code versus private subject data

Public: system architecture, code, synthetic tests, documentation, source adapters and research methods. Private by default: genomic raw files, personalized cloud records, credentials and authenticated MCP tool results. The older PR contains historical genotype descriptions; this is a separate history/privacy issue rather than an assumption that the repository is fully sanitized.

**Naming and migration:** Public product name: **SFS Genomics**. Legacy deployment IDs (`SFS-Labs/lagoon`, `lagoon-genomics-mcp.sfs-labs.workers.dev`, D1 `lagoon-genomics`) remain unchanged to preserve live URLs and existing integrations. They are not the public-facing product identity. A dedicated `SFS-Labs/sfs-genomics` repository is recommended for clean portfolio separation from the existing unrelated application; it has not been created.

## Supporting implementation

- [Scientific core](README.md) · [Cloud operational status](cloud/DEPLOYMENT_STATUS.md) · [LD quality gates](ld.py) · [Clinical endpoints](clinical.py) · [Browser interface](web/index.html)