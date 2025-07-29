"""
This module implements a command-line interface (CLI) for the Luma application.
It provides commands for database operations, configuration management, and other utilities.
"""

import importlib.metadata
from typing import Union

import typer

# Standard library imports
import urllib3
from rich.panel import Panel

import lumaCLI.commands.config as config
import lumaCLI.commands.dbt as dbt
import lumaCLI.commands.postgres as postgres
from lumaCLI.utils import check_ingestion_results
from lumaCLI.utils.options import CLI_NAME, IngestionId, LumaURL

__version__ = importlib.metadata.version(__package__ or __name__)

# Disable warnings related to insecure requests for specific cases
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Create a Typer application with configured properties
app = typer.Typer(
    name=CLI_NAME,
    no_args_is_help=True,
    pretty_exceptions_show_locals=False,
    pretty_exceptions_enable=True,
    pretty_exceptions_short=True,
)


def print_did_you_mean_luma():
    """Prints a suggestion panel if 'lumaCLI' is mistakenly used."""
    print(
        Panel(
            f"Whoops, you typed [bold red]lumaCLI[/bold red], did you mean '[bold green]luma[/bold green]' ??",
            border_style="blue",
        )
    )


def version_callback(show_version: bool):
    """
    Prints the version of the application and exits.

    Args:
        show_version (bool): If True, shows the version.
    """

    if show_version:
        typer.echo(__version__)
        raise typer.Exit()


@app.callback()
def main(
    version: bool = typer.Option(
        None,
        "--version",
        "-v",
        callback=version_callback,
        is_eager=True,
        help="Show the version and exit.",
    ),
):
    """
    Main function for the Typer application.

    Args:
        version (bool): Flag to show the version and exit.
    """
    pass


@app.command()
def status(
    ingestion_uuid: IngestionId,
    luma_url: str = LumaURL,
) -> Union[str, dict]:
    """Retrieve the status of an ingestion."""
    results = check_ingestion_results(luma_url, ingestion_uuid)
    print(f"Ingestion results for ID {ingestion_uuid}:")
    print(results)
    return results


# Add commands to the Typer application
app.add_typer(dbt.app, name="dbt", help="Ingest metadata from dbt.")
app.add_typer(postgres.app, name="postgres", help="Ingest metadata from Postgres.")
app.add_typer(config.app, name="config", help="Manage Luma instance configuration.")
