import test from "node:test";
import assert from "node:assert/strict";
import {encryptGenome,decryptGenome,validateVault,createVaultBackup,readVaultBackup,
  saveEncryptedGenome,readSavedGenome,deleteSavedGenome} from "../vault.mjs";
const encoder=new TextEncoder();
const fixture=encoder.encode("# MyHeritage Build 37\nrsid\tchromosome\tposition\tgenotype\nrs900000001\t22\t100\tAC\n");
const pass="correct horse battery staple, lagoon research";

// Deliberately minimal in-memory IDB shim to exercise the asynchronous
// transaction/serialization interface without any third-party packages.
// This is NOT a real Safari IndexedDB engine simulation.
function idbShim(){
 const disk=new Map();
 const obj={
  get(k){return op("get",k);},
  put(value,k){return op("put",k,value);},
  delete(k){return op("delete",k);}
 };
 let currentTx=null;
 function op(type,key,value){
  const request={onsuccess:null,onerror:null,result:null};
  queueMicrotask(()=>{
   if(type==="get")request.result=disk.get(key);
   if(type==="put")disk.set(key,structuredClone(value));
   if(type==="delete")disk.delete(key);
   request.onsuccess?.();
   queueMicrotask(()=>currentTx.oncomplete?.());
  });
  return request;
 }
 const db={
  objectStoreNames:{contains(){return false;}},
  createObjectStore(){return obj;},
  transaction(){
    currentTx={objectStore(){return obj;},oncomplete:null,onabort:null,onerror:null};
    return currentTx;
  },
  close(){}
 };
 return {open(){
  const request={onsuccess:null,onerror:null,onupgradeneeded:null,result:db};
  queueMicrotask(()=>{request.onupgradeneeded?.();request.onsuccess?.();});
  return request;
 }};
}
test("AES256-GCM vault round-trips original private array as full bytes",async()=>{
 const r=await encryptGenome(fixture,"at least sixteen chars and distinct password");
 assert.equal(r.cipher,"AES-256-GCM");
 assert.equal(r.iterations,600000);
 assert.notEqual(new TextDecoder().decode(r.ciphertext),new TextDecoder().decode(fixture));
 const raw=await decryptGenome(r,"at least sixteen chars and distinct password");
 assert.deepEqual(new Uint8Array(raw),fixture);
});
test("Wrong password must reject decrypt and never output partial genome",async()=>{
 const r=await encryptGenome(fixture,pass);
 await assert.rejects(decryptGenome(r,"other wrong password"),/Incorrect passphrase/);
});
test("Tamper with encrypted bytes, salt, IV or ciphertext tag always fails",async()=>{
 const r=await encryptGenome(fixture,pass);
 const bytes=new Uint8Array(r.ciphertext.slice(0));bytes[0]^=1;
 await assert.rejects(decryptGenome({...r,ciphertext:bytes.buffer},pass),/Incorrect passphrase/);
 const changed={...r,iv:"AAAAAAAAAAAAAAAA"};
 await assert.rejects(decryptGenome(changed,pass),/Incorrect passphrase/);
});
test("Passphrase minimum and unsupported input are rejected",async()=>{
 await assert.rejects(encryptGenome(fixture,"too-short"),/at least 16/);
 assert.throws(()=>validateVault({format:"random"}),/Unsupported/);
});
test("Portable backup restores ciphertext without leaking raw DNA",async()=>{
 const record=await encryptGenome(fixture,pass);
 const blob=createVaultBackup(record);
 const bytes=new Uint8Array(await blob.arrayBuffer());
 assert.equal(new TextDecoder().decode(bytes.subarray(0,9)),"LGVAULT1\n");
 const packed=await readVaultBackup(blob);
 assert.deepEqual(new Uint8Array(await decryptGenome(packed,pass)),fixture);
 assert.equal(packed.ciphertext.byteLength,record.ciphertext.byteLength);
});
test("Malformed backup magic, format and metadata cannot overwrite vault",async()=>{
 await assert.rejects(readVaultBackup(new Blob(["not a Lagoon backup"])),/invalid|Invalid|Not a Lagoon/);
 const fake=new Blob(["LGVAULT1\n{}\n",new Uint8Array(40)]);
 await assert.rejects(readVaultBackup(fake),/Unsupported/);
});
test("Encrypted IndexedDB record survives close/re-open and deletes cleanly",async()=>{
 const old=globalThis.indexedDB;
 globalThis.indexedDB=idbShim();
 try{
  const record=await encryptGenome(fixture,pass);
  const saved=await saveEncryptedGenome(record);
  assert.equal(saved.ciphertext.byteLength,record.ciphertext.byteLength);
  const nextVisit=await readSavedGenome();
  assert.deepEqual(new Uint8Array(await decryptGenome(nextVisit,pass)),fixture);
  await deleteSavedGenome();
  assert.equal(await readSavedGenome(),null);
 }finally{globalThis.indexedDB=old;}
});
