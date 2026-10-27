import test from "node:test";
import assert from "node:assert/strict";
import {parseArray,makeCandidateReport,EVIDENCE} from "../analysis-core.mjs";
const make=(text)=>{const b=new Blob([text]);return {size:b.size,stream:()=>b.stream()};};
const header="# MyHeritage DNA raw data; genome build 37\nRSID\tCHROMOSOME\tPOSITION\tRESULT\n";
test("browser-only SNP array parser with MyHeritage RESULT columns",async()=>{
 const file=make(header+"rs601338\t19\t49206674\tAA\nrs855791\t22\t37462936\tCT\n");
 const old=globalThis.fetch;let count=0;globalThis.fetch=()=>{count++;throw Error("unexpected network")};
 try{
   const res=await parseArray(file);
   assert.equal(res.qc.valid,2);assert.equal(res.qc.build,"GRCh37");
   assert.equal(res.qc.uploaded,false);assert.equal(count,0);
   const ans=makeCandidateReport(res,"b12");
   assert.equal(ans.status,"RESEARCH_ONLY");
   assert.equal(ans.candidates.find(x=>x.rsid==="rs601338").genotype,"AA");
   assert.ok(!("individual_absolute_risk" in ans));
 }finally{globalThis.fetch=old;}
});
test("rejects conflicting duplicate calls and excludes conflicted rsID",async()=>{
 const res=await parseArray(make(header+"rs601338\t19\t1000\tAG\nrs601338\t19\t1000\tAA\nrs855791\t22\t1001\tCT\n"));
 assert.equal(res.conflictCount,1);assert.equal(res.qc.conflicts,1);
 assert.equal(res.calls.has("rs601338"),false);
});
test("No-Call cannot masquerade as healthy wild type",async()=>{
 const res=await parseArray(make(header+"rs601338\t19\t1000\t--\nrs855791\t22\t1001\tCT\n"));
 assert.equal(res.qc.no_calls,1);
 assert.equal(makeCandidateReport(res,"b12").candidates.find(x=>x.rsid==="rs601338").status,"NOT_GENOTYPED");
});
test("Genome build not confirmed blocks candidate effect interpretation",async()=>{
 const res=await parseArray(make("rsid,chromosome,position,genotype\nrs601338,19,1000,AA\n"));
 assert.equal(res.qc.build,"UNKNOWN");
 assert.equal(makeCandidateReport(res).status,"BUILD_NOT_VERIFIED");
});
test("silently malformed input refused",async()=>{
 await assert.rejects(parseArray(make("# unknown\njust bad data\n")),/Header must contain/);
});
test("file size bounded",async()=>{
 await assert.rejects(parseArray({size:80*1024*1024+1,stream(){throw Error("should not read");}}),/oversized/);
});
test("same rsID and same call is deduplicated",async()=>{
 const res=await parseArray(make(header+"rs1\t1\t100\tAC\nrs1\t1\t100\tAC\n"));
 assert.equal(res.qc.duplicates,1);assert.equal(res.qc.valid,1);
});
test("609346 synthetic SNP full-file import bounded, no cloud",async()=>{
 const rows=[header];
 for(let i=0;i<609346;i++)rows.push("rs"+(900000000+i)+"\t1\t"+(1000+i)+"\tAC\n");
 const b=new Blob(rows);
 const res=await parseArray({size:b.size,stream:()=>b.stream()},{maxBytes:80*1024*1024});
 assert.equal(res.qc.valid,609346);
 assert.equal(res.calls.size,609346);
 assert.equal(res.qc.completed,true);
 assert.equal(res.qc.uploaded,false);
});
test("curated web registry has ten candidates and distinct normalized SNP IDs",()=>{
 assert.equal(EVIDENCE.length,10);
 assert.equal(new Set(EVIDENCE.map(x=>x.rsid)).size,10);
});
