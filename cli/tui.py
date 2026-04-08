"""WORLD ORDER — Cinematic Textual TUI.

Full-screen terminal application with animations, live world map,
leader cards, event feed, power rankings, and crisis injection.
"""

from __future__ import annotations

import asyncio
from typing import Any

from textual import on, work
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Container, Horizontal, Vertical, ScrollableContainer
from textual.css.query import NoMatches
from textual.reactive import reactive
from textual.screen import Screen
from textual.timer import Timer
from textual.widgets import (
    Header,
    Footer,
    Static,
    Label,
    Button,
    DataTable,
    Input,
    TextArea,
    ProgressBar,
    LoadingIndicator,
    RichLog,
    Select,
    Switch,
)
from rich.text import Text
from rich.panel import Panel
from rich.table import Table
from rich import box

from engine.config import SimulationConfig, Era, TimeScale, GameMode
from engine.simulation import Simulation
from engine.event_bus import SimEvent, EventSeverity
from data.mass_loader import load_all_countries_mass
from llm.registry import get_provider, available_providers


# ═══════════════════════════════════════════════════════════════
# CSS THEME — Dark cinematic military aesthetic
# ═══════════════════════════════════════════════════════════════
CSS = """
Screen {
    background: #0a0a0f;
}

#banner {
    width: 100%;
    height: auto;
    content-align: center middle;
    text-align: center;
    color: #4a9eff;
    padding: 1 0;
}

#subtitle {
    text-align: center;
    color: #666;
    text-style: italic;
    padding: 0 0 1 0;
}

/* ─── MAIN LAYOUT ─── */
#main-container {
    height: 1fr;
}

#left-panel {
    width: 70%;
    height: 100%;
    border-right: solid #1a1a2e;
}

#right-panel {
    width: 30%;
    height: 100%;
}

/* ─── POWER TABLE ─── */
#power-table {
    height: 1fr;
    border: solid #1a1a2e;
    background: #0d0d15;
}

DataTable {
    background: #0d0d15;
}

DataTable > .datatable--header {
    background: #1a1a2e;
    color: #4a9eff;
    text-style: bold;
}

DataTable > .datatable--cursor {
    background: #1a1a3e;
}

/* ─── EVENT LOG ─── */
#event-log {
    height: 40%;
    border: solid #1a1a2e;
    background: #0d0d15;
    padding: 0 1;
}

#event-log-title {
    color: #ff4a4a;
    text-style: bold;
    padding: 1 0 0 0;
}

RichLog {
    background: #0d0d15;
    scrollbar-size: 1 1;
}

/* ─── DECISIONS PANEL ─── */
#decisions-panel {
    height: 60%;
    border: solid #1a1a2e;
    background: #0d0d15;
    padding: 0 1;
}

#decisions-title {
    color: #9b59b6;
    text-style: bold;
    padding: 1 0 0 0;
}

/* ─── STATUS BAR ─── */
#status-bar {
    dock: bottom;
    height: 3;
    background: #12121a;
    border-top: solid #1a1a2e;
    padding: 0 2;
}

#year-display {
    color: #ffd700;
    text-style: bold;
    width: 20;
}

#turn-display {
    color: #4a9eff;
    width: 20;
}

#country-count {
    color: #4aff4a;
    width: 25;
}

#event-count {
    color: #ff4a4a;
    width: 20;
}

/* ─── CONTROLS ─── */
#controls {
    dock: bottom;
    height: 3;
    background: #1a1a2e;
    padding: 0 1;
    layout: horizontal;
}

Button {
    margin: 0 1;
    min-width: 16;
}

Button.btn-primary {
    background: #1a6b3a;
    color: #fff;
    border: none;
}

Button.btn-primary:hover {
    background: #2a8b4a;
}

Button.btn-danger {
    background: #6b1a1a;
    color: #fff;
    border: none;
}

Button.btn-danger:hover {
    background: #8b2a2a;
}

Button.btn-info {
    background: #1a3a6b;
    color: #fff;
    border: none;
}

Button.btn-info:hover {
    background: #2a4a8b;
}

/* ─── CONFIG SCREEN ─── */
#config-screen {
    align: center middle;
}

#config-panel {
    width: 80;
    height: auto;
    max-height: 40;
    background: #12121a;
    border: double #4a9eff;
    padding: 2;
}

#config-title {
    text-align: center;
    color: #4a9eff;
    text-style: bold;
    padding: 0 0 1 0;
}

.config-row {
    height: 3;
    layout: horizontal;
    padding: 0 1;
}

.config-label {
    width: 20;
    color: #888;
    padding: 1 0;
}

.config-input {
    width: 1fr;
}

Input {
    background: #0a0a0f;
    border: solid #2a2a3e;
    color: #e0e0e0;
}

Input:focus {
    border: solid #4a9eff;
}

Select {
    background: #0a0a0f;
    border: solid #2a2a3e;
}

/* ─── LOADING ─── */
#loading-container {
    align: center middle;
    height: 100%;
}

LoadingIndicator {
    color: #4a9eff;
}

/* ─── CRISIS MODAL ─── */
#crisis-modal {
    align: center middle;
}

#crisis-panel {
    width: 70;
    height: auto;
    background: #1a0a0a;
    border: double #ff4a4a;
    padding: 2;
}

#crisis-title-label {
    color: #ff4a4a;
    text-style: bold;
    text-align: center;
    padding: 0 0 1 0;
}
"""


