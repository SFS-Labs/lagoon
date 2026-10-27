/* Lagoon Genomics: private, streaming, browser-only SNP array parser.
 * No network, cookies, analytics, service provider, or persistent genotype storage.
 * Each file is reread explicitly on each visit. Zero dependencies.
 */
const RS=/^rs[0-9]{1,15}$/i;
const CHR=/^(?:[1-9]|1[0-9]|2[0-2]|X|Y|MT|M)$/i;
const GT=/^(?:[ACGT]{1,2}|--|00)$/i;
const MAX_BYTES=80*1024*1024;
const MAX_ROWS=1_500_000;

function normalizeBuild(text) {
  if (/\b(?:grch|genome\s*build|build)\s*[:#=-]?\s*(?:37|hg19)\b/i.test(text))return "GRCh37";
  if (/\b(?:grch|genome\s*build|build)\s*[:#=-]?\s*(?:38|hg38)\b/i.test(text))return "GRCh38";
  return "UNKNOWN";
}
function separator(line){return line.includes("\t")?"\t":",";}
function parseHeader(line){
  const sep=separator(line);
  const cols=line.replace(/^\uFEFF/,"").split(sep).map(s=>s.trim().replace(/^"|"$/g,"").toLowerCase().replace(/^#/,""));
  const ix={
    rsid:cols.findIndex(s=>["rsid","snp","snpid"].includes(s)),
    chr:cols.findIndex(s=>["chromosome","chr"].includes(s)),
    pos:cols.findIndex(s=>["position","pos"].includes(s)),
    gt:cols.findIndex(s=>["genotype","result","alleles"].includes(s))
  };
  return Object.values(ix).every(n=>n>=0)?{ix,sep}:null;
}
function makeQC(){
  return {rows:0,valid:0,no_calls:0,duplicates:0,conflicts:0,rejected:0,haploid:0,
          rejectionReasons:{non_rsid_marker:0,non_snv_indel:0,invalid_chromosome:0,invalid_position:0,unsupported_alleles:0,malformed_line:0},
          chromosomeCounts:{},
          build:"UNKNOWN",columns_confirmed:false,source:"private_browser_memory",
          uploaded:false,completed:false};
}
export async function parseArray(file,{onProgress=()=>{},maxBytes=MAX_BYTES,maxRows=MAX_ROWS}={}){
  if(!file||!Number.isFinite(file.size)||file.size<=0||file.size>maxBytes)
    throw Error("Missing/oversized file (max 80 MiB); no data uploaded.");
  if(typeof file.stream!=="function")throw Error("File.stream unavailable; unsupported browser.");
  const calls=new Map(),noCalls=new Set(),conflicts=new Set(),qc=makeQC(),decoder=new TextDecoder("utf-8",{fatal:true});
  const reader=file.stream().getReader();
  let buf="",read=0,header=null,completed=false;
  function line(raw){
    const t=raw.trim();
    if(!t)return;
    if(t.startsWith("#")){
      const b=normalizeBuild(t);
      if(b!=="UNKNOWN"){
        if(qc.build!=="UNKNOWN"&&qc.build!==b)throw Error("Conflicting genome-build metadata.");
        qc.build=b;
      }
      return;
    }
    if(!header){
      header=parseHeader(t);
      if(header){qc.columns_confirmed=true;return;}
      const sep=separator(t),parts=t.split(sep);
      if(parts.length<4||!RS.test(parts[0].trim()))
        throw Error("Expected SNP header or standard four-column rsid/chromosome/position/genotype data.");
      header={ix:{rsid:0,chr:1,pos:2,gt:3},sep};
      qc.columns_confirmed=false; // Headerless input: no inferred genome build or allele direction.
      // First headerless row is itself a SNP call and must not be dropped.
    }
    qc.rows++;
    if(qc.rows>maxRows)throw Error("Unexpectedly many SNP rows.");
    const fields=t.split(header.sep).map(v=>v.trim().replace(/^"|"$/g,""));
    if(fields.length<=Math.max(...Object.values(header.ix))){qc.rejected++;qc.rejectionReasons.malformed_line++;return;}
    const id=(fields[header.ix.rsid]||"").toLowerCase();
    const chr=(fields[header.ix.chr]||"").toUpperCase();
    const pos=Number(fields[header.ix.pos]);
    const geno=(fields[header.ix.gt]||"").toUpperCase().replace(/[ /]/g,"");
    const reject=(reason)=>{qc.rejected++;qc.rejectionReasons[reason]++;};
    if(!RS.test(id)){reject("non_rsid_marker");return;}
    if(!CHR.test(chr)){reject("invalid_chromosome");return;}
    if(!Number.isSafeInteger(pos)||pos<1||pos>300_000_000){reject("invalid_position");return;}
    if(geno==="--"||geno==="00"){qc.no_calls++;if(!calls.has(id))noCalls.add(id);return;}
    if(/^[ID]{1,2}$/.test(geno)){reject("non_snv_indel");return;}
    if(!GT.test(geno)){reject("unsupported_alleles");return;}
    if(geno.length===1)qc.haploid++;
    if(conflicts.has(id))return;
    const current=calls.get(id);
    if(current){
      if(current.gt===geno&&current.chr===chr&&current.pos===pos){qc.duplicates++;return;}
      calls.delete(id);conflicts.add(id);qc.conflicts++;
      qc.chromosomeCounts[current.chr]=Math.max(0,(qc.chromosomeCounts[current.chr]??1)-1);return;
    }
    noCalls.delete(id);
    calls.set(id,{chr,pos,gt:geno});
    qc.chromosomeCounts[chr]=(qc.chromosomeCounts[chr]??0)+1;
    qc.valid++;
  }
  try{
    while(true){
      const part=await reader.read();
      if(part.done){completed=true;break;}
      read+=part.value.byteLength;
      if(read>maxBytes)throw Error("Maximum input size exceeded.");
      buf+=decoder.decode(part.value,{stream:true});
      let idx;
      while((idx=buf.indexOf("\n"))>=0){
        line(buf.slice(0,idx).replace(/\r$/,""));
        buf=buf.slice(idx+1);
      }
      onProgress(Math.min(99,Math.floor(100*read/file.size)));
    }
    buf+=decoder.decode();
    if(buf)line(buf.replace(/\r$/,""));
    if(!header)throw Error("No genotype header found.");
    if(qc.valid<1)throw Error("No valid genetic calls.");
    qc.valid=calls.size;
    const accounted=qc.valid+qc.no_calls+qc.rejected+qc.duplicates+qc.conflicts;
    // This identity holds for standard unique exports. Once a conflicting
    // locus is excluded, its two rows become one conflict plus one removed
    // call; report that explicitly without silently inventing an extra SNP.
    qc.rejectedBreakdownVerified=Object.values(qc.rejectionReasons).reduce((a,b)=>a+b,0)===qc.rejected;
    qc.accounting_note=(qc.conflicts||qc.duplicates)
      ?"Doppel- oder Konfliktzeilen separat prüfen; Summen nicht blind addieren."
      :(accounted===qc.rows?"Alle Datenzeilen vollständig klassifiziert.":"Summendifferenz untersuchen.");
    qc.completed=completed;
    onProgress(100);
    return {calls,noCalls,qc,conflictCount:conflicts.size};
  }finally{try{await reader.cancel();}catch{}}
}
export const EVIDENCE=[
  {rsid:"rs601338",gene:"FUT2",nutrient:"b12",endpoint:"serum B12",category:"biomarker",source:"https://academic.oup.com/hmg/article/26/24/4975/4460048"},
  {rsid:"rs855791",gene:"TMPRSS6",nutrient:"iron",endpoint:"serum iron/transferrin saturation",category:"biomarker",source:"https://pubmed.ncbi.nlm.nih.gov/?term=TMPRSS6+rs855791+iron"},
  {rsid:"rs10741657",gene:"CYP2R1",nutrient:"vitamin_d",endpoint:"serum 25(OH)D",category:"biomarker",source:"https://www.ebi.ac.uk/gwas/search?query=rs10741657"},
  {rsid:"rs2282679",gene:"GC",nutrient:"vitamin_d",endpoint:"vitamin D binding protein and serum vitamin D",category:"transport_and_biomarker",source:"https://www.ebi.ac.uk/gwas/search?query=rs2282679"},
  {rsid:"rs12785878",gene:"DHCR7",nutrient:"vitamin_d",endpoint:"serum 25(OH)D",category:"biomarker",source:"https://www.ebi.ac.uk/gwas/search?query=rs12785878"},
  {rsid:"rs4988235",gene:"MCM6/LCT",nutrient:"lactose",endpoint:"lactase persistence (ancestry-sensitive)",category:"enzyme_phenotype",source:"https://www.ebi.ac.uk/gwas/search?query=rs4988235"},
  {rsid:"rs1801133",gene:"MTHFR",nutrient:"folate",endpoint:"folate and homocysteine biomarkers",category:"utilization_biomarker",source:"https://www.ebi.ac.uk/gwas/search?query=rs1801133"},
  {rsid:"rs1801131",gene:"MTHFR",nutrient:"folate",endpoint:"folate and homocysteine biomarkers",category:"utilization_biomarker",source:"https://www.ebi.ac.uk/gwas/search?query=rs1801131"},
  {rsid:"rs1799945",gene:"HFE",nutrient:"iron",endpoint:"iron loading / hereditary haemochromatosis carrier marker",category:"iron_homeostasis",source:"https://www.ncbi.nlm.nih.gov/clinvar/?term=rs1799945"},
  {rsid:"rs1800562",gene:"HFE",nutrient:"iron",endpoint:"iron loading / hereditary haemochromatosis carrier marker",category:"iron_homeostasis",source:"https://www.ncbi.nlm.nih.gov/clinvar/?term=rs1800562"}
];
export function makeCandidateReport(dataset, nutrient="all"){
  if(!dataset||!(dataset.calls instanceof Map)||!dataset.qc.completed)throw Error("Complete imported array required.");
  if(dataset.qc.build!=="GRCh37")return {status:"BUILD_NOT_VERIFIED",build:dataset.qc.build,
     message:"Raw file build must be verified as GRCh37; do not combine GRCh37 coordinates with other builds."};
  const selected=EVIDENCE.filter(x=>nutrient==="all"||x.nutrient===nutrient);
  return {status:"RESEARCH_ONLY",input_qc:dataset.qc,selected_nutrient:nutrient,
    analyzed_loci:selected.length,matched_loci:selected.filter(x=>dataset.calls.has(x.rsid)).length,
    candidates:selected.map(x=>{
      const found=dataset.calls.get(x.rsid);
      return {rsid:x.rsid,gene:x.gene,endpoint:x.endpoint,mechanism:x.category,
        genotype:found?.gt??null,chromosome:found?.chr??null,position:found?.pos??null,
        status:found?"ARRAY_CALL_UNVALIDATED":(dataset.noCalls?.has(x.rsid)?"ARRAY_NO_CALL":"NOT_ON_ARRAY"),source:x.source,
        interpretation:"Population evidence only. No individual risk or absorption diagnosis."};
    }),
    excluded_inferences:["Unknown SNPs do not imply reference genotype.",
      "Array cannot reliably exclude HLA celiac predisposition, rare monogenic disorders, CNVs or acquired malabsorption.",
      "Serum concentration association is not direct evidence of intestinal absorption.",
      "Effect alleles, strand, genome build and study ancestry must be independently harmonized before estimating direction.",
      "No validated personal absolute risk score is provided."]};
}
export function csvLine(values){
  return values.map(v=>'"'+String(v??"").replace(/"/g,'""')+'"').join(",");
}

/* Local random access across the entire imported array; zero network calls.
   Keep the original chromosome, coordinate, and two observed alleles.
   This is a lookup, never a medical variant classification. */
export function searchImportedSnps(dataset, input, {max=100}={}){
  if(!dataset||!(dataset.calls instanceof Map)||!dataset.qc.completed)throw Error("Complete local array required");
  const q=String(input??"").trim();
  if(!q)throw Error("Please enter at least one rsID.");
  const tokens=q.split(/[\s,;]+/).filter(Boolean).map(x=>x.toLowerCase());
  if(tokens.length>max)throw Error("Too many rsIDs in one query (maximum "+max+").");
  if(tokens.some(x=>!RS.test(x)))throw Error("One or more marker IDs are invalid; use rs123456.");
  const unique=[...new Set(tokens)];
  return {status:"LOCAL_SNP_LOOKUP_NO_RISK_INTERPRETATION",build:dataset.qc.build,
    looked_up:unique.length,matched:unique.filter(id=>dataset.calls.has(id)).length,
    variants:unique.map(rsid=>{
       const v=dataset.calls.get(rsid);
       return {rsid,genotype:v?.gt??null,chromosome:v?.chr??null,position:v?.pos??null,
         status:v?"ARRAY_CALL_UNVERIFIED":(dataset.noCalls?.has(rsid)?"ARRAY_NO_CALL":"NOT_ON_ARRAY"),
         study_search_url:"https://www.ebi.ac.uk/gwas/search?query="+rsid,
         reference_search_url:"https://grch37.ensembl.org/Homo_sapiens/Variation/Explore?v="+rsid};
    }),
    cautions:["Raw allele strings are not independently verified or harmonized to study effect alleles.",
      "Missing variant is unknown, not normal genotype.",
      "Links open public databases with only a public rsID; your private alleles are not sent."]};
}
