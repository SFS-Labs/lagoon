"""Rohdaten-Schemas: nur Felder, die aus Dokumenten/Bescheiden/User-Angaben stammen.

Diese Werte werden nicht geschätzt, sondern entweder direkt vom User befüllt
oder von einem aufrufenden LLM-Agenten (z.B. Claude Code mit PDF-Skill) aus
hochgeladenen Dokumenten extrahiert: Versicherungsverlauf, Ablehnungs-/
Widerspruchsbescheid, DRV-Schreiben, BAföG-Formblätter, Arbeitsvertrag,
Bewilligungsbescheid Persönliches Budget.
"""

from dataclasses import dataclass, field
from datetime import date
from typing import List, Optional


@dataclass
class Versicherungsverlaufseintrag:
    """Ein Zeitabschnitt aus dem Versicherungsverlauf der DRV."""
    von: date
    bis: date
    entgeltpunkte: Optional[float] = None
    bruttoentgelt_jahr: Optional[float] = None  # Alternative, falls EP nicht direkt vorliegen
    art: str = "Pflichtbeitrag"  # z.B. "Pflichtbeitrag", "Anrechnungszeit", "Ausbildung"


@dataclass
class PersonStammdaten:
    geburtsdatum: date
    em_beginn_medizinisch: date
    ausbildungsende: Optional[date] = None
    gdb: int = 0
    wohnort_bundesland: str = "NRW"


@dataclass
class Arbeitsvertragsdaten:
    stunden_woche_min: float
    stunden_woche_max: float
    stundenlohn_brutto: float
    schichtlaengen_stunden: List[float] = field(default_factory=list)  # tatsächliche/geplante Einzelschichten
    vertrag_beginn: Optional[date] = None
    vertrag_ende: Optional[date] = None
    beschaeftigungsart: str = "Übergangsbereich"  # "Minijob" | "Übergangsbereich" | "Midijob" | "sozialversicherungspflichtig"


@dataclass
class BafoegFormblattdaten:
    bedarfssatz_kategorie: str = "auswaertig_bei_eltern_krankenversichert"
    eltern_gesamteinkommen_jahr: float = 0.0
    eltern_anzahl_kinder_in_ausbildung: int = 1
    student_krankenversichert_ueber: str = "KVdR"  # "KVdR" | "studentischer_tarif" | "familienversicherung"
    wohnform: str = "auswaertig"  # "auswaertig" | "bei_eltern"


@dataclass
class PersoenlichesBudgetBewilligung:
    fachleistungsstunden_monat: float
    modell: str = "Arbeitgebermodell"
    assistenzqualifikation: str = "nicht_qualifiziert"  # "nicht_qualifiziert" | "fachkraft"
    bundesland: str = "NRW"


@dataclass
class Eingaben:
    """Bündelt alle Rohdaten für einen Berechnungslauf."""
    stammdaten: PersonStammdaten
    versicherungsverlauf: List[Versicherungsverlaufseintrag]
    arbeitsvertrag: Arbeitsvertragsdaten
    bafoeg: BafoegFormblattdaten
    budget: PersoenlichesBudgetBewilligung
