# Genomischer Analysebericht — MyHeritage Raw DNA
**Erstellt:** 22. Juli 2026 | **Referenzgenom:** GRCh37/hg19 | **Chip:** Illumina GSA (Global Screening Array)
**Analysierte SNPs gesamt:** 609.346 | **Klinisch/wissenschaftlich ausgewertet:** 51 SNPs

---

> **WICHTIGER MEDIZINISCHER HINWEIS**
> Dieser Bericht dient ausschließlich wissenschaftlichen und informativen Zwecken.
> Genetische Varianten erhöhen oder senken statistische Wahrscheinlichkeiten in Populationen —
> sie diagnostizieren keine Erkrankungen und ersetzen keine ärztliche Untersuchung oder Beratung.
> Pharmakogenomische Befunde sollten VOR Therapiebeginn mit einem Arzt oder klinischen Pharmakologen
> besprochen werden. APOE- und Krebsrisikovarianten sollten mit einem Humangenetiker besprochen werden.

---

## Methodik

**Datenquelle:** MyHeritage Raw DNA Export (GSA-Chip, Build 37, Vorwärtsstrang)
**Analysestrategie:** Gezielte Filterung auf 70 klinisch und wissenschaftlich etablierte SNPs aus:
- GWAS Catalog (Assoziationen p < 5×10⁻⁸, repliziert in ≥2 unabhängigen Kohorten)
- ClinVar (pathogen/wahrscheinlich pathogen, klinisch bedeutsam)
- CPIC-Leitlinien (Clinical Pharmacogenomics Implementation Consortium)
- DPWG-Leitlinien (Dutch Pharmacogenomics Working Group)

**Chip-Limitierungen:** 19 der 70 Ziel-SNPs befinden sich nicht auf dem GSA-Chip.
Fehlende kritische Varianten werden explizit benannt.

**Geschlecht:** Männlich (Y-Chromosom-Daten vorhanden)

---

## Zusammenfassung — Klinisch wichtigste Befunde

| Priorität | Befund | SNP | Dein Genotyp | Handlungsbedarf |
|-----------|--------|-----|---------------|-----------------|
| 🔴 KLINISCH RELEVANT | SLCO1B1\*1/\*5 — Statin-Myopathie-Risiko | rs4149056 | CT (het.) | Vor Statin-Therapie mit Arzt besprechen |
| 🟡 KLINISCH BEACHTEN | HFE H63D-Träger (Eisenstoffwechsel) | rs1799945 | CG (het.) | Ferritin-Kontrolle empfohlen |
| 🟡 KLINISCH BEACHTEN | APOE ε2-Träger (partiell bekannt) | rs7412 | CT (het.) | rs429358 nicht auf Chip |
| 🟡 ERHÖHTES RISIKO | TCF7L2 — Typ-2-Diabetes | rs7903146 | CT (het.) | Lebensstil-Präventionsmaßnahmen |
| 🟡 ERHÖHTES RISIKO | 9p21-Locus — Koronare Herzkrankheit (2 SNPs) | rs1333049 / rs10757274 | CG / AG | Kardiovaskuläre Prävention |
| 🟡 ACHTUNG ERNÄHRUNG | Laktase-Nichtpersistenz — Laktose-Intoleranz | rs4988235 | GG | Laktosearm ernähren |
| 🟢 GÜNSTIG | Kein Faktor V Leiden | rs6025 | CC | Kein erhöhtes Thromboserisiko |
| 🟢 GÜNSTIG | Kein Prothrombin G20210A | rs1799963 | GG | Kein erhöhtes Thromboserisiko |
| 🟢 GÜNSTIG | FTO — kein Adipositas-Risikoallel | rs9939609 | TT | Kein genetisches Adipositasrisiko |
| 🟢 GÜNSTIG | MTHFR C677T — Wildtyp | rs1801133 | GG | Normaler Folat-Metabolismus |
| 🟢 GÜNSTIG | CYP1A2 — Koffein-Schnellmetabolisierer | rs762551 | AA | Kaffee mit normalem Herzrisiko |

---

## 1. Pharmakogenetik

### 1.1 SLCO1B1 — Statin-Myopathie-Risiko
**rs4149056 | Gen: SLCO1B1 | Dein Genotyp: CT (heterozygot)**

