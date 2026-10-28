import test from 'node:test';
import assert from 'node:assert/strict';
import {createHash, webcrypto} from 'node:crypto';
import worker from '../worker.mjs';

// Purely synthetic markers; this does not contact production Cloudflare or
// contain an individual's genotype or credentials.
globalThis.crypto ??= webcrypto;
const token='x'.repeat(64);
const ownerHash=createHash('sha256').update(token).digest('hex');
function mkEnv(row) {
 const rows=row?[row]:[];
 const database={prepare(sql){
  const first=async()=>{
    if(sql.includes('FROM genome_meta'))return {state:'READY',total_calls:1,build:'GRCh37',updated_at:'test'};
    if(sql.includes('FROM genome_shards'))return {payload:JSON.stringify(rows)};
    throw new Error('Unexpected database statement: '+sql);
  };
  return {first,bind(...params){return {first};}};
 }};
 return {DB:database,OWNER_HASH:ownerHash};
}
async function call(name,args,row){
 const request=new Request('https://genomics.test/mcp',{
  method:'POST',headers:{'Authorization':'Bearer '+token,'Content-Type':'application/json'},
  body:JSON.stringify({jsonrpc:'2.0',id:1,method:'tools/call',params:{name,arguments:args}})});
 const response=await worker.fetch(request,mkEnv(row));
 assert.equal(response.status,200);
 const json=await response.json();
 assert.equal(json.result.isError,false,JSON.stringify(json.result));
 return JSON.parse(json.result.content[0].text);
}
test('public tool schema is advertised without a separate upload',async()=>{
 const request=new Request('https://genomics.test/mcp',{method:'POST',
  headers:{Authorization:'Bearer '+token,'Content-Type':'application/json'},
  body:JSON.stringify({jsonrpc:'2.0',id:42,method:'tools/list'})});
 const response=await worker.fetch(request,mkEnv());
 const j=await response.json();
 assert.ok(j.result.tools.some(x=>x.name==='validate_reference_marker'));
 assert.equal(j.result.tools.length,7);
});
test('MTHFR GRCh37 forward genomic coordinate and allele concordance',async()=>{
 const x=await call('validate_reference_marker',{rsid:'rs1801133'},['rs1801133','1',11856378,'GA']);
 assert.equal(x.status,'GRCH37_FORWARD_ALLELES_CONCORDANT');
 assert.equal(x.forward_alt_allele_dosage,1);
 assert.equal(x.clinically_validated,false);
});
test('palindromic C/G site abstains from orientation',async()=>{
 const x=await call('validate_reference_marker',{rsid:'rs1799945'},['rs1799945','6',26091179,'CG']);
 assert.equal(x.status,'PALINDROMIC_STRAND_UNRESOLVED');
 assert.equal(x.forward_alt_allele_dosage,undefined);
});
test('reverse complement is NOT silently converted',async()=>{
 const x=await call('validate_reference_marker',{rsid:'rs855791'},['rs855791','22',37462936,'CT']);
 assert.equal(x.status,'REVERSE_COMPLEMENT_CANDIDATE_UNVERIFIED');
});
test('GRCh37 coordinate mismatch prevents inference',async()=>{
 const x=await call('validate_reference_marker',{rsid:'rs1801133'},['rs1801133','1',11856379,'GG']);
 assert.equal(x.status,'GRCH37_COORDINATE_MISMATCH');
});
test('unknown public variant never inherits unrelated reference',async()=>{
 const x=await call('validate_reference_marker',{rsid:'rs123456789'},['rs123456789','1',20,'AA']);
 assert.equal(x.status,'REFERENCE_NOT_YET_VERIFIED');
});
test('not genotyped remains missing, not assumed reference',async()=>{
 const x=await call('validate_reference_marker',{rsid:'rs1801133'},null);
 assert.equal(x.status,'NO_CALL_OR_NOT_ON_ARRAY');
});
test('unauthorized MCP requests require token',async()=>{
 const r=await worker.fetch(new Request('https://genomics.test/mcp',{method:'GET'}),mkEnv());
 assert.equal(r.status,401);
 assert.match(r.headers.get('www-authenticate'),/resource_metadata=/);
});

test('D1 daily quota is surfaced as unavailable, never missing genotype',async()=>{
 const env=mkEnv();
 env.DB.prepare=()=>({async first(){throw new Error("D1_ERROR: Your account has exceeded D1's free tier daily row read limit.");}});
 const req=new Request('https://genomics.test/mcp',{
  method:'POST',headers:{Authorization:'Bearer '+token,'Content-Type':'application/json'},
  body:JSON.stringify({jsonrpc:'2.0',id:5,method:'tools/call',params:{name:'genome_status',arguments:{}}})});
 const res=await worker.fetch(req,env);
 assert.equal(res.status,200);
 const m=await res.json();
 assert.equal(m.result.isError,true);
 const item=JSON.parse(m.result.content[0].text);
 assert.equal(item.status,'TEMPORARILY_UNAVAILABLE');
 assert.equal(item.not_a_missing_genotype,true);
 assert.equal(item.error,'D1_DAILY_ROW_READ_QUOTA_EXCEEDED');
});
