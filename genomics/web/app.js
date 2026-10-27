import {parseArray,makeCandidateReport} from "./analysis-core.mjs";
const $=(id)=>document.getElementById(id);
let dataset=null,report=null;
function message(text){$("notice").textContent=text;}
function clearReport(){report=null;$("summary").textContent="";$("results").replaceChildren();$("copy").disabled=true;$("save").disabled=true;}
function buttons(yes){$("analyze").disabled=!yes;$("erase").disabled=!yes;}
$("raw").addEventListener("change",async()=>{
  dataset=null;buttons(false);clearReport();
  const file=$("raw").files?.[0];if(!file)return;
  $("progress").hidden=false;$("progress").value=0;
  message("Analysiere privat im iPhone-Browser …");
  try{
    // No fetch/network methods called. Only a user-selected File is read.
    dataset=await parseArray(file,{onProgress:p=>$("progress").value=p});
    const q=dataset.qc;
    message("Datei eingelesen: "+q.valid.toLocaleString("de-DE")+" eindeutige SNPs; "+q.no_calls+
      " No-Calls; "+q.rejected+" abgewiesene Zeilen; "+q.conflicts+
      " widersprüchliche rsIDs ausgeschlossen. Genome-Build: "+q.build+".");
    buttons(true);
  }catch(e){
    dataset=null;message("Import abgebrochen: "+e.message);$("raw").value="";
  }finally{$("progress").hidden=true;}
});
$("analyze").addEventListener("click",()=>{
  clearReport();if(!dataset)return;
  try{
    report=makeCandidateReport(dataset,$("nutrient").value);
    if(report.status!=="RESEARCH_ONLY"){
      $("summary").textContent=report.message;return;
    }
    $("summary").textContent=report.matched_loci+" von "+report.analyzed_loci+
      " Kandidaten im Rohdatensatz vorhanden. Keine individuelle Risikoberechnung.";
    const tbody=$("results");tbody.replaceChildren();
    for(const x of report.candidates){
      const tr=document.createElement("tr");
      for(const text of [x.rsid,x.gene,x.genotype??"Nicht genotypisiert",x.endpoint]){
        const td=document.createElement("td");td.textContent=text;tr.append(td);
      }
      const td=document.createElement("td"),link=document.createElement("a");
      link.textContent="Quelle";link.href=x.source;link.target="_blank";
      link.rel="noopener noreferrer";td.append(link);tr.append(td);tbody.append(tr);
    }
    $("copy").disabled=false;$("save").disabled=false;
  }catch(e){$("summary").textContent="Analyse verweigert: "+e.message;}
});
$("copy").addEventListener("click",async()=>{
  if(!report||report.status!=="RESEARCH_ONLY")return;
  const reduced={question:"Welche Genotypkonstellationen betreffen Mikronährstoff-Marker? Prüfe Quellen und Effekte vor Interpretation.",
    build:report.input_qc.build,markers:report.candidates.map(({rsid,gene,genotype,status,mechanism,endpoint,source})=>(
      {rsid,gene,genotype,status,mechanism,endpoint,source})),
    guardrails:report.excluded_inferences};
  try{
    await navigator.clipboard.writeText(JSON.stringify(reduced,null,2));
    message("Ausgewählte Genotypen in Zwischenablage kopiert. Erst Einfügen in ChatGPT übermittelt sie.");
  }catch(e){message("Kopieren nicht möglich: "+e.message);}
});
$("save").addEventListener("click",()=>{
  if(!report||report.status!=="RESEARCH_ONLY")return;
  const blob=new Blob([JSON.stringify(report,null,2)],{type:"application/json"});
  const url=URL.createObjectURL(blob),anchor=document.createElement("a");
  anchor.href=url;anchor.download="lagoon-genomics-private-research.json";
  anchor.click();setTimeout(()=>URL.revokeObjectURL(url),1500);
});
$("erase").addEventListener("click",()=>{
  dataset=null;report=null;$("raw").value="";$("progress").value=0;
  buttons(false);clearReport();message("Genotypdaten aus dem Browser-Arbeitsspeicher freigegeben. Zwischenablage oder bereits gespeicherte Exporte bleiben getrennt bestehen.");
});
if("serviceWorker" in navigator)navigator.serviceWorker.register("./sw.js").catch(()=>{});
