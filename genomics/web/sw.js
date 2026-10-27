/* Cache only public application code. IndexedDB encrypted user archives are
 * excluded from Service Worker cache. Never intercept data-file operations. */
const KEY="lagoon-genomics-code-v6";
const FILES=["./index.html","./app.js?v=6","./analysis-core.mjs?v=6",
             "./vault.mjs?v=6","./style.css?v=6","./manifest.webmanifest"];
self.addEventListener("install",e=>{
 e.waitUntil(caches.open(KEY).then(c=>c.addAll(FILES)).then(()=>self.skipWaiting()));
});
self.addEventListener("activate",e=>{
 e.waitUntil(caches.keys().then(keys=>Promise.all(keys.filter(k=>k!==KEY).map(k=>caches.delete(k))))
  .then(()=>self.clients.claim()));
});
self.addEventListener("fetch",e=>{
 const url=new URL(e.request.url);
 if(e.request.method!=="GET"||url.origin!==self.location.origin)return;
 if(!FILES.some(f=>new URL(f,self.registration.scope).href===url.href))return;
 e.respondWith(caches.match(e.request).then(r=>r||fetch(e.request)));
});
