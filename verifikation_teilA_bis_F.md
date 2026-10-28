# Verifikationslauf — Genomdatei-Diagnostik & Gegenprüfung

**Quelldatei:** `MyHeritage_raw_dna_data.csv` | **Kein Interpretationsanteil — reine Faktenprüfung.**
**Werkzeug-Einschränkung (gilt für den gesamten Bericht):** Direkter `curl`-Netzwerkzugriff auf externe Domains ist durch die Org-Egress-Policy dieser Session blockiert (bestätigt: `rest.ensembl.org` → 403 policy denial). NCBI dbSNP und SNPedia blocken Bot-Zugriffe auch über das WebFetch-Tool (403). Verfügbar war ausschließlich **WebSearch** (Suchmaschinen-Snippets, keine direkten DB-Abfragen). Wo das die Verifikationstiefe einschränkt, ist das explizit vermerkt — es wurde nichts geraten oder stillschweigend ergänzt.

---

## TEIL A — Dateidiagnostik

| Frage | Befund |
|---|---|
| Dateiname | `MyHeritage_raw_dna_data.csv` |
| Dateigröße | 20.339.959 Bytes (≈ 19,4 MB) |
| Format | MyHeritage Raw DNA Export, `##format=MHv1.0` |
| Chip | `##chip=GSA` (Illumina Global Screening Array). Keine spezifische Sub-Version (v1/v2/v3) im Header erkennbar. |
| Genome Build | **GRCh37/hg19**, explizit im Header: `##reference=build37`. **Beleg an bekanntem Marker:** rs4988235 (LCT/MCM6) steht in der Datei bei `chr2:136.608.646`. Das ist die kanonische **GRCh37**-Position dieses SNPs (GRCh38 wäre `chr2:135.851.076` — eine eindeutig unterscheidbare, ~757.000 bp abweichende Koordinate). Damit ist Build 37 nicht nur behauptet, sondern anhand einer bekannten Positionsdifferenz bestätigt. |
| Gesamtzahl Marker | 609.346 (Datenzeilen, ohne 13 Header-/Kommentarzeilen) |
| No-Calls gesamt (`--`) | 1.516 |
| Weitere No-Call-Formate geprüft | Keine `00`/`NN`/`0`-Tokens im gesamten Genotyp-Vokabular gefunden (siehe Tokenliste unten) — `--` ist das einzige No-Call-Format dieser Datei. |
| Enthält die Datei INDELs? | **Ja.** Genotyp-Vokabular enthält neben den 10 SNP-Kombinationen (AA/CC/GG/TT/AG/CT/AC/GT/CG/AT) auch INDEL-Codes: `II` (593×), `DD` (185×), `DI` (1×) — insgesamt 779 Marker. **Alle 779 liegen ausschließlich auf X (769) und Y (10)** — keine Autosomen betroffen. |
| Marker pro Chromosom | siehe Tabelle unten |
| Sortierprüfung | Datei ist durchgängig nach Chromosom, dann Position aufsteigend sortiert — 0 Anomalien über alle 609.346 Zeilen. |

### Marker pro Chromosom (inkl. X, Y)

| Chr | Marker | No-Calls | Chr | Marker | No-Calls |
|---|---|---|---|---|---|
| 1 | 45.474 | 80 | 13 | 19.151 | 36 |
| 2 | 46.458 | 89 | 14 | 17.039 | 39 |
| 3 | 42.459 | 60 | 15 | 16.628 | 32 |
| 4 | 39.531 | 92 | 16 | 17.922 | 44 |
| 5 | 37.674 | 61 | 17 | 16.330 | 31 |
| 6 | 43.616 | 100 | 18 | 15.863 | 39 |
| 7 | 34.228 | 101 | 19 | 12.924 | 43 |
| 8 | 31.914 | 60 | 20 | 13.508 | 26 |
| 9 | 21.832 | 37 | 21 | 7.742 | 19 |
| 10 | 30.755 | 67 | 22 | 8.397 | 28 |
| 11 | 30.252 | 73 | X | 29.694 | 248 |
| 12 | 26.460 | 47 | Y | 3.495 | 64 |

