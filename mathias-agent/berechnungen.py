"""Deterministische Berechnungsformeln.

Grundprinzip: Keine Beträge werden pauschal geschätzt. Jede Funktion nimmt
die benötigten statutarischen Konstanten (Rentenwert, Beitragssätze,
Freibeträge, Stundensätze ...) als explizite Parameter entgegen. Ist eine
Konstante nicht bekannt, liefert die aufrufende Stelle (agent.py) sie aus
einem `RechercheErgebnis` (siehe connectors.py) oder die Funktion markiert
das Ergebnis unsicher, statt einen Wert zu erfinden.
"""

from dataclasses import dataclass
from datetime import date
from typing import List, Optional, Tuple

from eingabedaten import Arbeitsvertragsdaten, PersonStammdaten, Versicherungsverlaufseintrag


def _jahre_zwischen(von: date, bis: date) -> float:
    return (bis - von).days / 365.25


# ---------------------------------------------------------------------------
# 1. Erwerbsminderungsrente
# ---------------------------------------------------------------------------

@dataclass
class EMRenteSchaetzung:
    entgeltpunkte_bisher: float
    entgeltpunkte_zurechnungszeit: float
    entgeltpunkte_gesamt_min: float
    entgeltpunkte_gesamt_max: float
    brutto_monat_min: float
    brutto_monat_max: float
    annahmen: List[str]


def entgeltpunkte_aus_verlauf(verlauf: List[Versicherungsverlaufseintrag]) -> Tuple[float, float]:
    """Summiert vorhandene Entgeltpunkte und liefert (bekannt, jahre_mit_beitrag)."""
    ep_summe = 0.0
    beitragsjahre = 0.0
    for eintrag in verlauf:
        dauer = _jahre_zwischen(eintrag.von, eintrag.bis)
        if eintrag.entgeltpunkte is not None:
            ep_summe += eintrag.entgeltpunkte
            if eintrag.art == "Pflichtbeitrag":
                beitragsjahre += dauer
    return ep_summe, beitragsjahre


def schaetze_em_rente(
    stammdaten: PersonStammdaten,
    verlauf: List[Versicherungsverlaufseintrag],
    aktueller_rentenwert: float,
    zurechnungszeit_endalter_jahre: float,
    zugangsfaktor: float = 1.0,
    rentenartfaktor_volle_em: float = 1.0,
    unsicherheit_prozent: float = 0.15,
) -> EMRenteSchaetzung:
    """Schätzt die volle EM-Rente (brutto/Monat) als Bandbreite.

    Formel: monatliche Rente = Entgeltpunkte(gesamt) x Zugangsfaktor
            x Rentenartfaktor x aktueller Rentenwert.
    Entgeltpunkte(gesamt) = EP aus dem bisherigen Verlauf + EP aus der
    Zurechnungszeit (fiktive Beitragszeit vom EM-Beginn bis zum
    gesetzlichen Zurechnungszeit-Endalter, bewertet mit dem
    Durchschnitts-EP/Jahr aus der bisherigen Erwerbsbiografie).
    """
    ep_bisher, beitragsjahre = entgeltpunkte_aus_verlauf(verlauf)
    annahmen = []

    if beitragsjahre > 0:
        durchschnitt_ep_pro_jahr = ep_bisher / beitragsjahre
    else:
        durchschnitt_ep_pro_jahr = 0.0
        annahmen.append(
            "Keine vollständigen Pflichtbeitragszeiten im Verlauf gefunden "
            "-> Durchschnitts-EP/Jahr konnte nicht berechnet werden, Zurechnungszeit-EP = 0."
        )

    alter_bei_em_beginn = _jahre_zwischen(stammdaten.geburtsdatum, stammdaten.em_beginn_medizinisch)
    zurechnungszeit_jahre = max(0.0, zurechnungszeit_endalter_jahre - alter_bei_em_beginn)
    ep_zurechnungszeit = zurechnungszeit_jahre * durchschnitt_ep_pro_jahr

    ep_gesamt = ep_bisher + ep_zurechnungszeit
    ep_min = ep_gesamt * (1 - unsicherheit_prozent)
    ep_max = ep_gesamt * (1 + unsicherheit_prozent)

    brutto_min = ep_min * zugangsfaktor * rentenartfaktor_volle_em * aktueller_rentenwert
    brutto_max = ep_max * zugangsfaktor * rentenartfaktor_volle_em * aktueller_rentenwert

    annahmen.append(
        f"Unsicherheitsspanne von +/-{unsicherheit_prozent:.0%} auf die Entgeltpunkte "
        "angesetzt, da Versicherungsverlauf/EP-Liste unvollständig ist."
    )
    annahmen.append(
        "Zugangsfaktor und Gesamtleistungsbewertung vereinfacht mit 1,0 angesetzt "
        "- vor Bescheid unbedingt anhand des tatsächlichen Rentenbescheids/Probeberechnung prüfen."
    )

    return EMRenteSchaetzung(
        entgeltpunkte_bisher=ep_bisher,
        entgeltpunkte_zurechnungszeit=ep_zurechnungszeit,
        entgeltpunkte_gesamt_min=ep_min,
        entgeltpunkte_gesamt_max=ep_max,
        brutto_monat_min=brutto_min,
        brutto_monat_max=brutto_max,
        annahmen=annahmen,
    )


