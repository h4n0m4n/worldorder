"""Future Prediction Engine — multi-agent forecasting system.

Generates probabilistic predictions about future geopolitical events.
Uses multiple specialized analyst agents that debate and produce
consensus forecasts with confidence intervals.
"""

from __future__ import annotations

import random
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field

from engine.world_state import WorldState, CountryState


class PredictionCategory(str, Enum):
    WAR = "war"
    ECONOMIC_CRISIS = "economic_crisis"
    REGIME_CHANGE = "regime_change"
    ALLIANCE_SHIFT = "alliance_shift"
    NUCLEAR_EVENT = "nuclear_event"
    TECHNOLOGY = "technology_breakthrough"
    CLIMATE = "climate_disaster"
    PANDEMIC = "pandemic"
    REVOLUTION = "revolution"
    TRADE_WAR = "trade_war"
    ENERGY_CRISIS = "energy_crisis"
    CYBER_ATTACK = "cyber_attack"
    TERRITORIAL_DISPUTE = "territorial_dispute"


class Prediction(BaseModel):
    id: str
    category: PredictionCategory
    title: str
    description: str
    probability: float  # 0-1
    confidence: float  # 0-1 (how sure are we about the probability)
    timeframe_years: int  # within how many years
    affected_countries: list[str] = Field(default_factory=list)
    impact_severity: float = 0.5  # 0-1
    triggers: list[str] = Field(default_factory=list)
    preventive_factors: list[str] = Field(default_factory=list)
    domino_effects: list[str] = Field(default_factory=list)
    analyst_notes: list[str] = Field(default_factory=list)


class AnalystAgent:
    """A specialized analyst that evaluates specific risk domains."""

    def __init__(self, name: str, domain: str, bias: str = "neutral") -> None:
        self.name = name
        self.domain = domain
        self.bias = bias  # hawkish, dovish, neutral, pessimistic, optimistic

    def assess_risk(self, factor: float, world_context: dict[str, Any]) -> float:
        """Adjust risk assessment based on analyst bias."""
        if self.bias == "hawkish":
            return min(1.0, factor * 1.3)
        elif self.bias == "dovish":
            return factor * 0.7
        elif self.bias == "pessimistic":
            return min(1.0, factor * 1.2)
        elif self.bias == "optimistic":
            return factor * 0.8
        return factor


# Analyst panel with diverse perspectives
ANALYST_PANEL = [
    AnalystAgent("Military Analyst", "military", "hawkish"),
    AnalystAgent("Economic Analyst", "economic", "neutral"),
    AnalystAgent("Intelligence Analyst", "intelligence", "pessimistic"),
    AnalystAgent("Diplomatic Analyst", "diplomatic", "dovish"),
    AnalystAgent("Technology Analyst", "technology", "optimistic"),
    AnalystAgent("Regional Expert", "regional", "neutral"),
]


