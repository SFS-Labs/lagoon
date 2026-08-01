"""Mathias Cashflow- & Rechts-Agent - Orchestrator.

Kombiniert Rechtsprüfung (rechtscheck.py) und Berechnung (berechnungen.py)
zu einem Bericht im Pflichtformat:
  1. Rechtliche Einschätzung
  2. Geschätzte Beträge
  3. Cashflow-Szenarien
  4. Priorisierte Handlungspfade

Live-Daten (Gesetzeslage, aktuelle Grenzwerte/Sätze, Marktsätze) kommen
NICHT aus eingebetteten Netzwerkaufrufen dieses Skripts, sondern über die
Recherche-Schnittstelle in connectors.py: Ein aufrufender Agent mit
Tool-Zugriff (z.B. Claude Code mit Legal Data Hunter/WebSearch) recherchiert
`recherche_bedarf()` und übergibt die Ergebnisse an `bericht()`.
"""

from dataclasses import dataclass, replace
from datetime import date
from typing import Dict, List, Optional

from berechnungen import (
    BafoegErgebnis,
    EMRenteSchaetzung,
    UebergangsbereichErgebnis,
    berechne_bafoeg,
    berechne_persoenliches_budget_wert,
    berechne_uebergangsbereich_netto,
    schaetze_em_rente,
)
from connectors import RechercheAuftrag, RechercheErgebnis, RechercheSammler, ergebnisse_zusammenfassen
from eingabedaten import Eingaben
from rechtscheck import (
    Befund,
    Status,
    alle_pruefungen,
    pruefe_bafoeg_krankenversicherungsanteil_bei_kvdr,
    pruefe_em_nebentaetigkeit,
    pruefe_hinzuverdienstgrenze,
    pruefe_kvdr_vs_studentische_versicherung,
    pruefe_wartezeit_widerspruch,
)


@dataclass
class Konstanten:
    """Statutarische Konstanten/Marktsätze. `None` = noch nicht recherchiert.

    Jedes Feld trägt zusätzlich einen recherche-Key, unter dem ein
    passendes `RechercheErgebnis` in `bericht()` eingespeist werden kann.
    """
    aktueller_rentenwert: Optional[float] = None
    zurechnungszeit_endalter_jahre: Optional[float] = None
    hinzuverdienstgrenze_jahr: Optional[float] = None
    hinzuverdienstgrenze_bezugsjahr: int = date.today().year

    uebergangsbereich_untere_grenze: Optional[float] = None
    uebergangsbereich_obere_grenze: float = 2000.0
    uebergangsbereich_f_faktor: Optional[float] = None
    uebergangsbereich_an_beitragssatz: Optional[float] = None

    bafoeg_eltern_freibetrag_jahr: Optional[float] = None
    bafoeg_anrechnungssatz_eltern: Optional[float] = None

    pb_stundensatz: Optional[float] = None


_KONSTANTEN_RECHERCHE: List[RechercheAuftrag] = [
    RechercheAuftrag(
        schluessel="aktueller_rentenwert",
        frage="Aktueller Rentenwert (West) in Euro pro Entgeltpunkt.",
        themenbereich="sozialrecht",
    ),
    RechercheAuftrag(
        schluessel="hinzuverdienstgrenze_jahr",
        frage="Aktuelle Hinzuverdienstgrenze für volle Erwerbsminderungsrente im laufenden Jahr.",
        themenbereich="sozialrecht",
    ),
    RechercheAuftrag(
        schluessel="zurechnungszeit_endalter_jahre",
        frage=(
            "Bis zu welchem Lebensalter (in Jahren, ggf. mit Monatsbruchteil) wird die "
            "Zurechnungszeit bei einer EM-Rente mit aktuellem Rentenbeginn angerechnet?"
        ),
        themenbereich="sozialrecht",
    ),
    RechercheAuftrag(
        schluessel="uebergangsbereich_untere_grenze",
        frage="Aktuelle untere Grenze des Übergangsbereichs (Minijob-Grenze) in Euro/Monat.",
        themenbereich="sozialrecht",
    ),
    RechercheAuftrag(
        schluessel="uebergangsbereich_f_faktor",
        frage="Aktueller F-Faktor für die Midijob-Formel (§ 20 Abs. 2a SGB IV) im laufenden Jahr.",
        themenbereich="sozialrecht",
    ),
    RechercheAuftrag(
        schluessel="uebergangsbereich_an_beitragssatz",
        frage="Aktueller durchschnittlicher Arbeitnehmer-Gesamtsozialversicherungsbeitragssatz.",
        themenbereich="sozialrecht",
    ),
    RechercheAuftrag(
        schluessel="bafoeg_eltern_freibetrag_jahr",
        frage="Aktueller BAföG-Elternfreibetrag pro Jahr für die vorliegende Familienkonstellation.",
        themenbereich="bafoeg",
    ),
    RechercheAuftrag(
        schluessel="bafoeg_anrechnungssatz_eltern",
        frage="Näherungsweiser Anrechnungssatz auf das über dem Freibetrag liegende Elterneinkommen.",
        themenbereich="bafoeg",
    ),
    RechercheAuftrag(
        schluessel="pb_stundensatz",
        frage=(
            "Marktüblicher/LVR-Stundensatz für nicht-qualifizierte Assistenz im "
            "Arbeitgebermodell (Persönliches Budget), aktuelles Jahr, relevantes Bundesland."
        ),
        themenbereich="persoenliches_budget",
    ),
]


