# Lagoon Genomics: audited research core (experimental)

> **Scope**: An executable, self-contained **local** genotype/research MCP module
> added to pull request #1. The existing unrelated Stacks/Next.js lending app is
> intentionally untouched. This is NOT a public hosted MCP endpoint, clinical
> test, diagnostic device, or validated genomic risk model.

## Correctness before prediction

- Input: locally held MyHeritage/23andMe-style rsID/chromosome/position/genotype TSV
  or CSV. **Never commit actual raw DNA files.**
- Outputs: measured calls, absent calls, rejected strand/allele mismatches,
  gene–trait links, quantitative population findings when supported by studies,
  citations and unresolved clinical hypotheses.
- Every missing SNP is `NOT_GENOTYPED`, not wild type. Research sources receive
  **only the public rsID**, never the raw genotype file.
- A source association with serum concentration does **not** prove reduced
  absorption, symptomatic deficiency, or an individual's probability of either.
- The markers are research leads, not a validated exhaustive SNP panel; even
  negative results cannot exclude hereditary metabolic or absorption disorders.
- HLA-DQ2/DQ8 for celiac disease must not be guessed from limited raw SNP tags.
- Genotype alleles may be on different strand conventions. Suspicious calls
  return `reverse_complement_candidate_UNVERIFIED` rather than silently flipping.
- Genomic coordinate validation, ancestry-calibrated scoring and clinical
  validation are **not** implemented. A matching letter pair is not enough
  to claim a clinically confirmed variant.

## Run it

Python 3.10+; standard library only. No subscription or commercial APIs.

```bash
python -m unittest discover -s genomics/tests -v
python -m genomics.mcp status
python -m genomics.mcp analyze --raw /PRIVATE/FILE/your-genome.txt --format markdown
python -m genomics.mcp research --rsid rs855791
GENOMICS_RAW_FILE=/PRIVATE/FILE/your-genome.txt python -m genomics.mcp mcp
```

STDIO MCP client config (only on a trusted personal computer/cloud workspace
that can access the private local file):

```json
{
  "mcpServers": {
    "lagoon-genomics": {
      "command": "python",
      "args": ["-m", "genomics.mcp", "mcp"],
      "env": {"GENOMICS_RAW_FILE": "/PRIVATE/FILE/your-genome.txt"}
    }
  }
}
```

The personal DNA source file is **not present in this public repository**.
Without the full raw file the tool correctly responds `NO_PRIVATE_RAW_FILE`.

## Research adapters (free, external HTTP; rate-limited)

`lookup_public_variant_evidence` queries:
1. GWAS Catalog **v2** (`associations?rs_id=...`), not retired v1.
2. Ensembl **GRCh37** variation endpoint, not silently GRCh38.
3. Europe PMC REST search for literature identifiers.

The response is raw source context, not a harmonised effect size.
Validate effect allele, risk direction, population, endpoint, study design,
LD, sample overlap, CI and p-value **before** drawing personalised conclusions.
The tool truncates individual upstream payloads and returns explicit upstream
errors instead of fabricating a successful lookup.

## Additional free MCPs (remote, separate services)

- **Official GWAS Catalog MCP**: https://ebi.ac.uk/gwas/mcp
  Search traits, studies and associations; hosted, Apache-2.0.
- **Official Open Targets Platform MCP**:
  https://mcp.platform.opentargets.org/mcp
  GraphQL-backed variant, disease and target discovery. Hosting is separate.
- NCBI E-utilities, ClinVar, ClinPGx and Open Targets GraphQL:
  free programmatic *APIs*; do not falsely describe them as installed MCPs.
- LDlink: free NIH utility with registration/token; use for ancestry-dependent
  LD checks when the relevant data are available, not to multiply correlated
  odds ratios. Check its individual terms.
- MyVariant.info: free aggregator, useful for cross-checking, but upstream
  licenses can differ; not a replacement for ClinVar/Ensembl primary records.
- OpenAlex: limited free API allowance; optional literature discovery, not
  necessary for base functionality.

Useful external documentation:
- https://www.ebi.ac.uk/gwas/docs/programmatic-access/rest-api/
- https://rest.ensembl.org/
- https://www.ncbi.nlm.nih.gov/clinvar/docs/programmatic_access/
- https://www.ebi.ac.uk/europepmc/webservices/rest/
- https://platform-docs.opentargets.org/data-access/graphql-api

## Unresolved issues in the original static report

1. `SLCO1B1 rs4149056`: the decreased-function allele is **C**, not T.
   Source: https://pmc.ncbi.nlm.nih.gov/articles/PMC3384438/
2. `DPYD rs67376798` is c.2846A>T; HapB3 corresponds to
   `rs75017182` (functional) / `rs56038477` (proxy).
   Source: https://pmc.ncbi.nlm.nih.gov/articles/PMC11280107/
3. GWAS effects from linked SNPs may be one LD signal, not two independent
   hits; no multiplying per-SNP ORs without a validated model.
4. Variant positions, assay strand and consumer-chip labels must be verified
   against an authoritative build-specific reference before medical use.
5. The original report's drug advice/dosages and some risk labels have **not**
   passed independent clinical validation. It must not be reissued as medical
   clearance or a prescription recommendation.

## Operational definition of "working"

✅ Local deterministic parser, curated evidence, missingness handling, strand
mismatch detection, three public research adapters, MCP stdio commands and
synthetic unit tests are committed to the PR branch.

⛔ **Not yet verified**: connection to a real personal genome, live upstream
requests in production, clinical variant harmonisation, personalized scoring,
remote iPhone-accessible authenticated MCP hosting or independent medical
review. Do not imply these exist merely because code is committed.

Security: The GitHub repository and this PR are **PUBLIC** and already contain
personal-genotype descriptions. Avoid expanding that disclosure. To revoke
historical exposure, a private repository and history remediation must be planned;
deleting a current file alone does not remove its Git history.
