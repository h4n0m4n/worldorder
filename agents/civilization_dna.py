"""Civilization DNA — the deep cultural/historical identity of a nation.

Leaders change, but a nation's DNA persists across centuries.
It shapes how leaders think, what populations tolerate, and
which strategies feel 'natural' to a country.
"""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class CivilizationDNA(BaseModel):
    country_code: str
    heritage: str = ""
    strategic_identity: str = ""
    cultural_tensions: str = ""
    historical_ambitions: str = ""
    negotiation_culture: str = ""
    national_psyche: str = ""
    extra: dict[str, Any] = Field(default_factory=dict)

    def to_prompt_section(self) -> str:
        lines = ["CIVILIZATION DNA (deep cultural identity):"]
        if self.heritage:
            lines.append(f"  Heritage: {self.heritage}")
        if self.strategic_identity:
            lines.append(f"  Strategic Identity: {self.strategic_identity}")
        if self.cultural_tensions:
            lines.append(f"  Cultural Tensions: {self.cultural_tensions}")
        if self.historical_ambitions:
            lines.append(f"  Historical Ambitions: {self.historical_ambitions}")
        if self.negotiation_culture:
            lines.append(f"  Negotiation Culture: {self.negotiation_culture}")
        if self.national_psyche:
            lines.append(f"  National Psyche: {self.national_psyche}")
        return "\n".join(lines)


def load_civilization_dna_from_country(country_yaml: dict[str, Any]) -> CivilizationDNA | None:
    """Extract civilization DNA from a country YAML profile."""
    dna_data = country_yaml.get("civilization_dna")
    if not dna_data:
        return None
    return CivilizationDNA(
        country_code=country_yaml.get("code", "??"),
        heritage=dna_data.get("heritage", ""),
        strategic_identity=dna_data.get("strategic_identity", ""),
        cultural_tensions=dna_data.get("cultural_tensions", ""),
        historical_ambitions=dna_data.get("historical_ambitions", ""),
        negotiation_culture=dna_data.get("negotiation_culture", ""),
        national_psyche=dna_data.get("national_psyche", ""),
    )


# Pre-built DNA for historical civilizations (used in ancient/medieval eras)
HISTORICAL_CIVILIZATIONS: dict[str, CivilizationDNA] = {
    "ottoman": CivilizationDNA(
        country_code="OT",
        heritage="Turkic nomadic warrior tradition fused with Islamic civilization and Byzantine administrative legacy",
        strategic_identity="Multi-ethnic empire controlling East-West trade routes and holy cities",
        cultural_tensions="Devshirme system, millet autonomy, Sunni orthodoxy vs. Sufi mysticism",
        historical_ambitions="Universal Islamic caliphate, Mediterranean dominance, European expansion",
        negotiation_culture="Grand Vizier diplomacy, capitulations system, strategic marriage alliances",
        national_psyche="Ghazi warrior ethos, cosmopolitan tolerance within hierarchy, fear of internal fragmentation",
    ),
    "roman": CivilizationDNA(
        country_code="RM",
        heritage="Latin city-state to Mediterranean empire, Republic to Principate",
        strategic_identity="Universal empire, civilization vs. barbarism paradigm",
        cultural_tensions="Patrician vs. Plebeian, Roman vs. Provincial, Pagan vs. Christian",
        historical_ambitions="Mare Nostrum, Pax Romana, eternal city mythology",
        negotiation_culture="Divide and conquer, client kingdoms, road-building integration",
        national_psyche="SPQR civic identity, military virtue, engineering pragmatism",
    ),
    "mongol": CivilizationDNA(
        country_code="MG",
        heritage="Steppe nomadic confederation united by Genghis Khan",
        strategic_identity="Largest contiguous land empire, Silk Road guarantor",
        cultural_tensions="Nomadic vs. settled subjects, religious pluralism, succession crises",
        historical_ambitions="World conquest, trade route control, meritocratic military state",
        negotiation_culture="Submit or be destroyed ultimatum, religious tolerance for subjects, Yasa law code",
        national_psyche="Eternal Blue Sky mandate, mobility as power, brutal efficiency",
    ),
    "persian": CivilizationDNA(
        country_code="PR",
        heritage="Achaemenid, Sassanid, Safavid empires spanning millennia",
        strategic_identity="Crossroads of civilizations, cultural superpower",
        cultural_tensions="Zoroastrian legacy vs. Islamic identity, Arab vs. Persian cultural pride",
        historical_ambitions="King of Kings title, civilizational refinement, regional hegemony",
        negotiation_culture="Sophisticated court diplomacy, gift exchange, poetic communication",
        national_psyche="Ancient civilization pride, resistance to foreign domination, cultural resilience",
    ),
    "british": CivilizationDNA(
        country_code="GB",
        heritage="Island nation, naval power, parliamentary tradition, colonial empire",
        strategic_identity="Balance of power architect, maritime hegemon, common law exporter",
        cultural_tensions="Class system, Celtic fringe, post-imperial identity crisis",
        historical_ambitions="Rule Britannia, free trade empire, English-speaking world leadership",
        negotiation_culture="Pragmatic, precedent-based, perfidious Albion reputation, understatement",
        national_psyche="Island mentality, Dunkirk spirit, quiet superiority, institutional trust",
    ),
}