**MT (mitochondrial):** Keine MT-Marker in dieser Datei — die Chromosomwerte umfassen ausschließlich 1–22, X, Y. Kein `MT`/`26`/`M`-Token gefunden.

**Genotyp-Token-Vokabular (vollständig, mit Häufigkeit):**
`CC` 143.118 · `GG` 142.630 · `AA` 107.676 · `TT` 107.598 · `AG` 42.855 · `CT` 42.793 · `AC` 9.809 · `GT` 9.775 · `--` 1.516 (No-Call) · `II` 593 · `CG` 506 · `AT` 291 · `DD` 185 · `DI` 1

---

## TEIL B — Positionsbasierte Gegenprüfung der gefundenen Marker

**Methodik-Hinweis:** Für alle 62 "gefunden"-Marker wurde geprüft, ob das gemeldete Chromosom mit dem Standard-Genort des ursprünglich zugewiesenen Gen-Labels übereinstimmt. Für **4 Fälle** ergab sich ein Konflikt oder eine Unsicherheit, die einzeln über WebSearch gegen unabhängige Quellen geprüft wurde. Die übrigen 58 Marker sind auf Chromosomenebene konsistent, wurden aber **nicht** einzeln per Live-Datenbankabfrage auf exakte Gen-Grenzen re-verifiziert (Tool-Einschränkung s.o.) — das wird hier transparent gemacht, nicht verschwiegen.

### Die drei explizit angefragten Fälle

| rsID | Gemeldete Position (Datei) | Ursprüngliches Label | Tatsächlicher Befund | annotation_konflikt |
|---|---|---|---|---|
| **rs17277546** | chr7:99.489.571 | SULT2A1 | **Falsch.** SULT2A1 liegt auf chr19. Die Position chr7:99.489.571 liegt im **ZKSCAN5/TTC26-Locus (chr7q22)** — derselben Region wie rs11761528 (ZKSCAN5) und rs740160 (TRIM4) aus dem DHEA-S-GWAS-Loci-Block. rs17277546 ist ein bekannter DHEA-S-assoziierter Marker in dieser Region, aber nicht SULT2A1-Genkörper. Quelle: WebSearch (GWAS Catalog/EBI-Kontext, Publikation zu SULT2A1-Expression). | **ja** |
| **rs2547231** | chr19:48.385.057 | PAPSS2 | **Falsch.** PAPSS2 liegt auf chr10. Die Position chr19:48.385.057 liegt **~12 kb downstream von SULT2A1** (chr19) — bestätigt durch einen PMC-Artikel, der rs2547231 explizit als SULT2A1-Expressions-QTL beschreibt, in LD mit rs2637125 (r²=0,658). Das Label hätte "SULT2A1" statt "PAPSS2" lauten müssen. | **ja** |
| **rs2637125** | chr19:48.401.893 | ARPC1A/SULT2A1-Region | **Kein Konflikt.** Position liegt im selben SULT2A1-Locus (chr19q13.3, Genkörper beginnt laut NCBI bei ~47.886.315). Web-Quelle bestätigt rs2637125 als das am stärksten assoziierte SNP dieser DHEA-S-Region. Label korrekt. | nein |

**Korrigierte Zuordnung für diesen Block:** rs17277546 sollte als "ZKSCAN5/TTC26-Locus (chr7q22, DHEA-S-GWAS)" geführt werden, nicht als SULT2A1. rs2547231 sollte als "SULT2A1 (downstream)" geführt werden, nicht als PAPSS2.

### Zusätzlich gefundener Konflikt (nicht ursprünglich angefragt)

| rsID | Gemeldete Position | Label | Befund | annotation_konflikt |
|---|---|---|---|---|
| **rs11064477** | chr12:7.074.365 | HSD17B12 | HSD17B12 liegt laut NCBI Gene / GeneCards bei **11p11.2 (chr11)**, nicht chr12. Die Datei meldet chr12:7.074.365 — welches Gen tatsächlich an dieser chr12-Position liegt, konnte mit den verfügbaren Tools **nicht identifiziert werden**. Es wird nicht geraten. | **ja** |

