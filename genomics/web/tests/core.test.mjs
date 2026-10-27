import test from "node:test";
import assert from "node:assert/strict";
import {parseArray,makeCandidateReport,searchImportedSnps,EVIDENCE} from "../analysis-core.mjs";
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
 assert.equal(makeCandidateReport(res,"b12").candidates.find(x=>x.rsid==="rs601338").status,"ARRAY_NO_CALL");
 assert.ok(res.noCalls.has("rs601338"));
});
test("Genome build not confirmed blocks candidate effect interpretation",async()=>{
 const res=await parseArray(make("rsid,chromosome,position,genotype\nrs601338,19,1000,AA\n"));
 assert.equal(res.qc.build,"UNKNOWN");
 assert.equal(makeCandidateReport(res).status,"BUILD_NOT_VERIFIED");
});
test("headerless standard arrays retain first SNP but cannot infer build",async()=>{
 const res=await parseArray(make("rs601338\t19\t1000\tAA\nrs855791\t22\t1001\tCT\n"));
 assert.equal(res.calls.size,2);
 assert.equal(res.qc.columns_confirmed,false);
 assert.equal(res.qc.build,"UNKNOWN");
 assert.equal(makeCandidateReport(res).status,"BUILD_NOT_VERIFIED");
});
test("silently malformed input refused",async()=>{
 await assert.rejects(parseArray(make("# unknown\njust bad data\n")),/Expected SNP header/);
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

test("synthetic SNP lookup does not generate personal risk inference",async()=>{
 const data=await parseArray(make(header+"rs900000001\t22\t37462936\tAC\n"));
 const result=searchImportedSnps(data,"rs900000001, rs900000002, rs900000001");
 assert.equal(result.looked_up,2);assert.equal(result.matched,1);
 assert.equal(result.variants[0].genotype,"AC");
 assert.equal(result.variants[0].status,"ARRAY_CALL_UNVERIFIED");
 assert.equal(result.variants[1].status,"NOT_ON_ARRAY");
 assert.ok(!JSON.stringify(result).includes("individual_risk"));
});

test("malformed identifiers and insertion-deletion alleles are separately counted",async()=>{
 const data=await parseArray(make(header+
   "rs1\t1\t100\tAA\n"+
   "i12345\t1\t101\tAC\n"+
   "rs2\t1\t102\tII\n"+
   "rs3\t1\t103\tDI\n"+
   "rs4\t1\t104\tZZ\n"+
   "rs5\tinvalid\t105\tTT\n"+
   "rs6\t1\t0\tCC\n"+
   "rs7\t1\t107\t--\n"+
   "badrow\n"));
 assert.equal(data.qc.rows,9);
 assert.equal(data.qc.valid,1);
 assert.equal(data.qc.rejected,7);
 assert.equal(data.qc.no_calls,1);
 assert.equal(data.qc.rejectionReasons.non_rsid_marker,1);
 assert.equal(data.qc.rejectionReasons.malformed_line,1);
 assert.equal(data.qc.rejectionReasons.non_snv_indel,2);
 assert.equal(data.qc.rejectionReasons.unsupported_alleles,1);
 assert.equal(data.qc.rejectionReasons.invalid_chromosome,1);
 assert.equal(data.qc.rejectionReasons.invalid_position,1);
 assert.equal(data.qc.rejectedBreakdownVerified,true);
 assert.equal(data.qc.accounting_note,"Alle Datenzeilen vollständig klassifiziert.");
});

test("whole-array search rejects IDs other than public rsIDs and excess query sizes",async()=>{
 const data=await parseArray(make(header+"rs1\t1\t100\tAC\n"));
 assert.throws(()=>searchImportedSnps(data,"i12345"),/invalid/);
 assert.throws(()=>searchImportedSnps(data,"rs1 rs2 rs3",{max:2}),/Too many/);
 assert.equal(searchImportedSnps(data,"rs1 rs2").matched,1);
});

test("all local variant searches perform no fetch calls",async()=>{
 const data=await parseArray(make(header+"rs900000001\t22\t100\tAC\n"));
 const prior=globalThis.fetch;
 globalThis.fetch=()=>{throw Error("Unexpected network call");};
 try{assert.equal(searchImportedSnps(data,"rs900000001").variants[0].genotype,"AC");}
 finally{globalThis.fetch=prior;}
});

test("same imported marker distinguishes no call from marker absent",async()=>{
 const file=make(header+"rs900000001\t1\t100\t--\nrs900000002\t1\t200\tAC\n");
 const data=await parseArray(file);
 const r=searchImportedSnps(data,"rs900000001 rs900000002 rs900000003");
 assert.deepEqual(r.variants.map(v=>v.status),["ARRAY_NO_CALL","ARRAY_CALL_UNVERIFIED","NOT_ON_ARRAY"]);
});
test("valid call supersedes prior raw no-call for the same rsID",async()=>{
 const data=await parseArray(make(header+"rs900000001\t1\t100\t--\nrs900000001\t1\t100\tAC\n"));
 assert.equal(data.noCalls.has("rs900000001"),false);
 assert.equal(data.calls.get("rs900000001").gt,"AC");
});
