"""Dynamic leader system — leaders change with elections, coups, and deaths.

Every country gets a leader. Major countries have hand-crafted profiles.
Others get auto-generated profiles based on country data + LLM enrichment.
"""

from __future__ import annotations

import random
from typing import Any

from pydantic import BaseModel, Field


class LeaderTerm(BaseModel):
    """A single term of a leader in power."""
    leader_id: str
    name: str
    country_code: str
    start_year: int
    end_year: int | None = None  # None = still in power
    title: str = "Head of State"
    party: str = ""
    ideology: str = ""
    traits: list[str] = Field(default_factory=list)
    risk_tolerance: float = 0.5
    decisiveness: float = 0.5
    communication_style: str = ""
    removal_reason: str | None = None  # election, coup, death, resignation, term_limit


class DynamicLeaderSystem:
    """Manages leader transitions across all countries."""

    def __init__(self, rng_seed: int | None = None) -> None:
        self.rng = random.Random(rng_seed)
        self.current_leaders: dict[str, LeaderTerm] = {}
        self.leader_history: dict[str, list[LeaderTerm]] = {}
        self._election_cycles: dict[str, int] = {}
        self._next_election: dict[str, int] = {}

    def initialize_leader(
        self,
        country_code: str,
        name: str,
        year: int,
        gov_type: str = "",
        **kwargs: Any,
    ) -> LeaderTerm:
        """Set the initial leader for a country."""
        leader = LeaderTerm(
            leader_id=f"{country_code}_{year}_{name.lower().replace(' ', '_')[:20]}",
            name=name,
            country_code=country_code,
            start_year=year,
            **kwargs,
        )
        self.current_leaders[country_code] = leader
        self.leader_history.setdefault(country_code, []).append(leader)

        cycle = self._election_cycle_for_gov(gov_type)
        self._election_cycles[country_code] = cycle
        if cycle > 0:
            self._next_election[country_code] = year + cycle
        return leader

    def check_transitions(self, year: int, world_stability: dict[str, float]) -> list[dict[str, Any]]:
        """Check all countries for leader changes this year. Returns list of transition events."""
        transitions: list[dict[str, Any]] = []

        for code, leader in list(self.current_leaders.items()):
            stability = world_stability.get(code, 0.5)

            # Scheduled election
            if code in self._next_election and year >= self._next_election[code]:
                if self.rng.random() < 0.45:  # 45% chance incumbent loses
                    transitions.append(self._transition(code, year, "election"))
                else:
                    self._next_election[code] = year + self._election_cycles.get(code, 4)

            # Coup risk (low stability + authoritarian)
            if stability < 0.25 and self.rng.random() < 0.08:
                transitions.append(self._transition(code, year, "coup"))

            # Revolution (very low stability)
            if stability < 0.15 and self.rng.random() < 0.05:
                transitions.append(self._transition(code, year, "revolution"))

            # Natural death/health (long-serving leaders)
            years_in_power = year - leader.start_year
            if years_in_power > 20 and self.rng.random() < 0.03:
                transitions.append(self._transition(code, year, "death"))
            elif years_in_power > 10 and self.rng.random() < 0.02:
                transitions.append(self._transition(code, year, "resignation"))

        return transitions

    def _transition(self, code: str, year: int, reason: str) -> dict[str, Any]:
        """Execute a leader transition."""
        old_leader = self.current_leaders.get(code)
        if old_leader:
            old_leader.end_year = year
            old_leader.removal_reason = reason

        new_name = self._generate_leader_name(code)
        new_traits = self._generate_traits(reason)

        new_leader = LeaderTerm(
            leader_id=f"{code}_{year}_{new_name.lower().replace(' ', '_')[:20]}",
            name=new_name,
            country_code=code,
            start_year=year,
            traits=new_traits,
            risk_tolerance=self.rng.uniform(0.2, 0.9),
            decisiveness=self.rng.uniform(0.3, 0.9),
        )

        self.current_leaders[code] = new_leader
        self.leader_history.setdefault(code, []).append(new_leader)

        cycle = self._election_cycles.get(code, 0)
        if cycle > 0:
            self._next_election[code] = year + cycle

        return {
            "country": code,
            "year": year,
            "reason": reason,
            "old_leader": old_leader.name if old_leader else None,
            "new_leader": new_name,
            "traits": new_traits,
        }

    def get_leader(self, code: str) -> LeaderTerm | None:
        return self.current_leaders.get(code)

    def get_history(self, code: str) -> list[LeaderTerm]:
        return self.leader_history.get(code, [])

    def _generate_leader_name(self, code: str) -> str:
        """Generate a plausible leader name. In production, LLM would do this."""
        return f"Leader of {code} ({self.rng.randint(1000, 9999)})"

    def _generate_traits(self, transition_reason: str) -> list[str]:
        """Generate personality traits based on how they came to power."""
        base_traits = ["pragmatic"]
        if transition_reason == "election":
            base_traits.extend(self.rng.sample(
                ["populist", "reformist", "moderate", "charismatic", "technocratic", "conservative"], 2
            ))
        elif transition_reason == "coup":
            base_traits.extend(self.rng.sample(
                ["authoritarian", "military-minded", "ruthless", "nationalist", "paranoid"], 2
            ))
        elif transition_reason == "revolution":
            base_traits.extend(self.rng.sample(
                ["ideological", "radical", "charismatic", "revolutionary", "populist"], 2
            ))
        elif transition_reason == "death":
            base_traits.extend(self.rng.sample(
                ["successor", "cautious", "loyalist", "reformist", "continuity"], 2
            ))
        else:
            base_traits.extend(self.rng.sample(
                ["moderate", "cautious", "diplomatic", "experienced"], 2
            ))
        return base_traits

    @staticmethod
    def _election_cycle_for_gov(gov_type: str) -> int:
        """Return election cycle in years based on government type."""
        gov_lower = gov_type.lower()
        if any(x in gov_lower for x in ["absolute monarchy", "one-party", "totalitarian", "emirate", "junta", "military"]):
            return 0  # no elections
        if "presidential" in gov_lower:
            return 4 if "us" not in gov_lower else 4
        if "parliamentary" in gov_lower:
            return 4
        if "semi-presidential" in gov_lower:
            return 5
        if "constitutional monarchy" in gov_lower:
            return 4
        return 5  # default