### Korrektur eines eigenen Fehlers aus dem ersten Lauf (kritisch)

**rs2208532 (SRD5A3):** Im ersten Chat-Turn wurde dieser Marker fälschlich als **"gefunden"** mit Genotyp `AG` bei chr4:56.230.287 ausgegeben. Bei der jetzigen Direktprüfung:
- `grep '"rs2208532"'` gegen die Rohdatei → **0 Treffer**.
- Die tatsächlich gespeicherte `hormone_snps.csv` (nicht die Chat-Textausgabe) hatte bereits korrekt `nicht_auf_chip` vermerkt — **der Fehler betraf ausschließlich die Chat-Textausgabe im ersten Turn, nicht die Datei.**
- Region-Scan über die komplette SRD5A3-Genspanne (chr4:56.212.409–56.239.267, NCBI Gene) mit 9 vorhandenen Markern bestätigt: kein Marker unter irgendeiner ID an dieser Position.

**Konsequenz:** Diese Verifikation zeigt exemplarisch, warum eine unabhängige Gegenprüfung sinnvoll ist — die Chat-Ausgabe allein war an dieser Stelle nicht verlässlich, die gespeicherte Datei war es.

---

## TEIL C — Sind die 52 Ausfälle echt?

### Globaler Befund (gilt für alle 48 eindeutigen fehlenden rsIDs gleichzeitig)

1. **Grep-Test (case-insensitive, mit/ohne "rs"-Präfix):** Alle 48 eindeutigen fehlenden rsIDs wurden gegen die komplette Rohdatei geprüft (`grep -i`, quotierte Form, numerische Form ohne Präfix). **Ergebnis: 0 Treffer für jede einzelne ID, in jeder geprüften Schreibweise.**
2. **dbSNP-Merge-Historie:** **Nicht prüfbar mit den verfügbaren Mitteln.** Ich habe keinen funktionierenden Zugriff auf die dbSNP-Merge-Tabelle (NCBI dbSNP blockt WebFetch mit 403, Live-API über Bash-curl ist durch Org-Policy blockiert). Das wird hier explizit als offene Lücke benannt, statt eine Vermutung zu äußern.
3. **Interne/alternative IDs (i-IDs, kgp-IDs) im Chip-Format:** Die gesamte Datei wurde durchsucht — **0 von 609.346 Zeilen** verwenden ein anderes ID-Format als `rsXXXXXX`. Es gibt in dieser MyHeritage-GSA-Exportdatei **keine einzige** interne/proprietäre ID. Der vom Nutzer vermutete häufigste Fehlerursache ("Chip führt Position unter i-ID statt rsID") **entfällt damit strukturell für diese gesamte Datei** — nicht nur für die 52 Ausfälle, sondern für alle 609.346 Marker.

### Positionsbasierte Tiefenprüfung der 14 priorisierten "unplausiblen" Ausfälle

