# SFS Genomics — AI-Native Genomic Intelligence Platform

**SFS Labs | Public engineering project**

A modular genomics intelligence stack combining high-volume SNP intake, EU cloud storage, AI-accessible MCP tools, scientific source federation and evidence-validation gates.

**Portfolio:** [System architecture, engineering competencies and verified status](PORTFOLIO.md) · [Live interface](https://sfs-labs.github.io/lagoon/) · [Cloud deployment status](cloud/DEPLOYMENT_STATUS.md)

**Implementation reality:** This system is publicly inspectable, with a deployed Cloudflare Worker and D1 database. Public OAuth discovery is tested, but original-personal-genome cloud migration and authenticated mobile MCP calls are not yet fully verified. It is not a validated clinical diagnostic model.

Below are the original research-core instructions and scientific limitations. The Python stdio MCP is one component of the larger cloud project; some original runtime instructions are historical.

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

## Trait-first matching against the private genome

Use the fifth tool: `scan_private_genome_against_gwas_trait` with one of
`b12`, `folate`, `vitamin_d`, `iron`, `ferritin`, `zinc`, `calcium`,
`magnesium`, `selenium`, and `pages` from 1 to 5.

Workflow: query the GWAS Catalog v2 by nutrient phenotype using only a PUBLIC
trait string, parse a bounded set of returned rsIDs, intersect with the local
raw-genotype calls without exporting them, return candidate markers to the MCP
client with explicit `NOT_HARMONIZED` status.

This is a discovery/triage feature, NOT an exhaustive scan: GWAS records are
paginated, limited to selected top associations, and the response parser
rejects unknown upstream schemas. It must not be used for odds ratio
computation without independent build/allele and study-level verification.

See [39-step implementation gates](IMPLEMENTATION_GATES.md) for roadmap and
acceptance criteria. Optional open-source research federation:
[BioMCP](https://github.com/genomoncology/biomcp), mostly free public APIs,
with optional keys for rate improvements. Its integration has not been tested
in this repository.

## Research-engine V3 — nine MCP tools and a mobile-first PWA

The standard-library MCP server now exposes:

1. `genomic_dataset_status`
2. `analyze_micronutrient_genetics`
3. `verify_micronutrient_variant_coordinates`
4. `scan_private_genome_against_gwas_trait`
5. `inspect_private_genomic_input`
6. `audit_quantitative_gwas_record`
7. `answer_micronutrient_genetic_question`
8. `inspect_gwas_study_allele_evidence`
9. `lookup_public_variant_evidence`

For the representative question, call `answer_micronutrient_genetic_question` with
`{"nutrient":"all"}` only after `GENOMICS_RAW_FILE` is configured with a
non-public array file. The response gives observed genotype status, published
gene-trait association and its actual physiological domain, source URL and
study population; every marker remains unconfirmed pending appropriate
reference verification. No diagnosis or personalised percentage is invented.

The `audit_quantitative_gwas_record` tool checks effect metadata and
independent coordinates, using `genomics/statistics.py` and only public rsIDs
in external requests. **The study record supplied to the tool is not verified
against the actual paper by these numerical checks.** Explicit study-level
review remains mandatory. Its `ancestry_match` is an asserted input, not a
genetically inferred ancestry.

Assay routing via `genomics/intake.py` prevents accidental interpretation
of NGS VCF, FASTQ, BAM/CRAM, FASTA and gzip streams as SNP-array genotype
text. A real WGS/WES request requires reference and tool preflight under
the NGS router, not the consumer-array parser.

GWAS v2 parsing was corrected against **live, observed**
`_embedded.associations[].snp_allele[].rs_id` records, with regression tests.
These rsID matches are discovery candidates, **not** harmonized allelic
effect results. Multi-SNP haplotypes and reported SNP interaction records
are skipped rather than treated as additive single-locus effects.

See [integration audit](INTEGRATION_AUDIT.md) for actual Wolfram, NGS,
Plasmole and Elicit calls and the precise free-tier restriction.

Regression: `python -m unittest discover -s genomics/tests -v`.
All automated tests use synthetic data. The public live API probe
contains only an rsID and no individual genotypes.

## Zero-credit mobile deployment, not native mobile MCP

The 100% free, personal-DNA-private path is the client-only site in
`genomics/web/`. A separate `gh-pages` branch contains **only** its
HTML/CSS/JS/manifest/service-worker assets. The branch has no genotype files
and was built from the default-branch ancestry rather than PR genotype-report commits.

The owner still needs to enable GitHub Pages under
`https://github.com/SFS-Labs/lagoon/settings/pages` → Deploy from a branch
→ `gh-pages` → `/(root)` → Save. **Do not claim the URL is live
until deployment is confirmed.** GitHub Pages for public repositories and
public Actions workflows require no incremental monetary plan.

Safari on iPhone opens the selected MyHeritage/23andMe SNP file through
a local file picker. `File.stream()` handles up to 80 MiB with
a 1.5-million-row guard. All 609,346 synthetic rows completed in CI;
this is **not** a run on the user's original private file.

Zero network uploads, no file persistence, no cookies, CSP `connect-src 'none'`,
and the service worker caches only app code. A separate button deliberately
copies an *individual subset* to the clipboard, which can then be pasted
into ChatGPT. Clinical scores and unharmonized effect directions are omitted.

CI cross-checks the independent Python and JavaScript implementations
against the same synthetic array for QC and present/absent markers.
Live GWAS v2 evidence retrieval is separately backed by `genomics/harmonization.py`;
study-strand orientation remains unresolved, even when a public Ensembl
coordinate match is available.

Cloudflare billing API returned HTTP 403, so no Cloudflare Worker/DB
was created or upgraded. An authenticated personal-genome remote MCP
and direct custom-MCP access in native iPhone ChatGPT are NOT delivered.
See [the exact no-cost deployment plan](ZERO_COST_DEPLOYMENT.md).
