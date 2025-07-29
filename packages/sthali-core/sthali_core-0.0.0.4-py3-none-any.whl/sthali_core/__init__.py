"""Sthali Core package CLI and main application entry points.

Provides Typer CLI commands for generating, updating, and serving documentation and projects.
"""

import mkdocs.commands.serve
import typer

from .scripts import Generate, Update
from .utils import base, enum_clients, run_server

__all__ = [
    "base",
    "enum_clients",
    "run_server",
]


app = typer.Typer()
state = {}


@app.callback()
def callback() -> None:
    pass


@app.command()
def generate(option: Generate.GenerateOptionsEnum, project_name: str | None = None) -> None:
    Generate.execute(option, project_name)


@app.command()
def update(option: Update.UpdateOptionsEnum) -> None:
    Update.execute(option)


@app.command()
def serve() -> None:
    config_file = "docs/mkdocs.yml"
    mkdocs.commands.serve.serve(config_file)  # type: ignore
