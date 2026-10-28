import {getOwnerToken,setOwnerToken,uploadGenomeToCloud,queryCloudStatus} from "./cloud-upload.mjs?v=8";
const elem=id=>document.getElementById(id);
const ui=t=>{elem("cloudMessage").textContent=t;};
async function check(){
 const token=getOwnerToken();
 if(!token){ui("Bitte den einmaligen Cloud-Einrichtungscode speichern.");return;}
 try{
  const r=await queryCloudStatus(token);
  ui(r.status==="READY"?
    "EU-Datenbank online: "+r.total_calls.toLocaleString("de-DE")+" SNP-Calls dauerhaft gespeichert. ChatGPT MCP bereit.":
    "Cloud-MCP erreichbar; der Genomdatensatz muss einmalig übertragen werden.");
 }catch(e){ui("Cloud-Status konnte nicht bestätigt werden: "+e.message);}
}
elem("cloudRememberToken").addEventListener("click",()=>{
 try{
  setOwnerToken(elem("cloudOwnerToken").value);
  elem("cloudOwnerToken").value="";
  ui("Einrichtungscode gespeichert. Du musst ihn nicht erneut eingeben.");
  check();
 }catch(e){ui(e.message);}
});
elem("cloudStatusButton").addEventListener("click",check);
elem("cloudUploadButton").addEventListener("click",async()=>{
 const data=window.getLagoonDataset?.();
 if(!data?.qc?.completed){ui("Genotypdatei muss zunächst vollständig geladen sein.");return;}
 const token=getOwnerToken();
 if(!token){ui("Bitte zuerst den einmaligen Einrichtungscode speichern.");return;}
 if(!confirm("Vollständige Genotypdaten dauerhaft in deine EU-Cloudflare-Datenbank übertragen?"))return;
 elem("cloudUploadButton").disabled=true;
 elem("cloudProgress").hidden=false;
 elem("cloudProgress").value=0;
 try{
  ui("Übertrage Genotypdaten an die EU-Datenbank. Bitte diese Seite geöffnet lassen.");
  const result=await uploadGenomeToCloud(data,token,{onProgress:(pct,n,max)=>{
   elem("cloudProgress").value=pct;
   if(n%16===0||n===max)ui("Speichere Segment "+n+" von "+max+" ("+pct+" %)");
  }});
  ui("Cloud-Import abgeschlossen: "+result.calls.toLocaleString("de-DE")+
     " SNPs dauerhaft in EU-D1. ChatGPT-Remote-MCP kann ab jetzt ohne CSV-Abfrage darauf zugreifen.");
 }catch(e){ui("Cloud-Import nicht abgeschlossen: "+e.message);}
 finally{elem("cloudUploadButton").disabled=false;elem("cloudProgress").hidden=true;}
});
check();
