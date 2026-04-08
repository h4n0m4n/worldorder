"""Shadow Powers — Arms dealers, financial barons, PMCs, energy cartels.

The invisible forces that shape wars, fund conflicts, and profit from chaos.
They operate across borders, influence leaders, and can tip the balance of power.
"""

from __future__ import annotations

import random
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class ShadowType(str, Enum):
    ARMS_DEALER = "arms_dealer"
    FINANCIAL_BARON = "financial_baron"
    PMC = "private_military_company"
    ENERGY_CARTEL = "energy_cartel"
    INTELLIGENCE_BROKER = "intelligence_broker"
    TECH_OLIGARCH = "tech_oligarch"
    NARCO_NETWORK = "narco_network"
    SANCTIONS_EVADER = "sanctions_evader"


class ShadowEntity(BaseModel):
    id: str
    name: str
    type: ShadowType
    description: str
    headquarters: str  # country code
    influence_score: float = 0.5  # 0-1 global influence
    wealth_billion: float = 10.0
    active_regions: list[str] = Field(default_factory=list)
    allied_countries: list[str] = Field(default_factory=list)
    opposed_countries: list[str] = Field(default_factory=list)
    capabilities: list[str] = Field(default_factory=list)
    motivations: list[str] = Field(default_factory=list)
    risk_tolerance: float = 0.7
    visibility: float = 0.3  # 0=completely hidden, 1=public


class ArmsDealer(ShadowEntity):
    """Major defense corporations and black market arms networks."""
    annual_revenue_billion: float = 0.0
    weapons_types: list[str] = Field(default_factory=list)
    export_destinations: list[str] = Field(default_factory=list)
    market_share: float = 0.0  # global market share
    government_contracts: dict[str, float] = Field(default_factory=dict)  # country -> $ billions
    black_market_activity: float = 0.0  # 0-1


class FinancialBaron(ShadowEntity):
    """Financial institutions and individuals who fund wars and profit from conflict."""
    assets_under_management_billion: float = 0.0
    sanctions_evasion_capability: float = 0.0  # 0-1
    money_laundering_networks: list[str] = Field(default_factory=list)
    crypto_operations: bool = False
    hawala_networks: bool = False


class PMC(ShadowEntity):
    """Private Military Companies — mercenaries for hire."""
    personnel_count: int = 0
    combat_experience: float = 0.5  # 0-1
    active_conflicts: list[str] = Field(default_factory=list)
    patron_state: str = ""  # primary state sponsor
    war_crimes_allegations: int = 0
    resource_extraction: list[str] = Field(default_factory=list)  # minerals they control


class EnergyCartel(ShadowEntity):
    """Energy cartels that weaponize oil, gas, and minerals."""
    daily_production_mboe: float = 0.0  # million barrels of oil equivalent
    pipeline_control: list[str] = Field(default_factory=list)
    chokepoint_influence: list[str] = Field(default_factory=list)
    price_manipulation_power: float = 0.0  # 0-1


# ═══════════════════════════════════════════════════════════════
# REAL-WORLD SHADOW ENTITIES DATABASE
# ═══════════════════════════════════════════════════════════════