# ═══════════════════════════════════════════════════════════════
# SPLASH SCREEN
# ═══════════════════════════════════════════════════════════════
class SplashScreen(Screen):
    BINDINGS = [Binding("enter", "proceed", "Continue")]

    def compose(self) -> ComposeResult:
        yield Static(
            Text.from_markup(
                "\n\n"
                "[bold cyan]"
                " ██╗    ██╗ ██████╗ ██████╗ ██╗     ██████╗\n"
                " ██║    ██║██╔═══██╗██╔══██╗██║     ██╔══██╗\n"
                " ██║ █╗ ██║██║   ██║██████╔╝██║     ██║  ██║\n"
                " ██║███╗██║██║   ██║██╔══██╗██║     ██║  ██║\n"
                " ╚███╔███╔╝╚██████╔╝██║  ██║███████╗██████╔╝\n"
                "  ╚══╝╚══╝  ╚═════╝ ╚═╝  ╚═╝╚══════╝╚═════╝\n"
                "\n"
                "  ██████╗ ██████╗ ██████╗ ███████╗██████╗\n"
                " ██╔═══██╗██╔══██╗██╔══██╗██╔════╝██╔══██╗\n"
                " ██║   ██║██████╔╝██║  ██║█████╗  ██████╔╝\n"
                " ██║   ██║██╔══██╗██║  ██║██╔══╝  ██╔══██╗\n"
                " ╚██████╔╝██║  ██║██████╔╝███████╗██║  ██║\n"
                "  ╚═════╝ ╚═╝  ╚═╝╚═════╝ ╚══════╝╚═╝  ╚═╝\n"
                "[/]\n"
                "[dim italic]History doesn't repeat itself, but it rhymes.[/]\n"
                "[dim italic]Now you can hear the next verse.[/]\n\n"
                "[bold yellow]176 NATIONS[/] · [bold cyan]DYNAMIC LEADERS[/] · [bold red]AI-POWERED DECISIONS[/]\n\n"
                "[dim]Press ENTER to begin[/]"
            ),
            id="banner",
        )

    def action_proceed(self) -> None:
        self.app.push_screen(ConfigScreen())