# ═══════════════════════════════════════════════════════════════
# HAND-CRAFTED CURRENT LEADERS (2025) for major countries
# ═══════════════════════════════════════════════════════════════
CURRENT_LEADERS_2025: dict[str, dict[str, Any]] = {
    "US": {"name": "Joe Biden", "title": "President", "start_year": 2021, "ideology": "center-left liberal", "traits": ["institutionalist", "cautious", "alliance-builder"], "risk_tolerance": 0.3},
    "CN": {"name": "Xi Jinping", "title": "President", "start_year": 2012, "ideology": "Marxist-Leninist nationalist", "traits": ["visionary", "authoritarian", "patient"], "risk_tolerance": 0.6},
    "RU": {"name": "Vladimir Putin", "title": "President", "start_year": 2000, "ideology": "authoritarian nationalist", "traits": ["strategic", "calculating", "risk-taker"], "risk_tolerance": 0.8},
    "TR": {"name": "Recep Tayyip Erdogan", "title": "President", "start_year": 2003, "ideology": "conservative-nationalist", "traits": ["pragmatic", "resilient", "populist"], "risk_tolerance": 0.7},
    "IN": {"name": "Narendra Modi", "title": "Prime Minister", "start_year": 2014, "ideology": "Hindu nationalist", "traits": ["nationalist", "decisive", "image-conscious"], "risk_tolerance": 0.6},
    "GB": {"name": "Keir Starmer", "title": "Prime Minister", "start_year": 2024, "ideology": "center-left social democrat", "traits": ["methodical", "cautious", "reformist"], "risk_tolerance": 0.3},
    "FR": {"name": "Emmanuel Macron", "title": "President", "start_year": 2017, "ideology": "centrist liberal", "traits": ["ambitious", "intellectual", "reformist"], "risk_tolerance": 0.5},
    "DE": {"name": "Friedrich Merz", "title": "Chancellor", "start_year": 2025, "ideology": "center-right conservative", "traits": ["business-minded", "Atlanticist", "pragmatic"], "risk_tolerance": 0.4},
    "JP": {"name": "Shigeru Ishiba", "title": "Prime Minister", "start_year": 2024, "ideology": "center-right realist", "traits": ["defense-focused", "pragmatic", "independent"], "risk_tolerance": 0.4},
    "BR": {"name": "Luiz Inacio Lula da Silva", "title": "President", "start_year": 2023, "ideology": "center-left populist", "traits": ["charismatic", "negotiator", "social-justice"], "risk_tolerance": 0.4},
    "SA": {"name": "Mohammed bin Salman", "title": "Crown Prince", "start_year": 2017, "ideology": "authoritarian modernizer", "traits": ["ambitious", "ruthless", "modernizer"], "risk_tolerance": 0.85},
    "IR": {"name": "Ali Khamenei", "title": "Supreme Leader", "start_year": 1989, "ideology": "revolutionary Islamist", "traits": ["ideological", "paranoid", "patient"], "risk_tolerance": 0.5},
    "IL": {"name": "Benjamin Netanyahu", "title": "Prime Minister", "start_year": 2022, "ideology": "right-wing nationalist", "traits": ["survivor", "hawkish", "media-savvy"], "risk_tolerance": 0.7},
    "UA": {"name": "Volodymyr Zelensky", "title": "President", "start_year": 2019, "ideology": "pro-European liberal", "traits": ["charismatic", "defiant", "media-savvy"], "risk_tolerance": 0.7},
    "KP": {"name": "Kim Jong-un", "title": "Supreme Leader", "start_year": 2011, "ideology": "Juche totalitarian", "traits": ["unpredictable", "ruthless", "strategic"], "risk_tolerance": 0.8},
    "KR": {"name": "Lee Jae-myung", "title": "President", "start_year": 2025, "ideology": "center-left progressive", "traits": ["populist", "bold", "confrontational"], "risk_tolerance": 0.6},
    "PK": {"name": "Shehbaz Sharif", "title": "Prime Minister", "start_year": 2024, "ideology": "center-right", "traits": ["administrator", "cautious", "establishment"], "risk_tolerance": 0.3},
    "EG": {"name": "Abdel Fattah el-Sisi", "title": "President", "start_year": 2014, "ideology": "military authoritarian", "traits": ["strongman", "stability-focused", "cautious"], "risk_tolerance": 0.4},
    "AU": {"name": "Anthony Albanese", "title": "Prime Minister", "start_year": 2022, "ideology": "center-left", "traits": ["pragmatic", "alliance-focused", "moderate"], "risk_tolerance": 0.3},
    "IT": {"name": "Giorgia Meloni", "title": "Prime Minister", "start_year": 2022, "ideology": "right-wing nationalist", "traits": ["assertive", "Atlanticist", "populist"], "risk_tolerance": 0.5},
    "ES": {"name": "Pedro Sanchez", "title": "Prime Minister", "start_year": 2018, "ideology": "center-left social democrat", "traits": ["survivor", "coalition-builder", "pragmatic"], "risk_tolerance": 0.4},
    "PL": {"name": "Donald Tusk", "title": "Prime Minister", "start_year": 2023, "ideology": "center-right pro-European", "traits": ["experienced", "EU-focused", "anti-populist"], "risk_tolerance": 0.4},
    "MX": {"name": "Claudia Sheinbaum", "title": "President", "start_year": 2024, "ideology": "center-left nationalist", "traits": ["technocratic", "continuity", "climate-focused"], "risk_tolerance": 0.3},
    "ID": {"name": "Prabowo Subianto", "title": "President", "start_year": 2024, "ideology": "nationalist", "traits": ["military-background", "assertive", "nationalist"], "risk_tolerance": 0.6},
    "NG": {"name": "Bola Tinubu", "title": "President", "start_year": 2023, "ideology": "center-right", "traits": ["political-operator", "reformist", "experienced"], "risk_tolerance": 0.5},
    "ZA": {"name": "Cyril Ramaphosa", "title": "President", "start_year": 2018, "ideology": "center-left", "traits": ["consensus-builder", "cautious", "business-friendly"], "risk_tolerance": 0.3},
    "AR": {"name": "Javier Milei", "title": "President", "start_year": 2023, "ideology": "libertarian right", "traits": ["radical", "confrontational", "anti-establishment"], "risk_tolerance": 0.8},
    "CO": {"name": "Gustavo Petro", "title": "President", "start_year": 2022, "ideology": "left-wing progressive", "traits": ["ideological", "reformist", "confrontational"], "risk_tolerance": 0.6},
    "TH": {"name": "Paetongtarn Shinawatra", "title": "Prime Minister", "start_year": 2024, "ideology": "populist", "traits": ["dynasty-heir", "populist", "pragmatic"], "risk_tolerance": 0.4},
    "VN": {"name": "To Lam", "title": "General Secretary", "start_year": 2024, "ideology": "communist", "traits": ["security-focused", "authoritarian", "anti-corruption"], "risk_tolerance": 0.5},
    "BD": {"name": "Muhammad Yunus", "title": "Chief Adviser", "start_year": 2024, "ideology": "centrist reformist", "traits": ["intellectual", "reformist", "consensus-builder"], "risk_tolerance": 0.3},
    "ET": {"name": "Abiy Ahmed", "title": "Prime Minister", "start_year": 2018, "ideology": "reformist nationalist", "traits": ["visionary", "controversial", "risk-taker"], "risk_tolerance": 0.7},
    "MY": {"name": "Anwar Ibrahim", "title": "Prime Minister", "start_year": 2022, "ideology": "center-right reformist", "traits": ["survivor", "charismatic", "reformist"], "risk_tolerance": 0.5},
    "SG": {"name": "Lawrence Wong", "title": "Prime Minister", "start_year": 2024, "ideology": "pragmatic centrist", "traits": ["technocratic", "cautious", "continuity"], "risk_tolerance": 0.2},
    "AE": {"name": "Mohammed bin Zayed", "title": "President", "start_year": 2022, "ideology": "authoritarian modernizer", "traits": ["strategic", "ambitious", "tech-focused"], "risk_tolerance": 0.6},
    "QA": {"name": "Tamim bin Hamad Al Thani", "title": "Emir", "start_year": 2013, "ideology": "pragmatic monarchist", "traits": ["diplomatic", "ambitious", "media-savvy"], "risk_tolerance": 0.5},
    "CL": {"name": "Gabriel Boric", "title": "President", "start_year": 2022, "ideology": "left-wing progressive", "traits": ["young", "idealistic", "reformist"], "risk_tolerance": 0.5},
    "NL": {"name": "Dick Schoof", "title": "Prime Minister", "start_year": 2024, "ideology": "center-right", "traits": ["technocratic", "security-focused", "pragmatic"], "risk_tolerance": 0.3},
    "SE": {"name": "Ulf Kristersson", "title": "Prime Minister", "start_year": 2022, "ideology": "center-right", "traits": ["moderate", "NATO-focused", "pragmatic"], "risk_tolerance": 0.3},
    "CH": {"name": "Swiss Federal Council", "title": "Collective Leadership", "start_year": 2024, "ideology": "consensus centrist", "traits": ["consensus-driven", "neutral", "pragmatic"], "risk_tolerance": 0.1},
    "EU": {"name": "European Council", "title": "Collective Leadership", "start_year": 2024, "ideology": "liberal democratic", "traits": ["consensus-seeking", "cautious", "values-driven"], "risk_tolerance": 0.2},
    "BY": {"name": "Alexander Lukashenko", "title": "President", "start_year": 1994, "ideology": "authoritarian", "traits": ["strongman", "Russia-dependent", "paranoid"], "risk_tolerance": 0.4},
    "VE": {"name": "Nicolas Maduro", "title": "President", "start_year": 2013, "ideology": "socialist authoritarian", "traits": ["survivor", "authoritarian", "populist"], "risk_tolerance": 0.5},
    "CU": {"name": "Miguel Diaz-Canel", "title": "President", "start_year": 2018, "ideology": "communist", "traits": ["continuity", "cautious", "technocratic"], "risk_tolerance": 0.3},
    "AF": {"name": "Hibatullah Akhundzada", "title": "Supreme Leader", "start_year": 2021, "ideology": "Islamist fundamentalist", "traits": ["reclusive", "hardline", "ideological"], "risk_tolerance": 0.6},
    "MM": {"name": "Min Aung Hlaing", "title": "Military Leader", "start_year": 2021, "ideology": "military nationalist", "traits": ["ruthless", "military-minded", "authoritarian"], "risk_tolerance": 0.7},
    "SY": {"name": "Ahmad al-Sharaa", "title": "President", "start_year": 2024, "ideology": "Islamist pragmatist", "traits": ["survivor", "pragmatic", "transitional"], "risk_tolerance": 0.6},
    "RW": {"name": "Paul Kagame", "title": "President", "start_year": 2000, "ideology": "authoritarian developmentalist", "traits": ["visionary", "authoritarian", "efficient"], "risk_tolerance": 0.6},
}
