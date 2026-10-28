# Lagoon Genomics — EUR 0 / no purchased credits execution plan

**Status:** 2026-10-27. Source: PR #1 `claude/analyze-snps-report-omgvm`. Separate static GitHub Pages branch: `gh-pages` (no private datasets).

## Constraints and reality check

Must satisfy: (A) genuine full original consumer genotype dataset, (B) evidence-gated reference and study allele harmonization, (C) safe mobile access, with **no new purchase, usage-based overages, credit depletion, or paid subscriptions**. Do not conflate a 609,346-row synthetic stress test with processing the individual's real source file.

**A hard logical constraint:** No one can independently validate an unseen private genome or produce its actual locus-level results. The source file must be consciously opened by its owner in the local app (or provided to a specifically authorized private runtime). No existing static PR snippet is a substitute.

**Mobile MCP limitation:** According to OpenAI's October 2026 custom-MCP documentation, native mobile connectivity to custom remote MCP apps is not supported; browser/web is documented. Therefore, zero-purchase mobile access is delivered **first as a standalone mobile PWA with deliberate copy/paste into ChatGPT**, not falsely claimed as a native custom remote MCP. The latter is an optional, not yet satisfied gate.

## Initial plan vs third-party-reviewed revision

| Goal | Initial candidate | Failure mode found | Adopted design |
|---|---|---|---|
| Storage | Upload complete 609k genotype file to Cloudflare KV/R2 | Exposes uniquely identifying data; not necessary for queries; paid overage risk; Workers Free CPU 10 ms | In-browser streaming parser; all calls live in temporary `Map`, never uploaded or persisted by default |
| Hosting | Cloudflare Workers/KV | Billing/subscription API returned 403 on connected account; plan cannot be guaranteed | GitHub Pages static branch `gh-pages` with **only** audited app assets; GitHub Pages Free for public repos |
| Research | Elicit Pro API + arbitrary MCP federation | Actual Elicit `api_access_denied`; variable credits/terms | Existing free GWAS Catalog v2, Ensembl GRCh37, Europe PMC and curated source links |
| Harmonization | Reverse-complement all mismatched effect alleles automatically | Strand ambiguity, palindromic alleles, study orientation unknown | `harmonization.py`: explicit `STUDY_EFFECT_ALLELE_STRAND_NOT_INDEPENDENTLY_VERIFIED` fail-closed gate |
| iPhone ChatGPT | Remote private MCP exposed with shared secret in URL | Incorrect mobile-support assumption and weak auth | Mobile PWA + explicit marker copy; no remote personal-genotype MCP enabled |
| Validation | Preview report from 10 loci | Not evidence of 609k-row coverage or independent parsing | Two independent Python / JS implementations; 609,346 synthetic variants stress test and cross-parser parity CI |

## No-cost stack and quota invariants

- **Host:** GitHub Pages for **public code-only** site. GitHub documents no cost for public repositories with GitHub Free. Dedicated `gh-pages` tree excludes the parent lending-app bundle and earlier genotype report files from *published site content*.
- **CI:** GitHub Actions on a public repository: GitHub documents public-repo Actions as free. Two Python versions, Node unit tests, 609,346 synthetic-row benchmark, parser parity. Never upload a real genome as CI artifact, fixture or GitHub secret.
- **Research:** Public GWAS Catalog REST v2, Ensembl GRCh37 REST and Europe PMC. Only public rsIDs / public phenotype strings leave the process in these calls. Use bounded pages, provider limits, no paid API credentials. Any upstream downtime produces an explicit partial result.
- **Browser:** Vanilla JavaScript + standards APIs `File.stream`, `TextDecoder`, `Map`, `Blob`, clipboard; no analytics, external npm/CDNs, WebAssembly download, LLM API billing, new compute or credential. App code cached offline; DNA is not cached.
- **Cloudflare:** No new Workers, KV, D1 or R2 deployed: the Cloudflare account's subscription could not be verified because billing read returned HTTP 403. Existing `sfs-entire-mcp` untouched. Conditional future feasibility only: Workers Free 100,000 requests/day with 10 ms CPU per request and KV Free 1 GB/1,000 writes/day; no permission to silently change plan.
- **Elicit:** Its connected API demanded a paid Pro subscription; excluded. Wolfram and Plasmole development-only validations are **not** runtime dependencies.

## What has actually been implemented

