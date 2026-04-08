"""WORLD ORDER CLI — terminal interface for the simulation."""

from __future__ import annotations

import asyncio
import sys
from typing import Any

import click
from rich.console import Console

from engine.config import SimulationConfig, Era, TimeScale, GameMode
from engine.simulation import Simulation
from engine.event_bus import SimEvent
from llm.registry import get_provider, available_providers
from cli.renderer import SimulationRenderer
from cli.map_ascii import render_world_map

console = Console()
renderer = SimulationRenderer(console)


@click.group()
def cli() -> None:
    """WORLD ORDER — AI-Powered Geopolitical Simulation Engine."""
    pass


@cli.command()
@click.option("--era", type=click.Choice([e.value for e in Era]), default="contemporary")
@click.option("--start-year", type=int, default=2025)
@click.option("--end-year", type=int, default=2100)
@click.option("--turns", type=int, default=20)
@click.option("--time-scale", type=click.Choice([t.value for t in TimeScale]), default="year")
@click.option("--mode", type=click.Choice(["god", "leader"]), default="god")
@click.option("--player-country", type=str, default=None, help="Country code if leader mode")
@click.option("--provider", type=click.Choice(available_providers()), default="ollama")
@click.option("--model", type=str, default="llama3.1")
@click.option("--seed", type=int, default=None)
@click.option("--no-advisors", is_flag=True, help="Disable advisor agents (faster)")
def start(
    era: str,
    start_year: int,
    end_year: int,
    turns: int,
    time_scale: str,
    mode: str,
    player_country: str | None,
    provider: str,
    model: str,
    seed: int | None,
    no_advisors: bool,
) -> None:
    """Start a new simulation."""
    renderer.render_banner()

    config = SimulationConfig(
        era=Era(era),
        start_year=start_year,
        end_year=end_year,
        max_turns=turns,
        time_scale=TimeScale(time_scale),
        game_mode=GameMode(mode),
        player_country=player_country,
        llm_provider=provider,
        llm_model=model,
        seed=seed,
    )

    renderer.render_config(config)

    llm = get_provider(provider, model=model)

    async def turn_callback(
        turn: int, year: int, events: list[SimEvent], decisions: dict[str, Any]
    ) -> None:
        renderer.render_events(events)
        renderer.render_all_decisions(decisions)

    sim = Simulation(config=config, llm=llm, on_turn=turn_callback)
    sim.setup()

    console.print(
        f"\n[bold green]Loaded {len(sim.world.countries)} countries, "
        f"{len(sim.leader_profiles)} leaders.[/]\n"
    )

    country_dict = {c.code: c for c in sim.world.all_countries()}
    console.print(render_world_map(country_dict))
    renderer.render_power_rankings(sim.world)

    console.print("\n[bold cyan]Starting simulation...[/]\n")

    async def run_loop() -> None:
        for t in range(config.max_turns):
            renderer.render_turn_header(t, sim.world.year, config.max_turns)
            result = await sim.run_turn()
            renderer.render_power_rankings(sim.world)
            renderer.render_diplomacy_web(sim.world)
            if not result["continue"]:
                renderer.render_simulation_end(sim.world, sim.event_bus.total_events)
                break
            console.input("\n[dim]Press Enter for next turn...[/]")

        if not sim.time_engine.finished:
            renderer.render_simulation_end(sim.world, sim.event_bus.total_events)

    asyncio.run(run_loop())


@cli.command()
def status() -> None:
    """Show available LLM providers and system info."""
    renderer.render_banner()
    console.print("[bold]Available LLM Providers:[/]")
    for p in available_providers():
        console.print(f"  - {p}")
    console.print()

    console.print("[bold]Checking Ollama...[/]")
    llm = get_provider("ollama")
    ok = asyncio.run(llm.health_check())
    if ok:
        console.print("[bold green]  Ollama is running.[/]")
    else:
        console.print("[bold red]  Ollama is NOT running. Start it with: ollama serve[/]")


@cli.command()
@click.argument("provider_name", type=click.Choice(available_providers()))
def check(provider_name: str) -> None:
    """Health-check an LLM provider."""
    llm = get_provider(provider_name)
    ok = asyncio.run(llm.health_check())
    if ok:
        console.print(f"[bold green]{provider_name} is reachable.[/]")
    else:
        console.print(f"[bold red]{provider_name} is NOT reachable.[/]")


# Register extended commands
from cli.commands import scenarios, news, wiki, show_map, history, war, predict, shadows

cli.add_command(scenarios)
cli.add_command(news)
cli.add_command(wiki)
cli.add_command(show_map)
cli.add_command(history)
cli.add_command(war)
cli.add_command(predict)
cli.add_command(shadows)


@cli.command()
def tui() -> None:
    """Launch the full-screen cinematic TUI."""
    from cli.tui import run_tui
    run_tui()


def main() -> None:
    cli()


if __name__ == "__main__":
    main()