ARMS_DEALERS: list[ArmsDealer] = [
    ArmsDealer(
        id="lockheed", name="Lockheed Martin", type=ShadowType.ARMS_DEALER,
        description="World's largest defense contractor. F-35, missiles, space systems.",
        headquarters="US", influence_score=0.95, wealth_billion=65,
        active_regions=["North America", "Europe", "Middle East", "East Asia", "Oceania"],
        allied_countries=["US", "GB", "IL", "JP", "AU", "KR", "SA"],
        capabilities=["fighter_jets", "missiles", "space_systems", "cyber", "nuclear_delivery"],
        motivations=["profit", "us_hegemony", "tech_dominance"],
        annual_revenue_billion=67.6, market_share=0.14,
        weapons_types=["F-35", "F-22", "THAAD", "Javelin", "Aegis", "Trident_D5"],
        export_destinations=["US", "GB", "JP", "AU", "KR", "IL", "SA", "AE", "PL", "FI"],
        government_contracts={"US": 45.0, "GB": 3.0, "JP": 2.5, "AU": 2.0, "SA": 4.0},
        visibility=1.0,
    ),
    ArmsDealer(
        id="rtx", name="RTX Corporation (Raytheon)", type=ShadowType.ARMS_DEALER,
        description="Missiles, air defense, engines. Patriot, Stinger, Tomahawk.",
        headquarters="US", influence_score=0.90, wealth_billion=42,
        active_regions=["North America", "Europe", "Middle East", "East Asia"],
        allied_countries=["US", "SA", "AE", "IL", "JP", "KR"],
        capabilities=["air_defense", "missiles", "radar", "engines"],
        motivations=["profit", "air_defense_dominance"],
        annual_revenue_billion=42.0, market_share=0.09,
        weapons_types=["Patriot", "Stinger", "Tomahawk", "AMRAAM", "Sidewinder"],
        export_destinations=["US", "SA", "AE", "JP", "KR", "TW", "PL", "UA"],
        government_contracts={"US": 28.0, "SA": 5.0, "AE": 2.0},
        visibility=1.0,
    ),
    ArmsDealer(
        id="bae", name="BAE Systems", type=ShadowType.ARMS_DEALER,
        description="UK's largest defense company. Ships, vehicles, electronics.",
        headquarters="GB", influence_score=0.80, wealth_billion=28,
        active_regions=["Europe", "Middle East", "North America", "Oceania"],
        allied_countries=["GB", "US", "SA", "AU"],
        capabilities=["naval", "armored_vehicles", "electronics", "cyber"],
        motivations=["profit", "british_defense_industry"],
        annual_revenue_billion=28.3, market_share=0.06,
        weapons_types=["Typhoon", "Challenger", "Type_26", "Hawk"],
        export_destinations=["GB", "SA", "AU", "US", "TR", "IN"],
        government_contracts={"GB": 10.0, "SA": 6.0, "AU": 3.0, "US": 5.0},
        visibility=1.0,
    ),
    ArmsDealer(
        id="norinco", name="NORINCO (China North Industries)", type=ShadowType.ARMS_DEALER,
        description="China's largest arms exporter. Tanks, missiles, small arms.",
        headquarters="CN", influence_score=0.70, wealth_billion=20,
        active_regions=["East Asia", "South Asia", "Africa", "Middle East"],
        allied_countries=["CN", "PK", "MM", "BD"],
        capabilities=["tanks", "artillery", "missiles", "small_arms", "drones"],
        motivations=["profit", "chinese_influence", "belt_and_road_security"],
        annual_revenue_billion=22.0, market_share=0.05,
        weapons_types=["VT-4_tank", "SY-400", "WS-series_MLRS", "CH-series_drones"],
        export_destinations=["PK", "BD", "MM", "TH", "NG", "TD", "SD"],
        government_contracts={"CN": 18.0, "PK": 2.0},
        visibility=0.7,
    ),
    ArmsDealer(
        id="rosoboronexport", name="Rosoboronexport", type=ShadowType.ARMS_DEALER,
        description="Russia's sole state arms export agency. S-400, Su-35, T-90.",
        headquarters="RU", influence_score=0.65, wealth_billion=15,
        active_regions=["Eurasia", "Middle East", "South Asia", "Africa"],
        allied_countries=["RU", "IN", "CN", "EG", "DZ", "VN"],
        capabilities=["air_defense", "fighter_jets", "tanks", "submarines"],
        motivations=["profit", "russian_influence", "counter_western_arms"],
        annual_revenue_billion=13.0, market_share=0.078,
        weapons_types=["S-400", "Su-35", "T-90", "Kilo_submarine", "BrahMos"],
        export_destinations=["IN", "CN", "EG", "DZ", "VN", "TR", "IR"],
        government_contracts={"RU": 10.0, "IN": 4.0, "EG": 2.0},
        visibility=0.8,
    ),
    ArmsDealer(
        id="turkish_defense", name="Turkish Defense Industries (SSB/TAI/Baykar)", type=ShadowType.ARMS_DEALER,
        description="Turkey's rising defense sector. Bayraktar TB2, KAAN, Altay.",
        headquarters="TR", influence_score=0.50, wealth_billion=8,
        active_regions=["Middle East", "Eastern Europe", "Africa", "Central Asia"],
        allied_countries=["TR", "UA", "AZ", "PK", "QA"],
        capabilities=["drones", "fighter_jets", "armored_vehicles", "naval"],
        motivations=["profit", "turkish_influence", "defense_independence"],
        annual_revenue_billion=8.5, market_share=0.02,
        weapons_types=["Bayraktar_TB2", "Bayraktar_Akinci", "KAAN", "Altay", "TCG_Anadolu"],
        export_destinations=["UA", "AZ", "PK", "QA", "NG", "ET", "MA", "KZ"],
        government_contracts={"TR": 5.0, "UA": 0.5, "PK": 0.8},
        visibility=0.9,
    ),
    ArmsDealer(
        id="rafael", name="Rafael / Israel Aerospace Industries", type=ShadowType.ARMS_DEALER,
        description="Israel's defense crown jewels. Iron Dome, Trophy, Spike.",
        headquarters="IL", influence_score=0.60, wealth_billion=12,
        active_regions=["Middle East", "Europe", "East Asia", "South Asia"],
        allied_countries=["IL", "US", "IN", "DE", "SG"],
        capabilities=["air_defense", "missiles", "cyber", "drones", "space"],
        motivations=["profit", "israeli_security", "tech_export"],
        annual_revenue_billion=12.0, market_share=0.03,
        weapons_types=["Iron_Dome", "David_Sling", "Arrow", "Spike", "Trophy", "Heron"],
        export_destinations=["IL", "IN", "DE", "SG", "AZ", "KR"],
        government_contracts={"IL": 6.0, "US": 2.0, "IN": 1.5},
        visibility=0.8,
    ),
    ArmsDealer(
        id="black_market", name="Global Black Market Arms Network", type=ShadowType.ARMS_DEALER,
        description="Decentralized illegal arms trade. Soviet surplus, looted weapons, DIY manufacturing.",
        headquarters="XX", influence_score=0.40, wealth_billion=5,
        active_regions=["Africa", "Middle East", "South Asia", "Central America"],
        capabilities=["small_arms", "explosives", "MANPADS", "ammunition"],
        motivations=["profit", "chaos"],
        annual_revenue_billion=5.0, market_share=0.01,
        weapons_types=["AK-47", "RPG-7", "MANPADS", "IEDs", "ammunition"],
        export_destinations=["conflict_zones"],
        black_market_activity=1.0,
        visibility=0.05,
    ),
]

