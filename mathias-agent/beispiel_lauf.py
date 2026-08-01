"""Beispiel-Lauf mit live recherchierten Werten (Stand: 01.08.2026).

Diese Werte wurden für diesen Lauf per WebSearch/Legal Data Hunter recherchiert
(siehe Quellenangaben) und hier als `RechercheErgebnis` eingespeist - genau der
Ablauf, den `connectors.py`/`agent.py` für zukünftige Läufe vorsehen: der
aufrufende Agent recherchiert `MathiasAgent.recherche_bedarf(...)` und speist
die Antworten hier ein, statt Werte im Code fest einzufrieren.

Eingabedaten (Versicherungsverlauf, Vertrag, BAföG-Formblatt, Budget) sind noch
Platzhalter aus dem Ursprungsdokument, da die echten Dokumente/Bescheide noch
nicht vorliegen - siehe README.md für den Ablauf, sobald sie eingespeist werden.
"""

from datetime import date

from agent import Konstanten, MathiasAgent
from connectors import RechercheErgebnis
from eingabedaten import (
    Arbeitsvertragsdaten,
    BafoegFormblattdaten,
    Eingaben,
    PersonStammdaten,
    PersoenlichesBudgetBewilligung,
    Versicherungsverlaufseintrag,
)

STAND = "2026-08-01"

RECHERCHEERGEBNISSE = {
    "aktueller_rentenwert": RechercheErgebnis(
        wert="42.52",
        quelle="Deutsche Rentenversicherung, Pressemeldung Rentenanpassung 2026 (ab 01.07.2026)",
        stand=STAND,
    ),
    "hinzuverdienstgrenze_jahr": RechercheErgebnis(
        wert="20763.75",
        quelle="Deutsche Rentenversicherung / sozialversicherung-kompetent.de, Hinzuverdienstgrenzen EM-Renten 2026",
        stand=STAND,
    ),
    "zurechnungszeit_endalter_jahre": RechercheErgebnis(
        wert="66.25",
        quelle="hopkins.law Zurechnungszeit-Tabelle 2026 (66 Jahre 3 Monate für Rentenbeginn 2026)",
        stand=STAND,
    ),
    "uebergangsbereich_untere_grenze": RechercheErgebnis(
        wert="603.01",
        quelle="TK Beratungsblatt Übergangsbereich 2026",
        stand=STAND,
    ),
    "uebergangsbereich_f_faktor": RechercheErgebnis(
        wert="0.6619",
        quelle="TK 'Was ist der Faktor F' 2026",
        stand=STAND,
    ),
    "uebergangsbereich_an_beitragssatz": RechercheErgebnis(
        wert="0.2175",
        quelle=(
            "Berechnet aus Sozialversicherungsrechengroessen 2026 (DRV Knappschaft-Bahn-See): "
            "KV 7,3%+1,45% + RV 9,3% + AV 1,3% + PV 2,4% (kinderlos, AN-Anteil) = 21,75% - "
            "PV-Kinderlosenzuschlag als Annahme, da Familienstatus nicht bestaetigt."
        ),
        stand=STAND,
    ),
    "bafoeg_eltern_freibetrag_jahr": RechercheErgebnis(
        wert="28800",
        quelle="bafoeg-optimierer.de, Grundfreibetrag 2.400 EUR/Monat fuer verheiratete Eltern x 12 (Annahme: verheiratet)",
        stand=STAND,
    ),
    "bafoeg_anrechnungssatz_eltern": RechercheErgebnis(
        wert="0.50",
        quelle="bafoeg-optimierer.de, Anrechnungssatz 50% auf Elterneinkommen ueber Freibetrag",
        stand=STAND,
    ),
    "pb_stundensatz": RechercheErgebnis(
        wert="33",
        quelle=(
            "assistenzplus.de, Stundensaetze Persoenliche Assistenz NRW 33-45 EUR - "
            "unterer Wert angesetzt, da nicht-qualifizierte Assistenz (Mutter) im Arbeitgebermodell; "
            "exakter LVR-Satz muss mit dem Kostentraeger verhandelt/bestaetigt werden."
        ),
        stand=STAND,
    ),
}


def main() -> None:
    eingaben = Eingaben(
        stammdaten=PersonStammdaten(
            geburtsdatum=date(1998, 1, 1),
            em_beginn_medizinisch=date(2023, 7, 11),
            ausbildungsende=date(2020, 7, 3),
            gdb=70,
        ),
        versicherungsverlauf=[
            Versicherungsverlaufseintrag(
                von=date(2019, 1, 1), bis=date(2023, 7, 11), entgeltpunkte=1.8, art="Pflichtbeitrag"
            ),
        ],
        arbeitsvertrag=Arbeitsvertragsdaten(
            stunden_woche_min=12,
            stunden_woche_max=15,
            stundenlohn_brutto=14.50,
            schichtlaengen_stunden=[2.5, 2.5, 2.0],
        ),
        bafoeg=BafoegFormblattdaten(eltern_gesamteinkommen_jahr=28000.0),
        budget=PersoenlichesBudgetBewilligung(fachleistungsstunden_monat=10.83),
    )

    agent = MathiasAgent()
    konstanten = Konstanten()

    print(agent.bericht(eingaben, konstanten, RECHERCHEERGEBNISSE))


if __name__ == "__main__":
    main()
