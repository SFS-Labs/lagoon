import test from "node:test";
import assert from "node:assert/strict";
import {readFileSync} from "node:fs";
import {resolve} from "node:path";
const root=resolve(import.meta.dirname,"..");
const get=file=>readFileSync(resolve(root,file),"utf8");
const html=get("index.html"),app=get("app.js"),sw=get("sw.js"),vault=get("device-vault.mjs");
test("Strict no-network browser CSP and versioned local-only assets",()=>{
 assert.match(html,/Content-Security-Policy/);
 assert.match(html,/connect-src 'none'/);
 assert.match(html,/script-src 'self'/);
 assert.match(html,/style-src 'self'/);
 assert.doesNotMatch(html,/<style\b/i);
 assert.doesNotMatch(html,/<script(?![^>]*\bsrc=)/i);
 assert.match(html,/href="\.\/style\.css\?v=7"/);
 assert.match(html,/src="\.\/app\.js\?v=7"/);
});
test("Service worker caches only application assets, not genomic data",()=>{
 assert.match(sw,/"\.\/device-vault\.mjs\?v=7"/);
 assert.match(sw,/e?vent\.request\.method!=="GET"/);
 assert.match(sw,/url\.origin!==self\.location\.origin/);
 assert.match(sw,/FILES\.some/);
 assert.doesNotMatch(sw,/\.put\(|indexedDB\.open\(/);
 assert.match(sw,/mode==="navigate"/);
});
test("Mobile PWA search and chromosome cards work without a wide table",()=>{
 for(const id of ["lookup","rsSearch","qcDetails","lookupResults"]){
  assert.match(html,new RegExp('id="'+id+'"'));
 }
 const css=get("style.css");
 assert.match(css,/\.marker-card/);
 assert.match(css,/@media\(min-width:720px\)/);
});
test("No password input, password function, or password prompt in live app",()=>{
 for(const text of [html,app,vault,sw]){
  assert.doesNotMatch(text,/type="password"|unlockPassword|vaultPassword|saveVault|deriveKey|PBKDF2|passphrase|passwort eingeben|password required/i);
 }
 assert.match(html,/id="rememberGenome"/);
 assert.match(html,/id="forgetGenome"/);
 assert.match(app,/from "\.\/device-vault\.mjs\?v=7"/);
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
