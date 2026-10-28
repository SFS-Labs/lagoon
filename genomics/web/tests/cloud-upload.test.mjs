import test from "node:test";
import assert from "node:assert/strict";
import {prepareShards,uploadGenomeToCloud,API} from "../cloud-upload.mjs";
const token="f".repeat(64);
function fakeDataset(size=12500){
 const calls=new Map();
 for(let i=1;i<=size;i++)calls.set("rs"+i,{chr:"1",pos:i,gt:"AC"});
 return {qc:{completed:true,build:"GRCh37",valid:size},calls};
}
test("all genome calls are deterministically sharded to 256 buckets",()=>{
 const ds=fakeDataset(12500),shards=prepareShards(ds);
 assert.equal(shards.length,256);
 assert.equal(shards.flat().length,12500);
 for(let i=0;i<256;i++)for(const row of shards[i])
  assert.equal(Number(BigInt(row[0].slice(2))%256n),i);
});
test("only explicit user-triggered upload sends 256 segments to cloud",async()=>{
 let shardWrites=0,started=0,committed=0;
 const old=globalThis.fetch;
 globalThis.fetch=async (url,init)=>{
  assert.equal(init.headers.Authorization,"Bearer "+token);
  assert.ok(url.startsWith(API));
  if(url.endsWith("/v1/import/start")){started++;return new Response(JSON.stringify({status:"READY",batch_id:"a".repeat(64)}),{status:200});}
  if(url.includes("/v1/import/shard/")){
   const body=JSON.parse(init.body);
   assert.equal(body.build,"GRCh37");
   assert.ok(Array.isArray(body.rows));
   shardWrites++;
   return new Response(JSON.stringify({status:"SAVED"}),{status:200});
  }
  if(url.includes("/v1/import/finish/")){
   committed++;return new Response(JSON.stringify({status:"CLOUD_GENOME_READY",calls:12500,shards:256}),{status:200});
  }
  throw Error("Unexpected cloud endpoint");
 };
 try{
  const ds=fakeDataset(12500);
  assert.equal(started,0);
  const result=await uploadGenomeToCloud(ds,token);
  assert.equal(result.status,"CLOUD_GENOME_READY");
  assert.equal(started,1);
  assert.equal(shardWrites,256);
  assert.equal(committed,1);
 }finally{globalThis.fetch=old;}
});
test("incomplete cloud upload must never commit active genotype database",async()=>{
 let committed=0;
 const old=globalThis.fetch;
 globalThis.fetch=async (url)=>{
  if(url.endsWith("/start"))return new Response(JSON.stringify({status:"READY",batch_id:"b".repeat(64)}),{status:200});
  if(url.includes("/shard/"))return new Response(JSON.stringify({error:"invalid_payload"}),{status:400});
  committed++;return new Response(JSON.stringify({status:"CLOUD_GENOME_READY",calls:12500}),{status:200});
 };
 try{
  await assert.rejects(uploadGenomeToCloud(fakeDataset(),token),/not|unterbrochen|invalid/);
  assert.equal(committed,0);
 }finally{globalThis.fetch=old;}
});
test("reject incorrect genome build and absent complete local array",()=>{
 assert.throws(()=>prepareShards({...fakeDataset(),qc:{build:"UNKNOWN",completed:true,valid:12500}}));
 assert.throws(()=>prepareShards({calls:new Map(),qc:{build:"GRCh37",completed:false,valid:0}}));
});
