# Mathias Cashflow- & Rechts-Agent

Werkzeug zur Rechtsprüfung und Cashflow-Berechnung für die konkrete Konstellation
volle EM-Rente + Nebenjob (Übergangsbereich, Split-Schichten) + Persönliches
Budget (Arbeitgebermodell) + BAföG (elternabhängig).

## Architektur

- **`eingabedaten.py`** – Rohdaten-Schemas (Versicherungsverlauf, Stammdaten,
  Arbeitsvertrag, BAföG-Formblätter, Persönliches Budget). Diese Werte kommen
  aus echten Dokumenten/Bescheiden, nicht aus Schätzungen.
- **`berechnungen.py`** – deterministische Formeln (EM-Rente aus Entgeltpunkten
  + Zurechnungszeit, Übergangsbereich-Netto nach § 20 SGB IV, BAföG-Freibetragsrechnung,
  Persönliches-Budget-Wert). Jede Formel nimmt die benötigten statutarischen
  Konstanten explizit als Parameter entgegen – nichts wird im Code fest geraten.
- **`rechtscheck.py`** – rechtliche Vorprüfungen (z.B. ist "volle EM + 12 Std/Woche
  in Split-Schichten" zulässig?), jede mit Status, Begründung und Rechtsgrundlage.
- **`connectors.py`** – Recherche-Schnittstelle: sammelt offene Fragen
  (`RechercheAuftrag`) und nimmt quellenbelegte Antworten (`RechercheErgebnis`)
  entgegen.
- **`agent.py`** – Orchestrator (`MathiasAgent`), erzeugt den Bericht im
  Pflichtformat (1. Rechtliche Einschätzung, 2. Geschätzte Beträge,
  3. Cashflow-Szenarien, 4. Priorisierte Handlungspfade).
- **`beispiel_lauf.py`** – Beispiel mit den aktuell (Stand 01.08.2026) live
  recherchierten Konstanten, siehe Quellenangaben darin.

## Warum keine eingebettete Live-API?

"Legal Data Hunter" (Gesetze/Rechtsprechung, 230+ Jurisdiktionen) und Web-Suche
sind MCP-Tools, die nur innerhalb einer Agent-/Tool-Use-Runtime (z.B. Claude
Code) zur Verfügung stehen – keine öffentlichen REST-APIs, die dieses Skript
selbst aufrufen könnte. Der Ablauf ist deshalb zweistufig:

1. `MathiasAgent.recherche_bedarf(eingaben, konstanten)` liefert eine Liste
   offener Fragen (`RechercheAuftrag`), z.B. "aktueller Rentenwert",
   "aktuelle Hinzuverdienstgrenze", "LVR-Marktsatz Persönliches Budget".
2. Der aufrufende Agent recherchiert diese Fragen live (Legal Data Hunter für
   Gesetzestexte/Rechtsprechung, WebSearch für aktuelle Zahlen/Sätze) und
   übergibt die Antworten als `Dict[str, RechercheErgebnis]` an
   `MathiasAgent.bericht(eingaben, konstanten, rechercheergebnisse)`.

So bleiben alle Zahlen nachvollziehbar und quellenbelegt statt erfunden.

## Nutzung

```bash
python3 agent.py          # zeigt offene Rechercheaufträge + Struktur-Check ohne Live-Daten
python3 beispiel_lauf.py  # vollständiger Bericht mit aktuell recherchierten Konstanten
```

Für einen eigenen Lauf: `Eingaben` mit den echten Dokumentdaten befüllen
(Versicherungsverlauf, Arbeitsvertrag, BAföG-Formblätter, Budget-Bewilligung),
`agent.recherche_bedarf(...)` aufrufen, offene Fragen recherchieren lassen,
Ergebnisse als `RechercheErgebnis` sammeln und `agent.bericht(...)` aufrufen.

## Welche Dokumente werden noch gebraucht?

- Vollständiger **Versicherungsverlauf** (Entgeltpunkte pro Zeitabschnitt) für
  eine belastbare EM-Renten-Schätzung.
- **EM-Rentenbescheid**, sobald vorhanden, zur Kalibrierung/Verifikation der
  Schätzung.
- **Arbeitsvertrag** mit exakten Schichtplänen.
- **BAföG-Formblätter 03/07** + Steuerbescheid der Eltern.
- **Bewilligungsbescheid Persönliches Budget** mit dem tatsächlich vom LVR
  festgelegten Stundensatz.

## Hinweis

Keine Rechtsberatung – datenbasierte Einschätzung zur Vorbereitung eines
Gesprächs mit DRV, BAföG-Amt, LVR bzw. einer Rechtsberatung.
