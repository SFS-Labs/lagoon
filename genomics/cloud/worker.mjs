// Lagoon Genomics: authenticated persistent cloud DB and MCP, no model credits.
// D1 EU; staged 256-shard import, no raw CSV committed to GitHub.
const RS=/^rs[0-9]{1,15}$/i, ORIGIN="https://sfs-labs.github.io",E=new TextEncoder();
const PANEL=[["rs601338","FUT2","serum B12"],["rs855791","TMPRSS6","serum iron"],["rs10741657","CYP2R1","vitamin D"],["rs2282679","GC","vitamin D binding"],["rs12785878","DHCR7","vitamin D"],["rs4988235","LCT","lactase"],["rs1801133","MTHFR","folate"],["rs1801131","MTHFR","folate"],["rs1799945","HFE","iron homeostasis"],["rs1800562","HFE","iron loading"]];
// Audited public GRCh37 reference loci; private calls are never committed.
const PINNED_REFERENCE={
 rs855791:{gene:"TMPRSS6",chr:"22",pos:37462936,ref:"A",alt:"G",source:"https://www.ncbi.nlm.nih.gov/clinvar/314922001/"},
 rs1801133:{gene:"MTHFR",chr:"1",pos:11856378,ref:"G",alt:"A",source:"https://www.ncbi.nlm.nih.gov/clinvar/variation/VCV000003520.60/"},
 rs1801131:{gene:"MTHFR",chr:"1",pos:11854476,ref:"T",alt:"G",source:"https://www.ncbi.nlm.nih.gov/clinvar/variation/VCV000003521.123/"},
 rs1799945:{gene:"HFE",chr:"6",pos:26091179,ref:"C",alt:"G",source:"https://www.ncbi.nlm.nih.gov/clinvar/RCV000394716/"},
 rs4988235:{gene:"MCM6/LCT",chr:"2",pos:136608646,ref:"G",alt:"A",source:"https://pmc.ncbi.nlm.nih.gov/articles/PMC7615474/"}
};
const COMP={A:"T",T:"A",C:"G",G:"C"};
function referenceQC(variant){
 const rsid=variant?.rsid||null, locus=PINNED_REFERENCE[rsid];
 const base={rsid,reference:locus||null,build:"GRCh37",clinically_validated:false};
 if(!variant||variant.status!=="ARRAY_CALL_UNVERIFIED")
  return {...base,status:"NO_CALL_OR_NOT_ON_ARRAY",reason:"Missing must never be treated as reference allele"};
 if(!locus)return {...base,status:"REFERENCE_NOT_YET_VERIFIED",reason:"No verified forward reference for this locus"};
 if(variant.chromosome!==locus.chr||variant.position!==locus.pos)
  return {...base,status:"GRCH37_COORDINATE_MISMATCH",reason:"rsID or platform locus disagree"};
 const genotype=variant.genotype;
 if(typeof genotype!=="string"||!/^[ACGT]{2}$/.test(genotype))
  return {...base,status:"INVALID_DIPLOID_BASES"};
 const forward=[...genotype].every(a=>a===locus.ref||a===locus.alt);
 const reverse=[...genotype].every(a=>COMP[a]===locus.ref||COMP[a]===locus.alt);
 if(forward&&reverse)return {...base,status:"PALINDROMIC_STRAND_UNRESOLVED",reason:"Cannot infer forward effect allele dosage"};
 if(forward)return {...base,status:"GRCH37_FORWARD_ALLELES_CONCORDANT",
  forward_alt_allele_dosage:[...genotype].filter(a=>a===locus.alt).length,
  reason:"Array genotype not independently confirmed; no clinical risk calculated"};
 if(reverse)return {...base,status:"REVERSE_COMPLEMENT_CANDIDATE_UNVERIFIED",reason:"Never silently flip platform alleles"};
 return {...base,status:"ALLELES_NOT_IN_REFERENCE_SET"};
}
const TOOLS=[
 {name:"genome_status",description:"Persistent cloud genotype database status. No genome upload required per query.",inputSchema:{type:"object",properties:{}}},
 {name:"validate_reference_marker",description:"Validate one private cloud genotype against a pinned GRCh37 locus, reference/alternative alleles and orientation gates. Explicitly NON-clinical; missing/ambiguous returns abstention.",inputSchema:{type:"object",properties:{rsid:{type:"string"}},required:["rsid"]}},
 {name:"lookup_snp",description:"Query one private rsID genotype from EU D1; no biomarker diagnosis implied.",inputSchema:{type:"object",properties:{rsid:{type:"string"}},required:["rsid"]}},
 {name:"lookup_snps",description:"Query up to 25 private rsID genotypes from permanent cloud database.",inputSchema:{type:"object",properties:{rsids:{type:"array",items:{type:"string"},maxItems:25}},required:["rsids"]}},
 {name:"micronutrient_panel",description:"Research panel B12, iron, vitamin D, folate, lactase, not a clinically calibrated diagnosis.",inputSchema:{type:"object",properties:{}}},
 {name:"public_gwas_evidence",description:"Published GWAS Catalog v2 research associations for a public rsID. Effect alleles NOT harmonized.",inputSchema:{type:"object",properties:{rsid:{type:"string"}},required:["rsid"]}},
 {name:"public_pairwise_ld",description:"Public Ensembl GRCh37 1000G population pairwise LD r2, not signed model covariance.",inputSchema:{type:"object",properties:{rsid_a:{type:"string"},rsid_b:{type:"string"},population:{type:"string",enum:["EUR","AFR","AMR","EAS","SAS"]}},required:["rsid_a","rsid_b","population"]}}
];
const now=()=>Math.floor(Date.now()/1000);
const random=()=>Array.from(crypto.getRandomValues(new Uint8Array(32)),x=>x.toString(16).padStart(2,"0")).join("");
async function hash(x){return Array.from(new Uint8Array(await crypto.subtle.digest("SHA-256",E.encode(x))),v=>v.toString(16).padStart(2,"0")).join("");}
async function pkce(v){return btoa(String.fromCharCode(...new Uint8Array(await crypto.subtle.digest("SHA-256",E.encode(v))))).replace(/\+/g,"-").replace(/\//g,"_").replace(/=/g,"");}
function header(origin,extra={}){const h=new Headers(extra);h.set("Cache-Control","no-store");h.set("X-Content-Type-Options","nosniff");if(origin===ORIGIN){h.set("Access-Control-Allow-Origin",ORIGIN);h.set("Access-Control-Allow-Headers","Authorization,Content-Type");h.set("Access-Control-Allow-Methods","GET,POST,PUT,OPTIONS");}return h;}
function out(v,status=200,origin=""){return new Response(JSON.stringify(v),{status,headers:header(origin,{"Content-Type":"application/json; charset=utf-8"})});}
function page(content,status=200){return new Response(content,{status,headers:header("",{"Content-Type":"text/html; charset=utf-8","Content-Security-Policy":"default-src 'none'; style-src 'unsafe-inline'; form-action 'self'; base-uri 'none'; frame-ancestors 'none'"})});}
function bearer(req){const m=(req.headers.get("Authorization")||"").match(/^Bearer ([A-Za-z0-9_-]{43,200})$/);return m?m[1]:"";}
async function isOwner(req,env){const s=bearer(req);return s&&await hash(s)===env.OWNER_HASH;}
async function canRead(req,env){if(await isOwner(req,env))return true;const t=bearer(req);if(!t)return false;const x=await env.DB.prepare("SELECT expires_at FROM oauth_tokens WHERE token_hash=? AND kind='access'").bind(await hash(t)).first();return !!x&&x.expires_at>now();}
const valid=id=>typeof id==="string"&&RS.test(id),bucket=id=>Number(BigInt(id.slice(2))%256n);
async function status(env){const r=await env.DB.prepare("SELECT state,total_calls,build,updated_at FROM genome_meta WHERE id=1").first();return r&&r.state==="READY"?{status:"READY",total_calls:r.total_calls,build:r.build,updated_at:r.updated_at}:{status:"EMPTY_CLOUD_DATABASE"};}
async function query(ids,env){
 if(!Array.isArray(ids)||ids.length<1||ids.length>25||ids.some(x=>!valid(x)))throw Error("1–25 public rsIDs required");
 const st=await status(env);if(st.status!=="READY")return {...st,variants:[]};
 const cache=new Map(),found=[];
 for(const raw of [...new Set(ids.map(x=>x.toLowerCase()))]){
  const b=bucket(raw);
  if(!cache.has(b)){const x=await env.DB.prepare("SELECT payload FROM genome_shards WHERE shard_id=?").bind(b).first();cache.set(b,new Map((x?JSON.parse(x.payload):[]).map(v=>[v[0],v])));}
  const c=cache.get(b).get(raw);
  found.push({rsid:raw,genotype:c?.[3]??null,chromosome:c?.[1]??null,position:c?.[2]??null,status:c?"ARRAY_CALL_UNVERIFIED":"NOT_ON_ARRAY_OR_NO_CALL"});
 }
 return {status:"OK",build:st.build,variants:found,medical_certainty:"RESEARCH_ONLY_NO_DIAGNOSIS_NO_UNVALIDATED_EFFECT_DIRECTION"};
}
async function runTool(name,args,env){
 if(name==="genome_status")return status(env);
 if(name==="validate_reference_marker"){if(!valid(args.rsid))throw Error("Invalid public rsID");const q=await query([args.rsid],env);if(q.status!=="OK")return q;return referenceQC(q.variants[0]);}
 if(name==="lookup_snp")return query([args.rsid],env);
 if(name==="lookup_snps")return query(args.rsids,env);
 if(name==="micronutrient_panel"){const r=await query(PANEL.map(x=>x[0]),env);return {...r,markers:r.variants.map(v=>({...v,gene:PANEL.find(x=>x[0]===v.rsid)?.[1],phenotype:PANEL.find(x=>x[0]===v.rsid)?.[2]}))};}
 if(name==="public_gwas_evidence"){
  if(!valid(args.rsid))throw Error("Invalid public rsID");
  const url="https://www.ebi.ac.uk/gwas/rest/api/v2/associations?rs_id="+args.rsid+"&size=8&page=0";
  const result=await fetch(url,{headers:{Accept:"application/json"}});if(!result.ok)throw Error("GWAS upstream unavailable");
  const data=await result.json();
  return {rsid:args.rsid,associations:(data?._embedded?.associations||[]).slice(0,8).map(x=>({study:x.accession_id,pubmed:x.pubmed_id,association_id:x.association_id,reported_effect_allele:x.snp_allele,p_value:x.p_value,reported_trait:x.reported_trait})),effect_strand_harmonized:false,clinical_diagnosis:null};
 }
 if(name==="public_pairwise_ld"){
  const a=args.rsid_a,b=args.rsid_b,p=args.population;
  if(!valid(a)||!valid(b)||a===b||!["EUR","AFR","AMR","EAS","SAS"].includes(p))throw Error("Invalid public rsIDs or reference ancestry");
  const url="https://grch37.rest.ensembl.org/ld/human/pairwise/"+a+"/"+b+"?population_name=1000GENOMES%3Aphase_3%3A"+p+";content-type=application%2Fjson";
  const response=await fetch(url,{headers:{Accept:"application/json"}});
  if(!response.ok)return {status:"LD_PROVIDER_UNAVAILABLE"};
  const data=await response.json(),rows=Array.isArray(data)?data:[data],r2=rows.map(x=>Number(x.r2)).find(x=>Number.isFinite(x)&&x>=0&&x<=1);
  return {status:r2===undefined?"LD_UNKNOWN":"PUBLIC_LD",r2:r2??null,population:p,source:url,combine_variants_as_independent:false,not_personal_ancestry:true};
 }
 throw Error("Unknown tool");
}
function authChallenge(req){
 const origin=new URL(req.url).origin;
 return new Response(JSON.stringify({error:"authentication_required"}),{
  status:401,headers:{"Content-Type":"application/json","Cache-Control":"no-store",
   "WWW-Authenticate":'Bearer resource_metadata="'+origin+'/.well-known/oauth-protected-resource/mcp", scope="genome:read"'}
 });
}
async function mcp(req,env){
 if(!await canRead(req,env))return authChallenge(req);
 const m=await req.json();if(!m||typeof m!=="object")return out({error:"invalid_request"},400);
 if(!Object.hasOwn(m,"id"))return new Response(null,{status:202});
 let v;
 if(m.method==="initialize")v={protocolVersion:"2025-06-18",capabilities:{tools:{listChanged:false}},serverInfo:{name:"lagoon-genomics-cloud",version:"1.0.0"}};
 else if(m.method==="ping")v={};
 else if(m.method==="tools/list")v={tools:TOOLS};
 else if(m.method==="tools/call"){try{const r=await runTool(m.params?.name,m.params?.arguments||{},env);v={content:[{type:"text",text:JSON.stringify(r)}],isError:false};}catch(e){
 const msg=String(e?.message||e);
 const readQuota=/exceeded D1.s free tier daily row read limit/i.test(msg);
 const writeQuota=/exceeded D1.s free tier daily row write limit/i.test(msg);
 const err=readQuota||writeQuota
  ?{error:readQuota?"D1_DAILY_ROW_READ_QUOTA_EXCEEDED":"D1_DAILY_ROW_WRITE_QUOTA_EXCEEDED",
    status:"TEMPORARILY_UNAVAILABLE",reset:"midnight UTC",not_a_missing_genotype:true}
  :{error:msg.slice(0,120)};
 v={content:[{type:"text",text:JSON.stringify(err)}],isError:true};
}}
 else return out({jsonrpc:"2.0",id:m.id,error:{code:-32601,message:"Unknown method"}});
 return out({jsonrpc:"2.0",id:m.id,result:v},200,req.headers.get("Origin"));
}
function redirectAllowed(uri){try{const u=new URL(uri);return u.protocol==="https:"&&!u.hash&&!u.username&&!u.password&&uri.length<700;}catch{return false;}}
const param=async r=>(r.headers.get("content-type")||"").includes("application/json")?r.json():Object.fromEntries((await r.formData()).entries());
async function registered(env,id,uri){const x=await env.DB.prepare("SELECT redirect_uris FROM oauth_clients WHERE client_id=?").bind(id).first();return !!x&&JSON.parse(x.redirect_uris).includes(uri);}
async function register(req,env){
 const x=await req.json(),urls=x.redirect_uris;
 if(!Array.isArray(urls)||!urls.length||urls.length>5||urls.some(u=>!redirectAllowed(u)))return out({error:"invalid_redirect_uri"},400);
 const id=random();
 await env.DB.prepare("INSERT INTO oauth_clients(client_id,redirect_uris,client_name,created_at) VALUES(?,?,?,?)").bind(id,JSON.stringify(urls),String(x.client_name||"ChatGPT").slice(0,90),now()).run();
 return out({client_id:id,client_id_issued_at:now(),redirect_uris:urls,token_endpoint_auth_method:"none",grant_types:["authorization_code","refresh_token"],response_types:["code"]},201);
}
async function authorize(req,env){
 const x=req.method==="GET"?Object.fromEntries(new URL(req.url).searchParams):await param(req);
 const {client_id,redirect_uri,state="",code_challenge,code_challenge_method,response_type}=x;
 if(response_type!=="code"||code_challenge_method!=="S256"||!code_challenge||!/^[A-Za-z0-9_-]{43,128}$/.test(code_challenge)||!await registered(env,client_id,redirect_uri))return page("<h1>Invalid OAuth request</h1>",400);
 if(req.method==="GET"){
  const data={client_id,redirect_uri,state,code_challenge,code_challenge_method,response_type};
  const hidden=Object.entries(data).map(([k,v])=>'<input type="hidden" name="'+k+'" value="'+String(v).replace(/&/g,"&amp;").replace(/"/g,"&quot;").replace(/</g,"&lt;")+'">').join("");
  return page('<html lang="de"><meta name="viewport" content="width=device-width,initial-scale=1"><title>SFS Genomics | ChatGPT verbinden</title><body style="font:16px system-ui;max-width:36rem;margin:30px auto;padding:24px;background:#071b23;color:#f2faf9;min-height:100vh"><p style="letter-spacing:.18em;color:#3fc7bd;font-size:.75rem;font-weight:700">SFS LABS / GENOMICS</p><h1 style="font-size:2rem;line-height:1.2">SFS <span style="color:#3fc7bd">Genomics</span></h1><p style="color:#a8c7c7">AI-Native Genomic Intelligence Platform</p><h2>ChatGPT verbinden</h2><p>Einmaliger OAuth-Verbindungsaufbau für deine Cloud-Datenbank.</p><form method="post" action="/authorize">'+hidden+'<label>Einmaliger Einrichtungscode<input type="password" name="setup_token" autocomplete="off" required style="display:block;padding:12px;width:95%;background:#112b34;color:white;border:1px solid #478681;border-radius:8px;margin-top:8px"></label><button style="margin-top:18px;padding:12px 18px;background:#3fc7bd;color:#061d26;border:0;border-radius:9px;font-weight:700;min-height:44px">ChatGPT-Zugriff autorisieren</button></form></body></html>');
 }
 if(typeof x.setup_token!=="string"||await hash(x.setup_token)!==env.OWNER_HASH)return page("<h1>Invalid setup token</h1>",403);
 const code=random();
 await env.DB.prepare("INSERT INTO oauth_codes(code_hash,client_id,redirect_uri,code_challenge,expires_at) VALUES(?,?,?,?,?)").bind(await hash(code),client_id,redirect_uri,code_challenge,now()+300).run();
 const url=new URL(redirect_uri);url.searchParams.set("code",code);if(state)url.searchParams.set("state",state);
 return new Response(null,{status:302,headers:{Location:url.href,"Cache-Control":"no-store"}});
}
async function issue(env,id,grant){
 const a=random(),r=random(),g=grant||random();
 await env.DB.batch([
 env.DB.prepare("INSERT INTO oauth_tokens(token_hash,client_id,kind,expires_at,grant_id) VALUES(?,?,?,?,?)").bind(await hash(a),id,"access",now()+3600,g),
 env.DB.prepare("INSERT INTO oauth_tokens(token_hash,client_id,kind,expires_at,grant_id) VALUES(?,?,?,?,?)").bind(await hash(r),id,"refresh",now()+2592000,g)]);
 return out({access_token:a,refresh_token:r,token_type:"Bearer",expires_in:3600,scope:"genome:read"});
}
async function token(req,env){
 const x=await param(req),id=x.client_id;
 if(!id)return out({error:"invalid_client"},401);
 if(x.grant_type==="authorization_code"){
  if(typeof x.code!=="string"||typeof x.code_verifier!=="string"||x.code_verifier.length<43||x.code_verifier.length>128)return out({error:"invalid_grant"},400);
  const idhash=await hash(x.code),row=await env.DB.prepare("SELECT * FROM oauth_codes WHERE code_hash=?").bind(idhash).first();
  if(!row||row.client_id!==id||row.redirect_uri!==x.redirect_uri||row.expires_at<=now()||await pkce(x.code_verifier)!==row.code_challenge)return out({error:"invalid_grant"},400);
  await env.DB.prepare("DELETE FROM oauth_codes WHERE code_hash=?").bind(idhash).run();
  return issue(env,id);
 }
 if(x.grant_type==="refresh_token"){
  if(typeof x.refresh_token!=="string")return out({error:"invalid_grant"},400);
  const old=await env.DB.prepare("SELECT * FROM oauth_tokens WHERE token_hash=? AND kind='refresh'").bind(await hash(x.refresh_token)).first();
  if(!old||old.client_id!==id||old.expires_at<=now())return out({error:"invalid_grant"},400);
  await env.DB.prepare("DELETE FROM oauth_tokens WHERE grant_id=?").bind(old.grant_id).run();return issue(env,id,old.grant_id);
 }
 return out({error:"unsupported_grant_type"},400);
}
async function upload(req,env,path){
 const origin=req.headers.get("Origin");
 if(!await isOwner(req,env))return out({error:"not_authorized"},401,origin);
 if(path==="/v1/import/start"&&req.method==="POST"){
  const id=random();
  await env.DB.prepare("INSERT INTO genome_upload_sessions(batch_id,state,created_at,expires_at) VALUES(?,?,?,?)").bind(id,"UPLOADING",now(),now()+7200).run();
  return out({status:"READY",batch_id:id,expected_shards:256},200,origin);
 }
 const m=path.match(/^\/v1\/import\/(shard|finish)\/([a-f0-9]{64})(?:\/([0-9]{1,3}))?$/);
 if(!m)return out({error:"bad_import_path"},404,origin);
 const sess=await env.DB.prepare("SELECT state,expires_at FROM genome_upload_sessions WHERE batch_id=?").bind(m[2]).first();
 if(!sess||sess.state!=="UPLOADING"||sess.expires_at<now())return out({error:"expired_import"},409,origin);
 if(m[1]==="shard"&&req.method==="PUT"){
  const index=Number(m[3]);if(!Number.isInteger(index)||index<0||index>255)return out({error:"bad_shard"},400,origin);
  const x=await req.json(),rows=x.rows;
  if(x.build!=="GRCh37"||!Array.isArray(rows)||rows.length>5000)return out({error:"invalid_payload"},400,origin);
  const seen=new Set();
  for(const row of rows){
   if(!Array.isArray(row)||row.length!==4||!valid(row[0])||bucket(row[0])!==index||seen.has(row[0])||!/^(?:[1-9]|1[0-9]|2[0-2]|X|Y|MT)$/.test(row[1])||!Number.isSafeInteger(row[2])||row[2]<1||row[2]>300000000||!/^[ACGT]{1,2}$/.test(row[3]))return out({error:"invalid_genotype_or_partition"},400,origin);
   seen.add(row[0]);
  }
  const payload=JSON.stringify(rows);if(payload.length>650000)return out({error:"shard_too_large"},413,origin);
  await env.DB.prepare("INSERT OR REPLACE INTO genome_staging(batch_id,shard_id,payload,call_count,build) VALUES(?,?,?,?,?)").bind(m[2],index,payload,rows.length,"GRCh37").run();
  return out({status:"SAVED",shard:index,count:rows.length},200,origin);
 }
 if(m[1]==="finish"&&req.method==="POST"){
  const x=await env.DB.prepare("SELECT COUNT(*) AS shards,COALESCE(SUM(call_count),0) AS calls FROM genome_staging WHERE batch_id=?").bind(m[2]).first();
  if(x.shards!==256||x.calls<10000||x.calls>1500000)return out({error:"incomplete_import",shards:x.shards,calls:x.calls},409,origin);
  await env.DB.batch([
   env.DB.prepare("DELETE FROM genome_shards"),
   env.DB.prepare("INSERT INTO genome_shards(shard_id,payload,call_count,build) SELECT shard_id,payload,call_count,build FROM genome_staging WHERE batch_id=?").bind(m[2]),
   env.DB.prepare("INSERT OR REPLACE INTO genome_meta(id,state,total_calls,build) VALUES(1,'READY',?,'GRCh37')").bind(x.calls),
   env.DB.prepare("UPDATE genome_upload_sessions SET state='COMPLETED' WHERE batch_id=?").bind(m[2]),
   env.DB.prepare("DELETE FROM genome_staging WHERE batch_id=?").bind(m[2])
  ]);
  return out({status:"CLOUD_GENOME_READY",calls:x.calls,shards:x.shards},200,origin);
 }
 return out({error:"method_not_allowed"},405,origin);
}
export default {async fetch(req,env){
 const url=new URL(req.url),p=url.pathname,origin=url.origin;
 try{
  if(req.method==="OPTIONS"&&req.headers.get("Origin")===ORIGIN)return new Response(null,{status:204,headers:header(ORIGIN)});
  if(p==="/health")return out({service:"lagoon-genomics-mcp",state:"ONLINE",storage:"Cloudflare EU D1",oauth:"PKCE"});
  if(p==="/.well-known/oauth-protected-resource"||p==="/.well-known/oauth-protected-resource/mcp")return out({resource:origin+"/mcp",authorization_servers:[origin],scopes_supported:["genome:read"]});
  if(p==="/.well-known/oauth-authorization-server")return out({issuer:origin,authorization_endpoint:origin+"/authorize",token_endpoint:origin+"/token",registration_endpoint:origin+"/register",grant_types_supported:["authorization_code","refresh_token"],response_types_supported:["code"],code_challenge_methods_supported:["S256"],token_endpoint_auth_methods_supported:["none"],scopes_supported:["genome:read"]});
  if(p==="/register"&&req.method==="POST")return register(req,env);
  if(p==="/authorize"&&["GET","POST"].includes(req.method))return authorize(req,env);
  if(p==="/token"&&req.method==="POST")return token(req,env);
  if(p==="/mcp"&&req.method==="POST")return mcp(req,env);
  if(p==="/mcp")return await canRead(req,env)?out({error:"POST_required"},405):authChallenge(req);
  if(p.startsWith("/v1/import/"))return upload(req,env,p);
  return out({error:"not_found"},404);
 }catch(e){
  const message=String(e?.message||e);
  if(/exceeded D1.s free tier daily row read limit/i.test(message))
   return out({error:"D1_DAILY_ROW_READ_QUOTA_EXCEEDED",state:"TEMPORARILY_UNAVAILABLE",
    retry_after:"00:00 UTC next reset",genotype_absence_inferred:false},503,req.headers.get("Origin"));
  if(/exceeded D1.s free tier daily row write limit/i.test(message))
   return out({error:"D1_DAILY_ROW_WRITE_QUOTA_EXCEEDED",state:"TEMPORARILY_UNAVAILABLE",
    retry_after:"00:00 UTC next reset",genotype_absence_inferred:false},503,req.headers.get("Origin"));
  return out({error:"server_error",kind:e.name||"Error"},500,req.headers.get("Origin"));
 }
}};