1. `genomics/web/analysis-core.mjs`: stream the full selected MyHeritage/23andMe raw text/CSV; normalized named headers, GRCh37 metadata, no-calls, duplicates, conflicts, bounded file size and row count; private in-memory lookup for any of the imported rsIDs.
2. `genomics/web/index.html`, `app.js`, `style.css`, `manifest.webmanifest`, `sw.js`: iPhone-appropriate accessible PWA, restrictive CSP, no data fetch, no auto-upload, one-click curated nutrient candidate report, explicit copy/export and erase.
3. `genomics/engine.py`: separate Python streaming array parser; accepts MyHeritage `RESULT` and 23andMe `genotype`, protects conflicting duplicates without O(n²) list scanning.
4. `genomics/harmonization.py`: live GWAS v2 SNP/PMID/study provenance from real API shape, public SNP queries and strict no-effect-direction gate; never treats serum concentration effect as measured intestinal absorption.
5. `genomics/parity_check.py` plus `genomics/web/parity-cli.mjs`: tests matching parser QC and candidate presence on an identical synthetic fixture.
6. GitHub Actions running Python/Node tests and real **public-only** source probes; no paid credits, no private data.
7. `gh-pages` branch created from clean main ancestry and containing only safe static application assets. GitHub Pages repo settings activation remains separate, so **do not assert the URL is live until tested**.

## Explicit operational gates

| Gate | Definition of done | Current status |
|---|---|---|
| A1 | Accept and parse a complete ~609k *synthetic* SNP array without upload | DONE in CI |
| A2 | Independently parse the actual original private genotype file | BLOCKED: actual original file not available to this conversation/runtime |
| A3 | Verify all candidate rsID coordinate mappings against the correct GRCh37 reference, report missing/palindromic mismatches | PARTIAL: remote lookup and refusal implemented, no original-data batch audit |
| B1 | Obtain linked GWAS source metadata PMID/study/allele from live API | DONE for public smoke; parser regression tests |
| B2 | Independently verify each study's effect-allele orientation, phenotype, ancestry, model, CI, LD and replication | OPEN: manual/full-text evidence and statistical calibration absent |
| B3 | Generate a reproducible calibrated individual probability of actual malabsorption | OPEN: not justified by existing array evidence; abstain instead of inventing |
| C1 | Mobile PWA code and safe isolated deployment branch | DONE |
| C2 | GitHub Pages setting enabled and live HTTPS end-to-end on iPhone | OPEN: Pages administrator setting and real iPhone browser test required |
| C3 | Cloud-backed authenticated private genome with mobile ChatGPT custom MCP | NOT ENABLED: payment status/consent/OAuth/mobile support unresolved |

## Next real-world action (GitHub admin UI)

Open `https://github.com/SFS-Labs/lagoon/settings/pages` as repository owner → under **Build and deployment**, choose **Deploy from a branch** → `gh-pages` → `/ (root)` → **Save**. This does not merge the genomic PR or publish genotypes. After successful GitHub Pages run, visit the Pages URL shown in GitHub Settings. The expected pattern is `https://sfs-labs.github.io/lagoon/`, but **it has not been verified live**.

On iPhone Safari visit the *verified* Pages URL → open the `.txt`, `.tsv` or `.csv` raw array from the Files picker. If downloaded as ZIP, extract locally first. Complete local QC → select nutrient → copy only selected SNPs into ChatGPT when desired. Clipboard sharing is a separate deliberate privacy decision. Add to Home Screen optionally. No file is stored server-side.

## Rollback and data security

- Close/reload the PWA to clear temporary JavaScript memory; local exports and system clipboard are separate and remain until separately cleared.
- Browser source is public and reproducible; **the file itself is private**. CSP allows only self-hosted JS/style; `connect-src 'none'`. Service worker caches a fixed allowlist of code, not genotypes.
- No tracking, external scripts, CRON, KV storage, API inference billing, automated cloud genotype transmission or billed model consumption.
- The older public PR already contains some individual genotype descriptions. New Pages branch does not copy them to its static site, but this does not erase the original GitHub history or its existing public visibility. Sanitizing public Git history is a separate privacy remediation.
- If any future variant of this project requires Cloudflare account billing, personal cloud storage, paid genomics services or ChatGPT API credits: STOP, do not auto-upgrade. Re-evaluate alternatives and obtain explicit authorization.

## Links / provider documentation

- GitHub Pages free and branch publishing: https://docs.github.com/en/pages/getting-started-with-github-pages/creating-a-github-pages-site
- GitHub Pages source settings: https://docs.github.com/en/pages/getting-started-with-github-pages/configuring-a-publishing-source-for-your-github-pages-site
- OpenAI custom MCP app mobile support: https://help.openai.com/en/articles/12584461-connecting-custom-mcp-servers-in-chatgpt
- Cloudflare Workers Free limits: https://developers.cloudflare.com/workers/platform/limits/
- Cloudflare KV free usage and refusal on limits: https://developers.cloudflare.com/kv/platform/pricing/
- GWAS Catalog source: https://www.ebi.ac.uk/gwas/
- Ensembl GRCh37: https://grch37.rest.ensembl.org/
- Europe PMC: https://europepmc.org/