# ═══════════════════════════════════════════════════════════════
# CONFIG SCREEN
# ═══════════════════════════════════════════════════════════════
class ConfigScreen(Screen):
    BINDINGS = [Binding("escape", "go_back", "Back")]

    def compose(self) -> ComposeResult:
        with Container(id="config-screen"):
            with Vertical(id="config-panel"):
                yield Static("[bold cyan]═══ SIMULATION CONFIGURATION ═══[/]", id="config-title")

                with Horizontal(classes="config-row"):
                    yield Label("Era:", classes="config-label")
                    yield Select(
                        [(e.value.replace("_", " ").title(), e.value) for e in Era],
                        value="contemporary",
                        id="era-select",
                        classes="config-input",
                    )

                with Horizontal(classes="config-row"):
                    yield Label("Start Year:", classes="config-label")
                    yield Input("2025", id="start-year", classes="config-input")

                with Horizontal(classes="config-row"):
                    yield Label("Max Turns:", classes="config-label")
                    yield Input("50", id="max-turns", classes="config-input")

                with Horizontal(classes="config-row"):
                    yield Label("LLM Provider:", classes="config-label")
                    yield Select(
                        [(p, p) for p in available_providers()],
                        value="ollama",
                        id="provider-select",
                        classes="config-input",
                    )

                with Horizontal(classes="config-row"):
                    yield Label("Model:", classes="config-label")
                    yield Input("llama3.1", id="model-input", classes="config-input")

                yield Static("")
                yield Button("▶  LAUNCH SIMULATION", id="launch-btn", classes="btn-primary", variant="success")

    @on(Button.Pressed, "#launch-btn")
    def on_launch(self) -> None:
        era = self.query_one("#era-select", Select).value
        start_year = int(self.query_one("#start-year", Input).value or "2025")
        max_turns = int(self.query_one("#max-turns", Input).value or "50")
        provider = self.query_one("#provider-select", Select).value
        model = self.query_one("#model-input", Input).value or "llama3.1"

        config = SimulationConfig(
            era=Era(era),
            start_year=start_year,
            end_year=start_year + max_turns * 2,
            max_turns=max_turns,
            llm_provider=provider,
            llm_model=model,
        )
        self.app.push_screen(SimulationScreen(config))

    def action_go_back(self) -> None:
        self.app.pop_screen()


# ═══════════════════════════════════════════════════════════════
# CRISIS INJECTION MODAL
# ═══════════════════════════════════════════════════════════════
class CrisisModal(Screen):
    BINDINGS = [Binding("escape", "dismiss_modal", "Close")]

    def __init__(self, sim: Simulation) -> None:
        super().__init__()
        self.sim = sim

    def compose(self) -> ComposeResult:
        with Container(id="crisis-modal"):
            with Vertical(id="crisis-panel"):
                yield Static("[bold red]⚡ INJECT CRISIS ⚡[/]", id="crisis-title-label")
                yield Label("Crisis Title:", classes="config-label")
                yield Input(placeholder="e.g. Nuclear Meltdown in Europe", id="crisis-title-input")
                yield Label("Description:", classes="config-label")
                yield Input(placeholder="Describe the crisis...", id="crisis-desc-input")
                yield Static("")
                yield Button("🔥 LAUNCH CRISIS", id="crisis-launch-btn", classes="btn-danger", variant="error")

    @on(Button.Pressed, "#crisis-launch-btn")
    def on_launch_crisis(self) -> None:
        title = self.query_one("#crisis-title-input", Input).value
        desc = self.query_one("#crisis-desc-input", Input).value
        if title:
            asyncio.create_task(self.sim.crisis_gen.inject_custom(title=title, description=desc or title))
        self.app.pop_screen()

    def action_dismiss_modal(self) -> None:
        self.app.pop_screen()