PMCS: list[PMC] = [
    PMC(
        id="wagner", name="Wagner Group / Africa Corps", type=ShadowType.PMC,
        description="Russian state-linked PMC. Operates across Africa and Middle East.",
        headquarters="RU", influence_score=0.60, wealth_billion=3,
        active_regions=["Africa", "Middle East", "Eastern Europe"],
        allied_countries=["RU", "SY", "ML", "BF", "NE", "CF", "LY"],
        capabilities=["infantry", "special_ops", "resource_extraction", "regime_protection"],
        motivations=["russian_influence", "resource_extraction", "profit"],
        personnel_count=50000, combat_experience=0.8,
        active_conflicts=["Ukraine", "Mali", "Burkina Faso", "Libya", "Syria"],
        patron_state="RU",
        war_crimes_allegations=47,
        resource_extraction=["gold", "diamonds", "oil"],
        visibility=0.5,
    ),
    PMC(
        id="academi", name="Academi (ex-Blackwater)", type=ShadowType.PMC,
        description="US-origin PMC. Training, security, covert operations.",
        headquarters="US", influence_score=0.35, wealth_billion=2,
        active_regions=["Middle East", "Africa"],
        allied_countries=["US", "AE", "SA"],
        capabilities=["training", "security", "special_ops", "intelligence"],
        motivations=["profit", "us_interests"],
        personnel_count=5000, combat_experience=0.7,
        patron_state="US",
        war_crimes_allegations=12,
        visibility=0.4,
    ),
    PMC(
        id="group4s", name="G4S / Allied Universal", type=ShadowType.PMC,
        description="World's largest private security company. 800,000+ employees.",
        headquarters="GB", influence_score=0.30, wealth_billion=15,
        active_regions=["Global"],
        capabilities=["security", "logistics", "intelligence", "cyber_security"],
        motivations=["profit"],
        personnel_count=800000, combat_experience=0.3,
        visibility=0.9,
    ),
    PMC(
        id="rsb_group", name="RSB Group", type=ShadowType.PMC,
        description="Russian PMC operating in Middle East and Africa.",
        headquarters="RU", influence_score=0.20, wealth_billion=0.5,
        active_regions=["Middle East", "Africa"],
        allied_countries=["RU", "SY"],
        capabilities=["infantry", "demining", "security"],
        motivations=["russian_influence", "profit"],
        personnel_count=3000, combat_experience=0.6,
        patron_state="RU",
        visibility=0.2,
    ),
]

