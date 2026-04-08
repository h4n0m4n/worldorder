"""News ingestion pipeline — pulls current events from RSS feeds.

Used to keep leader profiles and world state in sync with reality.
"""

from __future__ import annotations

import re
import xml.etree.ElementTree as ET
from dataclasses import dataclass, field
from typing import Any

import httpx


@dataclass
class NewsItem:
    title: str
    description: str
    link: str
    source: str
    published: str = ""
    countries_mentioned: list[str] = field(default_factory=list)


# Major international news RSS feeds
RSS_FEEDS: dict[str, str] = {
    "reuters_world": "https://feeds.reuters.com/Reuters/worldNews",
    "bbc_world": "https://feeds.bbci.co.uk/news/world/rss.xml",
    "aljazeera": "https://www.aljazeera.com/xml/rss/all.xml",
    "guardian_world": "https://www.theguardian.com/world/rss",
}

# Country name → code mapping for mention detection
COUNTRY_KEYWORDS: dict[str, str] = {
    "united states": "US", "america": "US", "washington": "US", "biden": "US",
    "russia": "RU", "moscow": "RU", "putin": "RU", "kremlin": "RU",
    "china": "CN", "beijing": "CN", "xi jinping": "CN",
    "turkey": "TR", "ankara": "TR", "erdogan": "TR",
    "ukraine": "UA", "kyiv": "UA", "zelensky": "UA",
    "iran": "IR", "tehran": "IR", "khamenei": "IR",
    "israel": "IL", "netanyahu": "IL", "tel aviv": "IL",
    "saudi": "SA", "riyadh": "SA", "mbs": "SA",
    "india": "IN", "delhi": "IN", "modi": "IN",
    "north korea": "KP", "pyongyang": "KP", "kim jong": "KP",
    "south korea": "KR", "seoul": "KR",
    "japan": "JP", "tokyo": "JP",
    "germany": "DE", "berlin": "DE",
    "france": "FR", "paris": "FR", "macron": "FR",
    "united kingdom": "GB", "britain": "GB", "london": "GB",
    "brazil": "BR", "brasilia": "BR",
    "pakistan": "PK", "islamabad": "PK",
    "egypt": "EG", "cairo": "EG",
    "nigeria": "NG", "abuja": "NG", "lagos": "NG",
    "australia": "AU", "canberra": "AU",
    "european union": "EU", "brussels": "EU",
}


async def fetch_feed(url: str, source_name: str) -> list[NewsItem]:
    """Parse a single RSS feed."""
    try:
        async with httpx.AsyncClient(timeout=15) as client:
            resp = await client.get(url, headers={"User-Agent": "WorldOrder/1.0"})
            if resp.status_code != 200:
                return []
    except Exception:
        return []

    items: list[NewsItem] = []
    try:
        root = ET.fromstring(resp.text)
        for item in root.iter("item"):
            title = _text(item, "title")
            desc = _text(item, "description")
            link = _text(item, "link")
            pub = _text(item, "pubDate")

            countries = _detect_countries(f"{title} {desc}")

            items.append(NewsItem(
                title=title,
                description=_clean_html(desc)[:500],
                link=link,
                source=source_name,
                published=pub,
                countries_mentioned=countries,
            ))
    except ET.ParseError:
        pass

    return items


async def fetch_all_feeds() -> list[NewsItem]:
    """Fetch news from all configured RSS feeds."""
    import asyncio
    tasks = [fetch_feed(url, name) for name, url in RSS_FEEDS.items()]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    all_items: list[NewsItem] = []
    for r in results:
        if isinstance(r, list):
            all_items.extend(r)
    return all_items


def filter_geopolitical(items: list[NewsItem]) -> list[NewsItem]:
    """Keep only items that mention at least one tracked country."""
    return [item for item in items if item.countries_mentioned]


def summarize_for_simulation(items: list[NewsItem], max_items: int = 20) -> str:
    """Create a text summary of current events for the simulation."""
    geo_items = filter_geopolitical(items)[:max_items]
    if not geo_items:
        return "No significant geopolitical news detected."

    lines = ["CURRENT REAL-WORLD EVENTS:"]
    for item in geo_items:
        countries = ", ".join(item.countries_mentioned)
        lines.append(f"  [{countries}] {item.title}")
    return "\n".join(lines)


def _detect_countries(text: str) -> list[str]:
    text_lower = text.lower()
    found: set[str] = set()
    for keyword, code in COUNTRY_KEYWORDS.items():
        if keyword in text_lower:
            found.add(code)
    return sorted(found)


def _text(element: ET.Element, tag: str) -> str:
    el = element.find(tag)
    return el.text.strip() if el is not None and el.text else ""


def _clean_html(text: str) -> str:
    return re.sub(r"<[^>]+>", "", text)
