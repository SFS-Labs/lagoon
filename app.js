import {parseArray,makeCandidateReport,searchImportedSnps} from "./analysis-core.mjs?v=6";
import {encryptGenome,decryptGenome,saveEncryptedGenome,readSavedGenome,deleteSavedGenome,
  createVaultBackup,readVaultBackup,storageMode} from "./vault.mjs?v=6";
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
    showQc(q);buttons(true);showSavePanel(true);
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
  buttons(false);resetViews();showSavePanel(false);clearPasswords();
  message("Diese Sitzung gesperrt. Der verschlüsselte DNA-Tresor bleibt für spätere Besuche gespeichert.");
});
if("serviceWorker" in navigator)navigator.serviceWorker.register("./sw.js").catch(()=>{});


/* All persistence is opt-in, ciphertext-only IndexedDB. The raw genome is
 * only transiently loaded from the user-selected File or after local decrypt.
 * The password is intentionally required after every browser restart. */
function vaultMessage(text){$("vaultStatus").textContent=text;}
function clearPasswords(){
  for(const id of ["vaultPassword","vaultPasswordRepeat","unlockPassword","restorePassword"])$(id).value="";
}
function showSavePanel(yes){
  $("vaultSavePanel").hidden=!yes;
  $("saveVault").disabled=!yes;
}
async function refreshVault(){
  try{
    const existing=await readSavedGenome();
    $("vaultExistingPanel").hidden=!existing;
    if(existing){
      vaultMessage("Verschlüsselte DNA-Datei ist in diesem Browser gespeichert. Zum Öffnen nur das Passwort eingeben – kein neuer Dateiimport.");
      return true;
    }
    vaultMessage("Noch keine dauerhaft verschlüsselte DNA-Datei auf diesem Gerät gespeichert.");
    return false;
  }catch(e){
    $("vaultExistingPanel").hidden=true;
    vaultMessage("Lokaler Tresor nicht verfügbar: "+e.message+" Verwende Safari außerhalb des In-App-Browsers.");
    return false;
  }
}
async function loadDecryptedBytes(raw){
  const blob=new Blob([raw]);
  new Uint8Array(raw).fill(0); // Best effort; immutable Blob may retain its own temporary copy.
  const result=await parseArray(blob,{onProgress:p=>$("progress").value=p});
  if(!result.qc.completed)throw Error("The decrypted DNA array did not finish parsing.");
  dataset=result;resetViews();showQc(dataset.qc);buttons(true);
  showSavePanel(false);
  message("Gespeicherte Originaldatei lokal entschlüsselt: "+de.format(dataset.qc.valid)+
      " SNP-Calls. Datei nicht erneut ausgewählt; kein Cloud-Zugriff.");
  return result;
}
$("saveVault").addEventListener("click",async()=>{
  const file=$("raw").files?.[0];
  if(!dataset||!dataset.qc.completed||!file){
    vaultMessage("Zuerst die Originaldatei lokal importieren.");return;
  }
  const pass=$("vaultPassword").value,repeated=$("vaultPasswordRepeat").value;
  if(pass!==repeated){vaultMessage("Die Passwörter stimmen nicht überein.");return;}
  let raw;
  $("saveVault").disabled=true;
  try{
    if(await readSavedGenome() && !confirm("Vorhandenen verschlüsselten DNA-Tresor wirklich ersetzen? Vorher eine verschlüsselte Sicherung erstellen."))return;
    vaultMessage("Verschlüssele die Originaldatei lokal …");
    raw=await file.arrayBuffer();
    const archive=await encryptGenome(raw,pass);
    new Uint8Array(raw).fill(0);raw=null;
    const confirmed=await saveEncryptedGenome(archive);
    // Authenticate saved bytes with the supplied password before confirming success.
    const plaintext=await decryptGenome(confirmed,pass);
    new Uint8Array(plaintext).fill(0);
    const mode=await storageMode();
    clearPasswords();
    await refreshVault();
    showSavePanel(false);
    vaultMessage("Gespeichert: Originaldatei vollständig AES-256-GCM-verschlüsselt im Browser-Tresor. "+
      (mode.persisted?"Browser hat persistenten Speicher bestätigt.":"Persistenter Speicher nicht bestätigt; Backup ist Pflicht.")+
      " Jetzt die verschlüsselte Backupdatei exportieren.");
  }catch(e){
    vaultMessage("Speichern NICHT bestätigt: "+e.message+" Vorheriges Backup nicht löschen.");
  }finally{
    if(raw)new Uint8Array(raw).fill(0);
    $("saveVault").disabled=false;
  }
});
$("unlockVault").addEventListener("click",async()=>{
  const pass=$("unlockPassword").value;
  if(!pass){vaultMessage("Tresor-Passwort eingeben.");return;}
  $("unlockVault").disabled=true;$("progress").hidden=false;$("progress").value=0;
  try{
    vaultMessage("Entschlüssele gespeicherte DNA lokal im Browser …");
    const record=await readSavedGenome();
    if(!record)throw Error("Keine Datei gespeichert. Importiere einmalig oder stelle ein Backup wieder her.");
    const bytes=await decryptGenome(record,pass);
    clearPasswords();await loadDecryptedBytes(bytes);
    vaultMessage("Tresor entsperrt: DNA-Daten wurden aus dem lokalen verschlüsselten Speicher geladen.");
  }catch(e){clearPasswords();vaultMessage("Entsperren fehlgeschlagen: "+e.message);}
  finally{$("unlockVault").disabled=false;$("progress").hidden=true;}
});
function downloadBlob(blob,filename){
  const href=URL.createObjectURL(blob),a=document.createElement("a");
  a.href=href;a.download=filename;document.body.append(a);a.click();a.remove();
  setTimeout(()=>URL.revokeObjectURL(href),10000);
}
$("backupVault").addEventListener("click",async()=>{
  try{
    const saved=await readSavedGenome();
    if(!saved)throw Error("Keine verschlüsselte DNA-Datei vorhanden.");
    downloadBlob(createVaultBackup(saved),"lagoon-dna-encrypted-backup.lgv");
    vaultMessage("Verschlüsseltes Backup vorbereitet. Sichere .lgv über Safari in der Dateien-App. Passwort separat und sicher aufbewahren.");
  }catch(e){vaultMessage("Backup fehlgeschlagen: "+e.message);}
});
$("restoreVault").addEventListener("click",async()=>{
  const file=$("restoreFile").files?.[0],pass=$("restorePassword").value;
  if(!file||!pass){vaultMessage("Verschlüsselte .lgv-Datei und zugehöriges Passwort erforderlich.");return;}
  let plain;
  $("restoreVault").disabled=true;$("progress").hidden=false;$("progress").value=0;
  try{
    const existing=await readSavedGenome();
    if(existing&&!confirm("Gespeicherte DNA-Datei durch dieses verschlüsselte Backup ersetzen?"))return;
    const record=await readVaultBackup(file);
    plain=await decryptGenome(record,pass);
    // Validate a backup *before* overwriting an existing encrypted archive.
    const blob=new Blob([plain]);new Uint8Array(plain).fill(0);plain=null;
    const validated=await parseArray(blob,{onProgress:p=>$("progress").value=p});
    if(!validated.qc.completed)throw Error("Backup raw SNP data could not be parsed.");
    await saveEncryptedGenome(record);
    dataset=validated;buttons(true);resetViews();showQc(dataset.qc);showSavePanel(false);
    $("raw").value="";$("restoreFile").value="";clearPasswords();
    const mode=await storageMode();
    await refreshVault();
    vaultMessage("Backup geprüft, entschlüsselt und erneut verschlüsselt im Browser-Tresor gespeichert. "+
      (mode.persisted?"Persistenter Speicher bestätigt.":"Halte weiterhin eine externe .lgv-Sicherung bereit."));
    message("Import aus verschlüsseltem Backup: "+de.format(dataset.qc.valid)+" SNP-Calls. Keine Original-CSV benötigt.");
  }catch(e){vaultMessage("Wiederherstellen fehlgeschlagen: "+e.message);}
  finally{if(plain)new Uint8Array(plain).fill(0);$("restoreVault").disabled=false;$("progress").hidden=true;}
});
$("deleteVault").addEventListener("click",async()=>{
  if(!confirm("Verschlüsselten DNA-Tresor dieses Browsers endgültig löschen? Eine .lgv-Backupdatei bleibt unberührt."))return;
  try{
    await deleteSavedGenome();
    dataset=null;report=null;lookup=null;
    $("raw").value="";buttons(false);resetViews();showSavePanel(false);clearPasswords();
    await refreshVault();
    vaultMessage("Verschlüsselter lokaler Tresor gelöscht; exportierte Sicherungen bleiben separat erhalten.");
  }catch(e){vaultMessage("Löschen fehlgeschlagen: "+e.message);}
});
refreshVault();
