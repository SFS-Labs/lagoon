/* Passwordless, opt-in local genome vault.
   A non-extractable AES-256-GCM CryptoKey and encrypted DNA bytes are
   stored in IndexedDB on the device. Nothing is sent over the network.
   Persistent access needs no password and is intentionally less protective:
   JavaScript from the same web origin can decrypt the genome. Do not claim
   immunity to device compromise, other same-origin scripts, or storage eviction.
   No API credits, no browser extensions, no cookies, no third-party libraries.
*/
const DB_NAME="lagoon-genomics-device-vault-v2";
const STORE="vault";
const FORMAT="lagoon-device-vault";
const VERSION=2;
const RAW_LIMIT=80*1024*1024;
const KEY="genome-key",DATA="genome-record";
const ADDITIONAL_DATA=new TextEncoder().encode("Lagoon-Genomics:device-vault:v2");
function webCrypto(){
  const c=globalThis.crypto;
  if(!c?.subtle||!c?.getRandomValues)throw Error("WebCrypto unavailable on this device.");
  return c;
}
function openDatabase(){
  if(!globalThis.indexedDB)return Promise.reject(Error("IndexedDB unavailable in this browser."));
  return new Promise((resolve,reject)=>{
    const req=indexedDB.open(DB_NAME,1);
    req.onupgradeneeded=()=>{if(!req.result.objectStoreNames.contains(STORE))req.result.createObjectStore(STORE);};
    req.onerror=()=>reject(req.error??Error("IndexedDB could not be opened."));
    req.onblocked=()=>reject(Error("Close other Lagoon tabs and reopen the app."));
    req.onsuccess=()=>resolve(req.result);
  });
}
async function useStore(mode,fn){
  const db=await openDatabase();
  try{
    return await new Promise((resolve,reject)=>{
      const tx=db.transaction(STORE,mode);
      const store=tx.objectStore(STORE);
      let result;
      try{result=fn(store,tx);}
      catch(e){try{tx.abort();}catch{}reject(e);return;}
      tx.oncomplete=()=>resolve(result);
      tx.onabort=()=>reject(tx.error??Error("Local vault write rolled back."));
      tx.onerror=()=>reject(tx.error??Error("Local vault access failed."));
    });
  }finally{db.close();}
}
function readValues(keys){
  return useStore("readonly",store=>new Promise((resolve,reject)=>{
    const got={};let n=0;
    for(const key of keys){
      const r=store.get(key);
      r.onsuccess=()=>{got[key]=r.result;if(++n===keys.length)resolve(got);};
      r.onerror=()=>reject(r.error??Error("Local vault read failed."));
    }
  }));
}
function validRecord(r){
  if(r?.format!==FORMAT||r?.version!==VERSION||!(r.iv instanceof Uint8Array)||r.iv.length!==12||
     !(r.ciphertext instanceof ArrayBuffer)||r.ciphertext.byteLength<17||
     r.ciphertext.byteLength>RAW_LIMIT+16)
      throw Error("Local encrypted genome is damaged or uses an unknown version.");
  return r;
}
function validKey(k){
  if(!k||k.type!=="secret"||k.extractable!==false||k.algorithm?.name!=="AES-GCM"||
     k.algorithm?.length!==256||!k.usages?.includes("decrypt"))
    throw Error("Device-only encryption key is missing or invalid.");
  return k;
}
export async function hasRememberedGenome(){
  const values=await readValues([KEY,DATA]);
  if(!values[DATA]&&!values[KEY])return {exists:false};
  validRecord(values[DATA]);validKey(values[KEY]);
  return {exists:true,createdAt:values[DATA].createdAt,
    encryptedBytes:values[DATA].ciphertext.byteLength};
}
export async function rememberGenome(bytes,metadata={}){
  const raw=bytes instanceof ArrayBuffer?bytes:
    ArrayBuffer.isView(bytes)?bytes.buffer.slice(bytes.byteOffset,bytes.byteOffset+bytes.byteLength):null;
  if(!raw||raw.byteLength<1||raw.byteLength>RAW_LIMIT)
    throw Error("Original genome file invalid or exceeds 80 MiB.");
  const c=webCrypto();
  const key=await c.subtle.generateKey({name:"AES-GCM",length:256},false,["encrypt","decrypt"]);
  const iv=c.getRandomValues(new Uint8Array(12));
  const cipher=await c.subtle.encrypt({name:"AES-GCM",iv,additionalData:ADDITIONAL_DATA,
    tagLength:128},key,raw);
  const record={format:FORMAT,version:VERSION,createdAt:new Date().toISOString(),
    genomeBuild:String(metadata?.build??"UNKNOWN").slice(0,30),
    iv,ciphertext:cipher};
  // Store key + ciphertext in one atomic transaction. Never store raw DNA.
  await useStore("readwrite",store=>{
    store.put(key,KEY);
    store.put(record,DATA);
  });
  // Read and cryptographically validate persisted data before confirming.
  const reloaded=await readValues([KEY,DATA]);
  const decoded=await c.subtle.decrypt({name:"AES-GCM",iv:validRecord(reloaded[DATA]).iv,
    additionalData:ADDITIONAL_DATA,tagLength:128},validKey(reloaded[KEY]),reloaded[DATA].ciphertext);
  const right=decoded.byteLength===raw.byteLength;
  new Uint8Array(decoded).fill(0);
  if(!right)throw Error("Saved genome verification failed.");
  return {saved:true,encryptedBytes:cipher.byteLength,createdAt:record.createdAt};
}
export async function openRememberedGenome(){
  const v=await readValues([KEY,DATA]);
  if(!v[DATA]&&!v[KEY])return null;
  const record=validRecord(v[DATA]);
  const key=validKey(v[KEY]);
  try{
    const decrypted=await webCrypto().subtle.decrypt({name:"AES-GCM",iv:record.iv,
      additionalData:ADDITIONAL_DATA,tagLength:128},key,record.ciphertext);
    if(decrypted.byteLength<1||decrypted.byteLength>RAW_LIMIT)throw Error("Invalid decoded DNA size.");
    return {bytes:decrypted,build:record.genomeBuild,createdAt:record.createdAt};
  }catch(e){throw Error("Saved DNA could not be unlocked on this device: "+e.message);}
}
export async function forgetRememberedGenome(){
  await useStore("readwrite",store=>{store.delete(DATA);store.delete(KEY);});
  const check=await hasRememberedGenome();
  if(check.exists)throw Error("Failed to delete the local DNA vault.");
}
export async function browserStorageStatus(){
  let persistent=false,quota=null,usage=null;
  try{
    if(navigator.storage?.persist)persistent=await navigator.storage.persist();
    else if(navigator.storage?.persisted)persistent=await navigator.storage.persisted();
  }catch{}
  try{const estimate=await navigator.storage?.estimate?.();quota=estimate?.quota??null;usage=estimate?.usage??null;}
  catch{}
  return {persistent:Boolean(persistent),quota,usage};
}
