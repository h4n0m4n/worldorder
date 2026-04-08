"""Extended CLI commands — scenarios, news, wiki enrichment."""

from __future__ import annotations

import asyncio
import json
from pathlib import Path
from typing import Any

import click
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
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