FINANCIAL_BARONS: list[FinancialBaron] = [
    FinancialBaron(
        id="swift_system", name="SWIFT Financial Network", type=ShadowType.FINANCIAL_BARON,
        description="Global interbank messaging system. Weaponized through sanctions.",
        headquarters="BE", influence_score=0.95, wealth_billion=0,
        active_regions=["Global"],
        capabilities=["payment_control", "sanctions_enforcement", "financial_surveillance"],
        motivations=["western_financial_order"],
        assets_under_management_billion=0,
        visibility=1.0,
    ),
    FinancialBaron(
        id="iran_shadow_bank", name="Iranian Shadow Banking Network", type=ShadowType.SANCTIONS_EVADER,
        description="$9B+ network of shell companies, hawala brokers, crypto for sanctions evasion.",
        headquarters="IR", influence_score=0.40, wealth_billion=9,
        active_regions=["Middle East", "East Asia", "Europe"],
        allied_countries=["IR", "RU", "CN"],
        capabilities=["sanctions_evasion", "money_laundering", "crypto", "hawala"],
        motivations=["regime_survival", "proxy_funding"],
        sanctions_evasion_capability=0.85,
        money_laundering_networks=["UAE", "HK", "TR", "IQ"],
        crypto_operations=True, hawala_networks=True,
        visibility=0.1,
    ),
    FinancialBaron(
        id="russian_oligarch_net", name="Russian Oligarch Financial Network", type=ShadowType.FINANCIAL_BARON,
        description="Network of Russian billionaires moving money through shell companies and crypto.",
        headquarters="RU", influence_score=0.50, wealth_billion=300,
        active_regions=["Europe", "Middle East", "Caribbean"],
        allied_countries=["RU"],
        capabilities=["sanctions_evasion", "political_influence", "media_control"],
        motivations=["wealth_preservation", "regime_support"],
        assets_under_management_billion=300,
        sanctions_evasion_capability=0.70,
        money_laundering_networks=["AE", "TR", "KZ", "CY"],
        crypto_operations=True,
        visibility=0.3,
    ),
    FinancialBaron(
        id="gulf_sovereign", name="Gulf Sovereign Wealth Funds", type=ShadowType.FINANCIAL_BARON,
        description="$4T+ combined assets. Can destabilize economies or prop up regimes.",
        headquarters="AE", influence_score=0.85, wealth_billion=4000,
        active_regions=["Global"],
        allied_countries=["AE", "SA", "QA", "KW"],
        capabilities=["market_manipulation", "regime_funding", "infrastructure_investment"],
        motivations=["wealth_growth", "political_influence", "post_oil_transition"],
        assets_under_management_billion=4000,
        visibility=0.8,
    ),
]

ENERGY_CARTELS: list[EnergyCartel] = [
    EnergyCartel(
        id="opec_plus", name="OPEC+", type=ShadowType.ENERGY_CARTEL,
        description="Controls 40% of global oil. Can crash or spike prices at will.",
        headquarters="AT", influence_score=0.90, wealth_billion=0,
        active_regions=["Global"],
        allied_countries=["SA", "RU", "AE", "IQ", "IR", "KW", "VE", "NG", "DZ", "LY"],
        capabilities=["oil_price_control", "supply_manipulation", "geopolitical_leverage"],
        motivations=["revenue_maximization", "geopolitical_power"],
        daily_production_mboe=42.0,
        chokepoint_influence=["Strait_of_Hormuz", "Bab_el_Mandeb", "Suez_Canal"],
        price_manipulation_power=0.85,
        visibility=1.0,
    ),
    EnergyCartel(
        id="gazprom_system", name="Gazprom / Russian Energy Complex", type=ShadowType.ENERGY_CARTEL,
        description="Russia's energy weapon. Controls European gas supply routes.",
        headquarters="RU", influence_score=0.65, wealth_billion=80,
        active_regions=["Eurasia", "Europe"],
        allied_countries=["RU", "BY"],
        opposed_countries=["UA", "PL", "LT", "LV", "EE"],
        capabilities=["gas_supply_control", "pipeline_politics", "energy_blackmail"],
        motivations=["russian_leverage", "revenue", "european_dependency"],
        daily_production_mboe=12.0,
        pipeline_control=["Nord_Stream", "TurkStream", "Power_of_Siberia", "Yamal"],
        price_manipulation_power=0.60,
        visibility=0.8,
    ),
]


# ═══════════════════════════════════════════════════════════════
# SHADOW POWER ENGINE
# ═══════════════════════════════════════════════════════════════

