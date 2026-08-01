"""Rechtliche Vorprüfungen.

Jede Prüf-Funktion liefert einen `Befund`: Status, Begründung, Rechtsgrundlage
und - falls die aktuelle Rechtslage/ein Grenzwert nicht mit Sicherheit
bekannt ist - einen `RechercheAuftrag` zur Live-Verifikation (siehe
connectors.py). Ziel: Der Bot behauptet nichts, was er nicht entweder aus
festem Wissen mit Rechtsgrundlage oder aus Live-Recherche belegen kann.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional

from connectors import RechercheAuftrag


class Status(Enum):
    ZULAESSIG = "zulaessig"
    RISIKO = "risiko"
    ZU_KLAEREN = "zu_klaeren"


@dataclass
class Befund:
    thema: str
    status: Status
    begruendung: str
    rechtsgrundlage: str
    recherche: Optional[RechercheAuftrag] = None


def pruefe_em_nebentaetigkeit(schichtlaengen_stunden: List[float]) -> Befund:
    """Kernfrage des Users: volle EM-Rente + Nebentätigkeit in Split-Schichten.

    Volle Erwerbsminderung bedeutet ein Restleistungsvermögen von unter
    3 Stunden täglich (§ 43 Abs. 2 SGB VI). Die DRV beurteilt dabei die
    *tägliche* Leistungsfähigkeit, nicht den Wochendurchschnitt. Kurze,
    voneinander getrennte Schichten unterhalb von 3 Stunden sind mit einer
    vollen EM grundsätzlich vereinbar; eine einzelne zusammenhängende
    Schicht von 3 Stunden oder mehr überschreitet dagegen das medizinisch
    attestierte Restleistungsvermögen und kann die DRV zu einer Neuprüfung
    veranlassen.
    """
    risikoschichten = [s for s in schichtlaengen_stunden if s >= 3.0]

    if not schichtlaengen_stunden:
        return Befund(
            thema="EM-Rente + Nebentätigkeit (Schichtlänge)",
            status=Status.ZU_KLAEREN,
            begruendung="Keine Schichtlängen übergeben - Prüfung nicht möglich.",
            rechtsgrundlage="§ 43 Abs. 2 SGB VI",
        )

    if risikoschichten:
        return Befund(
            thema="EM-Rente + Nebentätigkeit (Schichtlänge)",
            status=Status.RISIKO,
            begruendung=(
                f"{len(risikoschichten)} von {len(schichtlaengen_stunden)} geplanten Schichten "
                f"erreichen/überschreiten 3 zusammenhängende Stunden "
                f"({', '.join(f'{s:g}h' for s in risikoschichten)}). Das überschreitet das "
                "Restleistungsvermögen der vollen EM und kann eine Neubewertung/den Entzug "
                "der Rente auslösen, unabhängig vom Wochendurchschnitt."
            ),
            rechtsgrundlage="§ 43 Abs. 2 SGB VI i.V.m. medizinischer Leistungsbeurteilung",
            recherche=RechercheAuftrag(
                schluessel="em_nebentaetigkeit_aktuelle_rechtsprechung",
                frage=(
                    "Aktuelle Rechtsprechung/DRV-Praxis 2026: Wird bei voller EM-Rente eine "
                    "einzelne Schicht von 3-6 zusammenhängenden Stunden als Überschreitung "
                    "des Restleistungsvermögens gewertet, auch wenn der Tagesdurchschnitt "
                    "unter 3h liegt?"
                ),
                themenbereich="sozialrecht",
            ),
        )

    return Befund(
        thema="EM-Rente + Nebentätigkeit (Schichtlänge)",
        status=Status.ZULAESSIG,
        begruendung=(
            "Alle geplanten Schichten liegen unter 3 zusammenhängenden Stunden - "
            "grundsätzlich vereinbar mit dem Restleistungsvermögen der vollen EM."
        ),
        rechtsgrundlage="§ 43 Abs. 2 SGB VI",
    )


def pruefe_hinzuverdienstgrenze(
    jahresbrutto_job: float, hinzuverdienstgrenze_jahr: float, jahr: int
) -> Befund:
    if jahresbrutto_job <= hinzuverdienstgrenze_jahr:
        status = Status.ZULAESSIG
        begruendung = (
            f"Erwartetes Jahresbrutto aus dem Job ({jahresbrutto_job:,.2f} €) liegt unter der "
            f"Hinzuverdienstgrenze {jahr} für volle EM ({hinzuverdienstgrenze_jahr:,.2f} €)."
        )
    else:
        status = Status.RISIKO
        begruendung = (
            f"Erwartetes Jahresbrutto ({jahresbrutto_job:,.2f} €) überschreitet die "
            f"Hinzuverdienstgrenze {jahr} ({hinzuverdienstgrenze_jahr:,.2f} €) - "
            "40% des Überhangs werden auf die Rente angerechnet (§ 96a SGB VI)."
        )
    return Befund(
        thema="Hinzuverdienstgrenze volle EM",
        status=status,
        begruendung=begruendung,
        rechtsgrundlage="§ 96a SGB VI",
        recherche=RechercheAuftrag(
            schluessel="hinzuverdienstgrenze_jahr",
            frage=f"Aktuelle Hinzuverdienstgrenze für volle Erwerbsminderungsrente im Jahr {jahr}.",
            themenbereich="sozialrecht",
        ),
    )


def pruefe_kvdr_vs_studentische_versicherung(em_rente_wird_bewilligt: bool) -> Befund:
    if em_rente_wird_bewilligt:
        begruendung = (
            "Mit Bewilligung der EM-Rente greift bei erfüllter Vorversicherungszeit i.d.R. "
            "die Krankenversicherung der Rentner (KVdR). Eine bestehende freiwillige "
            "studentische Versicherung/ein Studententarif wird dadurch regelmäßig "
            "überflüssig, da die KVdR vorrangig und i.d.R. günstiger ist - die konkrete "
            "Vorversicherungszeit und der Übergangszeitpunkt sollten mit der Krankenkasse "
            "verifiziert werden."
        )
        status = Status.ZU_KLAEREN
    else:
        begruendung = (
            "Ohne bewilligte EM-Rente bleibt die bisherige studentische Versicherung "
            "maßgeblich."
        )
        status = Status.ZULAESSIG
    return Befund(
        thema="KVdR vs. studentische Krankenversicherung",
        status=status,
        begruendung=begruendung,
        rechtsgrundlage="§ 5 Abs. 1 Nr. 11 SGB V",
        recherche=RechercheAuftrag(
            schluessel="kvdr_vorversicherungszeit_status",
            frage=(
                "Ist die Vorversicherungszeit für KVdR erfüllt, und ab welchem Zeitpunkt "
                "würde die studentische Versicherung/der Studententarif entbehrlich?"
            ),
            themenbereich="sozialrecht",
        ),
    )


def pruefe_bafoeg_krankenversicherungsanteil_bei_kvdr() -> Befund:
    """User-Frage: Bleibt der im BAföG-Bedarfssatz enthaltene Kranken-/
    Pflegeversicherungszuschlag frei verfügbar, wenn man durch KVdR bereits
    anderweitig krankenversichert ist, oder entfällt dieser Anteil?
    """
    return Befund(
        thema="BAföG-Versicherungszuschlag bei KVdR-Doppelabsicherung",
        status=Status.ZU_KLAEREN,
        begruendung=(
            "Der BAföG-Bedarfssatz enthält einen Zuschlag zu Kranken-/"
            "Pflegeversicherung (§ 13a BAföG), der bei Studierenden ohne eigene "
            "Pflichtversicherung gezahlt wird. Ist man - wie hier über KVdR - bereits "
            "anderweitig pflichtversichert, entfällt der Zuschlag laut § 13a Abs. 2 "
            "BAföG regelmäßig, da er nur den tatsächlichen Versicherungsbedarf "
            "abdecken soll. Das ist mit dem BAföG-Amt anhand des konkreten "
            "Versicherungsstatus zu klären - keine automatische freie Verfügbarkeit."
        ),
        rechtsgrundlage="§ 13a BAföG",
        recherche=RechercheAuftrag(
            schluessel="bafoeg_versicherungszuschlag_kvdr",
            frage=(
                "Entfällt der BAföG-Kranken-/Pflegeversicherungszuschlag (§ 13a BAföG) "
                "vollständig, wenn die/der Studierende bereits über KVdR pflichtversichert "
                "ist, oder wird er anteilig weitergezahlt?"
            ),
            themenbereich="bafoeg",
        ),
    )


def pruefe_wartezeit_widerspruch(
    ausbildungsende_erfuellt: bool, pflichtbeitraege_vor_ausbildungsende_monate: float
) -> Befund:
    erfuellt = ausbildungsende_erfuellt and pflichtbeitraege_vor_ausbildungsende_monate >= 12
    return Befund(
        thema="Wartezeit-Widerspruch (Sonderregel)",
        status=Status.ZULAESSIG if erfuellt else Status.ZU_KLAEREN,
        begruendung=(
            "Die allgemeine Wartezeit (5 Jahre) kann nach § 53 Abs. 2 SGB VI vorzeitig als "
            "erfüllt gelten, wenn die Erwerbsminderung vor Abschluss einer Ausbildung "
            "eingetreten ist und in den letzten zwei Jahren davor mindestens 12 Monate "
            "Pflichtbeiträge geleistet wurden."
            + (
                " Beide Voraussetzungen sind laut vorliegenden Daten erfüllt - aussichtsreich."
                if erfuellt
                else " Mindestens eine Voraussetzung ist laut vorliegenden Daten nicht "
                "bestätigt - anhand der vollständigen Akte prüfen."
            )
        ),
        rechtsgrundlage="§ 53 Abs. 2 SGB VI",
        recherche=RechercheAuftrag(
            schluessel="wartezeit_widerspruch_aktuelle_auslegung",
            frage=(
                "Aktuelle DRV-/BSG-Auslegung 2026 zu § 53 Abs. 2 SGB VI: welche Nachweise "
                "werden für die 12-Monats-Pflichtbeitragszeit vor Ausbildungsende verlangt?"
            ),
            themenbereich="sozialrecht",
        ),
    )


def alle_pruefungen(befunde: List[Befund]) -> List[RechercheAuftrag]:
    """Extrahiert alle Rechercheaufträge aus einer Liste von Befunden."""
    return [b.recherche for b in befunde if b.recherche is not None]
