import test from "node:test";
import assert from "node:assert/strict";
import {rememberGenome,openRememberedGenome,hasRememberedGenome,
  forgetRememberedGenome} from "../device-vault.mjs";

const input=new TextEncoder().encode(
 "# Genome build 37\nrsid\tchromosome\tposition\tgenotype\nrs900000001\t1\t100\tAC\n");
function fakeIndexedDB(){
 const records=new Map();
 let openCount=0;
 const db={
  objectStoreNames:{contains(name){return name==="vault" && openCount>1;}},
  createObjectStore(){return {};},
  transaction(){
   const tx={oncomplete:null,onerror:null,onabort:null,error:null,
    objectStore(){
     return {
      put(v,k){
       const req={result:undefined,onsuccess:null,onerror:null};
       queueMicrotask(()=>{records.set(k,structuredClone(v));req.onsuccess?.();queueMicrotask(()=>tx.oncomplete?.());});
       return req;
      },
      get(k){
       const req={result:undefined,onsuccess:null,onerror:null};
       queueMicrotask(()=>{req.result=records.has(k)?structuredClone(records.get(k)):undefined;
         req.onsuccess?.();queueMicrotask(()=>tx.oncomplete?.());});
       return req;
      },
      delete(k){
       const req={result:undefined,onsuccess:null,onerror:null};
       queueMicrotask(()=>{records.delete(k);req.onsuccess?.();queueMicrotask(()=>tx.oncomplete?.());});
       return req;
      }
     };
    },
    abort(){tx.onabort?.();}
   };
   return tx;
  },
  close(){}
 };
 return {records, open(){
  openCount++;
  const r={result:db,onsuccess:null,onerror:null,onupgradeneeded:null};
  queueMicrotask(()=>{if(openCount===1)r.onupgradeneeded?.();r.onsuccess?.();});
  return r;
 }};
}
test("Password-free AES-GCM device key stays non-extractable and auto-opens",async()=>{
 const old=globalThis.indexedDB;
 const shim=fakeIndexedDB();
 globalThis.indexedDB=shim;
 try{
  assert.equal((await hasRememberedGenome()).exists,false);
  const saved=await rememberGenome(input,{build:"GRCh37"});
  assert.equal(saved.saved,true);
  const key=shim.records.get("genome-key");
  assert.equal(key.type,"secret");
  assert.equal(key.extractable,false);
  await assert.rejects(globalThis.crypto.subtle.exportKey("raw",key));
  const encrypted=shim.records.get("genome-record");
  assert.equal(encrypted.format,"lagoon-device-vault");
  assert.equal(encrypted.version,2);
  assert.notDeepEqual(new Uint8Array(encrypted.ciphertext),input);
  assert.equal((await hasRememberedGenome()).exists,true);
  // Model a new tab/session: only persisted IndexedDB, no runtime password.
  const opened=await openRememberedGenome();
  assert.equal(opened.build,"GRCh37");
  assert.deepEqual(new Uint8Array(opened.bytes),input);
 }finally{globalThis.indexedDB=old;}
});
test("Tampering with ciphertext fails authenticated decryption",async()=>{
 const old=globalThis.indexedDB,shim=fakeIndexedDB();
 globalThis.indexedDB=shim;
 try{
  await rememberGenome(input);
  const corrupted=shim.records.get("genome-record");
  const clone=structuredClone(corrupted);
  new Uint8Array(clone.ciphertext)[0]^=0xff;
  shim.records.set("genome-record",clone);
  await assert.rejects(openRememberedGenome(),/could not be unlocked/);
 }finally{globalThis.indexedDB=old;}
});
test("Device key and encrypted genome delete together without password",async()=>{
 const old=globalThis.indexedDB,shim=fakeIndexedDB();
 globalThis.indexedDB=shim;
 try{
  await rememberGenome(input);
  await forgetRememberedGenome();
  assert.equal(await openRememberedGenome(),null);
  assert.equal(shim.records.has("genome-key"),false);
  assert.equal(shim.records.has("genome-record"),false);
 }finally{globalThis.indexedDB=old;}
});
test("No fallback to plaintext when IndexedDB is unavailable",async()=>{
 const old=globalThis.indexedDB;
 delete globalThis.indexedDB;
 try{
  await assert.rejects(rememberGenome(input),/IndexedDB unavailable/);
  await assert.rejects(hasRememberedGenome(),/IndexedDB unavailable/);
 }finally{globalThis.indexedDB=old;}
});
test("Missing and oversized genome inputs fail before storage",async()=>{
 await assert.rejects(rememberGenome(new Uint8Array()),/invalid/);
 await assert.rejects(rememberGenome(new Uint8Array(80*1024*1024+1)),/exceeds/);
});
