# 39 evidence-gated delivery steps for Lagoon Genomics

Each step is DONE only if code or governance is actually implemented; OPEN means no claim of completion. Numbered steps are acceptance criteria, not an autonomous promise.

**Scope:** non-clinical, private genetic research. Public Git history already contains sensitive genotype descriptions. Existing static report is not clinically validated.

| # | Track | Acceptance gate | Status |
|---:|---|---|---|
| 1 | Provenance & privacy | Original PR and branch inspected | DONE |
| 2 | Provenance & privacy | Existing static report preserved without treating it as clinical truth | DONE |
| 3 | Provenance & privacy | No raw personal genome uploaded to public branch | DONE |
| 4 | Provenance & privacy | Private raw file input supported | DONE |
| 5 | Provenance & privacy | Consent, access policy and encryption at rest for private production store | OPEN |
| 6 | Provenance & privacy | Archive/retire public genotype descriptions, including history and forks | OPEN |
| 7 | Genotype integrity | Streaming SNP input parser with maximum file size/record limit | DONE |
| 8 | Genotype integrity | Skip no-calls and malformed rows | DONE |
| 9 | Genotype integrity | Reject contradictory repeated rsID calls | DONE |
| 10 | Genotype integrity | Require chromosome and coordinate fields | DONE |
| 11 | Genotype integrity | Determine genome build from metadata where available | DONE |
| 12 | Genotype integrity | Compare variant positions against Ensembl GRCh37 | DONE |
| 13 | Genotype integrity | Reject unsupported orientation; flag palindromic alleles | DONE |
| 14 | Genotype integrity | Clinically validate selected high-consequence array variants separately | OPEN |
| 15 | Phenotype knowledge | Distinguish blood biomarker, transport, utilization and true absorption | DONE |
| 16 | Phenotype knowledge | Represent explicit NOT_GENOTYPED state | DONE |
| 17 | Phenotype knowledge | Curate B12, iron, vitamin D, folate and lactose research leads | DONE |
| 18 | Phenotype knowledge | Expand to zinc, magnesium, copper, selenium, vitamin A/E/K, thiamine | OPEN |
| 19 | Phenotype knowledge | Investigate celiac HLA-DQ2/DQ8 via validated haplotyping, not tag SNP guess | OPEN |
| 20 | Phenotype knowledge | Investigate monogenic transport disorders where array coverage permits | OPEN |
| 21 | Phenotype knowledge | Build differential: diet, medications, inflammation, bariatric disease | PARTIAL |
| 22 | Evidence retrieval | GWAS Catalog REST v2 rsID adapter | DONE |
| 23 | Evidence retrieval | Ensembl GRCh37 variation adapter | DONE |
| 24 | Evidence retrieval | Europe PMC search adapter | DONE |
| 25 | Evidence retrieval | Integrate official GWAS Catalog MCP as a tool option | OPEN |
| 26 | Evidence retrieval | Integrate official Open Targets MCP as a tool option | OPEN |
| 27 | Evidence retrieval | Evaluate BioMCP for ClinVar, ClinGen, gnomAD, literature | OPEN |
| 28 | Evidence retrieval | Build trait-first discovery with pagination and local intersect | PARTIAL |
| 29 | Evidence retrieval | Cache/source-snapshot and respect rate limits and licensing | OPEN |
| 30 | Statistical reliability | Require effect allele/strand and GRCh37 allele normalization | PARTIAL |
| 31 | Statistical reliability | Require OR or beta, confidence interval, unit, phenotype and ancestry | PARTIAL |
| 32 | Statistical reliability | Identify linked SNPs and prune/correct LD double-counting | OPEN |
| 33 | Statistical reliability | Exclude underpowered and unreproduced associations from score | OPEN |
| 34 | Statistical reliability | Validate ancestry-matched baseline and externally calibrated PRS | OPEN |
| 35 | Statistical reliability | Distinguish estimated genetic association from laboratory diagnosis | DONE |
| 36 | Delivery and QA | Local STDIO MCP with status, research, analysis and coordinate tools | DONE |
| 37 | Delivery and QA | Synthetic unit tests and Python-version matrix | DONE |
| 38 | Delivery and QA | Independent dry run on real genomics file with approved access | OPEN |
| 39 | Delivery and QA | Authenticated remote or secure tunnel iPhone workflow, adversarial QA | OPEN |

**As of 2026-10-27: 20/39 documented gates met in code/design; 4 partially implemented; 15 unresolved.**

PARTIAL means a subcomponent exists, but the full acceptance gate is not satisfied. Statistical audit rejects incomplete records but does not extract and verify study results automatically.\n\n**Do not merge as 'ready for personalized clinical recommendations'.** Test coverage on synthetic fixtures and working stdio protocol is necessary but not sufficient.

Primary free data infrastructure: official GWAS Catalog MCP (https://ebi.ac.uk/gwas/mcp), official Open Targets Platform MCP (https://mcp.platform.opentargets.org/mcp), and optionally BioMCP (https://github.com/genomoncology/biomcp). Other research sources can be consulted by free read-only HTTP adapters. Validate provider terms and authentication before production.

Data-handling invariant: public provider calls use only public rsIDs and phenotype search strings. Do not send individual genotypes, raw datasets, name, diagnoses, lab results or other private data to third-party research APIs. Query-results returned to an LLM also contain personal genotype-derived information and need an explicit privacy policy.

Absolute probability, clinical penetrance, or risk scores must be omitted when external validation/ancestry-calibrated model is absent.
