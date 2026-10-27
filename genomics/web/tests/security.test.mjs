import test from "node:test";
import assert from "node:assert/strict";
import {readFileSync} from "node:fs";
import {resolve} from "node:path";
const root=resolve(import.meta.dirname,"..");
const html=readFileSync(resolve(root,"index.html"),"utf8");
const sw=readFileSync(resolve(root,"sw.js"),"utf8");
test("strict no-network HTML CSP and locally hosted scripts/styles",()=>{
  assert.match(html,/Content-Security-Policy/);
  assert.match(html,/connect-src 'none'/);
  assert.match(html,/script-src 'self'/);
  assert.match(html,/style-src 'self'/);
  assert.doesNotMatch(html,/<style\b/i);
  assert.doesNotMatch(html,/<script(?![^>]*\bsrc=)/i);
  assert.match(html,/href="\.\/style\.css"/);
  assert.match(sw,/"\.\/style\.css"/);
});
test("public service worker only caches safe application assets",()=>{
  assert.doesNotMatch(sw,/\b(?:genotype|rawFile|rs601338|localStorage|indexedDB)\b/);
  assert.match(sw,/e\.request\.method!=="GET"/);
  assert.match(sw,/u\.origin!==self\.location\.origin/);
  assert.match(sw,/FILES\.some/);
});

test("mobile UI has cards, all-array lookup and no raw genotype uploads",()=>{
 assert.match(html,/id="lookup"/);
 assert.match(html,/id="rsSearch"/);
 assert.match(html,/id="qcDetails"/);
 assert.match(html,/id="lookupResults"/);
 assert.doesNotMatch(html,/data-upload/);
 const css=readFileSync(resolve(root,"style.css"),"utf8");
 assert.match(css,/\.marker-card/);
 assert.match(css,/@media\(min-width:720px\)/);
});