class ShadowPowerEngine:
    """Manages shadow entities and their influence on the simulation."""

    def __init__(self, rng_seed: int | None = None) -> None:
        self.rng = random.Random(rng_seed)
        self.arms_dealers = list(ARMS_DEALERS)
        self.pmcs = list(PMCS)
        self.financials = list(FINANCIAL_BARONS)
        self.energy_cartels = list(ENERGY_CARTELS)
        self.all_entities: list[ShadowEntity] = (
            self.arms_dealers + self.pmcs + self.financials + self.energy_cartels
        )
        self.activity_log: list[dict[str, Any]] = []

    def get_entity(self, entity_id: str) -> ShadowEntity | None:
        for e in self.all_entities:
            if e.id == entity_id:
                return e
        return None

    def get_arms_suppliers(self, country_code: str) -> list[ArmsDealer]:
        """Which arms dealers supply this country?"""
        return [
            d for d in self.arms_dealers
            if country_code in d.export_destinations or country_code in d.allied_countries
        ]

    def get_active_pmcs(self, region: str) -> list[PMC]:
        """Which PMCs operate in this region?"""
        return [p for p in self.pmcs if region in p.active_regions or "Global" in p.active_regions]

    def calculate_war_profit(self, belligerents: list[str], intensity: float) -> list[dict[str, Any]]:
        """Calculate which shadow entities profit from a conflict."""
        profits: list[dict[str, Any]] = []
        for dealer in self.arms_dealers:
            supplying = [c for c in belligerents if c in dealer.export_destinations or c in dealer.allied_countries]
            if supplying:
                revenue_boost = intensity * len(supplying) * dealer.annual_revenue_billion * 0.1
                profits.append({
                    "entity": dealer.name,
                    "type": "arms_dealer",
                    "revenue_boost_billion": round(revenue_boost, 2),
                    "supplying": supplying,
                })
        for pmc in self.pmcs:
            involved = [c for c in belligerents if c in pmc.allied_countries]
            if involved:
                profits.append({
                    "entity": pmc.name,
                    "type": "pmc",
                    "personnel_deployed": int(pmc.personnel_count * intensity * 0.3),
                    "supporting": involved,
                })
        return profits

    def apply_sanctions_effect(self, target_country: str) -> dict[str, Any]:
        """Calculate shadow network response to sanctions."""
        evasion_networks = [
            f for f in self.financials
            if target_country in f.allied_countries and f.sanctions_evasion_capability > 0.3
        ]
        total_evasion = sum(f.sanctions_evasion_capability for f in evasion_networks) / max(1, len(evasion_networks))
        return {
            "target": target_country,
            "evasion_capability": round(total_evasion, 2),
            "networks_active": len(evasion_networks),
            "networks": [f.name for f in evasion_networks],
        }

    def energy_weapon_effect(self, aggressor: str, targets: list[str]) -> dict[str, Any]:
        """Calculate effect of energy weaponization."""
        relevant_cartels = [
            c for c in self.energy_cartels
            if aggressor in c.allied_countries
        ]
        if not relevant_cartels:
            return {"effect": "none", "price_impact": 0}

        total_power = sum(c.price_manipulation_power for c in relevant_cartels)
        price_spike = total_power * 50  # % increase in energy prices
        return {
            "aggressor": aggressor,
            "targets": targets,
            "cartels_involved": [c.name for c in relevant_cartels],
            "oil_price_spike_pct": round(price_spike, 1),
            "gas_price_spike_pct": round(price_spike * 1.5, 1),
            "affected_stability_reduction": round(total_power * 0.15, 2),
        }

    def tick(self, year: int, active_wars: list[tuple[str, str]], world_stability: dict[str, float]) -> list[dict[str, Any]]:
        """Process shadow power activities for this turn."""
        events: list[dict[str, Any]] = []

        for war in active_wars:
            profits = self.calculate_war_profit(list(war), 0.7)
            for p in profits:
                events.append({"year": year, "type": "war_profiteering", **p})

        for pmc in self.pmcs:
            for country in pmc.allied_countries:
                stab = world_stability.get(country, 0.5)
                if stab < 0.3 and self.rng.random() < 0.3:
                    events.append({
                        "year": year,
                        "type": "pmc_deployment",
                        "entity": pmc.name,
                        "country": country,
                        "personnel": int(pmc.personnel_count * 0.1),
                    })

        self.activity_log.extend(events)
        return events
