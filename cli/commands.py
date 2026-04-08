"""Extended CLI commands — scenarios, news, wiki, war, predict, shadows."""

from __future__ import annotations

import asyncio
import json
from pathlib import Path
from typing import Any

import click
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich import box

from engine.config import DATA_DIR

console = Console()


@click.command()
def scenarios() -> None:
    """List available pre-built scenarios."""
    events_path = DATA_DIR / "historical" / "events.json"
    with open(events_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    templates = data.get("scenario_templates", [])
    table = Table(title="[bold]Available Scenarios[/]", box=box.ROUNDED)
    table.add_column("ID", width=18)
    table.add_column("Title", min_width=25)
    table.add_column("Year", width=6)
    table.add_column("Key Countries", min_width=20)
    table.add_column("Description", min_width=35)

    for t in templates:
        table.add_row(
            t["id"],
            f"[bold]{t['title']}[/]",
            str(t["start_year"]),
            ", ".join(t["key_countries"]),
            t["description"],
        )
    console.print(table)


@click.command()
def news() -> None:
    """Fetch latest geopolitical news from RSS feeds."""
    from data.scrapers.news_feed import fetch_all_feeds, filter_geopolitical

    console.print("[bold cyan]Fetching news feeds...[/]")
    items = asyncio.run(fetch_all_feeds())
    geo = filter_geopolitical(items)

    if not geo:
        console.print("[yellow]No geopolitical news found (feeds may be unavailable).[/]")
        return

    table = Table(title=f"[bold]Geopolitical News ({len(geo)} items)[/]", box=box.ROUNDED)
    table.add_column("Countries", width=12)
    table.add_column("Source", width=15)
    table.add_column("Headline", min_width=45)

    for item in geo[:25]:
        table.add_row(
            ", ".join(item.countries_mentioned),
            item.source,
            item.title,
        )
    console.print(table)


@click.command()
@click.argument("query")
def wiki(query: str) -> None:
    """Search Wikipedia for country/leader info."""
    from data.scrapers.wikipedia import search_wiki, fetch_summary

    results = asyncio.run(search_wiki(query, limit=5))
    if not results:
        console.print(f"[yellow]No Wikipedia results for '{query}'[/]")
        return

    for r in results:
        summary = asyncio.run(fetch_summary(r["title"]))
        console.print(Panel(
            summary.get("extract", "No extract available.")[:500],
            title=f"[bold]{r['title']}[/]",
            subtitle=summary.get("description", ""),
            border_style="cyan",
        ))


@click.command(name="map")
def show_map() -> None:
    """Display the ASCII world map with power rankings."""
    from data.loader import load_all_countries
    from cli.map_ascii import render_world_map

    countries = load_all_countries()
    country_dict = {c.code: c for c in countries}
    text = render_world_map(country_dict)
    console.print(text)


@click.command()
def history() -> None:
    """Show historical timeline of major events."""
    events_path = DATA_DIR / "historical" / "events.json"
    with open(events_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    for era_name, era_data in data.get("eras", {}).items():
        console.print(f"\n[bold yellow]═══ {era_name.upper().replace('_', ' ')} ═══[/]")
        for event in era_data.get("events", []):
            year = event["year"]
            year_str = f"{abs(year)} BC" if year < 0 else str(year)
            countries = ", ".join(event.get("countries", []))
            cat = event.get("category", "")
            cat_color = {
                "military": "red",
                "political": "yellow",
                "economic": "green",
                "diplomatic": "cyan",
                "technological": "magenta",
                "cultural": "blue",
                "social": "white",
            }.get(cat, "white")
            console.print(
                f"  [{cat_color}]{year_str:>8}[/] │ "
                f"[bold]{event['title']}[/] "
                f"[dim]({countries})[/]"
            )


@click.command()
@click.argument("attacker")
@click.argument("defender")
def war(attacker: str, defender: str) -> None:
    """Simulate a war between two countries (use country codes, e.g. US RU)."""
    from data.mass_loader import load_all_countries_mass
    from engine.world_state import WorldState
    from engine.event_bus import EventBus
    from engine.war_simulator import WarSimulator

    countries = load_all_countries_mass()
    world = WorldState()
    for c in countries:
        world.add_country(c)
    event_bus = EventBus()
    sim = WarSimulator(world, event_bus)

    attacker = attacker.upper()
    defender = defender.upper()

    # First show analysis without starting war
    console.print(f"\n[bold red]═══ WAR SCENARIO ANALYSIS: {attacker} vs {defender} ═══[/]\n")

    narrative = sim.generate_scenario_analysis(attacker, defender)
    for line in narrative:
        if line.startswith("═══"):
            console.print(f"[bold cyan]{line}[/]")
        elif line.startswith("FORCE") or line.startswith("ALLIANCE") or line.startswith("ECONOMIC") or line.startswith("NUCLEAR") or line.startswith("PROJECTED") or line.startswith("OUTCOME"):
            console.print(f"\n[bold yellow]{line}[/]")
        elif "█" in line:
            console.print(f"[bold]{line}[/]")
        elif "⚠" in line:
            console.print(f"[bold red]{line}[/]")
        else:
            console.print(f"  {line}")

    # Show arms suppliers
    from engine.shadow_powers import ShadowPowerEngine
    shadows = ShadowPowerEngine()
    att_suppliers = shadows.get_arms_suppliers(attacker)
    def_suppliers = shadows.get_arms_suppliers(defender)

    if att_suppliers or def_suppliers:
        console.print(f"\n[bold magenta]SHADOW POWERS INVOLVED:[/]")
        if att_suppliers:
            console.print(f"  Arms supplying {attacker}:")
            for s in att_suppliers:
                console.print(f"    - {s.name} (${s.annual_revenue_billion:.0f}B revenue)")
        if def_suppliers:
            console.print(f"  Arms supplying {defender}:")
            for s in def_suppliers:
                console.print(f"    - {s.name} (${s.annual_revenue_billion:.0f}B revenue)")

    profits = shadows.calculate_war_profit([attacker, defender], 0.7)
    if profits:
        console.print(f"\n[bold magenta]WAR PROFITEERS:[/]")
        for p in profits:
            if "revenue_boost_billion" in p:
                console.print(f"    {p['entity']}: +${p['revenue_boost_billion']:.1f}B revenue boost")
            elif "personnel_deployed" in p:
                console.print(f"    {p['entity']}: {p['personnel_deployed']:,} personnel deployed")


@click.command()
@click.option("--timeframe", "-t", type=int, default=10, help="Prediction timeframe in years")
@click.option("--top", "-n", type=int, default=25, help="Number of top predictions to show")
@click.option("--country", "-c", type=str, default=None, help="Filter by country code")
def predict(timeframe: int, top: int, country: str | None) -> None:
    """Generate future predictions based on current world state."""
    from data.mass_loader import load_all_countries_mass
    from engine.world_state import WorldState
    from engine.future_predictor import FuturePredictionEngine

    countries = load_all_countries_mass()
    world = WorldState()
    for c in countries:
        world.add_country(c)

    predictor = FuturePredictionEngine(world)
    predictor.generate_all_predictions(timeframe=timeframe)

    if country:
        preds = predictor.get_risks_for_country(country.upper())
        console.print(f"\n[bold cyan]═══ PREDICTIONS FOR {country.upper()} (next {timeframe} years) ═══[/]\n")
    else:
        preds = predictor.get_top_risks(top)
        console.print(f"\n[bold cyan]═══ TOP {top} GLOBAL PREDICTIONS (next {timeframe} years) ═══[/]\n")

    for i, p in enumerate(preds[:top], 1):
        prob_pct = p.probability * 100
        impact_bar = "█" * int(p.impact_severity * 10) + "░" * (10 - int(p.impact_severity * 10))

        if prob_pct > 30:
            prob_color = "bold red"
        elif prob_pct > 15:
            prob_color = "yellow"
        else:
            prob_color = "green"

        cat_colors = {
            "war": "red", "economic_crisis": "yellow", "regime_change": "magenta",
            "nuclear_event": "bold red", "territorial_dispute": "red",
            "energy_crisis": "yellow", "technology_breakthrough": "cyan",
        }
        cat_color = cat_colors.get(p.category.value, "white")

        console.print(Panel(
            f"[{prob_color}]Probability: {prob_pct:.1f}%[/] | "
            f"Confidence: {p.confidence:.0%} | "
            f"Impact: [{impact_bar}] {p.impact_severity:.0%}\n"
            f"Countries: [cyan]{', '.join(p.affected_countries)}[/]\n"
            f"{p.description}\n"
            + (f"\n[dim]Triggers: {'; '.join(p.triggers[:3])}[/]" if p.triggers else "")
            + (f"\n[dim]Domino effects: {'; '.join(p.domino_effects[:3])}[/]" if p.domino_effects else ""),
            title=f"[bold]{i}. [{cat_color}]{p.category.value.upper()}[/] {p.title}[/]",
            border_style=cat_color,
        ))


@click.command()
def shadows() -> None:
    """Show all shadow powers — arms dealers, PMCs, financial networks, energy cartels."""
    from engine.shadow_powers import ShadowPowerEngine

    engine = ShadowPowerEngine()

    # Arms Dealers
    console.print("\n[bold red]═══ ARMS DEALERS & DEFENSE CORPORATIONS ═══[/]\n")
    table = Table(box=box.ROUNDED, show_lines=True)
    table.add_column("Name", min_width=30)
    table.add_column("HQ", width=4)
    table.add_column("Revenue", width=10)
    table.add_column("Share", width=7)
    table.add_column("Key Weapons", min_width=30)
    table.add_column("Clients", min_width=20)

    for d in engine.arms_dealers:
        table.add_row(
            f"[bold]{d.name}[/]",
            d.headquarters,
            f"${d.annual_revenue_billion:.0f}B",
            f"{d.market_share:.0%}" if d.market_share > 0 else "—",
            ", ".join(d.weapons_types[:4]),
            ", ".join(d.export_destinations[:6]),
        )
    console.print(table)

    # PMCs
    console.print("\n[bold magenta]═══ PRIVATE MILITARY COMPANIES ═══[/]\n")
    table2 = Table(box=box.ROUNDED, show_lines=True)
    table2.add_column("Name", min_width=25)
    table2.add_column("Patron", width=8)
    table2.add_column("Personnel", width=10)
    table2.add_column("Combat XP", width=10)
    table2.add_column("Active In", min_width=25)
    table2.add_column("War Crimes", width=10)

    for p in engine.pmcs:
        table2.add_row(
            f"[bold]{p.name}[/]",
            p.patron_state or "—",
            f"{p.personnel_count:,}",
            f"{p.combat_experience:.0%}",
            ", ".join(p.active_conflicts[:3]) if p.active_conflicts else ", ".join(p.active_regions[:3]),
            str(p.war_crimes_allegations) if p.war_crimes_allegations > 0 else "—",
        )
    console.print(table2)

    # Financial Networks
    console.print("\n[bold yellow]═══ FINANCIAL POWER NETWORKS ═══[/]\n")
    for f in engine.financials:
        aum = f"${f.assets_under_management_billion:.0f}B AUM" if f.assets_under_management_billion > 0 else ""
        evasion = f"Sanctions evasion: {f.sanctions_evasion_capability:.0%}" if f.sanctions_evasion_capability > 0 else ""
        console.print(Panel(
            f"{f.description}\n"
            f"[dim]{aum} {evasion}[/]\n"
            f"Influence: {f.influence_score:.0%} | Visibility: {f.visibility:.0%}",
            title=f"[bold]{f.name}[/] ({f.headquarters})",
            border_style="yellow",
        ))

    # Energy Cartels
    console.print("\n[bold green]═══ ENERGY CARTELS ═══[/]\n")
    for c in engine.energy_cartels:
        console.print(Panel(
            f"{c.description}\n"
            f"Production: {c.daily_production_mboe:.0f}M boe/day | "
            f"Price manipulation: {c.price_manipulation_power:.0%}\n"
            f"Chokepoints: {', '.join(c.chokepoint_influence)}" if c.chokepoint_influence else c.description,
            title=f"[bold]{c.name}[/]",
            border_style="green",
        ))