| rsID | grep_treffer | alternative_id_an_position | echter_ausfall |
|---|---|---|---|
| rs6152 | 0 | Keine. Position chrX:66.765.627 (GRCh37, per WebSearch/SNPedia-Kontext) liegt zwischen zwei vorhandenen Markern (rs137852590 @66.765.509, rs148972137 @66.765.802) — kein Marker exakt auf der rs6152-Position, obwohl die Region dicht mit anderen AR-Markern belegt ist. | **ja (hohe Konfidenz)** |
| rs1799941 | 0 | Nicht abschließend prüfbar — exakte GRCh37-bp-Position über verfügbare Tools nicht ermittelbar. Das vom Nutzer vorgegebene SHBG-Fenster (17:7.517.000–7.541.000) deckt vermutlich nicht den SHBG-Promotorbereich ab, in dem dieser Marker liegt (Literatur beschreibt ihn 8bp upstream des Transkriptionsstarts). | wahrscheinlich ja (grep-bestätigt, Position unklar) |
| rs6259 | 0 | Nicht abschließend prüfbar — exakte GRCh37-Position nicht ermittelbar. | wahrscheinlich ja (grep-bestätigt, Position unklar) |
| rs523349 | 0 | Keine. Vollständige SRD5A2-Genspanne (chr2:31.388.766–31.834.506 lt. Atlas Genetics Oncology) mit 105 vorhandenen Markern im Kernbereich (31.522.000–31.806.000) dicht gescannt — kein Treffer. | **ja (hohe Konfidenz)** |
| rs9282858 | 0 | Keine — dieselbe SRD5A2-Abdeckung wie oben. | **ja (hohe Konfidenz)** |
| rs248793 | 0 | Keine. SRD5A1-Region (chr5:6.630.000–6.694.000) mit 18 Markern gescannt, kein Treffer. | ja (mittel-hohe Konfidenz — exakte Genspanne nicht per Primärquelle re-bestätigt) |
| rs3822430 | 0 | Keine — dieselbe SRD5A1-Region. | ja (mittel-hohe Konfidenz) |
| rs166050 | 0 | Keine — dieselbe SRD5A1-Region. | ja (mittel-hohe Konfidenz) |
| rs2208532 | 0 | Keine. SRD5A3-Genspanne (chr4:56.212.409–56.239.267, NCBI Gene) mit 9 Markern gescannt, kein Treffer. **Siehe auch Korrektur oben — im ersten Chat-Turn fälschlich als gefunden gemeldet.** | **ja (hohe Konfidenz)** |
| rs41423247 | 0 | Keine. NR3C1-Region (chr5:142.657.000–142.815.000) mit 37 Markern gescannt, kein Treffer. | **ja (hohe Konfidenz)** |
| rs1047303 | 0 | Keine. HSD3B1/HSD3B2-Region (chr1:119.957.000–120.060.000) mit 22 Markern gescannt, kein Treffer. | **ja (hohe Konfidenz)** |
| rs12861525 | 0 | Keine. STS-Region (chrX:7.137.000–7.288.000) mit 15 Markern gescannt, kein Treffer. | **ja (hohe Konfidenz)** |
| rs7741 | 0 | Keine. AKR1C-Cluster (chr10:5.050.000–5.350.000) mit 86 Markern **sehr dicht** gescannt, kein Treffer. | **ja (hohe Konfidenz)** |
| rs9470080 | 0 | Keine. FKBP5-Region (chr6:35.400.000–35.750.000) mit 79 Markern **sehr dicht** gescannt, kein Treffer. | **ja (hohe Konfidenz)** |

### Die übrigen 34 nicht-priorisierten Ausfälle

Für diese wurde **nur** der Grep-Test durchgeführt (0/34 Treffer, ebenfalls case-insensitive und ohne Präfix) — keine individuelle Regions-Scan-Tiefenprüfung, da außerhalb der vom Nutzer priorisierten Liste. Der globale Befund "0 Nicht-rs-IDs in der gesamten Datei" (s.o.) reduziert aber auch hier die Wahrscheinlichkeit eines Alternative-ID-Artefakts strukturell auf praktisch null.

---

## TEIL D — Regionale Abdeckung (positionsbasiert, unabhängig von rsID-Liste)

| Region | Intervall (GRCh37) | Anzahl Marker gefunden |
|---|---|---|
| SHBG | chr17:7.517.000–7.541.000 | **5** (rs12150660, rs117642538, rs13894, rs6258, rs727428) |
| AR | chrX:66.760.000–66.951.000 | **81** (weit überwiegend seltene ClinVar-/Pathogenitäts-Sonden, z.B. rs137852xxx-Serie) |
| SRD5A1 | chr5:6.630.000–6.694.000 | **18** |
| SRD5A2 | chr2:31.522.000–31.806.000 | **105** |
| HSD3B1/HSD3B2 | chr1:119.957.000–120.060.000 | **22** |
| NR3C1 | chr5:142.657.000–142.815.000 | **37** |
| STS | chrX:7.137.000–7.288.000 | **15** |
| GABRD | chr1:1.950.000–1.963.000 | **2** (rs139300921, rs16824627) |
| UGT2B15/17 | chr4:69.400.000–69.560.000 | **75** |
| CYP19A1 | chr15:51.500.000–51.630.000 | **52** |

