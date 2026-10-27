import {parseArray,makeCandidateReport,searchImportedSnps} from "./analysis-core.mjs";
const $=id=>document.getElementById(id);
let dataset=null,report=null,lookup=null;
const de=new Intl.NumberFormat("de-DE");
function message(text){$("notice").textContent=text;}
function resetViews(){
  report=null;lookup=null;
  for(const name of ["results","lookupResults","summary","lookupSummary","qcDetails"])
    $(name).replaceChildren();
  $("qcDetails").hidden=true;
  for(const name of ["copy","save","copyLookup"])$(name).disabled=true;
}
function buttons(yes){
  for(const name of ["analyze","erase","lookup"])$(name).disabled=!yes;
}
function metaPair(dl,k,v){
  const dt=document.createElement("dt"),dd=document.createElement("dd");
  dt.textContent=k;dd.textContent=de.format(v);dl.append(dt,dd);
}
function showQc(q){
  const root=$("qcDetails");root.replaceChildren();root.hidden=false;
  const heading=document.createElement("h3");heading.textContent="Qualitätsprüfung – Eingangszeilen";root.append(heading);
  const dl=document.createElement("dl");root.append(dl);
  for(const [k,v] of [
    ["Zeilen insgesamt",q.rows],["Gültige SNPs",q.valid],["No-Calls",q.no_calls],
    ["Abgewiesene Zeilen",q.rejected],["Duplikate",q.duplicates],["Widersprüche",q.conflicts],
    ["Nicht-rsID-Marker",q.rejectionReasons.non_rsid_marker],
    ["Indels (I/D)",q.rejectionReasons.non_snv_indel],
    ["Ungültige Chromosomen",q.rejectionReasons.invalid_chromosome],
    ["Ungültige Positionen",q.rejectionReasons.invalid_position],
    ["Nicht unterstützte Allele",q.rejectionReasons.unsupported_alleles],
    ["Fehlerhafte Zeilen",q.rejectionReasons.malformed_line]
  ])metaPair(dl,k,v);
  const note=document.createElement("p");note.className="marker-meta";
  note.textContent="Abgewiesene Zeilen werden nur nach Fehlerklasse gezählt; keine Allelwerte werden an Server gesendet. Gültige SNPs sind noch nicht gegen externe Referenzen verifiziert.";
  root.append(note);
}
function element(tag,cls,text){
  const e=document.createElement(tag);
  if(cls)e.className=cls;
  if(text!==undefined)e.textContent=text;
  return e;
}
function researchLink(url,label){
  const a=element("a","",label);
  a.href=url;a.target="_blank";a.rel="noopener noreferrer";
  return a;
}
function card({rsid,gene,genotype,chromosome,position,endpoint,status,source,study_search_url,reference_search_url}){
  const div=element("article","marker-card");div.setAttribute("role","listitem");
  const top=element("div","marker-top");
  const name=element("h3","marker-title"),id=element("code","",rsid);
  name.append(id);
  if(gene)name.append(element("span","marker-gene",gene));
  top.append(name,element("span","marker-gt",genotype??(status==="ARRAY_NO_CALL"?"No-Call":"Fehlt")));
  div.append(top);
  if(endpoint)div.append(element("div","marker-desc",endpoint));
  if(chromosome&&position)div.append(element("div","marker-meta","Originaldatei: Chromosom "+chromosome+", Position "+de.format(position)));
  const state=status==="ARRAY_NO_CALL"?"Marker in Datei vorhanden, Messung ohne verwertbaren Genotyp (No-Call)":
    status==="NOT_ON_ARRAY"?"Marker in der Rohdatei nicht vorhanden":
    "Array-Call vorhanden, Referenz-/Studienallel noch ungeprüft";
  div.append(element("div","marker-meta",state));
  const actions=element("div","marker-actions");
  if(source)actions.append(researchLink(source,"Forschungsquelle"));
  if(study_search_url)actions.append(researchLink(study_search_url,"GWAS-Suche"));
  if(reference_search_url)actions.append(researchLink(reference_search_url,"Ensembl GRCh37"));
  div.append(actions);return div;
}
$("raw").addEventListener("change",async()=>{
  dataset=null;buttons(false);resetViews();
  const file=$("raw").files?.[0];if(!file)return;
  $("progress").hidden=false;$("progress").value=0;
  message("Analysiere Rohdatei ausschließlich im Browser …");
  try{
    dataset=await parseArray(file,{onProgress:p=>$("progress").value=p});
    const q=dataset.qc;
    message("Import erfolgreich: "+de.format(q.valid)+" SNPs, "+de.format(q.no_calls)+" No-Calls, "+
       de.format(q.rejected)+" abgewiesene Zeilen, "+de.format(q.conflicts)+" Konflikte; Referenz: "+q.build+".");
    showQc(q);buttons(true);
  }catch(e){
    dataset=null;message("Import verweigert: "+e.message);$("raw").value="";
  }finally{$("progress").hidden=true;}
});
$("analyze").addEventListener("click",()=>{
  if(!dataset)return;
  report=null;$("results").replaceChildren();
  $("copy").disabled=true;$("save").disabled=true;
  try{
    report=makeCandidateReport(dataset,$("nutrient").value);
    if(report.status!=="RESEARCH_ONLY"){
      $("summary").textContent=report.message;return;
    }
    $("summary").textContent=de.format(report.matched_loci)+" von "+report.analyzed_loci+
      " Forschungsmarkern vorhanden. Das ist KEINE Diagnose oder persönliche Risikoquantifizierung.";
    for(const v of report.candidates)$("results").append(card(v));
    $("copy").disabled=false;$("save").disabled=false;
  }catch(e){$("summary").textContent="Analyse verweigert: "+e.message;}
});
$("lookup").addEventListener("click",()=>{
  if(!dataset)return;
  $("lookupResults").replaceChildren();$("copyLookup").disabled=true;lookup=null;
  try{
    lookup=searchImportedSnps(dataset,$("rsSearch").value);
    $("lookupSummary").textContent=de.format(lookup.matched)+" von "+lookup.looked_up+
      " angefragten rsIDs vorhanden. Keine Wirkungs- oder Risikobewertung.";
    for(const v of lookup.variants)$("lookupResults").append(card(v));
    $("copyLookup").disabled=false;
  }catch(e){$("lookupSummary").textContent=e.message;}
});
async function copySubset(obj){
  try{
    await navigator.clipboard.writeText(JSON.stringify(obj,null,2));
    message("Gewählte Marker in die Zwischenablage kopiert. Erst das Einfügen in ChatGPT überträgt sie.");
  }catch(e){message("Kopieren fehlgeschlagen: "+e.message);}
}
$("copy").addEventListener("click",()=>{
  if(report?.status!=="RESEARCH_ONLY")return;
  copySubset({question:"Prüfe zu diesen SNPs öffentliche Studien, Referenzorientierung und Wirksamkeit. Keine unbelegten individuellen Prozentwerte.",
   build:report.input_qc.build,markers:report.candidates.map(({rsid,gene,genotype,status,mechanism,endpoint,source})=>(
    {rsid,gene,genotype,status,mechanism,endpoint,source})),
   cautions:report.excluded_inferences});
});
$("copyLookup").addEventListener("click",()=>{
  if(!lookup)return;
  copySubset({question:"Untersuche diese selektierten Genotypen wissenschaftlich. Effektallele/Strang gegen GRCh37 und GWAS Studien einzeln prüfen.",
    build:lookup.build,variants:lookup.variants.map(({rsid,genotype,chromosome,position,status})=>(
      {rsid,genotype,chromosome,position,status})),cautions:lookup.cautions});
});
$("save").addEventListener("click",()=>{
  if(report?.status!=="RESEARCH_ONLY")return;
  const blob=new Blob([JSON.stringify(report,null,2)],{type:"application/json"});
  const url=URL.createObjectURL(blob),a=document.createElement("a");
  a.href=url;a.download="lagoon-genomics-private-research.json";a.click();
  setTimeout(()=>URL.revokeObjectURL(url),1500);
});
$("erase").addEventListener("click",()=>{
  dataset=null;report=null;lookup=null;$("raw").value="";$("rsSearch").value="";$("progress").value=0;
  buttons(false);resetViews();
  message("Temporäre Genotypen freigegeben. Bereits exportierte Dateien und Zwischenablage bleiben separat bestehen.");
});
if("serviceWorker" in navigator)navigator.serviceWorker.register("./sw.js").catch(()=>{});
