"""Wikipedia scraper — enriches country and leader profiles with real data."""

from __future__ import annotations

import re
from typing import Any

import httpx

WIKI_API = "https://en.wikipedia.org/api/rest_v1"
WIKI_SEARCH = "https://en.wikipedia.org/w/api.php"


async def fetch_summary(title: str) -> dict[str, Any]:
    """Fetch Wikipedia summary for a given page title."""
    url = f"{WIKI_API}/page/summary/{title.replace(' ', '_')}"
    async with httpx.AsyncClient(timeout=15) as client:
        resp = await client.get(url, headers={"User-Agent": "WorldOrder/1.0"})
        if resp.status_code != 200:
            return {"error": f"HTTP {resp.status_code}", "title": title}
        data = resp.json()
        return {
            "title": data.get("title", title),
            "extract": data.get("extract", ""),
            "description": data.get("description", ""),
            "thumbnail": data.get("thumbnail", {}).get("source"),
        }


async def search_wiki(query: str, limit: int = 3) -> list[dict[str, str]]:
    """Search Wikipedia and return top results."""
    params = {
        "action": "query",
        "list": "search",
        "srsearch": query,
        "srlimit": limit,
        "format": "json",
    }
    async with httpx.AsyncClient(timeout=15) as client:
        resp = await client.get(
            WIKI_SEARCH,
            params=params,
            headers={"User-Agent": "WorldOrder/1.0"},
        )
        if resp.status_code != 200:
            return []
        results = resp.json().get("query", {}).get("search", [])
        return [
            {"title": r["title"], "snippet": _clean_html(r.get("snippet", ""))}
            for r in results
        ]


async def fetch_country_info(country_name: str) -> dict[str, Any]:
    """Fetch key info about a country from Wikipedia."""
    summary = await fetch_summary(country_name)
    return {
        "name": country_name,
        "summary": summary.get("extract", ""),
        "description": summary.get("description", ""),
    }


async def fetch_leader_info(leader_name: str) -> dict[str, Any]:
    """Fetch key info about a world leader from Wikipedia."""
    summary = await fetch_summary(leader_name)
    return {
        "name": leader_name,
        "bio": summary.get("extract", ""),
        "description": summary.get("description", ""),
        "image": summary.get("thumbnail"),
    }


async def enrich_all_profiles(
    countries: list[str],
    leaders: list[str],
) -> dict[str, Any]:
    """Batch-fetch Wikipedia data for all countries and leaders."""
    import asyncio

    country_tasks = [fetch_country_info(c) for c in countries]
    leader_tasks = [fetch_leader_info(l) for l in leaders]

    country_results = await asyncio.gather(*country_tasks, return_exceptions=True)
    leader_results = await asyncio.gather(*leader_tasks, return_exceptions=True)

    return {
        "countries": {
            c: r for c, r in zip(countries, country_results)
            if not isinstance(r, Exception)
        },
        "leaders": {
            l: r for l, r in zip(leaders, leader_results)
            if not isinstance(r, Exception)
        },
    }


def _clean_html(text: str) -> str:
    return re.sub(r"<[^>]+>", "", text)