*(Vollständige Marker-Listen mit rsID/Position/Genotyp je Region wurden im Zuge dieser Prüfung erzeugt und liegen den obigen Teil-B/C-Befunden zugrunde; auf Wunsch als separate Datei exportierbar.)*

Alle 10 Regionen liegen laut Header in **GRCh37** — kein Liftover nötig, da Datei-Build mit den vom Nutzer angegebenen (GRCh37-)Koordinaten übereinstimmt.

---

## TEIL E — Qualitätsflags

### 1. Palindromische SNPs unter den gefundenen Markern

Palindromizität ist **nur bei heterozygoten Calls direkt aus den Rohdaten ablesbar** (das Allelpaar ist sichtbar). Bei homozygoten Calls ist das zweite (nicht beobachtete) Allel aus den Rohdaten nicht bestimmbar — hierzu wurde **nichts geraten**.

| rsID | Gen | Genotyp | Palindromisch |
|---|---|---|---|
| **rs12529** | AKR1C3 | CG | **JA** (C/G) — wie vom Nutzer vermutet |
| **rs1937840** | AKR1C3 | CG | **JA** (C/G) — wie vom Nutzer vermutet |
| **rs2070951** | NR3C2 | CG | **JA** (C/G) — zusätzlich gefunden, nicht ursprünglich genannt |

Alle übrigen heterozygoten Marker (rs9340799, rs4986938, rs10835638, rs6166, rs2293275, rs6280, rs4680, rs2547231, rs1042838, rs471767, rs3219151, rs1799998, rs5522, rs1360780, rs3800373) zeigen nicht-palindromische Allelpaare (A/G, C/T, A/C oder G/T) — kein Strang-Ambiguitätsproblem.

47 der 62 gefundenen Marker sind homozygot; für diese ist eine Palindrom-Prüfung aus den vorliegenden Rohdaten **nicht möglich**.

### 2. X-Chromosom-Kodierung

**Drei Rohzeilen im Originalformat:**
```
"rs60233760","X","2699898","DI"
"rs2306737","X","2699968","AG"
"rs5939319","X","2700157","GG"
```

**Befund:** Alle 29.446 X-Chromosom-Marker (100 %) haben einen **zweistelligen** Genotyp-String — es gibt **keinen einzigen echten Ein-Buchstaben-Hemizygot-Call** in der gesamten Datei. Der Chip/die MyHeritage-Pipeline kodiert X-Marker bei männlichen Proben durchgängig als pseudo-diploiden Doppel-Call (z.B. `GG` statt `G`). Das gilt auch für rs1204038, rs2361634 und rs5934505 aus der Hormonliste.

**Y-Chromosom-Plausibilitätscheck:** 3.495 Y-Marker vorhanden, davon **3.431 gecallt** (98,2 %), nur 64 No-Calls. Beispiele: rs201588461 (CC), rs11575897 (GG), rs104894965 (CC), rs2534636 (CC), rs1800865 (GG) — durchgängig positive Calls. Ein Y-Chromosom mit so hoher Call-Rate ist mit einer männlichen Probe konsistent (bei einer weiblichen Probe wären Y-Marker überwiegend No-Call).

### 3. Zusammenhängende No-Call-Blöcke (≥5 aufeinanderfolgend)