class MathiasAgent:
    def __init__(self) -> None:
        self.rechtliche_annahmen = [
            "Keine Rechtsberatung - datenbasierte Einschätzung zur Vorbereitung eines "
            "Gesprächs mit DRV/BAföG-Amt/LVR bzw. einer Rechtsberatung.",
        ]

    # -- Phase 1: Rechercheaufträge sammeln -----------------------------------

    def recherche_bedarf(self, eingaben: Eingaben, konstanten: Konstanten) -> List[RechercheAuftrag]:
        sammler = RechercheSammler()

        befunde = self._rechtliche_befunde(eingaben, konstanten)
        sammler.hinzufuegen(alle_pruefungen(befunde))

        offene_konstanten = [
            auftrag
            for auftrag in _KONSTANTEN_RECHERCHE
            if getattr(konstanten, auftrag.schluessel, None) is None
        ]
        sammler.hinzufuegen(offene_konstanten)

        return sammler.offene_auftraege()

    # -- Phase 2: Rechtliche Befunde -------------------------------------------

    def _rechtliche_befunde(self, eingaben: Eingaben, konstanten: Konstanten) -> List[Befund]:
        jahresbrutto_job = self._job_jahresbrutto(eingaben)
        befunde = [
            pruefe_em_nebentaetigkeit(eingaben.arbeitsvertrag.schichtlaengen_stunden),
        ]
        if konstanten.hinzuverdienstgrenze_jahr is not None:
            befunde.append(
                pruefe_hinzuverdienstgrenze(
                    jahresbrutto_job,
                    konstanten.hinzuverdienstgrenze_jahr,
                    konstanten.hinzuverdienstgrenze_bezugsjahr,
                )
            )
        else:
            befunde.append(
                Befund(
                    thema="Hinzuverdienstgrenze volle EM",
                    status=Status.ZU_KLAEREN,
                    begruendung="Aktuelle Hinzuverdienstgrenze noch nicht recherchiert.",
                    rechtsgrundlage="§ 96a SGB VI",
                    recherche=RechercheAuftrag(
                        schluessel="hinzuverdienstgrenze_jahr",
                        frage=f"Aktuelle Hinzuverdienstgrenze für volle Erwerbsminderungsrente im Jahr {konstanten.hinzuverdienstgrenze_bezugsjahr}.",
                        themenbereich="sozialrecht",
                    ),
                )
            )
        befunde.append(pruefe_kvdr_vs_studentische_versicherung(em_rente_wird_bewilligt=True))
        befunde.append(pruefe_bafoeg_krankenversicherungsanteil_bei_kvdr())
        befunde.append(
            pruefe_wartezeit_widerspruch(
                ausbildungsende_erfuellt=eingaben.stammdaten.ausbildungsende is not None,
                pflichtbeitraege_vor_ausbildungsende_monate=12.0,
            )
        )
        return befunde

    def _job_jahresbrutto(self, eingaben: Eingaben) -> float:
        stunden_woche = eingaben.arbeitsvertrag.stunden_woche_max
        return stunden_woche * eingaben.arbeitsvertrag.stundenlohn_brutto * 52

    # -- Phase 3: Bericht -------------------------------------------------------

    def _konstanten_auffuellen(
        self, konstanten: Konstanten, rechercheergebnisse: Dict[str, RechercheErgebnis]
    ) -> Konstanten:
        werte = {}
        for feld in _KONSTANTEN_RECHERCHE:
            ergebnis = rechercheergebnisse.get(feld.schluessel)
            if ergebnis is not None and getattr(konstanten, feld.schluessel, None) is None:
                try:
                    werte[feld.schluessel] = float(ergebnis.wert)
                except ValueError:
                    pass
        return replace(konstanten, **werte) if werte else konstanten

    def bericht(
        self,
        eingaben: Eingaben,
        konstanten: Konstanten,
        rechercheergebnisse: Optional[Dict[str, RechercheErgebnis]] = None,
    ) -> str:
        rechercheergebnisse = rechercheergebnisse or {}
        konstanten = self._konstanten_auffuellen(konstanten, rechercheergebnisse)

        befunde = self._rechtliche_befunde(eingaben, konstanten)

        em_schaetzung: Optional[EMRenteSchaetzung] = None
        if konstanten.aktueller_rentenwert and konstanten.zurechnungszeit_endalter_jahre:
            em_schaetzung = schaetze_em_rente(
                stammdaten=eingaben.stammdaten,
                verlauf=eingaben.versicherungsverlauf,
                aktueller_rentenwert=konstanten.aktueller_rentenwert,
                zurechnungszeit_endalter_jahre=konstanten.zurechnungszeit_endalter_jahre,
            )

        job_ergebnis: Optional[UebergangsbereichErgebnis] = None
        if (
            konstanten.uebergangsbereich_untere_grenze
            and konstanten.uebergangsbereich_f_faktor
            and konstanten.uebergangsbereich_an_beitragssatz
        ):
            brutto_monat = eingaben.arbeitsvertrag.stunden_woche_max * eingaben.arbeitsvertrag.stundenlohn_brutto * 52 / 12
            job_ergebnis = berechne_uebergangsbereich_netto(
                brutto_monat=brutto_monat,
                untere_grenze=konstanten.uebergangsbereich_untere_grenze,
                obere_grenze=konstanten.uebergangsbereich_obere_grenze,
                f_faktor=konstanten.uebergangsbereich_f_faktor,
                an_beitragssatz_gesamt=konstanten.uebergangsbereich_an_beitragssatz,
            )

        pb_wert: Optional[float] = None
        if konstanten.pb_stundensatz:
            pb_wert = berechne_persoenliches_budget_wert(
                eingaben.budget.fachleistungsstunden_monat, konstanten.pb_stundensatz
            )

        bafoeg_ergebnis: Optional[BafoegErgebnis] = None
        if konstanten.bafoeg_eltern_freibetrag_jahr and konstanten.bafoeg_anrechnungssatz_eltern:
            eigenes_einkommen_monat = (job_ergebnis.netto_monat if job_ergebnis else 0.0) + (
                (em_schaetzung.brutto_monat_min + em_schaetzung.brutto_monat_max) / 2
                if em_schaetzung
                else 0.0
            )
            bafoeg_ergebnis = berechne_bafoeg(
                bedarf_monat=992.0,
                eltern_einkommen_jahr=eingaben.bafoeg.eltern_gesamteinkommen_jahr,
                eltern_freibetrag_jahr=konstanten.bafoeg_eltern_freibetrag_jahr,
                anrechnungssatz_eltern=konstanten.bafoeg_anrechnungssatz_eltern,
                eigenes_anrechenbares_einkommen_monat=eigenes_einkommen_monat,
            )

        return self._formatiere_bericht(
            eingaben, befunde, em_schaetzung, job_ergebnis, pb_wert, bafoeg_ergebnis, rechercheergebnisse
        )

    # -- Formatierung -------------------------------------------------------

    def _formatiere_bericht(
        self,
        eingaben: Eingaben,
        befunde: List[Befund],
        em: Optional[EMRenteSchaetzung],
        job: Optional[UebergangsbereichErgebnis],
        pb_wert: Optional[float],
        bafoeg: Optional[BafoegErgebnis],
        rechercheergebnisse: Dict[str, RechercheErgebnis],
    ) -> str:
        zeilen: List[str] = []

        zeilen.append("1. RECHTLICHE EINSCHAETZUNG")
        zeilen.append("=" * 60)
        for b in befunde:
            zeilen.append(f"[{b.status.value.upper()}] {b.thema} ({b.rechtsgrundlage})")
            zeilen.append(f"  {b.begruendung}")
        zeilen.append("")

        zeilen.append("2. GESCHAETZTE BETRAEGE")
        zeilen.append("=" * 60)
        if em:
            zeilen.append(
                f"EM-Rente brutto/Monat: {em.brutto_monat_min:,.2f} - {em.brutto_monat_max:,.2f} EUR "
                f"(EP gesamt: {em.entgeltpunkte_gesamt_min:.2f} - {em.entgeltpunkte_gesamt_max:.2f})"
            )
            for a in em.annahmen:
                zeilen.append(f"  Annahme: {a}")
        else:
            zeilen.append("EM-Rente: nicht berechenbar - Rentenwert/Zurechnungszeit-Endalter fehlen (live recherchieren).")

        if job:
            zeilen.append(
                f"Job netto/Monat: {job.netto_monat:,.2f} EUR (brutto {job.brutto_monat:,.2f} EUR, "
                f"AN-SV-Anteil {job.arbeitnehmeranteil_sv:,.2f} EUR)"
            )
        else:
            zeilen.append("Job netto: nicht berechenbar - Übergangsbereich-Konstanten fehlen (live recherchieren).")

        if pb_wert is not None:
            zeilen.append(
                f"Persoenliches Budget: {pb_wert:,.2f} EUR/Monat "
                f"({eingaben.budget.fachleistungsstunden_monat} Std x Stundensatz)"
            )
        else:
            zeilen.append("Persoenliches Budget: Stundensatz fehlt (live recherchieren).")

        if bafoeg:
            zeilen.append(f"BAfoeG-Foerderbetrag/Monat: {bafoeg.foerderbetrag_monat:,.2f} EUR")
            for a in bafoeg.annahmen:
                zeilen.append(f"  Annahme: {a}")
        else:
            zeilen.append("BAfoeG: nicht berechenbar - Freibetrag/Anrechnungssatz fehlen (live recherchieren).")
        zeilen.append("")

        zeilen.append("3. CASHFLOW-SZENARIEN")
        zeilen.append("=" * 60)
        if em and job and pb_wert is not None and bafoeg:
            em_mitte = (em.brutto_monat_min + em.brutto_monat_max) / 2
            summe_basis = em_mitte + job.netto_monat + pb_wert + bafoeg.foerderbetrag_monat
            zeilen.append(f"Basis (Mittelwerte): {summe_basis:,.2f} EUR/Monat")
            summe_min = em.brutto_monat_min + job.netto_monat + pb_wert + bafoeg.foerderbetrag_monat
            summe_max = em.brutto_monat_max + job.netto_monat + pb_wert + bafoeg.foerderbetrag_monat
            zeilen.append(f"Bandbreite (EM-Unsicherheit): {summe_min:,.2f} - {summe_max:,.2f} EUR/Monat")
        else:
            zeilen.append("Vollstaendiges Szenario erst nach Live-Recherche der fehlenden Konstanten moeglich.")
        zeilen.append("")

        zeilen.append("4. PRIORISIERTE HANDLUNGSPFADE")
        zeilen.append("=" * 60)
        risiken = [b for b in befunde if b.status == Status.RISIKO]
        zu_klaeren = [b for b in befunde if b.status == Status.ZU_KLAEREN]
        prio = 1
        for b in risiken:
            zeilen.append(f"{prio}. [RISIKO] {b.thema} klaeren/entschaerfen: {b.begruendung.splitlines()[0]}")
            prio += 1
        for b in zu_klaeren:
            zeilen.append(f"{prio}. [KLAEREN] {b.thema}")
            prio += 1
        zeilen.append("")

        zeilen.append("LIVE-RECHERCHEERGEBNISSE")
        zeilen.append("=" * 60)
        zeilen.append(ergebnisse_zusammenfassen(rechercheergebnisse))

        return "\n".join(zeilen)


if __name__ == "__main__":
    from datetime import date as _date
    from eingabedaten import (
        Arbeitsvertragsdaten,
        BafoegFormblattdaten,
        Eingaben,
        PersonStammdaten,
        PersoenlichesBudgetBewilligung,
        Versicherungsverlaufseintrag,
    )

    eingaben = Eingaben(
        stammdaten=PersonStammdaten(
            geburtsdatum=_date(1998, 1, 1),
            em_beginn_medizinisch=_date(2023, 7, 11),
            ausbildungsende=_date(2020, 7, 3),
            gdb=70,
        ),
        versicherungsverlauf=[
            Versicherungsverlaufseintrag(
                von=_date(2019, 1, 1), bis=_date(2023, 7, 11), entgeltpunkte=1.8, art="Pflichtbeitrag"
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

    print("=== Offene Rechercheauftraege ===")
    for auftrag in agent.recherche_bedarf(eingaben, konstanten):
        print(f"- [{auftrag.themenbereich}] {auftrag.schluessel}: {auftrag.frage} (-> {auftrag.empfohlener_connector})")

    print("\n=== Bericht (ohne Live-Recherche, nur Struktur-Check) ===")
    print(agent.bericht(eingaben, konstanten))
