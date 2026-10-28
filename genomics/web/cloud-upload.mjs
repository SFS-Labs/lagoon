/* User-authorized, one-time transfer of the full SNP array to EU Cloudflare D1.
 * 256 bounded genomic data shards, no paid API keys, no third-party analytics.
 * Unlike earlier versions the persistent query source becomes CLOUD storage.
 */
export const API="https://lagoon-genomics-mcp.sfs-labs.workers.dev";
const LOCAL_TOKEN_KEY="lagoon-genomics-owner-token-v1";
function digestInput(id){return Number(BigInt(id.slice(2))%256n);}
export function getOwnerToken(){return localStorage.getItem(LOCAL_TOKEN_KEY)||"";}
export function setOwnerToken(value){
 const t=String(value||"").trim();
 if(!/^[a-f0-9]{64}$/.test(t))throw Error("Ungültiger einmaliger Einrichtungscode.");
 localStorage.setItem(LOCAL_TOKEN_KEY,t);
 return t;
}
export function clearOwnerToken(){localStorage.removeItem(LOCAL_TOKEN_KEY);}
async function call(path,token,method="POST",payload,attempts=3){
 const url=API+path;
 for(let attempt=0;attempt<attempts;attempt++){
  let response;
  try{
   response=await fetch(url,{method,cache:"no-store",referrerPolicy:"no-referrer",
     headers:{"Authorization":"Bearer "+token,...(payload===undefined?{}:{"Content-Type":"application/json"})},
     body:payload===undefined?undefined:JSON.stringify(payload)});
  }catch(e){
   if(attempt===attempts-1)throw Error("Cloudflare nicht erreichbar: "+String(e.message).slice(0,80));
   await new Promise(r=>setTimeout(r,500*(attempt+1)));continue;
  }
  const data=await response.json().catch(()=>({error:"non_json_response"}));
  if(response.ok)return data;
  if(response.status===401)throw Error("Einrichtungscode nicht berechtigt. Bitte den neuen Code eingeben.");
  if([429,500,502,503,504].includes(response.status)&&attempt<attempts-1){
   await new Promise(r=>setTimeout(r,500*(attempt+1)));continue;
  }
  throw Error("Cloud-Fehler "+response.status+": "+String(data.error||"unbekannt"));
 }
}
export function prepareShards(dataset){
 if(!dataset?.qc?.completed||dataset.qc.build!=="GRCh37"||!(dataset.calls instanceof Map))
   throw Error("Vollständige GRCh37-SNP-Datei muss geladen sein.");
 const shards=Array.from({length:256},()=>[]);
 for(const [rsid,v] of dataset.calls){
  if(!/^rs[0-9]{1,15}$/.test(rsid))continue;
  const chr=v.chr==="M"?"MT":v.chr;
  shards[digestInput(rsid)].push([rsid,chr,v.pos,v.gt]);
 }
 const n=shards.reduce((sum,x)=>sum+x.length,0);
 if(n!==dataset.qc.valid)throw Error("Datenintegritätsfehler: Upload-Gesamtzahl weicht von QC ab.");
 return shards;
}
export async function uploadGenomeToCloud(dataset,token,{onProgress=()=>{}}={}){
 const shards=prepareShards(dataset);
 const begin=await call("/v1/import/start",token);
 if(begin.status!=="READY"||!begin.batch_id)throw Error("Cloud-Import konnte nicht gestartet werden.");
 let next=0,done=0;
 const failures=[];
 async function worker(){
  while(next<shards.length&&failures.length===0){
   const i=next++;
   try{
    const r=await call("/v1/import/shard/"+begin.batch_id+"/"+i,token,"PUT",
      {build:"GRCh37",rows:shards[i]});
    if(r.status!=="SAVED")throw Error("Segment nicht gespeichert: "+i);
    done++;onProgress(Math.floor(done/256*99),done,256);
   }catch(e){failures.push({shard:i,message:String(e.message)});return;}
  }
 }
 await Promise.all(Array.from({length:3},worker));
 if(failures.length)throw Error("Upload unterbrochen; "+failures[0].message+". Kein unvollständiger Datenbestand wird aktiviert.");
 const result=await call("/v1/import/finish/"+begin.batch_id,token);
 if(result.status!=="CLOUD_GENOME_READY"||result.calls!==dataset.qc.valid)
   throw Error("Cloud-Bestand nicht vollständig bestätigt.");
 onProgress(100,256,256);
 return result;
}
export async function queryCloudStatus(token){
 const data=await call("/mcp",token,"POST",{jsonrpc:"2.0",id:1,method:"tools/call",
  params:{name:"genome_status",arguments:{}}});
 const t=data?.result?.content?.[0]?.text;
 if(!t)throw Error("Cloud MCP hat keine Statusdaten zurückgegeben.");
 return JSON.parse(t);
}
export async function queryPrivateCloudSnp(token,rsid){
 const data=await call("/mcp",token,"POST",{jsonrpc:"2.0",id:2,method:"tools/call",
  params:{name:"lookup_snp",arguments:{rsid}}});
 const t=data?.result?.content?.[0]?.text;
 return t?JSON.parse(t):{status:"INVALID_MCP_RESPONSE"};
}