**Ergebnis: 0 Blöcke.** Über alle 609.346 Zeilen in Dateireihenfolge (= Positions-sortiert) gibt es **keinen einzigen** Lauf von 5 oder mehr aufeinanderfolgenden No-Calls — auch nicht in den Regionen STS (Xp22.31) oder UGT2B17 (chr4). Alle 1.516 No-Calls in der Datei sind isoliert verteilt. Das ist ein reines Faktum aus der Datenstruktur — es liefert **keinen** Hinweis auf eine größere Deletion in diesen Regionen, da GSA-Array-Daten ohnehin keine Coverage-basierte CNV-Erkennung ermöglichen (dafür wären Bewertungen der Signalintensität nötig, die in dieser Textdatei nicht enthalten sind).

### 4. Heterozygotenrate

- Homozygote SNP-Calls: 501.022
- Heterozygote SNP-Calls: 106.029
- **Heterozygotenrate: 17,47 %** (heterozygot / [heterozygot+homozygot], ohne No-Calls und Indels)

**Faktischer Befund:** Das liegt **deutlich unter** dem von Ihnen genannten Referenzbereich von ~30–35 %. Das ist keine Interpretation, sondern ein reines Zahlenfaktum aus der Datei. Ein möglicher struktureller Grund (Faktum über Chip-Design, keine gesundheitliche Bewertung): GSA-Arrays enthalten neben häufigen Populations-SNPs auch einen hohen Anteil klinischer/ClinVar-Marker mit sehr niedriger Populations-Allelfrequenz (in dieser Region z.B. die vielen `rs137852xxx`-Einträge im AR-Bereich), was den Gesamt-Heterozygotie-Schnitt gegenüber älteren, rein auf häufige SNPs optimierten Ancestry-Chips senkt. Dies wird als Fakt zur Chip-Zusammensetzung berichtet, nicht als gesundheitliche Einschätzung der Probe.

---

## TEIL F — AR CAG-Repeat

| Frage | Antwort |
|---|---|
| Enthält die Datei Sequenzreads (FASTQ/BAM/CRAM)? | **Nein.** Die Datei enthält ausschließlich Genotyp-Calls im Format `RSID,CHROMOSOME,POSITION,RESULT` (Array-basierte SNP-Calls, keine Sequenzdaten). |
| Ist die AR-CAG-Repeatlänge aus dieser Datei bestimmbar? | **Nein — bestätigt.** Array-Genotyp-Daten können repetitive Trinukleotid-Repeat-Längen (CAG-Repeat in AR Exon 1) grundsätzlich nicht auflösen, da SNP-Arrays einzelne Basenpositionen abfragen und keine Repeat-Struktur oder -Länge messen. Es wurde **keine Schätzung** vorgenommen und **keine Proxy-Konstruktion** aus benachbarten SNPs versucht (wie explizit gefordert). Status: **nicht_bestimmbar.** |
| Coverage-Angabe für chrX:66.764.000–66.766.000? | Entfällt — keine Reads vorhanden, daher keine Coverage-Berechnung möglich. |

---

## Zusammenfassung

- **Dateidiagnostik:** GRCh37 bestätigt (nicht nur behauptet), 609.346 Marker, 1.516 No-Calls, 779 INDEL-Marker (nur X/Y), keine MT-Daten.
- **Gen-Annotation:** 4 von 62 gefundenen Markern hatten ein fehlerhaftes oder unsicheres Gen-Label (rs17277546, rs2547231, rs11064477, rs2208532) — Details und Korrekturen oben. **rs2208532 war zusätzlich ein Fehler in meiner eigenen ersten Chat-Ausgabe (nicht in der gespeicherten Datei).**
- **Ausfälle:** Alle 14 priorisierten "unplausiblen" Ausfälle wurden gegen echte Genregionen geprüft — **kein einziger** erwies sich als Artefakt einer internen/alternativen ID (die Datei enthält global keine solchen IDs). Sie sind nach aktuellem Prüfstand echte Lücken auf diesem Chip.
- **Nicht abschließend klärbar:** dbSNP-Merge-Historie (kein funktionierender Datenbankzugriff in dieser Session); exakte GRCh37-Position für rs1799941 und rs6259.

**Von 52 ursprünglichen Ausfällen sind 0 unter alternativer ID doch vorhanden.**
