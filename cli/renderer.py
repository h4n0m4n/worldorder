"""Rich terminal renderer — beautiful output for the simulation."""

from __future__ import annotations

from typing import Any

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.columns import Columns
from rich.layout import Layout
from rich.live import Live
from rich import box

from engine.world_state import WorldState, CountryState, RelationType
from engine.event_bus import SimEvent, EventSeverity
from agents.decision import LeaderDecision, Mood


SEVERITY_STYLES = {
    EventSeverity.LOW: "dim",
    EventSeverity.MEDIUM: "yellow",
    EventSeverity.HIGH: "bold red",
    EventSeverity.CRITICAL: "bold white on red",
}

MOOD_DISPLAY = {
    Mood.CONFIDENT: ("[green]CONFIDENT[/]", "😎"),
    Mood.ANXIOUS: ("[yellow]ANXIOUS[/]", "😰"),
    Mood.AGGRESSIVE: ("[red]AGGRESSIVE[/]", "😡"),
    Mood.DEFENSIVE: ("[blue]DEFENSIVE[/]", "🛡"),
    Mood.OPPORTUNISTIC: ("[magenta]OPPORTUNISTIC[/]", "🦊"),
    Mood.DESPERATE: ("[bold red]DESPERATE[/]", "💀"),
}


class SimulationRenderer:
    """Handles all terminal rendering for the simulation."""

    def __init__(self, console: Console | None = None) -> None:
        self.console = console or Console()

    def render_banner(self) -> None:
        banner = r"""
 ██╗    ██╗ ██████╗ ██████╗ ██╗     ██████╗      ██████╗ ██████╗ ██████╗ ███████╗██████╗
 ██║    ██║██╔═══██╗██╔══██╗██║     ██╔══██╗    ██╔═══██╗██╔══██╗██╔══██╗██╔════╝██╔══██╗
 ██║ █╗ ██║██║   ██║██████╔╝██║     ██║  ██║    ██║   ██║██████╔╝██║  ██║█████╗  ██████╔╝
 ██║███╗██║██║   ██║██╔══██╗██║     ██║  ██║    ██║   ██║██╔══██╗██║  ██║██╔══╝  ██╔══██╗
 ╚███╔███╔╝╚██████╔╝██║  ██║███████╗██████╔╝    ╚██████╔╝██║  ██║██████╔╝███████╗██║  ██║
  ╚══╝╚══╝  ╚═════╝ ╚═╝  ╚═╝╚══════╝╚═════╝      ╚═════╝ ╚═╝  ╚═╝╚═════╝ ╚══════╝╚═╝  ╚═╝
"""
        self.console.print(Text(banner, style="bold cyan"))
        self.console.print(
            "[dim italic]  History doesn't repeat itself, but it rhymes. "
            "Now you can hear the next verse.[/]\n"
        )

    def render_config(self, config: Any) -> None:
        self.console.print(Panel(
            f"Era: [bold]{config.era.value}[/] | "
            f"Years: {config.start_year}–{config.end_year}\n"
            f"Turns: {config.max_turns} | "
            f"Scale: 1 turn = 1 {config.time_scale.value}\n"
            f"Mode: [bold]{config.game_mode.value.upper()}[/] | "
            f"LLM: {config.llm_provider}/{config.llm_model}",
            title="[bold green]Simulation Configuration[/]",
            border_style="green",
        ))

    def render_turn_header(self, turn: int, year: int, max_turns: int) -> None:
        self.console.print()
        self.console.rule(
            f"[bold yellow]TURN {turn + 1}/{max_turns} — YEAR {year}[/]",
            style="yellow",
        )
        self.console.print()

    def render_events(self, events: list[SimEvent], max_show: int = 8) -> None:
        if not events:
            return
        table = Table(
            title="[bold]Breaking Events[/]",
            box=box.ROUNDED,
            show_lines=True,
            title_style="bold red",
        )
        table.add_column("SEV", width=10, justify="center")
        table.add_column("TYPE", width=14)
        table.add_column("EVENT", min_width=40)
        table.add_column("FROM", width=6, justify="center")

        for e in events[-max_show:]:
            sev_style = SEVERITY_STYLES.get(e.severity, "white")
            table.add_row(
                Text(e.severity.value.upper(), style=sev_style),
                e.category.value.title(),
                f"[bold]{e.title}[/]\n{e.description[:150]}",
                e.source_country or "—",
            )
        self.console.print(table)

    def render_leader_decision(self, code: str, decision: dict[str, Any]) -> None:
        mood_str = decision.get("mood", "confident")
        try:
            mood = Mood(mood_str)
            display, emoji = MOOD_DISPLAY.get(mood, (mood_str, ""))
        except ValueError:
            display, emoji = mood_str, ""

        statement = decision.get("public_statement", "...")
        actions = decision.get("actions", [])

        content = f'[italic]"{statement}"[/italic]\n'
        if actions:
            content += "\n[bold]Actions:[/]\n"
            for a in actions:
                intensity = float(a.get("intensity", 0.5))
                filled = int(intensity * 10)
                bar = "█" * filled + "░" * (10 - filled)
                atype = a.get("type", "?").upper().replace("_", " ")
                target = a.get("target", "?")
                detail = a.get("detail", "")
                content += f"  {emoji} [{bar}] {atype} → {target}: {detail}\n"

        self.console.print(Panel(
            content,
            title=f"[bold]{code}[/] | Mood: {display}",
            border_style="cyan",
            expand=True,
        ))

    def render_all_decisions(self, decisions: dict[str, Any]) -> None:
        for code, dec in decisions.items():
            self.render_leader_decision(code, dec)

    def render_power_rankings(self, world: WorldState) -> None:
        table = Table(
            title="[bold]Global Power Rankings[/]",
            box=box.HEAVY_EDGE,
            title_style="bold white",
        )
        table.add_column("#", width=3, justify="right")
        table.add_column("Country", min_width=22)
        table.add_column("Power", width=8, justify="right")
        table.add_column("GDP", width=10, justify="right")
        table.add_column("Military", width=10, justify="center")
        table.add_column("Stability", width=10, justify="center")
        table.add_column("Status", min_width=18)

        for i, c in enumerate(world.ranked_by_power(), 1):
            status_parts = []
            if c.economy.gdp_growth < 0:
                status_parts.append("[red]RECESSION[/]")
            if c.economy.inflation > 10:
                status_parts.append("[yellow]HIGH INFL[/]")
            if c.domestic.stability < 0.4:
                status_parts.append("[red]UNSTABLE[/]")
            wars = [k for k, v in c.relations.items() if v == RelationType.WAR]
            if wars:
                status_parts.append(f"[bold red]WAR[/]")
            if c.military.nuclear:
                status_parts.append("[magenta]☢[/]")

            rank_style = "bold green" if i <= 3 else "yellow" if i <= 8 else "white"
            table.add_row(
                Text(str(i), style=rank_style),
                f"[bold]{c.name}[/] ({c.code})",
                f"{c.composite_power:.1f}",
                f"${c.economy.gdp_trillion:.1f}T",
                f"{c.military.power_index:.0%}",
                self._stability_bar(c.domestic.stability),
                " ".join(status_parts) or "[green]Stable[/]",
            )
        self.console.print(table)

    def render_diplomacy_web(self, world: WorldState) -> None:
        """Show key diplomatic relationships."""
        table = Table(
            title="[bold]Diplomatic Tensions[/]",
            box=box.SIMPLE,
        )
        table.add_column("Country", width=8)
        table.add_column("Hostile / War Relations", min_width=40)

        for c in world.ranked_by_power():
            hostile = []
            for k, v in c.relations.items():
                if v in (RelationType.HOSTILE, RelationType.WAR, RelationType.TENSE):
                    style = "bold red" if v == RelationType.WAR else "red" if v == RelationType.HOSTILE else "yellow"
                    hostile.append(f"[{style}]{k} ({v.value})[/]")
            if hostile:
                table.add_row(f"[bold]{c.code}[/]", ", ".join(hostile))

        if table.row_count > 0:
            self.console.print(table)

    @staticmethod
    def _stability_bar(value: float) -> str:
        filled = int(value * 10)
        if value >= 0.7:
            color = "green"
        elif value >= 0.4:
            color = "yellow"
        else:
            color = "red"
        return f"[{color}]{'█' * filled}{'░' * (10 - filled)}[/] {value:.0%}"

    def render_simulation_end(self, world: WorldState, total_events: int) -> None:
        self.console.print()
        self.console.rule("[bold red]SIMULATION COMPLETE[/]", style="red")
        self.console.print(f"\n[bold]Final Year:[/] {world.year}")
        self.console.print(f"[bold]Total Turns:[/] {world.turn}")
        self.console.print(f"[bold]Total Events:[/] {total_events}")
        self.console.print()
        self.render_power_rankings(world)
