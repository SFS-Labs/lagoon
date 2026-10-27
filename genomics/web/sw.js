/* Offline cache ONLY public static code; IndexedDB is managed by page-side
 * device-vault.mjs. Never caches genome plaintext, ciphertext, or keys.
 * Network-first navigation avoids showing obsolete password-vault UI.
 */
const KEY="lagoon-genomics-code-v7";
const FILES=["./index.html","./app.js?v=7","./analysis-core.mjs?v=7",
             "./device-vault.mjs?v=7","./style.css?v=7","./manifest.webmanifest"];
self.addEventListener("install",event=>{
  event.waitUntil(caches.open(KEY).then(c=>c.addAll(FILES)).then(()=>self.skipWaiting()));
});
self.addEventListener("activate",event=>{
  event.waitUntil(caches.keys().then(keys=>Promise.all(keys.filter(k=>k!==KEY).map(k=>caches.delete(k))))
    .then(()=>self.clients.claim()));
});
self.addEventListener("fetch",event=>{
  const url=new URL(event.request.url);
  if(event.request.method!=="GET"||url.origin!==self.location.origin)return;
  if(!FILES.some(f=>new URL(f,self.registration.scope).href===url.href))return;
  if(event.request.mode==="navigate"){
    event.respondWith(fetch(event.request).catch(()=>caches.match("./index.html")));
    return;
  }
  event.respondWith(caches.match(event.request).then(cached=>cached||fetch(event.request)));
});
