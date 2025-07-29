from pathlib import Path
from typing import Dict, List

import typer
from rich import print
from rich.panel import Panel

from lumaCLI.models import Config, RequestInfo
from lumaCLI.utils import get_config, get_db_metadata, send_config, perform_request
from lumaCLI.utils.options import (
    ConfigDir,
    DryRun,
    LumaURL,
    NoConfig,
    PostgresDatabase,
    PostgresHost,
    PostgresPassword,
    PostgresPort,
    PostgresUsername,
)

app = typer.Typer(no_args_is_help=True, pretty_exceptions_show_locals=False)


@app.command()
def ingest(
    luma_url: str = LumaURL,
    username: str = PostgresUsername,
    database: str = PostgresDatabase,
    host: str = PostgresHost,
    port: str = PostgresPort,
    password: str = PostgresPassword,
    dry_run: bool = DryRun,
    config_dir: Path = ConfigDir,
    no_config: bool = NoConfig,
) -> RequestInfo:
    """
    Ingests metadata from a PostgreSQL database and sends it to a specified Luma ingestion endpoint.
    """

    should_send_config = not no_config
    config = None
    # get_config

    if should_send_config:
        try:
            config: Config = get_config(config_dir=config_dir)
        except FileNotFoundError:
            print(
                Panel(
                    f"[blue]No config files found. Continuing with the operation...[/blue]"
                )
            )

    # Retrieve database metadata
    db_metadata: Dict[str, List[Dict]] = get_db_metadata(
        username=username, database=database, host=host, port=port, password=password
    )

    # In dry run mode, print the database metadata and exit
    if dry_run:
        print(db_metadata)
        raise typer.Exit(0)

    endpoint = f"{luma_url}/api/v1/postgres"

    # Create the request info object to return
    request_info = RequestInfo(
        url=endpoint,
        method="POST",
        payload=db_metadata,
        verify=False,
    )
    if config and should_send_config:
        config_response = send_config(config=config, luma_url=luma_url)

    response = perform_request(request_info)
    if not response.ok:
        raise typer.Exit(1)

    return response


if __name__ == "__main__":
    app()
