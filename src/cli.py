"""CLI tool for generating curriculum packets and TA guides."""

import json
from pathlib import Path
from typing import Any

import click
from rich.console import Console

from src.main import (
    check_output_permissions,
    getPrecontext,
    process_curriculum,
)

console = Console()


@click.group()
@click.version_option()
def cli() -> None:
    """MopMan PacketMaker CLI - Generate curriculum packets and TA guides."""


@cli.command()
@click.argument("curriculum_id", type=str)
@click.option(
    "--output-dir",
    type=click.Path(path_type=Path),
    default=Path("./output/"),
    help="Directory to save generated files",
)
@click.option(
    "--config",
    type=click.Path(exists=True, path_type=Path),
    default=Path("config.json"),
    help="Path to config file",
)
def generate(curriculum_id: str, output_dir: Path, config: Path) -> None:
    """Generate curriculum packets and TA guides for a specific curriculum."""
    try:
        with Path.open(config) as f:
            config_data: dict[str, Any] = json.load(f)

        output_dir.mkdir(parents=True, exist_ok=True)

        with console.status("Getting precontext..."):
            precontext = getPrecontext(curriculum_id, output_dir, option_num=1)
            if not precontext:
                raise click.ClickException("Failed to get precontext")

        click.echo(f"Successfully generated packets in {output_dir}")

    except Exception as e:
        raise click.ClickException(str(e))


@cli.command()
@click.option(
    "--config",
    type=click.Path(exists=True, path_type=Path),
    default=Path("config.json"),
    help="Path to config file",
)
def generate_all(config: Path) -> None:
    """Generate packets for all curricula specified in config."""
    try:
        with Path.open(config) as f:
            config_data: dict[str, Any] = json.load(f)

        base_output_dir = Path(config_data["output_dir"])
        check_output_permissions(base_output_dir)

        for curriculum, details in config_data["curriculum"].items():
            if details["make_packet"]:
                click.echo(f"Generating packet for {curriculum}...")
                process_curriculum(curriculum, details, base_output_dir)

    except Exception as e:
        raise click.ClickException(str(e))
