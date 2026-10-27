/* Lagoon Genomics private vault.
 * PBKDF2-HMAC-SHA256 (600k) + AES-256-GCM; random per-save salt and IV.
 * Complete original genotype bytes stored ONLY as ciphertext in IndexedDB.
 * No network, cookies, analytics, third-party scripts, or shared secrets.
 * Backup is ciphertext plus public encryption metadata. Password is NEVER saved.
 * An XSS/malicious future site deployment could read plaintext after unlock:
 * review updates, secure GitHub access and keep an offline encrypted backup.
 */
const FORMAT="lagoon-genomics-vault";
const VERSION=1,ITERATIONS=600000,MAX_RAW=80*1024*1024;
const AAD=new TextEncoder().encode(FORMAT+":raw:1");
const MAGIC="LGVAULT1\n";
const DB_NAME="lagoon-genomics-encrypted-vault-v1",STORE="files",KEY="primary";
const B64=/^[A-Za-z0-9+/]+={0,2}$/;

function requiredCrypto(){
  if(!globalThis.crypto?.subtle || !globalThis.crypto?.getRandomValues)
    throw Error("WebCrypto is unavailable in this browser.");
  return globalThis.crypto;
}
function base64(a){return btoa(String.fromCharCode(...a));}
function decode(s,count){
  if(typeof s!=="string"||!B64.test(s)||s.length>128)throw Error("Invalid vault key metadata.");
  try{const v=Uint8Array.from(atob(s),c=>c.charCodeAt(0));if(v.length!==count)throw Error();return v;}
  catch{throw Error("Invalid vault key metadata.");}
}
function normaliseCiphertext(record){
  if(record?.ciphertext instanceof ArrayBuffer)return record.ciphertext;
  if(ArrayBuffer.isView(record?.ciphertext))
    return record.ciphertext.buffer.slice(record.ciphertext.byteOffset,record.ciphertext.byteOffset+record.ciphertext.byteLength);
  throw Error("Encrypted DNA payload missing.");
}
export function validateVault(record){
  if(!record||record.format!==FORMAT||record.version!==VERSION||record.kdf!=="PBKDF2-SHA256"||
     record.cipher!=="AES-256-GCM"||record.iterations!==ITERATIONS)
    throw Error("Unsupported encrypted vault format or KDF.");
  decode(record.salt,16);decode(record.iv,12);
  const bytes=normaliseCiphertext(record);
  if(bytes.byteLength<17||bytes.byteLength>MAX_RAW+16)
    throw Error("Invalid encrypted DNA file size.");
  return {...record,ciphertext:bytes};
}
function passphraseOK(pass){
  return typeof pass==="string" && [...pass].length>=16 && [...pass].length<=512;
}
async function derive(pass,salt){
  const c=requiredCrypto();
  const input=new TextEncoder().encode(pass);
  try{
    const imported=await c.subtle.importKey("raw",input,"PBKDF2",false,["deriveKey"]);
    return await c.subtle.deriveKey({name:"PBKDF2",salt,iterations:ITERATIONS,hash:"SHA-256"},
       imported,{name:"AES-GCM",length:256},false,["encrypt","decrypt"]);
  }finally{input.fill(0);}
}
export async function encryptGenome(bytes,pass){
  if(!passphraseOK(pass))throw Error("Use a long passphrase with at least 16 characters.");
  const raw=bytes instanceof ArrayBuffer?bytes:(ArrayBuffer.isView(bytes)?
      bytes.buffer.slice(bytes.byteOffset,bytes.byteOffset+bytes.byteLength):null);
  if(!raw||raw.byteLength<1||raw.byteLength>MAX_RAW)throw Error("Raw genome file size out of range.");
  const c=requiredCrypto(),salt=c.getRandomValues(new Uint8Array(16)),iv=c.getRandomValues(new Uint8Array(12));
  const key=await derive(pass,salt);
  const ciphertext=await c.subtle.encrypt({name:"AES-GCM",iv,additionalData:AAD,tagLength:128},key,raw);
  return validateVault({format:FORMAT,version:VERSION,kdf:"PBKDF2-SHA256",
    cipher:"AES-256-GCM",iterations:ITERATIONS,salt:base64(salt),
    iv:base64(iv),ciphertext});
}
export async function decryptGenome(record,pass){
  const r=validateVault(record);
  if(typeof pass!=="string"||!pass)throw Error("Passphrase required.");
  const key=await derive(pass,decode(r.salt,16));
  try{
    const raw=await requiredCrypto().subtle.decrypt({
      name:"AES-GCM",iv:decode(r.iv,12),additionalData:AAD,tagLength:128},
      key,r.ciphertext);
    if(raw.byteLength>MAX_RAW)throw Error("Decrypted file exceeds size limit.");
    return raw;
  }catch{throw Error("Incorrect passphrase or damaged encrypted vault.");}
}
function openDb(){
  if(!globalThis.indexedDB) return Promise.reject(Error("IndexedDB unavailable in this browser."));
  return new Promise((resolve,reject)=>{
    const request=indexedDB.open(DB_NAME,1);
    request.onupgradeneeded=()=>{if(!request.result.objectStoreNames.contains(STORE))
       request.result.createObjectStore(STORE);};
    request.onsuccess=()=>resolve(request.result);
    request.onerror=()=>reject(request.error||Error("Local database unavailable."));
    request.onblocked=()=>reject(Error("Close other Lagoon tabs before changing the encrypted vault."));
  });
}
async function dbOp(mode,callback){
  const db=await openDb();
  try{
    return await new Promise((resolve,reject)=>{
      const tx=db.transaction(STORE,mode);
      const store=tx.objectStore(STORE);
      let result;
      try{
        const r=callback(store);
        r.onsuccess=()=>{result=r.result;};
        r.onerror=()=>reject(r.error||Error("Local storage operation failed."));
      }catch(e){reject(e);return;}
      tx.oncomplete=()=>resolve(result??null);
      tx.onabort=()=>reject(tx.error||Error("Local encrypted vault transaction aborted."));
      tx.onerror=()=>reject(tx.error||Error("Local encrypted vault transaction failed."));
    });
  }finally{db.close();}
}
export async function readSavedGenome(){const v=await dbOp("readonly",s=>s.get(KEY));return v?validateVault(v):null;}
export async function saveEncryptedGenome(record){
  const r=validateVault(record);
  await dbOp("readwrite",s=>s.put(r,KEY));
  const saved=await readSavedGenome();
  if(!saved||saved.ciphertext.byteLength!==r.ciphertext.byteLength||
     saved.salt!==r.salt||saved.iv!==r.iv)
    throw Error("Saved vault could not be verified after writing.");
  return saved;
}
export async function deleteSavedGenome(){return dbOp("readwrite",s=>s.delete(KEY));}
export async function storageMode(){
  let persisted=false,estimate=null;
  try{
    if(globalThis.navigator?.storage?.persist)
      persisted=Boolean(await navigator.storage.persist());
    else if(globalThis.navigator?.storage?.persisted)
      persisted=Boolean(await navigator.storage.persisted());
  }catch{}
  try{
    if(globalThis.navigator?.storage?.estimate)estimate=await navigator.storage.estimate();
  }catch{}
  return {persisted,quota:estimate?.quota??null,usage:estimate?.usage??null,
    warning:persisted?"Browser accepted persistent storage; manual clearing still removes it.":
    "Safari/browser can evict site storage; keep an encrypted backup in Files."};
}
export function createVaultBackup(record){
  const r=validateVault(record);
  const metadata={format:r.format,version:r.version,kdf:r.kdf,cipher:r.cipher,
    iterations:r.iterations,salt:r.salt,iv:r.iv};
  return new Blob([MAGIC,JSON.stringify(metadata),"\n",r.ciphertext],
     {type:"application/octet-stream"});
}
export async function readVaultBackup(file){
  if(!file||file.size<32||file.size>MAX_RAW+4096)
    throw Error("Encrypted backup file invalid or too large.");
  const prefix=await file.slice(0,2048).text();
  if(!prefix.startsWith(MAGIC))throw Error("Not a Lagoon encrypted backup.");
  const index=prefix.indexOf("\n",MAGIC.length);
  if(index<0||index>1500)throw Error("Encrypted backup header invalid.");
  let meta;
  try{meta=JSON.parse(prefix.slice(MAGIC.length,index));}
  catch{throw Error("Encrypted backup metadata invalid.");}
  const cipher=await file.slice(index+1).arrayBuffer();
  return validateVault({...meta,ciphertext:cipher});
}
