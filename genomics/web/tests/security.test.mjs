import test from "node:test";
import assert from "node:assert/strict";
import {readFileSync} from "node:fs";
import {resolve} from "node:path";
const root=resolve(import.meta.dirname,"..");
const get=file=>readFileSync(resolve(root,file),"utf8");
const html=get("index.html"),app=get("app.js"),sw=get("sw.js"),vault=get("device-vault.mjs");
test("Strict no-network browser CSP and versioned local-only assets",()=>{
 assert.match(html,/Content-Security-Policy/);
 assert.ok(html.includes("connect-src https://lagoon-genomics-mcp.sfs-labs.workers.dev"));
 assert.match(html,/script-src 'self'/);
 assert.match(html,/style-src 'self'/);
 assert.doesNotMatch(html,/<style\b/i);
 assert.doesNotMatch(html,/<script(?![^>]*\bsrc=)/i);
 assert.match(html,/href="\.\/style\.css\?v=8"/);
 assert.match(html,/src="\.\/app\.js\?v=8"/);
});
test("Service worker caches only application assets, not genomic data",()=>{
 assert.match(sw,/"\.\/device-vault\.mjs\?v=8"/);
 assert.match(sw,/cloud-upload\.mjs\?v=8/);
 assert.match(sw,/e?vent\.request\.method!=="GET"/);
 assert.match(sw,/url\.origin!==self\.location\.origin/);
 assert.match(sw,/FILES\.some/);
 assert.doesNotMatch(sw,/\.put\(|indexedDB\.open\(/);
 assert.match(sw,/mode==="navigate"/);
});
test("SFS Genomics public branding and private-console separation",()=>{
 assert.match(html,/SFS <span class="brand-accent">Genomics/);
 assert.match(html,/AI-Native Genomic Intelligence Platform/);
 assert.match(html,/class="operator-console"/);
 assert.match(html,/SFS LABS/);
 const manifest=get("manifest.webmanifest");
 assert.match(manifest,/SFS Genomics/);
});
test("Mobile PWA search and chromosome cards work without a wide table",()=>{
 for(const id of ["lookup","rsSearch","qcDetails","lookupResults"]){
  assert.match(html,new RegExp('id="'+id+'"'));
 }
 const css=get("style.css");
 assert.match(css,/\.marker-card/);
 assert.match(css,/@media\(min-width:720px\)/);
});
test("Remote upload onboarding is explicit, local vault still uses no routine password",()=>{
 for(const text of [app,vault,sw]){
  assert.doesNotMatch(text,/type="password"|unlockPassword|vaultPassword|saveVault|deriveKey|PBKDF2|passphrase|passwort eingeben|password required/i);
 }
 assert.match(html,/id="rememberGenome"/);
 assert.match(html,/id="cloudOwnerToken"/);
 assert.match(html,/id="cloudUploadButton"/);
 assert.match(html,/id="forgetGenome"/);
 assert.match(app,/from "\.\/device-vault\.mjs\?v=8"/);
 assert.match(app,/await rememberGenome\(/);
 assert.match(app,/await openRememberedGenome\(/);
 assert.doesNotMatch(app,/\bfetch\(/);
});
test("Ciphertext and a non-extractable key are stored; no plaintext IndexedDB writes",()=>{
 assert.match(vault,/extractable!==false/);
 assert.match(vault,/generateKey\(\{name:"AES-GCM",length:256\},false/);
 assert.match(vault,/store\.put\(key,KEY\)/);
 assert.match(vault,/store\.put\(record,DATA\)/);
 assert.doesNotMatch(vault,/store\.put\(raw/);
 assert.match(vault,/forgetRememberedGenome/);
});
