# Password-free local persistence (Lagoon Genomics v0.6)

**User requirement:** Once the full SNP array is imported, revisiting the iPhone site must not require re-selecting the file or entering any password, PIN or authentication challenge. A user is entitled to elect this threat model explicitly.

## What was implemented

- `device-vault.mjs`: local IndexedDB using a non-extractable WebCrypto AES-256-GCM CryptoKey and separately stored encrypted genome bytes in one atomic transaction.
- A user presses **Einmalig auf diesem Gerät merken** once after the first import. Next visit: `hasRememberedGenome()` and `openRememberedGenome()` happen automatically; no prompt or cloud API.
- The 609k SNP array's original bytes are encrypted with random IV and a freshly generated 256-bit key; the key is intentionally also stored in the same browser-origin IndexedDB to permit automatic unlock.
- A write is reported as successful only after reading back and decrypting the stored record.
- **Dauerhafte Speicherung löschen** deletes both persisted key and ciphertext. **Aktuelle Sitzung sperren** clears the in-memory analysis while leaving durable storage intact.
- Existing raw CSV remains the recovery backup, especially if Safari evicts Website Data; `navigator.storage.persist()` is best effort, never a durability guarantee.
- The service worker only caches public app files; no genome, decryption key or report is included.
- Free: zero paid hosting/inference/API credits, no Cloudflare Worker needed, no Google account, no key server.

## Security model — important limitations

1. There is deliberately **no authentication requirement**. Someone with access to the unlocked device/browser context can reopen the genome.
2. Keeping the decryption key on the same device and origin as the ciphertext is a convenience tradeoff, not end-to-end encryption against an attacker who can execute JavaScript on that origin.
3. GitHub Pages project sites can share the `https://sfs-labs.github.io` origin, even across repository paths. Another compromised site hosted at that same origin may be able to access origin-scoped storage. A dedicated origin (free separate Pages hostname or owned domain) would strengthen origin isolation. Do not promise perfect secrecy in the current setup.
4. Browser data may be deleted/evicted, devices lost, and browser environments partitioned. Preserve the original MyHeritage CSV in the Files app or the user's independently controlled backup.
5. On first switching from transient v0.4 to v0.6, if the old browser tab was closed, the owner must select the raw file **one final time** because prior versions never persisted it. All subsequent visits within the same origin/storage partition auto-open it. This is an honest migration boundary.
6. Password-based vault UI and implementation have been removed from the active app. No password, passphrase or biometric prompt is requested, including on reopening.

## Validation

- Node tests verify encrypted device-key storage, non-extractability, ciphertext authentication, subsequent session decrypt without credential, delete of key and ciphertext, and absence of fallback to plaintext if storage is denied.
- Python genotype parser and JavaScript array parser are independently tested, including the 609,346 synthetic row benchmark and read-only reference API smoke tests.
- Real-world Safari/ChatGPT in-app browser retention must be evaluated on the user's actual phone. Reopening through a *different* browser context can expose an empty isolated storage partition; this is not a reimport requirement within the *same* context.

## Usage

1. Prefer standalone Safari at `https://sfs-labs.github.io/lagoon/`, not a changing in-app webview.
2. Select the original `MyHeritage_raw_dna_data.csv` once; wait until local QC completes.
3. Tap **Einmalig auf diesem Gerät merken** once and verify success.
4. At the next visit use the same Safari environment. No CSV, password, or login.
5. Keep the original CSV in Files as fallback. To remove local storage use **Dauerhafte Speicherung löschen**.
