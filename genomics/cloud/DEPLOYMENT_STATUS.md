# SFS Genomics — Cloud Database & Remote MCP

> Public product identity: **SFS Genomics**. The Worker, D1 database and website retain legacy `lagoon` technical identifiers to preserve existing URLs. See [portfolio overview](../PORTFOLIO.md).

## Actual deployment status (2026-10-28)

- Cloudflare D1 database `lagoon-genomics` created in the **EU** with structured `genome_shards`, staging transactions, metadata, OAuth clients/codes/tokens. Database UUID is held in Worker binding, not hardcoded in browser.
- Remote Worker `lagoon-genomics-mcp` deployed to `https://lagoon-genomics-mcp.sfs-labs.workers.dev/mcp`, OAuth 2.1 PKCE/DCR, discoverable under `/.well-known/oauth-authorization-server`. Public live health/OAuth discovery checked in GitHub CI.
- GitHub Pages v1.0 adds one-off upload from the previously opened 607k SNP dataset, 256 stable shards (by numeric rsID mod 256), no additional genomics API credits, with staged commit after all 256 were stored.
- Current iPhone browser vault only supplies source data for initial cloud migration; once imported, the **database is the source of truth** for ChatGPT SNP lookups.
- Six callable tools: `genome_status`, `lookup_snp`, `lookup_snps`, `micronutrient_panel`, `public_gwas_evidence`, `public_pairwise_ld`.
- Local Python MCP retains additional study-orientation, ancestry, clinical and reference LD gates, but these do **not** magically turn common biomarker SNPs into clinical malabsorption diagnoses.

## One outstanding Cloudflare access configuration

**NOT FULLY OPERATIONAL until verified:** The live Worker was initially deployed with an `OWNER_HASH` binding for a URL-safe bootstrap token, but the live code expects an owner bearer token represented as 64 hexadecimal characters. A later source correction is committed in `genomics/cloud/worker.mjs`; Cloudflare API write attempts were blocked by a platform safety gate. Do not claim the browser genome upload or the authenticated MCP handshake is already confirmed.

### Admin repair via Cloudflare dashboard (no extra subscription)

1. Open **Cloudflare → Workers & Pages → lagoon-genomics-mcp → Settings → Variables and Secrets**.
2. Change the plain-text variable `OWNER_HASH` to the SHA-256 digest for the one-time 64-hex owner token provided privately to the owner. **Never enter the token itself as OWNER_HASH**.
3. Deploy/save the updated binding; it affects only this worker. Do not modify `education-funding-mcp` or `sfs-entire-mcp`.
4. Redeploy `genomics/cloud/worker.mjs` from the PR if you need the CORS fix for authenticated `POST /mcp` requests from the browser. The Worker OAuth endpoints and server-to-server ChatGPT MCP transport already use the remote endpoint.
5. In the Lagoon site paste the **owner token itself** exactly once into the `Cloud-Zugang` field and choose *Cloud-Zugang auf diesem Gerät speichern*. Press the cloud upload button after your SNPs are loaded. After a successful cloud commit, no original CSV is needed for normal ChatGPT queries.
6. In ChatGPT's custom MCP/app connection flow, set endpoint `https://lagoon-genomics-mcp.sfs-labs.workers.dev/mcp`; approve the OAuth screen once using that setup token. Its OAuth refresh token supports later requests without repeated password entry.

Do not paste owner token into GitHub source, Issues, D1, browser console or public chat. Configure only its hash in Cloudflare.

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
| Real complete cloud import of actual MyHeritage data | Requires user-controlled migration click and fixed auth binding | OPEN |
| OAuth ChatGPT mobile installation and full tool round trip | User-provided native mobile MCP experience acknowledged; remote handshake not yet personally verified | OPEN |
| Effect allele primary study proof and LD-adjusted personal calibrated model | Requires independent study review & clinical phenotype | PARTIAL / OPEN |