# ---------------------------------------------------------------------------
# 2. Job im Übergangsbereich (Midijob, § 20 SGB IV)
# ---------------------------------------------------------------------------

@dataclass
class UebergangsbereichErgebnis:
    brutto_monat: float
    beitragspflichtige_einnahme: float
    arbeitnehmeranteil_sv: float
    netto_monat: float
    annahmen: List[str]


def berechne_uebergangsbereich_netto(
    brutto_monat: float,
    untere_grenze: float,
    obere_grenze: float,
    f_faktor: float,
    an_beitragssatz_gesamt: float,
) -> UebergangsbereichErgebnis:
    """Netto im Übergangsbereich nach der Midijob-Formel (§ 20 Abs. 2a SGB IV).

    bE = F x G + [(obere/(obere-untere)) - (F x untere/(obere-untere))] x (AE - G)

    `f_faktor`, `untere_grenze`, `obere_grenze` und `an_beitragssatz_gesamt`
    ändern sich jährlich per Verordnung/Gesetz und müssen für das jeweilige
    Kalenderjahr aktuell recherchiert werden (siehe connectors.py).
    """
    annahmen = [
        "F-Faktor, Grenzwerte und AN-Beitragssatz sind jahresabhängige Werte "
        "-> vor Verwendung Aktualität für das jeweilige Kalenderjahr prüfen."
    ]
    if brutto_monat <= untere_grenze:
        return UebergangsbereichErgebnis(
            brutto_monat=brutto_monat,
            beitragspflichtige_einnahme=brutto_monat,
            arbeitnehmeranteil_sv=0.0,
            netto_monat=brutto_monat,
            annahmen=annahmen + ["Bruttolohn liegt in/unter der Minijob-Zone -> keine AN-SV-Beiträge."],
        )

    faktor_a = obere_grenze / (obere_grenze - untere_grenze)
    faktor_b = f_faktor * untere_grenze / (obere_grenze - untere_grenze)
    bemessungsgrundlage = (
        f_faktor * untere_grenze + (faktor_a - faktor_b) * (brutto_monat - untere_grenze)
    )
    an_anteil = bemessungsgrundlage * an_beitragssatz_gesamt
    netto = brutto_monat - an_anteil

    return UebergangsbereichErgebnis(
        brutto_monat=brutto_monat,
        beitragspflichtige_einnahme=bemessungsgrundlage,
        arbeitnehmeranteil_sv=an_anteil,
        netto_monat=netto,
        annahmen=annahmen,
    )


# ---------------------------------------------------------------------------
# 3. BAföG (elternabhängig, vereinfachte Freibetragsrechnung § 25 BAföG)
# ---------------------------------------------------------------------------

@dataclass
class BafoegErgebnis:
    bedarf_monat: float
    anrechenbares_elterneinkommen_monat: float
    anrechenbares_eigenes_einkommen_monat: float
    foerderbetrag_monat: float
    annahmen: List[str]


def berechne_bafoeg(
    bedarf_monat: float,
    eltern_einkommen_jahr: float,
    eltern_freibetrag_jahr: float,
    anrechnungssatz_eltern: float,
    eigenes_anrechenbares_einkommen_monat: float,
) -> BafoegErgebnis:
    """Vereinfachte BAföG-Berechnung. Der echte Anrechnungssatz ist gestaffelt
    (mehrstufiger Tarif nach § 25 Abs. 4 BAföG); hier wird ein pauschaler,
    per Parameter übergebener Satz verwendet - für eine bescheidgenaue Zahl
    ist der offizielle BAföG-Rechner bzw. das Amt für Ausbildungsförderung
    heranzuziehen.
    """
    annahmen = [
        "Vereinfachter linearer Anrechnungssatz statt gestaffeltem Tarif "
        "(§ 25 Abs. 4 BAföG) - Näherung, kein Bescheidersatz."
    ]
    ueberschuss_jahr = max(0.0, eltern_einkommen_jahr - eltern_freibetrag_jahr)
    anrechnung_eltern_monat = (ueberschuss_jahr * anrechnungssatz_eltern) / 12

    foerderbetrag = max(
        0.0, bedarf_monat - anrechnung_eltern_monat - eigenes_anrechenbares_einkommen_monat
    )

    return BafoegErgebnis(
        bedarf_monat=bedarf_monat,
        anrechenbares_elterneinkommen_monat=anrechnung_eltern_monat,
        anrechenbares_eigenes_einkommen_monat=eigenes_anrechenbares_einkommen_monat,
        foerderbetrag_monat=foerderbetrag,
        annahmen=annahmen,
    )


# ---------------------------------------------------------------------------
# 4. Persönliches Budget
# ---------------------------------------------------------------------------

def berechne_persoenliches_budget_wert(stunden_monat: float, stundensatz: float) -> float:
    return stunden_monat * stundensatz
