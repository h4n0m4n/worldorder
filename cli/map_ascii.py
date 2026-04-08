"""ASCII world map renderer with country highlighting."""

from __future__ import annotations

from typing import Any

from rich.text import Text
from rich.console import Console

# Simplified ASCII world map with approximate country positions
# Each tuple: (row, col, char, country_code_or_None)
WORLD_MAP_TEMPLATE = r"""
        . _..::__:  ,-"-"._       |7       ,     _,.__
_.___ _ _<_>`!(._`.`-.    /        _._     `_ ,_/  '  '-._.---.-.__
>.{     " " `-==,',._\{  \  / {)     / _ ">_,-' `                mt._
  \_.:-diffg'm(googl)googl)g  \googl)g  \googl)g  \googl)g  \googl)g
"""

# Compact map with labeled regions
MAP_LINES = [
    "                          . ___ .                                        ",
    "                     ,--'       `--.                                     ",
    "                   ,'    EUROPE     `.    RUSSIA                         ",
    "                  / GB DE FR    UA    \\-----RU-----------\\              ",
    "                 |                     |                    |             ",
    "    .---.        |  TR    IR          CN    JP  KR         |             ",
    "   /     \\       |     SA    PK  IN        KP             |             ",
    "  | US    |      | EG                                     |             ",
    "  |       |      |  NG                                   AU             ",
    "   \\     /       |                                        |             ",
    "    `---'        |  BR                                    |             ",
    "                  \\                                      /              ",
    "                   `-.                              _.-'               ",
    "                      `----.________________.----'                     ",
]

COUNTRY_POSITIONS: dict[str, tuple[int, int]] = {
    "US": (7, 5),
    "GB": (3, 17),
    "DE": (3, 20),
    "FR": (3, 23),
    "UA": (3, 30),
    "RU": (3, 42),
    "TR": (5, 19),
    "IR": (5, 24),
    "SA": (6, 22),
    "PK": (6, 28),
    "IN": (6, 32),
    "CN": (5, 38),
    "JP": (5, 44),
    "KR": (5, 48),
    "KP": (6, 44),
    "EG": (7, 19),
    "NG": (8, 19),
    "BR": (10, 19),
    "AU": (8, 55),
    "IL": (5, 21),
    "EU": (3, 26),
}


def render_world_map(
    countries: dict[str, Any],
    highlight: dict[str, str] | None = None,
    console: Console | None = None,
) -> Text:
    """Render ASCII world map with colored country codes.

    Args:
        countries: dict of country_code -> CountryState
        highlight: dict of country_code -> color (e.g. {"US": "green", "RU": "red"})
    """
    if highlight is None:
        highlight = {}

    # Auto-color by power ranking
    if not highlight and countries:
        sorted_codes = sorted(
            countries.keys(),
            key=lambda c: getattr(countries[c], "composite_power", 0),
            reverse=True,
        )
        for i, code in enumerate(sorted_codes):
            if i < 3:
                highlight[code] = "bold green"
            elif i < 8:
                highlight[code] = "yellow"
            elif i < 15:
                highlight[code] = "cyan"
            else:
                highlight[code] = "dim"

    text = Text()
    text.append("╔" + "═" * 72 + "╗\n", style="blue")
    text.append("║", style="blue")
    text.append("  WORLD ORDER — Global Power Map".center(72), style="bold white")
    text.append("║\n", style="blue")
    text.append("╠" + "═" * 72 + "╣\n", style="blue")

    for line in MAP_LINES:
        text.append("║ ", style="blue")
        i = 0
        padded = line.ljust(70)
        while i < len(padded):
            found = False
            for code, (_, _) in COUNTRY_POSITIONS.items():
                if padded[i: i + len(code)] == code:
                    style = highlight.get(code, "white")
                    text.append(code, style=style)
                    i += len(code)
                    found = True
                    break
            if not found:
                text.append(padded[i], style="dim blue")
                i += 1
        text.append(" ║\n", style="blue")

    text.append("╠" + "═" * 72 + "╣\n", style="blue")

    # Legend
    text.append("║ ", style="blue")
    legend = " [TOP 3] "
    text.append(legend, style="bold green")
    text.append(" [TOP 8] ", style="yellow")
    text.append(" [TOP 15] ", style="cyan")
    text.append(" [OTHER] ", style="dim")
    remaining = 70 - len(legend) * 4 + 18
    text.append(" " * max(0, remaining), style="blue")
    text.append("║\n", style="blue")
    text.append("╚" + "═" * 72 + "╝\n", style="blue")

    return text


def render_conflict_map(
    countries: dict[str, Any],
    wars: list[tuple[str, str]],
    tensions: list[tuple[str, str]],
) -> Text:
    """Render map highlighting active conflicts."""
    highlight: dict[str, str] = {}
    war_codes = set()
    for a, b in wars:
        war_codes.add(a)
        war_codes.add(b)
    for code in war_codes:
        highlight[code] = "bold red"
    tension_codes = set()
    for a, b in tensions:
        tension_codes.add(a)
        tension_codes.add(b)
    for code in tension_codes:
        if code not in highlight:
            highlight[code] = "yellow"
    for code in countries:
        if code not in highlight:
            highlight[code] = "dim"

    return render_world_map(countries, highlight)
