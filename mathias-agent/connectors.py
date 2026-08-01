"""Recherche-Schnittstelle für Live-Daten (Gesetzesstand, Rechtsprechung, Marktsätze).

Wichtig: Dies ist bewusst KEIN eingebetteter HTTP-/API-Client. "Legal Data
Hunter" ist ein MCP-Tool, das nur innerhalb einer Agent-/Tool-Use-Runtime
(z.B. Claude Code) zur Verfügung steht - keine öffentliche REST-API, die
dieses Skript selbst aufrufen könnte.

Der Ablauf ist deshalb zweistufig:
  1. Dieses Modul sammelt offene Fragen als `RechercheAuftrag`-Objekte
     (aus rechtscheck.py und berechnungen.py, überall dort, wo eine
     statutarische Konstante oder Rechtsfrage nicht mit Sicherheit bekannt
     ist).
  2. Der aufrufende Agent (mit Zugriff auf Legal Data Hunter / WebSearch)
     beantwortet die Aufträge und übergibt die Ergebnisse als
     `RechercheErgebnis` zurück an `agent.py`, das sie in Flags/Beträge
     einarbeitet.
"""

from dataclasses import dataclass
from typing import Dict, List


@dataclass
class RechercheAuftrag:
    schluessel: str  # eindeutiger Key, unter dem später das Ergebnis erwartet wird
    frage: str
    themenbereich: str  # z.B. "sozialrecht", "bafoeg", "persoenliches_budget"
    empfohlener_connector: str = "Legal Data Hunter"  # "Legal Data Hunter" | "WebSearch"


@dataclass
class RechercheErgebnis:
    wert: str
    quelle: str
    stand: str  # Datum/Zeitpunkt der Recherche


class RechercheSammler:
    """Sammelt Aufträge aus mehreren Quellen und nimmt Ergebnisse entgegen."""

    def __init__(self) -> None:
        self._auftraege: List[RechercheAuftrag] = []

    def hinzufuegen(self, auftraege: List[RechercheAuftrag]) -> None:
        bekannte_keys = {a.schluessel for a in self._auftraege}
        for auftrag in auftraege:
            if auftrag.schluessel not in bekannte_keys:
                self._auftraege.append(auftrag)
                bekannte_keys.add(auftrag.schluessel)

    def offene_auftraege(self) -> List[RechercheAuftrag]:
        return list(self._auftraege)


def ergebnisse_zusammenfassen(ergebnisse: Dict[str, RechercheErgebnis]) -> str:
    """Formatiert Rechercheergebnisse für den Bericht (Quellenangabe je Wert)."""
    if not ergebnisse:
        return "Keine Live-Rechercheergebnisse eingespeist - alle Werte sind Schätzungen."
    zeilen = [
        f"- {schluessel}: {ergebnis.wert} (Quelle: {ergebnis.quelle}, Stand: {ergebnis.stand})"
        for schluessel, ergebnis in ergebnisse.items()
    ]
    return "\n".join(zeilen)