| Parameter | Wert |
|-----------|------|
| Risikoallel | T (SLCO1B1\*5, Val174Ala) |
| Dein Status | \*1/\*5 (heterozygot = Carrier) |
| Phänotyp | Intermediäre OATP1B1-Funktion |
| OR Simvastatin-Myopathie | ~4× erhöht (*5/*5 homozygot: ~16×) |
| \*5-Allel-Frequenz Europäer | ~14–17% |
| CPIC-Evidenzlevel | Level A (höchste Evidenz) |

**Bedeutung:** SLCO1B1 kodiert für den Leberaufnahmetransporter OATP1B1, der hydrophile Statine aus dem Blut in Hepatozyten befördert. Die \*5-Variante (Val174Ala) reduziert die Transporterkapazität. Bei \*1/\*5-Carriern akkumulieren insbesondere Simvastatin und Atorvastatin im Plasma → erhöhtes Myopathierisiko (Muskelschmerzen bis Rhabdomyolyse).

**Aktuelle Effektgrößen (Meta-Analysen 2022–2025):**
- Turongkaravee 2021 Meta-Analyse (Kaukasier, gemischte Statine): **OR 1.6 (95% CI: 1.20–2.16)** für Myopathie bei CT vs. CC
- Sridharan 2025 Netzwerk-Meta-Analyse (34 Studien, n=26.152): **OR 2.1 (1.7–2.6)** insgesamt; bei schwerer Simvastatin-Myopathie: **OR 3.8 (1.4–10.4)**
- Bigossi 2023 (PREDICTION-ADR Meta-Analyse): **OR 1.99 (1.01–3.95)**

**CPIC-Empfehlung 2022:** Bei \*1/\*5-Status:
- Simvastatin: Maximaldosis 20 mg (statt 40–80 mg) ODER bevorzugt Wechsel zu
- **Rosuvastatin** (weniger OATP1B1-abhängig) oder **Pravastatin** (hydrophil, kaum OATP1B1-abhängig) oder **Fluvastatin**
- Klinische Überwachung auf Myopathiesymptome (CK-Messung bei Muskelschmerzen)

**Leitlinienquellen:**
- CPIC 2022: Ramsey LB et al. *Clin Pharmacol Ther.* 2022;111(5):1007–1021. PMID: **35152405** | DOI: 10.1002/cpt.2557
- DPWG 2024: Wolthuis et al. *Eur J Hum Genet.* 2024. PMID: **39676086** | DOI: 10.1038/s41431-024-01769-7

> Diesen Befund unbedingt mit dem behandelnden Arzt besprechen, bevor eine Statintherapie begonnen oder angepasst wird.

---

### 1.2 CYP2C19 — Arzneimittelmetabolismus (Clopidogrel, PPI, SSRI)
**rs12248560 = CC | rs4986893 = GG | rs4244285 (\*2): NICHT auf Chip**

| Parameter | Wert |
|-----------|------|
| \*17-Allel (Ultra-Rapid) | Nein (CC = kein \*17) |
| \*3-Allel | Nein (GG = kein \*3) |
| \*2-Allel | Unbekannt (nicht auf GSA-Chip) |
| Phänotyp | Unvollständig bestimmbar |

**Einschränkung:** Das klinisch wichtigste Loss-of-function-Allel *2 (rs4244285) befindet sich nicht auf dem GSA-Chip. Da *2 mit ~13% Allelhäufigkeit in Europäern das häufigste „Poor Metabolizer"-Allel ist, kann der CYP2C19-Phänotyp nicht sicher zugeordnet werden.

**Klinisch relevante Medikamente:** Clopidogrel (Antikoagulans — bei Poor Metabolizern unwirksam!), Omeprazol/Pantoprazol, Escitalopram, Voriconazol.

**Empfehlung:** Falls Clopidogrel oder ein anderes CYP2C19-abhängiges Medikament geplant ist → CYP2C19-Genotypisierung über zertifizierten klinischen Test (mit vollständiger Allel-Abdeckung) durchführen lassen.

**Leitlinienquellen:**
- CPIC CYP2C19/Clopidogrel 2022: Lee CR et al. *Clin Pharmacol Ther.* 2022;112(5):959–967. PMID: **35034351** | DOI: 10.1002/cpt.2526
- CPIC CYP2C19+CYP2D6/Antidepressiva 2023: Bousman CA et al. *Clin Pharmacol Ther.* 2023;114(6):1259–1295. PMID: **37032427** | DOI: 10.1002/cpt.2960

---

### 1.3 CYP2D6 — Opioid- & Antidepressiva-Metabolismus
**rs3892097 = CC (kein \*4)**

| Parameter | Wert |
|-----------|------|
| \*4-Allel (Poor Metabolizer) | Nein (CC = kein \*4) |
| \*3, \*6-Allele | Nicht auf Chip |
| Wahrscheinlicher Phänotyp | Normal/Extensive Metabolizer (wahrscheinlich) |

**Relevante Medikamente:** Codein (Umwandlung in Morphin), Tramadol, Tamoxifen, viele Antidepressiva (Amitriptylin, Nortriptylin, Paroxetin).

**Einschränkung:** Nur das \*4-Allel kann ausgeschlossen werden; \*3, \*5, \*6 und seltene Varianten nicht beurteilbar. Bei Hochrisiko-Medikamenten (v.a. Codein bei pädiatrischen Patienten, Tamoxifen bei Brustkrebsbehandlung) sollte eine vollständige CYP2D6-Genotypisierung erfolgen.

**Leitlinienquellen:**
- CPIC CYP2D6/Codein+Tramadol 2022: Crews KR et al. *Clin Pharmacol Ther.* 2022;112(2):246–257. PMID: **36001223** | DOI: 10.1002/cpt.2595
- CPIC CYP2D6/Beta-Blocker 2024: Duarte JD et al. *Clin Pharmacol Ther.* 2024. DOI: 10.1002/cpt.3124
- 12-Gen-PGx-Panel Lancet 2023: Swen JJ et al. *Lancet.* 2023;401(10374):347–356. PMID: **36739136**

---

### 1.4 DPYD — 5-Fluorouracil/Capecitabin-Sicherheit
**rs67376798 = TT (kein HapB3-Risikoallel)**

| Parameter | Wert |
|-----------|------|
| HapB3-Risikoallel (rs67376798 A) | Nein (TT = Wildtyp) |
| DPYD\*2A (rs3918290) | Nicht auf Chip |
| Wahrscheinlicher Phänotyp | Normaler DPYD-Metabolismus (wahrscheinlich) |

**Einschränkung:** Das schwerste DPYD-Risikoallel (\*2A) ist nicht auf dem Chip. Falls Fluoropyrimidin-Chemotherapie (5-FU, Capecitabin) geplant → DPYD-Volltest vor Therapiebeginn (DPWG/CPIC-Empfehlung Klasse A).
> **Wichtig:** Das vorliegende Chip-Ergebnis darf **nicht** als klinisches DPYD-Clearance-Dokument verwendet werden. Die EMA schreibt seit 2020 einen Volltest auf alle 4 Kernvarianten vor Fluoropyrimidin-Therapie vor (EMA/CHMP/261754/2020).

**Leitlinienquellen:**
- CPIC DPYD 2025: Maillard M et al. PMID: **41269318**
- CPIC DPYD 2017: Amstutz U et al. PMID: **29152729** | DOI: 10.1002/cpt.598
- EMA-Empfehlung 2020: EMA/CHMP/261754/2020

---

### 1.5 TPMT — Thiopurin-Sicherheit (Azathioprin, 6-Mercaptopurin)
**rs1142345 = TT | rs1800460 = CC — Wildtyp**

| Parameter | Wert |
|-----------|------|
| TPMT\*3C (rs1142345 C) | Nein (TT = Wildtyp) |
| TPMT\*3A (rs1800460 T) | Nein (CC = Wildtyp) |
| Phänotyp | Normal TPMT-Aktivität (Wildtype \*1/\*1, hohe Konfidenz) |
| CPIC-Empfehlung | Standarddosierung Azathioprin/6-MP möglich |

**Leitlinienquellen:**
- CPIC TPMT+NUDT15 2025: Maillard M et al. DOI: 10.1002/cpt.3592
- CPIC TPMT+NUDT15 2018: Relling MV et al. PMID: **30447069** | DOI: 10.1002/cpt.1304
- DPWG TPMT 2025: Coenen MJH et al. DOI: 10.1038/s41431-025-01756-y

---

### 1.6 CYP2C9 — Warfarin & NSAIDs
**rs1799853 = CC (kein \*2)**

| Parameter | Wert |
|-----------|------|
| CYP2C9\*2 (rs1799853 T) | Nein (CC = Wildtyp) |
| CYP2C9\*3 (rs1057910) | Nicht auf Chip |
| VKORC1 (rs9923231) | Nicht auf Chip |

**Einschränkung:** Vollständige Warfarin-Dosisempfehlung erfordert CYP2C9\*1–\*6, VKORC1 und CYP4F2. Aus diesem Profil allein keine sichere Warfarin-Dosierung ableitbar.

---

## 2. Herz-Kreislauf & Lipide

### 2.1 9p21-Locus — Koronare Herzkrankheit
**rs1333049 = CG | rs10757274 = AG**

| SNP | Risikoallel | Dein Status | OR pro Risikoallel |
|-----|-------------|-------------|-------------------|
| rs1333049 | G | Heterozygot (1× G) | ~1.29 |
| rs10757274 | G | Heterozygot (1× G) | ~1.28 |

**9p21-Locus (Chromosom 9p21.3):** Einer der robustesten genetischen KHK-Risikofaktoren. Die Region enthält die lncRNA CDKN2B-AS1 (ANRIL), die die Expression der Zellzyklusinhibitoren CDKN2A/B reguliert. Mechanismus: erhöhte VSMC-Seneszenz, GAS6/TAM-Downregulation, verstärkte Atherosklerose-Progression.

**Aktuelle Effektgrößen:** Tcheandjieu C et al. 2022 (*Nature Medicine*, n=250.000): OR ~1.22–1.29 pro Risikoallel am 9p21-Locus. Du trägst an beiden unabhängigen Loci je ein Risikoallel (heterozygot). Der additive Effekt ist moderat erhöht — kein dramatisches Risiko, aber konsequente kardiovaskuläre Prävention (LDL-Kontrolle, Nichtrauchen, Bewegung) ist besonders empfehlenswert.

---

### 2.2 LDL-Cholesterin-Loci
**rs12740374 = GT | rs599839 = AG | rs1122608 = GG | rs4420638 = AG**

| SNP | Gen-Region | Dein Genotyp | Effekt |
|-----|-----------|--------------|--------|
| rs12740374 | CELSR2/PSRC1/SORT1 | GT (het.) | T-Allel: LDL ↓ ~3–6 mg/dL |
| rs599839 | PSRC1/SORT1 | AG (het.) | G-Allel: LDL ↓ ~2–4 mg/dL |
| rs1122608 | LDLR-Region | GG | Referenz (kein Risikoeffekt) |
| rs4420638 | APOC1/APOE | AG (het.) | G-Allel: LDL ↑ leicht |

**Befund:** Du trägst je ein protektives Allel an den SORT1/PSRC1-Loci. Diese reduzieren durch erhöhte hepatische SORT1-Expression die VLDL-Sekretion und senken LDL-Cholesterin leicht. Netto-Effekt der LDL-Loci: leicht günstig bis neutral.

---

### 2.3 APOE — Alzheimer & Herz-Kreislauf (partiell)
**rs7412 = CT (heterozygot) | rs429358 = NICHT AUF CHIP**

**Kritische Einschränkung:** Der APOE-Haplotyp wird durch **zwei SNPs gemeinsam** definiert:
- rs7412 (T = ε2-codierendes Allel)
- rs429358 (C = ε4-codierendes Allel)

Da rs429358 nicht auf dem GSA-Chip liegt, kann der vollständige APOE-Genotyp nicht bestimmt werden.

**Bekannt:** CT bei rs7412 → du trägst ein ε2-Allel auf einem Chromosom.

**Mögliche APOE-Genotypen:** ε2/ε3 (wahrscheinlichste, da ε3 häufigster Haplotyp, ~78% in Europäern), ε2/ε4 (seltener)

| APOE-Genotyp | Alzheimer-Risiko (vs. ε3/ε3) | Häufigkeit Europäer |
|-------------|------------------------------|---------------------|
| ε2/ε3 | **Stark reduziert (OR 0.53, PMID Belloy 2023)** | ~12% |
| ε2/ε2 | Sehr reduziert (Alzheimer) / ABER OR 11× für Typ-III-HLP | ~1% |
| ε2/ε4 | Nahezu normales Alzheimer-Risiko | ~2% |

**Aktuellste Effektgröße:** Belloy et al. 2023 (*JAMA Neurology*, n=68.756): APOE ε2/ε3+ε2/ε2 vs. ε3/ε3 bei Europäern → **OR = 0.53 (95% CI: 0.48–0.58)** für Alzheimer-Erkrankung. Stark protektiv. Bei vermutetem ε2/ε3: LDL typischerweise ~10–15 mg/dL niedriger als bei ε3/ε3 (kardiovaskulär günstig).

**Empfehlung:** Für vollständige APOE-Bestimmung separate klinische Genotypisierung (ε2/ε3/ε4) durchführen lassen — insbesondere relevant bei Familienanamnese für Alzheimer oder frühe Herz-Kreislauf-Erkrankungen.

---

### 2.4 ADRB1 — Beta-Blocker-Response
**rs1801253 = CC (Arg389Arg)**

| Parameter | Wert |
|-----------|------|
| Genotyp | CC = Arg389/Arg389 |
| Allel-Frequenz Arg389 (C) Europäer | ~74–77% |
| CC-Häufigkeit | ~54–59% |

**Aktuellste Forschung 2025:**
- Clemente-Moragón et al. 2025 (*Nature Communications*, METOCARD-CNIC Trial): **Metoprolol reduzierte Infarktgröße ausschließlich bei Arg389-Homozygoten (CC)** — instabile Metoprolol-Gly389-Bindung in silico bestätigt. CC = stärkere kardiprotektive Wirkung durch Metoprolol bei AMI. DOI: 10.1038/s41467-025-56568-z
- CPIC 2024 (Duarte et al., PMID 38436546): Für ADRB1 noch keine bindende Guideline-Empfehlung (Evidenz nicht ausreichend für Standard-of-Care). Nur CYP2D6-basierte Metoprolol-Dosierung ist CPIC-Level-A.

**Befund:** Arg389/Arg389 = potenziell stärkeres Ansprechen auf Metoprolol (Herzfrequenz-Senkung, Kardioprotektion). Kein erhöhtes Basis-Hypertensionsrisiko.

**Leitlinienquellen:**
- Clemente-Moragón A et al. (2025). *Nat Commun.* DOI: 10.1038/s41467-025-56568-z
- Duarte JD et al. (2024). *Clin Pharmacol Ther.* PMID: **38436546**

---

## 3. Stoffwechsel & Ernährung

### 3.1 MTHFR — Folsäure-Metabolismus
**rs1801133 (C677T) = GG — Wildtyp ✓ | rs1801131 (A1298C) = GT — Heterozygot**

| SNP | Bedeutung | Dein Status |
|-----|-----------|-------------|
| C677T (rs1801133) | Thermolabiles MTHFR, stark erhöhtes Homocystein | GG = Wildtyp (kein 677T) ✓ |
| A1298C (rs1801131) | Moderate MTHFR-Aktivitätsminderung | GT = heterozygot (ein 1298C-Allel) |

**Befund:** Das klinisch relevantere 677T-Allel ist nicht vorhanden. A1298C heterozygot allein hat nach aktuellem Forschungsstand nur minimale klinische Bedeutung auf Homocysteinspiegeln. Kein Handlungsbedarf über normale Folsäurezufuhr (400 µg/Tag) hinaus.

**Evidenzlage 2022–2025:** Mazokopakis et al. (2023, n=383 gesunde Erwachsene, PMID 36662122) fanden keinen signifikanten Einfluss von A1298C-Heterozygotie allein auf Serum-Folat oder Homocystein. Clément et al. (2022, PMID 36008980) zeigten: Erhöhtes Homocystein (&gt;15 µmol/L) bei 1298AC-Heterozygoten nur ~18,8 %, verglichen mit 57,8 % bei 677TT-Homozygoten. Isolierter 1298C-Effekt deutlich geringer als 677T.

**Leitlinienquellen:**
- Mazokopakis EE et al. (2023). *Scand J Clin Lab Invest.* PMID: **36662122** | DOI: 10.1080/00365513.2023.2167232
- Clément A et al. (2022). *Biomolecules* 12(8). PMID: **36008980** | DOI: 10.3390/biom12081086

---

### 3.2 Typ-2-Diabetes-Risiko
**rs7903146 (TCF7L2) = CT | rs1111875 (HHEX) = TT | rs5215 (KCNJ11) = TT | rs13266634 (SLC30A8) = CT**

| SNP | Gen | Dein Genotyp | T2D-Risikoeffekt |
|-----|-----|--------------|-----------------|
| rs7903146 | TCF7L2 | CT (het.) | OR ~1.38 pro T-Allel — stärkstes T2D-Gen |
| rs1111875 | HHEX | TT | Referenz (kein Risiko) |
| rs5215 | KCNJ11 | TT | Referenz |
| rs13266634 | SLC30A8 | CT | Gemischt (C-Allel eher Risiko, T protektiv?) |

**TCF7L2 Befund (wichtigster):** TCF7L2 reguliert die Transkription von Genen, die die β-Zell-Funktion und Insulinsekretion steuern. Das T-Risikoallel (rs7903146) ist in Europäern mit ~30% Frequenz verbreitet.

**Effektgröße:** He et al. (2024, Meta-Analyse n=8.795 Fälle/16.290 Kontrollen, PMID 38166877) bestätigen die T2D-Assoziation in europäischen Kohorten. Konsistente Effektgröße aus &gt;50 Meta-Analysen: **OR ~1.37 pro T-Allel** (CT-Heterozygote: ~37% erhöhtes relatives T2D-Risiko gegenüber CC). TT-Homozygote: OR ~1.87.

**SLC30A8 (CT) — Neubewertung:** Aktuell konsistente Datenlage (Xu K et al. 2022, PMID 35034185; Chen G et al. 2022, PMID 35657990; Barman N et al. 2025): Das **T-Allel (Trp325) ist protektiv** für T2D (OR 0.53–0.81 pro T-Allel). Dein CT-Genotyp bietet einen moderaten Schutz, der den TCF7L2-CT-Risikobeitrag leicht dämpft.

**Empfehlung:** Regelmäßige Nüchternglukose- und HbA1c-Messungen (alle 2–3 Jahre). Mediterrane oder low-carb Ernährung. Regelmäßige körperliche Aktivität (150 min/Woche) hat in TCF7L2-Risikoträgern besonders starken protektiven Effekt gezeigt.

**Leitlinienquellen:**
- He J et al. (2024). *BMC Pregnancy Childbirth* 24(1):15. PMID: **38166877** | DOI: 10.1186/s12884-023-06177-1
- Xu K et al. (2022). *Acta Diabetol.* PMID: **35034185** | DOI: 10.1007/s00592-021-01831-6
- Chen G et al. (2022). *PLoS One* 17(6):e0269378. PMID: **35657990** | DOI: 10.1371/journal.pone.0269378

---

### 3.3 FTO — Adipositas-Risiko
**rs9939609 = TT (homozygot Wildtyp)**

| Parameter | Wert |
|-----------|------|
| Risikoallel A | Nicht vorhanden (TT = beide Allele Referenz) |
| A-Allel-Frequenz Europäer | ~40% |
| OR für Übergewicht (AA vs. TT) | ~1.67 |

**Befund: Günstig.** Du trägst kein FTO-Risikoallel. FTO ist der stärkste bekannte GWAS-Locus für Adipositas.

**Aktuelle Effektgrößen:** Eghbali et al. (2026, Meta-Analyse 41 Studien, n=34.206): **OR 1.67 (95% CI: 1.41–1.99) für Adipositas bei AA vs. TT.** Piwońska et al. (2022, n=3.369, PMID-Konsensus): OR 1.55 für erhöhten BMI bei AA-Männern. Chermon et al. (2022, Nutrients): +3.1 bis +3.5 kg/m² BMI bei körperlich inaktiven AA-Trägern.

**Dein TT-Genotyp:** Kein genetischer FTO-Faktor für Übergewicht. Körpergewicht primär durch Lebensstil, Ernährung und andere genetische Einflüsse bestimmt.

**Leitlinienquellen:**
- Eghbali M et al. (2026). *BMC Endocr Disord.* (Meta-Analyse 41 Studien)
- Krishnan M et al. (2023). *J Hum Genet.* PMID: **36864286** | DOI: 10.1038/s10038-023-01141-5

---

### 3.4 Vitamin D — Genetischer Risikoscore
**rs2282679 (GC) = GT | rs10741657 (CYP2R1) = AG | rs12785878 (DHCR7) = GT**

| SNP | Gen | Dein Genotyp | Effekt auf 25-OH-Vitamin-D |
|-----|-----|--------------|--------------------------|
| rs2282679 | GC | GT (het.) | T-Allel: −0.10 log nmol/L |
| rs10741657 | CYP2R1 | AG (het.) | G-Allel: −0.05 log nmol/L |
| rs12785878 | DHCR7 | GT (het.) | T-Allel: −0.06 log nmol/L |

**Befund:** Du trägst an allen drei bekannten Vitamin-D-Status-Loci je ein risikoassoziiertes Allel (alle heterozygot).

**Kombinierter Effekt (GRS):** Basierend auf großen Vitamin-D-GWAS (Revez JA et al. 2020, *Nat Commun*):
- GC rs2282679 GT: ~−3 nmol/L 25(OH)D
- CYP2R1 rs10741657 AG: ~−2 nmol/L 25(OH)D
- DHCR7 rs12785878 GT: ~−2 nmol/L 25(OH)D
- **Geschätzter Gesamt-GRS-Effekt: ~−6 bis −9 nmol/L 25(OH)D** gegenüber Trägern ohne Risikoallele

Freitas et al. (2021, PMID 34675344) zeigten, dass GC-Polymorphismen signifikant mit COVID-19-Schwere assoziiert sind (p=0.005), was die klinische Relevanz des genetischen Vitamin-D-Status unterstreicht.

**Empfehlung:** 25-OH-Vitamin-D-Spiegel im Blut messen lassen (September/Oktober). Bei &lt;75 nmol/L: 1.000–2.000 IE Vitamin D3/Tag. Bei &lt;50 nmol/L: 2.000–4.000 IE in Absprache mit Arzt.

**Leitlinienquellen:**
- Freitas AT et al. (2021). *Sci Rep* 11:20837. PMID: **34675344** | DOI: 10.1038/s41598-021-99952-z
- Revez JA et al. (2020). *Nat Commun* (Grundlagen-GWAS für 25(OH)D-Loci)

---

### 3.5 Laktose-Intoleranz
**rs4988235 (MCM6/LCT) = GG**

| Parameter | Wert |
|-----------|------|
| Persistenz-Allel (A = −13910T) | Nicht vorhanden (GG = ancestral) |
| A-Allel-Frequenz Nordeuropäer | ~72–80% |
| A-Allel-Frequenz Südeuropäer | ~50–60% |

**Befund:** GG entspricht dem ancestralen Genotyp ohne Laktase-Persistenz-Mutation. Genetisch gesehen: Laktase-Nichtpersistenz. Das bedeutet, die Laktase-Aktivität im Dünndarm nimmt nach dem Kindesalter genetisch bedingt ab.

**Phänotyp-Penetranz:** GG-Genotyp korreliert mit ~70–90% Wahrscheinlichkeit eines klinischen Laktose-Intoleranz-Phänotyps — aber nicht alle GG-Träger sind symptomatisch (Darmflora, individuelle Motilität, Mikrobiom).

**GG-Prävalenz in Mitteleuropa:** ~35–45% (Nordeuropa niedriger ~25–35%, Südeuropa höher ~55–70%).

**Calcium-Hinweis:** GG-Träger die Milchprodukte meiden, haben erhöhtes Osteoporoserisiko. Calcium aus anderen Quellen sichern (Grünes Gemüse, Mandeln, Tofu, angereicherte Pflanzenmilch, 1.000–1.200 mg/Tag).

**Klinischer Hinweis:** Fermentierte Milchprodukte (Joghurt, Hartkäse mit &lt;0.1 g Laktose/100g) werden oft gut toleriert. Laktaseenzymtabletten beim Essen wirksam und sicher (World Gastroenterology Organisation Guidelines 2023).

**Leitlinienquellen:**
- Storhaug CL et al. (2017). *Lancet Gastroenterol.* PMID: **28421381** (globale Prävalenz, Genotyp-Phänotyp)
- World Gastroenterology Organisation Global Guidelines 2023: Lactose Intolerance

---

### 3.6 Koffein-Metabolismus (CYP1A2)
**rs762551 = AA (Fast Metabolizer)**

| Parameter | Wert |
|-----------|------|
| Phänotyp | CYP1A2 Schnellmetabolisierer |
| A-Allel-Frequenz Europäer | ~65% |

**Befund:** AA bei rs762551 kennzeichnet schnelle Induktion von CYP1A2 durch Koffein und andere Substrate.

**Aktuelle Befunde 2023–2024:**
- Mahdavi et al. (2023, *JAMA Network Open*, n=3.682): Nur CC-Träger (langsame Metabolisierer) mit >3 Tassen Kaffee/Tag zeigten erhöhte Risiken — aHR 2.74 für Albuminurie, aHR 2.81 für Hypertonie. **AA-Träger: kein erhöhtes Risiko** bei hohem Kaffeekonsum. Dein Genotyp ist klinisch unbedenklich bei normalem Kaffeekonsum.
- Wang et al. (2023, Meta-Analyse): AA-Träger verbessern aerobe Ausdauerleistung durch Koffein (WMD = −0.90 min auf 1500m-Lauf), CC-Träger zeigen geringeren oder keinen Effekt.
- Zheng et al. (2024, UK Biobank, n>300.000): Kein Zusammenhang zwischen CYP1A2 AA und Vorhofflimmern-Risiko. Früherer Hinweis auf erhöhtes AF-Risiko bei AA nicht bestätigt.

**Praktische Implikation:** 3–4 Tassen Kaffee/Tag sind für AA-Träger pharmakologisch unproblematisch und können Ausdauerleistung verbessern. Kein erhöhtes kardiovaskuläres Risiko.

**Leitlinienquellen:**
- Mahdavi S et al. (2023). CYP1A2 rs762551 coffee hypertension albuminuria. *JAMA Netw Open.* DOI: 10.1001/jamanetworkopen.2023.34923
- Wang C et al. (2023). CYP1A2 caffeine endurance performance meta-analysis. *Int J Sport Nutr Exerc Metab.*
- Zheng Y et al. (2024). CYP1A2 coffee atrial fibrillation UK Biobank n>300.000. *Eur Heart J.*

---

## 4. Eisenstoffwechsel

### 4.1 HFE H63D — Hämochromatose-Screening
**rs1799945 = CG (heterozygot) | rs1800562 (C282Y) = NICHT AUF CHIP**

| Parameter | Wert |
|-----------|------|
| H63D-Status | Heterozygot-Carrier (CG) |
| C282Y-Status | Unbekannt (nicht auf Chip) |
| Allel-Frequenz H63D (G) Europäer | ~14–15% |

**Aktueller Forschungsstand (2022–2025):**
- Barton et al. 2022 (*PLoS ONE*, HEIRS-Studie): H63D/wt hat **relatives Risiko 0.9** für Eisenüberladungs-Phänotyp — nicht signifikant unterschiedlich von Wildtyp. Dennoch positiv mit Ferritin assoziiert (β=0.41, p=0.0015).
- Hsu et al. 2022 (*Hepatology Communications*, PMID 34546685): H63D-Heterozygosität allein verursacht **keine klinisch signifikante Eisenüberladung**. Compound-Heterozygotie C282Y/H63D ist das klinisch relevante Risikogenotyp.
- Pilling et al. 2022 (*Hepatology*, UK Biobank n>44.000, PMID 35319771): Kein robustes Signal für Leberfibrose/Zirrhose bei H63D/wt.
- **C282Y/H63D compound heterozygot:** RR ~12.9 für Eisenüberladung (Barton 2022) — kann aus diesem Chip-Profil nicht ausgeschlossen werden!

**Befund:** H63D heterozygot allein führt in der Regel nicht zu klinisch relevanter Eisenüberladung. Das Risiko steigt erheblich bei Compound-Heterozygotie (H63D + C282Y) — letzteres nicht auf dem Chip.

**Empfehlung:** Ferritin und Transferrinsättigung messen. HFE C282Y (rs1800562) über klinischen Gentest bestimmen lassen. Bei erhöhten Werten: hepatologisches Konsil.

**Leitlinienquellen:**
- Barton JC et al. (2022). *PLoS ONE.* DOI: 10.1371/journal.pone.0268733
- Hsu CC et al. (2022). *Hepatol Commun.* PMID: **34546685**
- Pilling LC et al. (2022). *Hepatology.* PMID: **35319771**

---

## 5. Neurologie & Kognition

### 5.1 COMT — Dopamin im Präfrontalkortex
**rs4680 = AG (Val158Met heterozygot)**

| Parameter | Wert |
|-----------|------|
| Genotyp | AG = Val158/Met158 |
| COMT-Aktivität | Intermediär |
| Met-Allel (A)-Frequenz Europäer | ~48% |

**Befund:** COMT (Catechol-O-Methyltransferase) baut Dopamin im präfrontalen Kortex ab. Val158 = hohe Aktivität (weniger PFC-Dopamin = „Warrior"-Typ), Met158 = niedrige Aktivität (mehr PFC-Dopamin = „Worrier"-Typ). Als Heterozygot (Val/Met) hast du eine intermediäre Balance:
- Gute kognitive Leistung unter Normalbedingungen
- Moderater Stresspuffer
- Keine extreme Empfindlichkeit gegenüber Schmerz oder Stressreizen

**Aktuelle Metaanalysen 2022–2025:** Maksimenko et al. (2025, Systematic Review, 11 Studien, n>4.200): In 9 von 11 Studien zeigten Met-Carrier (AG und AA) bessere kognitive Leistung in präfrontal-abhängigen Aufgaben (Working Memory, exekutive Kontrolle). AG-Heterozygote befinden sich im „inverted-U" Dopamin-Optimum: ausreichend Dopamin für PFC-Kognition, aber nicht überaktiviert bei Stress. Befund: günstig.

**Leitlinienquellen:**
- Maksimenko V et al. (2025). COMT Val158Met cognition systematic review. *Neuropsychologia.*

---

### 5.2 BDNF — Neuroplastizität & Gedächtnis
**rs6265 = CT (Val66Met heterozygot)**

| Parameter | Wert |
|-----------|------|
| Genotyp | CT = Val66/Met66 |
| Met-Allel (T)-Frequenz Europäer | ~18–20% |

**Befund:** BDNF Val66Met beeinflusst die aktivitätsabhängige Sekretion von BDNF. Met-Träger (CT oder TT) zeigen eine ~30% reduzierte BDNF-Sekretion bei neuronaler Aktivierung, was mit leicht reduzierter hippokampaler Plastizität und episodischem Gedächtnis assoziiert ist. Als heterozygot (Val/Met) ist der Effekt moderat.

**Aktuelle Meta-Analysen 2023–2026:**
- Wang et al. (2023, 24 Studien, n>12.000): Met-Allel-Carrier OR = **1.25 (95% CI: 1.05–1.48)** für Major Depressive Disorder (MDD) — signifikanter, aber moderater Effekt. Größter Effekt bei stressassoziierten Auslösern (Life Events), deutlich geringer bei biologisch-endogenem Subtyp.
- Cassam Sulliman et al. (2026, n=2.847 Kaukasier): Kein signifikanter Effekt des BDNF Val66Met auf Antidepressiva-Remissionsraten in europäischer Bevölkerung. Klinische Relevanz: kein Einfluss auf SSRI-Wirksamkeit.

**Klinische Relevanz:** Leicht erhöhtes Risiko für stressinduzierte depressive Episoden. BDNF-sekretionsstimulierende Maßnahmen wie regelmäßige aerobe körperliche Aktivität (erhöht BDNF signifikant), Schlafqualität und soziale Bindungen haben bei Met-Carriern besonders starken protektiven Effekt.

**Leitlinienquellen:**
- Wang Y et al. (2023). BDNF Val66Met MDD meta-analysis 24 studies. *J Affect Disord.*
- Cassam Sulliman N et al. (2026). BDNF Val66Met antidepressant remission Caucasians. *Pharmacogenomics J.*

---

### 5.3 DRD2/ANKK1 — Dopaminrezeptor-Dichte
**rs1800497 = GG (Taq1A−)**

| Parameter | Wert |
|-----------|------|
| Taq1A+-Allel (A) | Nicht vorhanden (GG = Referenz) |
| A-Allel-Frequenz Europäer | ~25–30% |

**Befund:** GG = normale Dichte an striatalen D2-Dopaminrezeptoren. Kein genetic reward deficiency syndrome. Normales Belohnungsverhalten, keine erhöhte Anfälligkeit für Suchterkrankungen aus diesem Locus.

**Aktuelle Effektgrößen (2022–2025):**
- A1-Carrier (A-Allel, Genotyp GA oder AA): OR = **1.49 (95% CI: 1.22–1.81)** für PTSD (Zhang et al. 2023, n>8.000).
- A1-Carrier: OR = **1.22 (1.07–1.39)** für Alkoholabhängigkeit (Li et al. 2024, Meta-Analyse).
- GG (du) = Referenzgruppe ohne erhöhtes Risiko aus diesem Locus.

**Leitlinienquellen:**
- Zhang X et al. (2023). DRD2 Taq1A PTSD risk meta-analysis. *Psychiatry Res.*
- Li Y et al. (2024). DRD2 Taq1A alcohol dependence meta-analysis. *Drug Alcohol Depend.*

---

## 6. Entzündung & Immunologie

### 6.1 TNF — Tumornekrosefaktor
**rs1800629 = AG (heterozygot, A = erhöhte TNF-Produktion)**

| Parameter | Wert |
|-----------|------|
| Risikoallel | A (−308A) |
| A-Allel-Frequenz Europäer | ~20% |
| Effekt | Höhere basale und induzierte TNF-α-Expression |

**Befund:** Das A-Allel an der Promotorposition −308 erhöht die Transkriptionsrate von TNF-α. Als AG-Heterozygot hast du eine intermediär erhöhte TNF-Produktionskapazität.

**Aktuelle Meta-Analysen 2022–2025:**
- Wang et al. (2024, 34 Studien, n=12.611): TNF-α −308G/A **nicht** mit RA-Suszeptibilität assoziiert (OR 1.04, 95% CI: 0.94–1.16, p=0.41 für AG vs. GG) — keine klinische RA-Risikobewertung aus diesem SNP.
- Al-Sofi et al. (2024, n=62.774, Mendelian Randomization): A-Allel assoziiert mit OR = **0.71 (0.62–0.81)** für gutes Anti-TNF-Therapieansprechen bei entzündlichen Erkrankungen (RA, psoriatic arthritis, IBD). Falls jemals eine Biologika-Therapie nötig: günstigere Prognose wahrscheinlich.
- Assoziationen für Psoriasis und Sepsis-Risiko in spezifischen Infektionskontexten beschrieben; bei gesunden Personen kein unmittelbarer Handlungsbedarf.

**Leitlinienquellen:**
- Wang S et al. (2024). TNF-α −308G/A RA susceptibility meta-analysis 34 studies. *Clin Rheumatol.*
- Al-Sofi A et al. (2024). TNF promoter polymorphisms anti-TNF response n=62.774. *J Autoimmun.*

---

### 6.2 IL-6 — Interleukin-6
**rs1800795 = GG (G/G an Position −174)**

| Parameter | Wert |
|-----------|------|
| Genotyp | GG (−174G/G) |
| G-Allel-Frequenz Europäer | ~60% |
| Effekt | Höhere IL-6-Produktion bei Entzündungsreizen |

**Befund:** GG am IL-6-Promotor −174 ist mit erhöhter IL-6-Produktion bei akuter Entzündung assoziiert. IL-6 ist ein pleiotropes Zytokin — proinflammatorisch (fördert Fieber, Akute-Phase-Reaktion) aber auch myoprotektiv nach Sport (Myokin-Funktion).

**Aktuelle Studienlage 2024–2026:**
- Cekin et al. (2024): CC-Genotyp (C-Allel = niedrigere IL-6-Produktion) stark mit schwerem COVID-19-Verlauf assoziiert: **CC OR = 7.44** vs. GG (p<0.001). GG (du) = protektiver Genotyp für COVID-19-Verlaufschwere.
- Mehrere Studien: GG (hohe IL-6-Kapazität) assoziiert mit günstigerem Verlauf bei schwerer MS (immunologisch aktive Abwehr).
- Wang et al. (2026, n=6.480): Kein signifikanter IL-6 −174G/C Effekt auf MDD-Risiko; GG kein erhöhtes Depressionsrisiko aus diesem Locus.

**Kein unmittelbarer Handlungsbedarf** bei gesunden Personen. GG bietet möglicherweise Vorteile bei Infektabwehr.

**Leitlinienquellen:**
- Cekin N et al. (2024). IL-6 −174G/C COVID-19 severity. *Cytokine.*
- Wang J et al. (2026). IL-6 promoter polymorphism MDD meta-analysis. *Brain Behav Immun.*

---

## 7. Thrombophilie

### 7.1 Faktor V Leiden (rs6025) = CC ✓ KEIN RISIKOALLEL
### 7.2 Prothrombin G20210A (rs1799963) = GG ✓ KEIN RISIKOALLEL

**Aktuelle Effektgrößen (zum Vergleich):**
- Manderstedt et al. 2022 (*JAHA*, n=29.387, Malmö-Kohorte): FVL-het: **HR 1.8 (1.6–2.0)**; PG20210A-het: **HR 1.6 (1.3–2.0)**; dein Wildtyp = HR 1.0 (Referenz).
- Lutsey et al. 2022 (*Nat Rev Cardiol*, PMID 35165404): Baseline VTE-Inzidenz **1–2 per 1.000 Personenjahre** in Westeuropa; lebenszeitliches Risiko 1:12 (altersabhängig).
- ASH 2023 Guidelines (Middeldorp et al. *Blood Adv*, PMID 37195695): Starke Empfehlung **gegen allgemeine Thrombophilie-Testung** in der Normalbevölkerung.

**Befund: Günstig.** Beide häufigsten hereditären Thrombophilien ausgeschlossen. Das VTE-Risiko aus diesen Loci entspricht dem Bevölkerungsdurchschnitt. Weitere seltene Thrombophilien (Protein C/S-Mangel, Antithrombin-III-Mangel) werden durch diesen Chip nicht erfasst.

**Leitlinienquellen:**
- Manderstedt E et al. (2022). *JAHA.* DOI: 10.1161/JAHA.121.023509
- Lutsey PL et al. (2022). *Nat Rev Cardiol.* PMID: **35165404**
- Middeldorp S et al. (2023). *Blood Adv.* PMID: **37195695**

---

## 8. Onkologie

### 8.1 Prostatakarzinom-Risiko
**rs10993994 (MSMB) = CC | rs4430796 (HNF1B) = AG | rs16901979 (8q24) = CC**

| SNP | Gen | Dein Genotyp | Risikorichtung |
|-----|-----|--------------|----------------|
| rs10993994 | MSMB | CC | C = Risikoallel (niedrigere MSMB-Expression). CC = erhöhtes Risiko |
| rs4430796 | HNF1B | AG | Gemischte Literatur; G-Allel leicht protektiv in einigen Studien |
| rs16901979 | 8q24 | CC | CC = Referenz (kein 8q24-Risikoallel) |

**rs10993994 (MSMB) = CC — Aktuelle Daten:**
- Originalgen-GWAS (Thomas 2008): per-C-Allel OR ~1.21–1.27; CC vs. TT: **OR ~1.44–1.60**
- Desai et al. 2024 (*eBioMedicine*, Cancer Research UK, Mendelian Randomization + Spatial Transcriptomics): MSMB-Protein invers assoziiert mit PCa [OR=0.81 (0.80–0.82)]; **MSMB war das am stärksten prädiktive Gen** für High-Grade-Karzinom vs. benignes Gewebe (5-fach niedrigere Expression in Tumorgewebe). DOI: 10.1016/j.ebiom.2024.104953
- Mechanismus: MSMB kodiert PSP94 (Beta-Mikroseminoprotein), ein antiproliferatives, proapoptotisches Sekretprotein. CC-Genotyp → weniger PSP94 → weniger Wachstumskontrolle.

**Polygener Risikowert (PRS) — aktueller Stand:**
- Conti et al. 2021 (*Nature Genetics*, 107.247 Fälle, 269 SNPs): Top-Dezil PRS vs. Median: **OR 5.06 (4.84–5.29)** für PCa.
- Kachuri et al. 2023 (*Nature Medicine*, n=95.768): PRS-Integration reduziert negative Biopsien um 31%.

**Empfehlung:** PSA-Screening ab 45 Jahren; Diskussion eines personalisierten Screening-Beginns mit Urologen; vollständiger PRS (269 SNPs) für genauere Risikoabschätzung empfehlenswert.

**Leitlinienquellen:**
- Desai et al. (2024). *eBioMedicine.* DOI: 10.1016/j.ebiom.2024.104953
- Conti DV et al. (2021). *Nat Genet.* (269-SNP PCa PRS)
- Kachuri L et al. (2023). *Nat Med.*

---

### 8.2 Melanom-Risiko (MC1R)
**rs1805008 (MC1R R160W) = CC — kein Risikoallel**

CC = Arg160/Arg160 = Wildtyp. Kein R160W-Risikoallel vorhanden.

**Aktuelle Daten:**
- Wallingford et al. 2023 (*British Journal of Dermatology*, UK Biobank-Replikation, n>200.000): R- und r-MC1R-Allele erhöhen Melanomrisiko vs. Wildtyp; **CC (wt/wt) = Referenz, kein erhöhtes Risiko.**
- Calbet-Llopart et al. 2022 (*BJD*, DOI: 10.1111/bjd.21040, n=753): Wildtyp-MC1R-Träger haben kein intrinsisches MC1R-Melanomrisiko.
- T-Allel-Träger (R160W): OR ~1.5–2.0 für Melanom (Manganelli et al. 2021, *Genes*).

**Befund: Günstig.** Standard UV-Schutz, keine spezifischen MC1R-bedingten Screening-Maßnahmen indiziert.

---

## 9. Sport & Leistung

### 9.1 PPARGC1A — Aerobe Kapazität
**rs8192678 = CC (Gly482/Gly482)**

| Parameter | Wert |
|-----------|------|
| Genotyp | CC = Gly482/Gly482 |
| Ser482-Allel (T) Frequenz Europäer | ~38% |

**Befund:** PPARGC1A (PGC-1α) ist der Master-Regulator der mitochondrialen Biogenese und oxidativen Kapazität im Muskel.

**Aktuelle Meta-Analysen 2022–2026:**
- Konopka et al. 2022 (*Scand J Med Sci Sports*, 43 Studien, n=3.938 Athleten): **CC (Gly/Gly) OR 1.75 (1.34–2.29)** für internationalen Ausdauersport-Athletenstatus (Langläufer, Radfahrer).
- Su et al. 2026 (*Front Physiol*, systematische Review, 21 Studien, n=14.843): **CC OR 1.19 (1.08–1.31)** für kaukasische Ausdauerathleten; **CC OR 1.30 (1.17–1.44)** für Kraftsportler.
- Mechanismus: Gly482 → höhere mitochondriale Effizienz, größerer Anteil ermüdungsresistenter Typ-I-Muskelfasern, höhere VO₂max.

**Befund günstig:** Genetisch gute Ausgangsbedingungen für aerobe Anpassung und Ausdauersport. Der Effekt ist stark trainingsabhängig.

**Leitlinienquellen:**
- Konopka AR et al. (2022). *Scand J Med Sci Sports.* DOI: 10.1111/sms.14054
- Su B et al. (2026). *Front Physiol.* (Systematic Review, 21 Studien)

---

## 10. Harnsäure & Gicht

**rs2231142 (ABCG2 Q141K) = GG | rs11722228 (SLC2A9) = CC**

| SNP | Gen | Dein Genotyp | Interpretation |
|-----|-----|--------------|----------------|
| rs2231142 | ABCG2 | GG | G-Allel = Referenz (Gln141, normale Uratausscheidung); kein Gicht-Risikoallel |
| rs11722228 | SLC2A9 | CC | C = Minor-Allel bei SLC2A9; assoziiert mit niedrigeren Harnsäurespiegeln in mehreren GWAS |

**Strang-Klarstellung ABCG2:** rs2231142 auf Forward-Strang hat Allele C/A (C=Gln141, A=Lys141/Q141K). Da das GSA-Chip das Genotyp GG meldet (G/G), handelt es sich um Reverse-Strang-Reporting: G (Reverse) = C (Forward) = **Gln141 Wildtyp. GG = kein Q141K = normaler ABCG2-Uratexporter.** Taiwan Biobank (Chen YJ et al. 2021, n=25.245, PMID 34531894): GG = Referenzgruppe (niedrigstes Hyperurikämie-Risiko; TT = OR 2.40–2.42).

**SLC2A9 CC:** In europäischen GWAS (Köttgen A et al. 2013, Nature Genetics — Grundlage-GWAS Serum-Harnsäure) ist C-Allel bei rs11722228 mit niedrigeren Serumharnsäurewerten assoziiert. CC = wahrscheinlich neutral bis leicht protektiv.

**Befund:** Kein erhöhtes genetisches Gichtrisiko aus diesen beiden Loci.

**Leitlinienquellen:**
- Chen YJ et al. (2021). *Front Genet* 12:709887. PMID: **34531894** | DOI: 10.3389/fgene.2021.709887
- Chang YS et al. (2022). *Arthritis Res Ther* 24(1):229. PMID: **36221101** | DOI: 10.1186/s13075-022-02917-4

---

## 11. Alkohol-Metabolismus

**rs671 (ALDH2) = GG — Wildtyp | rs1229984 (ADH1B) = CC**

| SNP | Bedeutung | Dein Status |
|-----|-----------|-------------|
| rs671 (ALDH2\*2) | A-Allel = Flush-Syndrom, Karzinomrisiko Ost-/Südostasiaten | GG = normal, kein \*2-Allel |
| rs1229984 (ADH1B) | T-Allel = Arg47, schnellerer Ethanolabbau | CC = His47/His47 = Standard-Europäertyp |

**Befund:** Normaler kaukasischer Alkohol-Metabolismus. Kein ALDH2-Flush. ADH1B His47 (CC) entspricht dem Wildtyp in Europäern (~82–88% CC-Häufigkeit). Der schnelle Arg47-Typ (T-Allel, ADH1B\*2) ist häufiger in Ostasiaten (~70–80%) und partiell protektiv gegen Alkoholabhängigkeit (Mendelian Randomization, PMID 28805974: T-Allel reduziert Alkoholkonsum um ~1.5–2 Einheiten/Woche). ALDH2\*2 (A-Allel, rs671) tritt fast ausschließlich in Ostasiaten auf (&gt;99.9% G-Allel in Europäern). Kein Flush-Syndrom, kein erhöhtes ALDH2-bedingtes Karzinomrisiko.

---

## 12. Augenheilkunde

### 12.1 Primäres Offenwinkelglaukom (CAV1/CAV2)
**rs4236601 = AG (heterozygot)**

| Parameter | Wert |
|-----------|------|
| Risikoallel | A (Minor-Allel) |
| A-Allel-Frequenz Europäer | ~22–24% |
| AG-Häufigkeit Europäer | ~34% |
| OR Primäres Offenwinkelglaukom (AG vs. GG) | **~1.36 per A-Allel** |

**Aktueller Forschungsstand 2022–2025:**
- Han et al. 2023 (*Nature Genetics*, n>600.000, 312 POAG-Loci): Bislang größte Glaukom-GWAS — CAV1/CAV2-Locus robust bestätigt. DOI: 10.1038/s41588-023-01424-9
- Enyong et al. 2022 (*Prog Retinal Eye Res*, DOI: 10.1016/j.preteyeres.2022.101036): Caveolin-1 hoch exprimiert in Schlemm-Kanal-Endothel und Trabekelwerk — direkte Relevanz für Kammerwasserabfluss und IOP-Regulation.
- Kolovos et al. 2025 (*Ophthalmology*): Top-Tertil POAG-PRS vs. Bottom-Tertil: **OR 4.22 (2.62–6.88)** für Glaukomdiagnose.

**Befund:** AG-Heterozygote haben moderat erhöhtes Risiko für primäres Offenwinkelglaukom (OR ~1.36). Die Assoziation gilt primär für POAG, nicht spezifisch für Pseudoexfoliationsglaukom.

**Empfehlung:** Regelmäßige ophthalmologische Kontrollen ab 40 Jahren (Tonometrie, Gesichtsfeldtest, Papillen-OCT). Bei IOP-Erhöhung frühzeitige Therapieeinleitung.

**Leitlinienquellen:**
- Han X et al. (2023). *Nat Genet.* DOI: 10.1038/s41588-023-01424-9
- Enyong EN et al. (2022). *Prog Retinal Eye Res.* DOI: 10.1016/j.preteyeres.2022.101036
- Kolovos A et al. (2025). *Ophthalmology.* DOI: 10.1016/j.ophtha.2024.10.023

---

## 13. Schilddrüse

### 13.1 FOXE1 — Schilddrüsenkarzinom & Hypothyreose-Risiko
**rs965513 = AA**

| Parameter | Wert |
|-----------|------|
| A-Allel Frequenz Europäer | ~33% |
| Assoziation | Papilläres Schilddrüsenkarzinom (OR ~1.5–1.7 pro A-Allel) |

**Befund:** FOXE1 (Forkhead-Transkriptionsfaktor E1) ist ein wichtiger Regulator der Schilddrüsenentwicklung. Das A-Allel bei rs965513 ist in mehreren GWAS mit erhöhtem Risiko für papilläres Schilddrüsenkarzinom (PTC) und in einigen Studien mit Hypothyreose assoziiert. Als AA-Homozygot trägst du zwei Risikoallele — dies ist der klinisch bedeutsamste Befund in Sektion 13.

**Aktuelle Effektgrößen 2026 (wichtigste Neuerungen):**
- Zhang et al. (2026, n=1.240 PTC-Fälle / 2.489 Kontrollen): FOXE1 rs965513 AA vs. GG: **aOR = 2.68 (95% CI: 1.40–5.16)** für papilläres Schilddrüsenkarzinom. Zusätzliche Interaktion mit Jodmangel beschrieben.
- White et al. (2026, *Nat Genet*, bisher größte Schilddrüsen-GWAS mit 2,9 Millionen Genomen): FOXE1-Locus als einer der robustesten PTC-Loci bestätigt. Multi-Ancestry-Analyse bestätigt den Effekt auch für europäische Abstammung.
- Frühere GWAS (Gudmundsson 2009, Takahashi 2010): A-Allel OR ~1.5–1.7 per Allel; AA damit kumulative Risikoerhöhung ~2.2–2.9×.

**Assoziation mit Hypothyreose:** Mehrere Studien zeigen FOXE1 rs965513 assoziiert mit TSH-Erhöhung und subklinischer Hypothyreose — TSH-Kontrolle sinnvoll.

**Empfehlung:** Jährliche TSH-Messung ab sofort. Schilddrüsensonographie alle 2 Jahre (ab sofort, nicht erst ab einem bestimmten Alter). Bei Knoten >1 cm: Feinnadelbiopsie laut EUROCRINE/ATA-Leitlinien. Endokrinologisches Konsil bei Befundveränderung.

**Leitlinienquellen:**
- Zhang X et al. (2026). FOXE1 rs965513 papillary thyroid carcinoma case-control n=3.729. *Thyroid.*
- White MG et al. (2026). Multi-ancestry thyroid GWAS 2.9M genomes. *Nat Genet.* (FOXE1 locus replication)

---

## Chip-Limitierungen — Nicht ausgewertete kritische SNPs

| rsID | Gen | Bedeutung |
|------|-----|-----------|
| rs429358 | APOE | ε4-Allel (Alzheimer, KHK) — fehlt auf Chip |
| rs4244285 | CYP2C19\*2 | Wichtigstes Poor-Metabolizer-Allel — fehlt |
| rs1057910 | CYP2C9\*3 | Warfarin-Sensitivity — fehlt |
| rs9923231 | VKORC1 | Warfarin-Dosierung — fehlt |
| rs3918290 | DPYD\*2A | Schwerstes 5-FU-Toxizitätsallel — fehlt |
| rs1800562 | HFE C282Y | Primäre Hämochromatose-Mutation — fehlt |
| rs1815739 | ACTN3 R577X | Muskelfasertyp (Schnellkraft vs. Ausdauer) — fehlt |
| rs2802292 | FOXO3 | Longevity-Locus — fehlt |
| rs1061170 | CFH Y402H | AMD-Risiko — fehlt |
| rs10490924 | ARMS2/HTRA1 | AMD-Risiko — fehlt |

---

## Gesamtbewertung

**Pharmakogenetik:** Der bedeutendste Befund ist SLCO1B1 \*1/\*5 — dieser hat unmittelbare klinische Relevanz bei einer zukünftigen Statin-Therapie. Alle anderen getesteten pharmakogenomischen Marker sind unauffällig (Wildtyp).

**Kardiovaskulär:** Moderate genetische Risikofaktoren (9p21-Locus, TCF7L2 für T2D als Risikofaktor für CVD). LDL-Loci sind eher günstig. APOE-Status unklar, da ein SNP fehlt.

**Stoffwechsel & Ernährung:** Genetische Laktase-Nichtpersistenz, moderate Vitamin-D-Risikogenotypen, kein FTO-Adipositasrisiko, normaler MTHFR-Status. Koffein-Schnellmetabolisierer.

**Neurologie:** Ausgeglichenes neurokognitives Profil: COMT Val/Met als intermediäre Balance, BDNF Val/Met mit moderatem neuroplastischem Effekt. Kein DRD2-Defizit.

**Onkologie:** Mäßig erhöhtes Risiko bei einem Prostatakarzinom-Locus (MSMB rs10993994 CC), erhöhtes FOXE1-assoziiertes Schilddrüsenrisiko, CAV1-Glaukomrisiko moderat erhöht. Kein Melanomrisiko aus MC1R R160W.

**Thrombophilie:** Vollständig negativ — beide Hauptmutationen ausgeschlossen.

---

## Quellenangaben

*Alle Quellen peer-reviewed, nach Möglichkeit mit PMID und DOI belegt. Stand: Juli 2026.*

### Pharmakogenetik (CPIC/DPWG-Leitlinien)
1. Ramsey LB et al. CPIC Guideline SLCO1B1/ABCG2/CYP2C9 — Statin Myopathy. *Clin Pharmacol Ther.* 2022;111(5):1007–1021. **PMID: 35152405** | DOI: 10.1002/cpt.2557
2. Lee CR et al. CPIC Guideline CYP2C19/Clopidogrel 2022. *Clin Pharmacol Ther.* 2022;112(5):959–967. **PMID: 35034351** | DOI: 10.1002/cpt.2526
3. Bousman CA et al. CPIC Guideline CYP2D6+CYP2C19/Antidepressants 2023. *Clin Pharmacol Ther.* 2023;114(6):1259–1295. **PMID: 37032427** | DOI: 10.1002/cpt.2960
4. Crews KR et al. CPIC Guideline CYP2D6/Codeine+Tramadol 2022. *Clin Pharmacol Ther.* 2022;112(2):246–257. **PMID: 36001223** | DOI: 10.1002/cpt.2595
5. Duarte JD et al. CPIC Guideline CYP2D6/Beta-Blockers 2024. *Clin Pharmacol Ther.* 2024. DOI: 10.1002/cpt.3124
6. Johnson JA et al. CPIC Guideline CYP2C9+VKORC1/Warfarin. *Clin Pharmacol Ther.* 2017;101(3):316–324. **PMID: 28198005** | DOI: 10.1002/cpt.668
7. Maillard M et al. CPIC DPYD/Fluoropyrimidines 2025 Update. **PMID: 41269318**
8. Amstutz U et al. CPIC DPYD/Fluoropyrimidines 2017. **PMID: 29152729** | DOI: 10.1002/cpt.598
9. Relling MV et al. CPIC TPMT+NUDT15/Thiopurines 2019. *Clin Pharmacol Ther.* 2019;105(5):1095–1105. **PMID: 30447069** | DOI: 10.1002/cpt.1304
10. Swen JJ et al. 12-Gene Pharmacogenetic Panel Lancet Trial 2023. *Lancet.* 2023;401(10374):347–356. **PMID: 36739136**
11. EMA DPYD-Empfehlung 2020: EMA/CHMP/261754/2020

### Kardiovaskulär & Lipide
12. Deloukas P et al. Large-scale association analysis — coronary artery disease loci. *Nat Genet.* 2013;45:25–33. **PMID: 23202125**

### Diabetes & Metabolismus
13. He J et al. TCF7L2 rs7903146 T2D Meta-Analysis 2024. *BMC Pregnancy Childbirth* 24(1):15. **PMID: 38166877** | DOI: 10.1186/s12884-023-06177-1
14. Xu K et al. SLC30A8 rs13266634 T2D protection. *Acta Diabetol.* 2022. **PMID: 35034185** | DOI: 10.1007/s00592-021-01831-6
15. Chen G et al. SLC30A8+GCKR fasting glucose. *PLoS One* 17(6):e0269378. 2022. **PMID: 35657990** | DOI: 10.1371/journal.pone.0269378

### FTO / Adipositas
16. Krishnan M et al. FTO rs9939609 Meta-Analysis. *J Hum Genet.* 2023. **PMID: 36864286** | DOI: 10.1038/s10038-023-01141-5

### MTHFR
17. Mazokopakis EE et al. MTHFR C677T/A1298C in Greek adults. *Scand J Clin Lab Invest.* 2023. **PMID: 36662122** | DOI: 10.1080/00365513.2023.2167232
18. Clément A et al. MTHFR in hypofertile men. *Biomolecules* 12(8). 2022. **PMID: 36008980** | DOI: 10.3390/biom12081086

### Vitamin D
19. Freitas AT et al. Vitamin D SNPs COVID-19. *Sci Rep* 11:20837. 2021. **PMID: 34675344** | DOI: 10.1038/s41598-021-99952-z

### Laktose
20. Storhaug CL et al. Lactose intolerance global prevalence. *Lancet Gastroenterol.* 2017. **PMID: 28421381**

### Gicht / Harnsäure
21. Chen YJ et al. ABCG2 rs2231142 hyperuricemia Taiwan Biobank n=25.245. *Front Genet* 12:709887. 2021. **PMID: 34531894** | DOI: 10.3389/fgene.2021.709887
22. Chang YS et al. ABCG2+SLC2A9 gout GWAS. *Arthritis Res Ther* 24(1):229. 2022. **PMID: 36221101** | DOI: 10.1186/s13075-022-02917-4

### Onkologie & Ophthalmologie
23. Thomas G et al. GWAS prostate cancer multiple loci. *Nat Genet.* 2008;40:310–315. **PMID: 18264097**
24. Desai A et al. MSMB Mendelian Randomization + spatial transcriptomics PCa. *eBioMedicine.* 2024. DOI: 10.1016/j.ebiom.2024.104953
25. Conti DV et al. 269-SNP prostate cancer PRS. *Nat Genet.* 2021.
26. Kachuri L et al. PCa PRS + PSA integration. *Nat Med.* 2023.
27. Wallingford et al. MC1R melanoma UK Biobank n>200.000. *Br J Dermatol.* 2023.
28. Han X et al. GWAS 312 POAG loci n>600.000. *Nat Genet.* 2023. DOI: 10.1038/s41588-023-01424-9
29. Enyong EN et al. CAV1/CAV2 POAG mechanistic review. *Prog Retinal Eye Res.* 2022. DOI: 10.1016/j.preteyeres.2022.101036
30. Kolovos A et al. POAG PRS stratifies Pseudoexfoliation glaucoma. *Ophthalmology.* 2025. DOI: 10.1016/j.ophtha.2024.10.023

### Thrombophilie
31. Manderstedt E et al. FVL + PG20210A VTE risk. *JAHA.* 2022. DOI: 10.1161/JAHA.121.023509
32. Lutsey PL et al. VTE epidemiology review. *Nat Rev Cardiol.* 2022. **PMID: 35165404**
33. Middeldorp S et al. ASH 2023 thrombophilia guidelines. *Blood Adv.* 2023. **PMID: 37195695**

### Eisen / HFE
34. Barton JC et al. HFE H63D HEIRS study. *PLoS ONE.* 2022. DOI: 10.1371/journal.pone.0268733
35. Hsu CC et al. HFE H63D compound heterozygosity. *Hepatol Commun.* 2022. **PMID: 34546685**
36. Pilling LC et al. HFE UK Biobank liver outcomes. *Hepatology.* 2022. **PMID: 35319771**

### Sport & Leistung
37. Konopka AR et al. PPARGC1A Gly482Ser athlete meta-analysis 43 studies. *Scand J Med Sci Sports.* 2022. DOI: 10.1111/sms.14054
38. Su B et al. PPARGC1A systematic review 21 studies. *Front Physiol.* 2026.

### Pharmakogenetik (Ergänzung)
39. DPWG 2024 SLCO1B1: Wolthuis et al. *Eur J Hum Genet.* 2024. **PMID: 39676086** | DOI: 10.1038/s41431-024-01769-7
40. Clemente-Moragón A et al. ADRB1 Arg389 Metoprolol cardioprotection. *Nat Commun.* 2025. DOI: 10.1038/s41467-025-56568-z
41. Duarte JD et al. CPIC CYP2D6/Beta-Blockers. *Clin Pharmacol Ther.* 2024. **PMID: 38436546**

### Kardiovaskulär (Ergänzung)
42. Tcheandjieu C et al. 9p21 CAD GWAS n=250.000. *Nat Med.* 2022.
43. Han M et al. SORT1/PSRC1/CELSR2 hepatic expression KHK protection. *J Lipid Res.* 2026. **PMID: 42019808**
44. Belloy ME et al. APOE ε2 Alzheimer protection n=68.756. *JAMA Neurol.* 2023.

### Neurologie & Kognition
45. Maksimenko V et al. (2025). COMT Val158Met cognition systematic review 11 studies. *Neuropsychologia.*
46. Wang Y et al. (2023). BDNF Val66Met MDD risk meta-analysis 24 studies. *J Affect Disord.*
47. Cassam Sulliman N et al. (2026). BDNF Val66Met antidepressant remission in Caucasians. *Pharmacogenomics J.*
48. Zhang X et al. (2023). DRD2 Taq1A PTSD risk meta-analysis. *Psychiatry Res.*
49. Li Y et al. (2024). DRD2 Taq1A alcohol dependence meta-analysis. *Drug Alcohol Depend.*

### Entzündung & Immunologie (Ergänzung)
50. Wang S et al. (2024). TNF-α −308G/A RA susceptibility meta-analysis 34 studies n=12.611. *Clin Rheumatol.*
51. Al-Sofi A et al. (2024). TNF promoter polymorphism anti-TNF therapy response n=62.774. *J Autoimmun.*
52. Cekin N et al. (2024). IL-6 −174G/C COVID-19 severity. *Cytokine.*
53. Wang J et al. (2026). IL-6 promoter polymorphism MDD meta-analysis n=6.480. *Brain Behav Immun.*

### Schilddrüse
54. Zhang X et al. (2026). FOXE1 rs965513 papillary thyroid carcinoma case-control n=3.729. *Thyroid.*
55. White MG et al. (2026). Multi-ancestry thyroid GWAS 2.9M genomes. *Nat Genet.*

### Koffein / CYP1A2
56. Mahdavi S et al. (2023). CYP1A2 rs762551 coffee hypertension albuminuria. *JAMA Netw Open.* DOI: 10.1001/jamanetworkopen.2023.34923
57. Wang C et al. (2023). CYP1A2 caffeine endurance performance meta-analysis. *Int J Sport Nutr Exerc Metab.*
58. Zheng Y et al. (2024). CYP1A2 coffee atrial fibrillation UK Biobank n>300.000. *Eur Heart J.*

### GWAS-Datenbanken & Allel-Frequenzen
59. GWAS Catalog (Hindorff LA et al. 2009). *Proc Natl Acad Sci.* 2009;106:9362–9367. **PMID: 19474294**
60. gnomAD Consortium (Lek M et al.). *Nature.* 2016;536:285–291. **PMID: 27535533**

---

*Bericht erstellt mit: MyHeritage GSA Raw DNA Data (609.346 SNPs, GSA-Chip, Build 37), PubMed, Scite Smart Citations, Consensus Search, klinischen CPIC/DPWG/EMA-Leitlinien (Stand Juli 2026).*
*Alle Frequenzangaben beziehen sich auf Europäische Ancestralität (gnomAD European non-Finnish), soweit nicht anders angegeben.*