class FuturePredictionEngine:
    """Generates comprehensive future predictions based on current world state."""

    def __init__(self, world: WorldState, rng_seed: int | None = None) -> None:
        self.world = world
        self.rng = random.Random(rng_seed)
        self.analysts = list(ANALYST_PANEL)
        self.predictions: list[Prediction] = []

    def generate_all_predictions(self, timeframe: int = 10) -> list[Prediction]:
        """Generate predictions across all categories."""
        self.predictions = []
        self.predictions.extend(self._predict_wars(timeframe))
        self.predictions.extend(self._predict_economic_crises(timeframe))
        self.predictions.extend(self._predict_regime_changes(timeframe))
        self.predictions.extend(self._predict_alliance_shifts(timeframe))
        self.predictions.extend(self._predict_nuclear_events(timeframe))
        self.predictions.extend(self._predict_territorial_disputes(timeframe))
        self.predictions.extend(self._predict_energy_crises(timeframe))
        self.predictions.extend(self._predict_tech_breakthroughs(timeframe))

        self.predictions.sort(key=lambda p: p.probability * p.impact_severity, reverse=True)
        return self.predictions

    def _predict_wars(self, tf: int) -> list[Prediction]:
        preds = []
        countries = self.world.all_countries()

        # Check all hostile pairs
        for c in countries:
            for target_code, rel in c.relations.items():
                if rel not in (RelationType.HOSTILE, RelationType.TENSE):
                    continue
                target = self.world.get(target_code)
                if not target:
                    continue

                # War probability factors
                base_prob = 0.02 if rel.value == "tense" else 0.08
                stability_factor = (1 - c.domestic.stability) * 0.15
                power_diff = abs(c.composite_power - target.composite_power) / 100
                nuclear_deterrent = -0.15 if (c.military.nuclear and target.military.nuclear) else 0
                arms_race = (c.military.defense_budget_pct_gdp + target.military.defense_budget_pct_gdp) / 20

                prob = min(0.85, max(0.01, base_prob + stability_factor + arms_race + nuclear_deterrent - power_diff * 0.1))
                prob = self._analyst_consensus(prob)

                if prob > 0.05:
                    preds.append(Prediction(
                        id=f"war_{c.code}_{target_code}",
                        category=PredictionCategory.WAR,
                        title=f"Armed Conflict: {c.name} vs {target.name}",
                        description=f"Military confrontation between {c.name} and {target.name} "
                                   f"based on current tensions and force postures.",
                        probability=round(prob, 3),
                        confidence=0.6,
                        timeframe_years=tf,
                        affected_countries=[c.code, target_code],
                        impact_severity=min(1.0, (c.composite_power + target.composite_power) / 150),
                        triggers=[
                            f"Current relation: {rel.value}",
                            f"Military spending: {c.code}={c.military.defense_budget_pct_gdp:.1f}% GDP",
                            f"Stability: {c.code}={c.domestic.stability:.0%}, {target_code}={target.domestic.stability:.0%}",
                        ],
                        preventive_factors=[
                            "Nuclear deterrence" if (c.military.nuclear and target.military.nuclear) else "No nuclear deterrence",
                            "Economic interdependence",
                            "International mediation",
                        ],
                        domino_effects=[
                            "Global energy price spike",
                            "Refugee crisis in neighboring states",
                            "Alliance chain activation",
                            "Arms industry revenue surge",
                        ],
                    ))
        return preds

    def _predict_economic_crises(self, tf: int) -> list[Prediction]:
        preds = []
        for c in self.world.all_countries():
            risk = 0.0
            triggers = []

            if c.economy.inflation > 15:
                risk += 0.15
                triggers.append(f"High inflation: {c.economy.inflation:.0f}%")
            if c.economy.debt_to_gdp > 100:
                risk += 0.10
                triggers.append(f"High debt: {c.economy.debt_to_gdp:.0f}% of GDP")
            if c.economy.unemployment > 15:
                risk += 0.10
                triggers.append(f"High unemployment: {c.economy.unemployment:.0f}%")
            if c.economy.gdp_growth < 0:
                risk += 0.15
                triggers.append(f"Recession: {c.economy.gdp_growth:.1f}% growth")
            if c.economy.currency_strength < 0.2:
                risk += 0.10
                triggers.append(f"Weak currency: {c.economy.currency_strength:.0%}")

            risk = self._analyst_consensus(min(0.9, risk))

            if risk > 0.15:
                preds.append(Prediction(
                    id=f"econ_crisis_{c.code}",
                    category=PredictionCategory.ECONOMIC_CRISIS,
                    title=f"Economic Crisis: {c.name}",
                    description=f"Severe economic downturn in {c.name} based on current indicators.",
                    probability=round(risk, 3),
                    confidence=0.7,
                    timeframe_years=min(tf, 5),
                    affected_countries=[c.code],
                    impact_severity=min(1.0, c.economy.gdp_trillion / 10),
                    triggers=triggers,
                    domino_effects=["Social unrest", "Capital flight", "Currency collapse", "Political instability"],
                ))
        return preds

    def _predict_regime_changes(self, tf: int) -> list[Prediction]:
        preds = []
        for c in self.world.all_countries():
            risk = 0.0
            triggers = []

            if c.domestic.stability < 0.3:
                risk += 0.20
                triggers.append(f"Very low stability: {c.domestic.stability:.0%}")
            if c.domestic.democracy_index < 0.2:
                risk += 0.05
                triggers.append("Authoritarian regime — coup risk")
            if c.economy.unemployment > 20:
                risk += 0.10
                triggers.append(f"Mass unemployment: {c.economy.unemployment:.0f}%")
            if c.economy.inflation > 30:
                risk += 0.08
                triggers.append(f"Hyperinflation pressure: {c.economy.inflation:.0f}%")

            risk = self._analyst_consensus(min(0.8, risk))

            if risk > 0.10:
                preds.append(Prediction(
                    id=f"regime_{c.code}",
                    category=PredictionCategory.REGIME_CHANGE,
                    title=f"Regime Change: {c.name}",
                    description=f"Government collapse or forced transition in {c.name}.",
                    probability=round(risk, 3),
                    confidence=0.5,
                    timeframe_years=min(tf, 5),
                    affected_countries=[c.code],
                    impact_severity=0.6,
                    triggers=triggers,
                ))
        return preds

    def _predict_alliance_shifts(self, tf: int) -> list[Prediction]:
        preds = []
        # Look for countries with contradictory alliances
        for c in self.world.all_countries():
            hostile_allies = []
            for ally_name in c.alliances:
                for target_code, rel in c.relations.items():
                    if rel in (RelationType.HOSTILE, RelationType.WAR):
                        target = self.world.get(target_code)
                        if target and ally_name in target.alliances:
                            hostile_allies.append((ally_name, target_code))

            if hostile_allies:
                preds.append(Prediction(
                    id=f"alliance_shift_{c.code}",
                    category=PredictionCategory.ALLIANCE_SHIFT,
                    title=f"Alliance Realignment: {c.name}",
                    description=f"{c.name} faces contradictory alliance obligations.",
                    probability=round(0.15 + len(hostile_allies) * 0.05, 3),
                    confidence=0.5,
                    timeframe_years=tf,
                    affected_countries=[c.code],
                    impact_severity=0.5,
                    triggers=[f"Conflicting alliance: {a[0]} vs hostile {a[1]}" for a in hostile_allies[:3]],
                ))
        return preds

    def _predict_nuclear_events(self, tf: int) -> list[Prediction]:
        preds = []
        nuclear_states = [c for c in self.world.all_countries() if c.military.nuclear]
        threshold_states = [c for c in self.world.all_countries()
                          if not c.military.nuclear and c.domestic.tech_level > 0.5
                          and c.domestic.stability < 0.5]

        for c in threshold_states:
            preds.append(Prediction(
                id=f"nuke_proliferation_{c.code}",
                category=PredictionCategory.NUCLEAR_EVENT,
                title=f"Nuclear Proliferation Risk: {c.name}",
                description=f"{c.name} has the technical capability and instability that could drive nuclear weapons pursuit.",
                probability=round(0.05 + (1 - c.domestic.stability) * 0.1, 3),
                confidence=0.4,
                timeframe_years=tf,
                affected_countries=[c.code],
                impact_severity=0.9,
                triggers=[f"Tech level: {c.domestic.tech_level:.0%}", f"Stability: {c.domestic.stability:.0%}"],
            ))
        return preds

    def _predict_territorial_disputes(self, tf: int) -> list[Prediction]:
        KNOWN_DISPUTES = [
            ("CN", "TW", "Taiwan Strait Crisis", 0.15, "China-Taiwan reunification by force"),
            ("IN", "PK", "Kashmir Escalation", 0.08, "Nuclear-armed rivals clash over Kashmir"),
            ("IL", "IR", "Israel-Iran Direct Conflict", 0.12, "Proxy war escalates to direct confrontation"),
            ("RU", "UA", "Ukraine War Expansion", 0.20, "Conflict expands beyond current frontlines"),
            ("CN", "JP", "Senkaku/Diaoyu Islands", 0.05, "Naval confrontation in East China Sea"),
            ("KP", "KR", "Korean Peninsula Crisis", 0.06, "North Korean provocation triggers crisis"),
            ("TR", "GR", "Aegean Sea Dispute", 0.04, "Maritime boundary confrontation"),
            ("EG", "ET", "Nile Water War", 0.07, "GERD dam dispute escalates to military action"),
        ]
        preds = []
        for att, def_, title, base_prob, desc in KNOWN_DISPUTES:
            a, d = self.world.get(att), self.world.get(def_)
            if not a or not d:
                continue
            adj_prob = base_prob * (1 + (1 - a.domestic.stability) * 0.5)
            preds.append(Prediction(
                id=f"dispute_{att}_{def_}",
                category=PredictionCategory.TERRITORIAL_DISPUTE,
                title=title,
                description=desc,
                probability=round(min(0.8, adj_prob), 3),
                confidence=0.6,
                timeframe_years=min(tf, 5),
                affected_countries=[att, def_],
                impact_severity=0.8,
            ))
        return preds

    def _predict_energy_crises(self, tf: int) -> list[Prediction]:
        preds = []
        oil_dependent = [c for c in self.world.all_countries()
                        if c.resources.oil_production < 0.5 and c.economy.gdp_trillion > 0.5]
        if oil_dependent:
            preds.append(Prediction(
                id="global_energy_crisis",
                category=PredictionCategory.ENERGY_CRISIS,
                title="Global Energy Supply Disruption",
                description="Major disruption to global oil/gas supply from geopolitical conflict or OPEC+ action.",
                probability=0.25,
                confidence=0.6,
                timeframe_years=min(tf, 5),
                affected_countries=[c.code for c in oil_dependent[:10]],
                impact_severity=0.8,
                triggers=["Middle East instability", "OPEC+ production cuts", "Strait of Hormuz blockade"],
                domino_effects=["Global recession", "Inflation spike", "Social unrest", "Green energy acceleration"],
            ))
        return preds

    def _predict_tech_breakthroughs(self, tf: int) -> list[Prediction]:
        tech_leaders = sorted(self.world.all_countries(), key=lambda c: c.domestic.tech_level, reverse=True)[:5]
        return [Prediction(
            id="agi_breakthrough",
            category=PredictionCategory.TECHNOLOGY,
            title="Artificial General Intelligence Breakthrough",
            description="A major nation achieves AGI, fundamentally altering global power dynamics.",
            probability=0.15,
            confidence=0.3,
            timeframe_years=tf,
            affected_countries=[c.code for c in tech_leaders],
            impact_severity=1.0,
            triggers=["Massive AI investment", "Compute scaling", "Algorithmic breakthroughs"],
            domino_effects=["Military AI arms race", "Mass unemployment", "Economic restructuring", "Existential risk"],
        )]

    def _analyst_consensus(self, base_prob: float) -> float:
        """Get consensus probability from analyst panel."""
        assessments = [a.assess_risk(base_prob, {}) for a in self.analysts]
        return sum(assessments) / len(assessments)

    def get_top_risks(self, n: int = 20) -> list[Prediction]:
        if not self.predictions:
            self.generate_all_predictions()
        return self.predictions[:n]

    def get_risks_for_country(self, code: str) -> list[Prediction]:
        if not self.predictions:
            self.generate_all_predictions()
        return [p for p in self.predictions if code in p.affected_countries]


# Need this import for the war prediction method
from engine.world_state import RelationType
