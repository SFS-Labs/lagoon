/* Only versioned public app code is cached. Personal DNA files and analysis
 * outputs are never cached, uploaded or persisted by this service worker. */
const KEY="lagoon-genomics-code-v1";
const FILES=["./index.html","./app.js","./analysis-core.mjs","./manifest.webmanifest"];
self.addEventListener("install",e=>{e.waitUntil(caches.open(KEY).then(c=>c.addAll(FILES)).then(()=>self.skipWaiting()));});
self.addEventListener("activate",e=>{e.waitUntil(caches.keys().then(keys=>Promise.all(keys.filter(k=>k!==KEY).map(k=>caches.delete(k)))).then(()=>self.clients.claim()));});
self.addEventListener("fetch",e=>{
  const u=new URL(e.request.url);
  if(e.request.method!=="GET"||u.origin!==self.location.origin)return;
  if(!FILES.some(f=>new URL(f,self.registration.scope).href===u.href))return;
  e.respondWith(caches.match(e.request).then(r=>r||fetch(e.request)));
});
