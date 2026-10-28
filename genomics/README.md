# SFS Genomics
## AI-Native Genomic Intelligence Platform

**Mobile genomic data engineering · OAuth-enabled MCP · cloud persistence · evidence-aware AI tooling**

[Read the technical case study on GitBook](https://sfs-labs.gitbook.io/sfs-labs-docs/ai-docs/featured-engineering-project-sfs-genomics/sfs-genomics) · [Launch the mobile interface](https://sfs-labs.github.io/lagoon/) · [Validation protocol](SCIENTIFIC_VALIDATION_PROTOCOL.md) · [Cloud deployment status](cloud/DEPLOYMENT_STATUS.md) · [Portfolio evidence](PORTFOLIO.md)

### Why this project exists

A consumer SNP-array file is not an API, a research-grade dataset or a diagnosis. SFS Genomics builds the infrastructure between those layers: large-file parsing on an iPhone, a validated and staged import into persistent Cloudflare EU D1, an OAuth PKCE/DCR-protected remote MCP for ChatGPT, and source-aware research tools that separate a reported association from medically meaningful inference.

The value proposition is not a row lookup. It is a fully integrated **mobile → persistence → authenticated AI tool → external scientific reference → explicit confidence boundary** workflow with reproducible tests, transparent failure semantics and traceable architecture.

### Verified release evidence (2026-10-28)

| Capability | Status | Acceptance evidence |
| --- | --- | --- |
| Real mobile file intake | VERIFIED | 609,346 lines: 607,051 accepted unique calls, 1,516 no-calls, 779 rejected lines |
| Durable genomic storage | VERIFIED | Direct D1 aggregate: 256 distinct genome shards; 607,051 stored calls |
| Authenticated ChatGPT remote MCP | VERIFIED | Private status, individual, batch and micronutrient-panel calls |
| OAuth 2.1 interoperability | VERIFIED | Independent HTTP 401 metadata discovery, DCR and PKCE S256 GitHub CI |
| Public research adapters | VERIFIED FOR SELECTED QUERIES | GWAS study results and Ensembl population LD |
| GRCh37 reference verification | PILOT | Five pinned public loci, deterministic Python/Node abstention gates |
| Seventh MCP reference-validation tool | DEPLOYED; SYNTHETICALLY TESTED | Client tool-list refresh and post-quota private real-data test outstanding |
| Clinical decision support | NOT VALIDATED | No individual disease risk / dose / diagnosis claims |

**A passing reference-allele check is not a medically validated variant or phenotype.** The full 607k-array has not been independently clinically or scientifically harmonized. All released documentation and CI fixtures are public-only and synthetic; private array data remain in owner-authorized storage.

### Technical architecture

```text
iPhone SNP-array export
  → browser input QC and 256 deterministic partitions
  → authenticated, staged Cloudflare Worker import
  → 256-shard EU Cloudflare D1 database
  → OAuth discovery + DCR + authorization code with PKCE
  → authenticated MCP JSON-RPC tools in ChatGPT
  → bounded genotype retrieval / public GWAS / Ensembl LD
  → reference-alignment and scientific evidence gates
```

**Key directories**

- `web/`: browser parser, responsive user interface, optional local vault and cloud upload.
- `cloud/worker.mjs`: import, D1 access, OAuth and remote MCP. **Source changes alone do not deploy**; verify the Worker’s live version.
- `cloud/tests/`: offline synthetic Worker regressions, including quota/error handling.
- `engine.py`, `research.py`, `validation.py`, `statistics.py`, `harmonization.py`, `ld.py`, `clinical.py`: Python research and inference gates.
- `mcp.py`: **local Python stdio** MCP with additional research tools. It is not identical to the remote Cloudflare tool catalog.
- `tests/`: Python synthetic unit and cross-language parser checks.
- `SCIENTIFIC_VALIDATION_PROTOCOL.md`: versioned reference/allele/LD/clinical endpoint review standards.

### Reproduce locally (synthetic only)

From the repository feature branch, with Python 3.10+ and Node 22:

```bash
python -m unittest discover -s genomics/tests -v
node --test genomics/web/tests/*.test.mjs
node --test genomics/cloud/tests/*.test.mjs
python -m genomics.parity_check
node --check genomics/cloud/worker.mjs
python -m compileall -q genomics
```

The research and browser test suites require no private genome. Live-provider checks depend on third-party service availability; complete clinical validation is not implied by passing CI.

### Operational constraints

- **Cloudflare D1 Free row-read quotas** are enforced account-wide; the observed limit interrupted follow-up tool calls after import. The MCP now identifies quota exhaustion as temporary unavailability—not as an absent genotype.
- **OAuth setup credentials must remain private.** OAuth access is subject to the application's own permissions; public discovery and server accessibility do not make genome records public.
- **GitHub/GitBook are public surfaces.** Do not add raw genotype files, patient records, setup tokens or private tool results.
- **Legacy names:** the Worker, database and Pages hostname retain `lagoon` for compatibility. This source branch is attached to an unrelated historical repository and is **not merged**. A dedicated `sfs-genomics` repository and coordinated issuer/domain migration remain open engineering-hygiene work.

### Documentation and audit trail

The canonical human-readable engineering record is published on [SFS Labs Docs / AI Docs](https://sfs-labs.gitbook.io/sfs-labs-docs/ai-docs/featured-engineering-project-sfs-genomics/sfs-genomics) and includes nine linked chapters on architecture, ingestion, OAuth, scientific evidence, use cases, reproducibility, operations, and design decisions. The public documentation source is versioned in `SFS-Labs/ai-docs/docs/projects/sfs-genomics/` and Git Sync imports it to GitBook.

[Read the complete technical documentation](https://sfs-labs.gitbook.io/sfs-labs-docs/ai-docs/featured-engineering-project-sfs-genomics/sfs-genomics).