# ═══════════════════════════════════════════════════════════════
# MAIN SIMULATION SCREEN
# ═══════════════════════════════════════════════════════════════
class SimulationScreen(Screen):
    BINDINGS = [
        Binding("n", "next_turn", "Next Turn"),
        Binding("c", "inject_crisis", "Crisis"),
        Binding("q", "quit_sim", "Quit"),
        Binding("r", "refresh_rankings", "Refresh"),
    ]

    sim: Simulation | None = None
    is_processing = reactive(False)

    def __init__(self, config: SimulationConfig) -> None:
        super().__init__()
        self.config = config

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)

        with Horizontal(id="status-bar"):
            yield Static("[bold yellow]YEAR: ----[/]", id="year-display")
            yield Static("[bold cyan]TURN: --/--[/]", id="turn-display")
            yield Static("[bold green]NATIONS: ---[/]", id="country-count")
            yield Static("[bold red]EVENTS: ---[/]", id="event-count")

        with Horizontal(id="main-container"):
            with Vertical(id="left-panel"):
                yield DataTable(id="power-table")

            with Vertical(id="right-panel"):
                yield Static("[bold red]⚡ BREAKING EVENTS[/]", id="event-log-title")
                yield RichLog(id="event-log", wrap=True, markup=True, max_lines=200)
                yield Static("[bold magenta]🧠 LEADER DECISIONS[/]", id="decisions-title")
                yield RichLog(id="decisions-panel", wrap=True, markup=True, max_lines=200)

        with Horizontal(id="controls"):
            yield Button("▶ Next Turn [N]", id="next-btn", classes="btn-primary")
            yield Button("⚡ Crisis [C]", id="crisis-btn", classes="btn-danger")
            yield Button("✕ Quit [Q]", id="quit-btn", classes="btn-info")

        yield Footer()

    def on_mount(self) -> None:
        self.setup_simulation()

    @work(thread=False)
    async def setup_simulation(self) -> None:
        """Initialize the simulation."""
        llm = get_provider(self.config.llm_provider, model=self.config.llm_model)
        self.sim = Simulation(config=self.config, llm=llm)
        self.sim.setup()

        table = self.query_one("#power-table", DataTable)
        table.add_columns("#", "Country", "Power", "GDP", "Military", "Stability", "Pop(M)", "Leader", "Status")
        self.refresh_table()
        self.update_status()

        log = self.query_one("#event-log", RichLog)
        log.write("[bold cyan]Simulation initialized.[/]")
        log.write(f"[dim]{len(self.sim.world.countries)} nations loaded.[/]")

    def refresh_table(self) -> None:
        if not self.sim:
            return
        table = self.query_one("#power-table", DataTable)
        table.clear()

        for i, c in enumerate(self.sim.world.ranked_by_power(), 1):
            rank_style = "bold yellow" if i <= 3 else "bold white" if i <= 10 else ""
            nuke = " ☢" if c.military.nuclear else ""

            leader_name = "—"
            if self.sim.leader_system and c.code in self.sim.leader_system.current_leaders:
                leader_name = self.sim.leader_system.current_leaders[c.code].name
                if len(leader_name) > 22:
                    leader_name = leader_name[:20] + ".."

            status_parts = []
            if c.economy.gdp_growth < 0:
                status_parts.append("[red]REC[/]")
            if c.economy.inflation > 10:
                status_parts.append("[yellow]INF[/]")
            if c.domestic.stability < 0.4:
                status_parts.append("[red]⚠[/]")
            wars = [k for k, v in c.relations.items() if v.value == "war"]
            if wars:
                status_parts.append("[bold red]WAR[/]")

            stab_pct = int(c.domestic.stability * 100)
            stab_color = "green" if stab_pct > 60 else "yellow" if stab_pct > 35 else "red"

            table.add_row(
                Text(str(i), style=rank_style),
                Text(f"{c.name} ({c.code}){nuke}", style=rank_style),
                Text(f"{c.composite_power:.1f}", style="bold"),
                f"${c.economy.gdp_trillion:.2f}T",
                f"{c.military.power_index:.0%}",
                Text(f"{'█' * (stab_pct // 10)}{'░' * (10 - stab_pct // 10)} {stab_pct}%", style=stab_color),
                f"{c.domestic.population_million:.0f}",
                leader_name,
                Text.from_markup(" ".join(status_parts)) if status_parts else Text("OK", style="green"),
            )

    def update_status(self) -> None:
        if not self.sim:
            return
        w = self.sim.world
        self.query_one("#year-display", Static).update(f"[bold yellow]YEAR: {w.year}[/]")
        self.query_one("#turn-display", Static).update(f"[bold cyan]TURN: {w.turn}/{self.config.max_turns}[/]")
        self.query_one("#country-count", Static).update(f"[bold green]NATIONS: {len(w.countries)}[/]")
        self.query_one("#event-count", Static).update(f"[bold red]EVENTS: {self.sim.event_bus.total_events}[/]")

    @on(Button.Pressed, "#next-btn")
    def on_next_pressed(self) -> None:
        self.action_next_turn()

    @on(Button.Pressed, "#crisis-btn")
    def on_crisis_pressed(self) -> None:
        self.action_inject_crisis()

    @on(Button.Pressed, "#quit-btn")
    def on_quit_pressed(self) -> None:
        self.action_quit_sim()

    def action_next_turn(self) -> None:
        if self.is_processing or not self.sim:
            return
        self.run_next_turn()

    @work(thread=False)
    async def run_next_turn(self) -> None:
        self.is_processing = True
        btn = self.query_one("#next-btn", Button)
        btn.label = "⏳ Processing..."
        btn.disabled = True

        try:
            result = await self.sim.run_turn()

            event_log = self.query_one("#event-log", RichLog)
            recent = self.sim.event_bus.history(last_n=5)
            for e in recent:
                sev_color = {"low": "dim", "medium": "yellow", "high": "red", "critical": "bold white on red"}.get(e.severity.value, "white")
                src = f" [{e.source_country}]" if e.source_country else ""
                event_log.write(Text.from_markup(
                    f"[{sev_color}][{e.severity.value.upper()}][/] "
                    f"[bold]{e.title}[/]{src}\n"
                    f"  [dim]{e.description[:120]}[/]"
                ))

            dec_log = self.query_one("#decisions-panel", RichLog)
            for code, dec in result.get("decisions", {}).items():
                mood = dec.get("mood", "?")
                mood_color = {"confident": "green", "anxious": "yellow", "aggressive": "red", "defensive": "blue", "opportunistic": "magenta", "desperate": "bold red"}.get(mood, "white")
                statement = dec.get("public_statement", "...")
                dec_log.write(Text.from_markup(
                    f"[bold cyan]{code}[/] [{mood_color}]{mood.upper()}[/]\n"
                    f"  [italic]\"{statement}\"[/]"
                ))
                for a in dec.get("actions", []):
                    intensity = float(a.get("intensity", 0.5))
                    bar_filled = int(intensity * 8)
                    bar = "█" * bar_filled + "░" * (8 - bar_filled)
                    dec_log.write(Text.from_markup(
                        f"  [{bar}] {a.get('type', '?').upper()} → {a.get('target', '?')}: {a.get('detail', '')}"
                    ))

            self.refresh_table()
            self.update_status()

            if not result.get("continue", True):
                event_log.write("[bold red]═══ SIMULATION COMPLETE ═══[/]")

        except Exception as e:
            event_log = self.query_one("#event-log", RichLog)
            event_log.write(f"[bold red]Error: {e}[/]")
        finally:
            self.is_processing = False
            btn.label = "▶ Next Turn [N]"
            btn.disabled = False

    def action_inject_crisis(self) -> None:
        if self.sim:
            self.app.push_screen(CrisisModal(self.sim))

    def action_quit_sim(self) -> None:
        self.app.exit()

    def action_refresh_rankings(self) -> None:
        self.refresh_table()


# ═══════════════════════════════════════════════════════════════
# MAIN APP
# ═══════════════════════════════════════════════════════════════
class WorldOrderApp(App):
    TITLE = "WORLD ORDER"
    SUB_TITLE = "AI-Powered Geopolitical Simulation"
    CSS = CSS

    BINDINGS = [
        Binding("ctrl+q", "quit", "Quit", priority=True),
    ]

    def on_mount(self) -> None:
        self.push_screen(SplashScreen())


def run_tui() -> None:
    app = WorldOrderApp()
    app.run()


if __name__ == "__main__":
    run_tui()
