import time
from enum import Enum
from pathlib import Path
from typing import Optional

import typer
from rich import print
from rich.console import Console
from rich.panel import Panel

from lumaCLI.models import RequestInfo
from lumaCLI.models.dbt import ManifestDict
from lumaCLI.utils import (
    check_ingestion_results,
    check_ingestion_status,
    json_to_dict,
    perform_ingestion_request,
)
from lumaCLI.utils.options import (
    DryRun,
    Follow,
    LumaURL,
    MetadataDir,
)

# Create Typer application
app = typer.Typer(no_args_is_help=True, pretty_exceptions_show_locals=False)
console = Console()


class IngestionStatus(Enum):
    successful = 0
    failed = 1
    pending = 2


@app.command()
def ingest(
    metadata_dir: Path = MetadataDir,
    luma_url: str = LumaURL,
    dry_run: bool = DryRun,
    follow: bool = Follow,
):
    """
    Ingests a bundle of JSON files (manifest.json, catalog.json, sources.json, run_results.json)
    located in the specified directory to a Luma endpoint.
    manifest.json and catalog.json are required, if not present, the command will fail.
    Uses the current working directory if 'metadata_dir' is not specified.
    """
    # Define JSON paths
    manifest_json_path = metadata_dir / "manifest.json"
    catalog_json_path = metadata_dir / "catalog.json"
    sources_json_path = metadata_dir / "sources.json"
    run_results_json_path = metadata_dir / "run_results.json"

    # Ensure all JSON files are valid
    if not manifest_json_path.is_file():
        print(Panel(f"[red]{manifest_json_path.absolute()} is not a file[/red]"))
        raise typer.Exit(1)
    if not catalog_json_path.is_file():
        print(Panel(f"[red]{catalog_json_path.absolute()} is not a file[/red]"))
        raise typer.Exit(1)

    # Convert each JSON to dict
    manifest_dict: Optional[dict] = json_to_dict(json_path=manifest_json_path)
    catalog_dict: Optional[dict] = json_to_dict(json_path=catalog_json_path)
    sources_dict: Optional[dict] = json_to_dict(json_path=sources_json_path)
    run_results_dict: Optional[dict] = json_to_dict(json_path=run_results_json_path)

    # Validate manifest_dict using ManifestDict
    ManifestDict.validate(manifest_dict)

    # Define bundle dict
    bundle_dict = {
        "manifest_json": manifest_dict,
        "catalog_json": catalog_dict,
        "sources_json": sources_dict,
        "run_results_json": run_results_dict,
    }

    # If in dry run mode, print the bundle and exit
    if dry_run:
        print(bundle_dict)
        raise typer.Exit(0)

    # Create the request information
    endpoint = f"{luma_url}/api/v1/dbt/"
    request_info = RequestInfo(
        url=endpoint,
        method="POST",
        payload=bundle_dict,
        verify=False,
    )

    response, ingestion_uuid = perform_ingestion_request(request_info)
    if not response.ok:
        raise typer.Exit(1)

    if follow and ingestion_uuid:
        ingestion_status = None

        with console.status("Waiting...", spinner="dots") as spinner:
            for _ in range(30):
                ingestion_status = check_ingestion_status(luma_url, ingestion_uuid)
                if ingestion_status == IngestionStatus.successful.value:
                    response = check_ingestion_results(luma_url, ingestion_uuid)
                    print()
                    print(f"Ingestion results for ID {ingestion_uuid}:")
                    print()
                    print(response)
                    return

                if ingestion_status == IngestionStatus.failed.value:
                    print()
                    print(f"Ingestion failed for ID {ingestion_uuid}")
                    return

                if ingestion_status == IngestionStatus.pending.value:
                    time.sleep(1)

        if ingestion_status != IngestionStatus.successful.value:
            print(
                f"Ingestion did not complete successfully within the wait period. Status: {ingestion_status}"
            )


@app.command()
def send_test_results(
    metadata_dir: Path = MetadataDir,
    luma_url: str = LumaURL,
    dry_run: bool = DryRun,
    follow: bool = Follow,
):
    """
    Sends the 'run_results.json' file located in the specified directory to a Luma endpoint.
    The command will fail if the 'run_results.json' file is not present in the directory.
    The current working directory is used if 'metadata_dir' is not specified.
    """

    # Define the path to 'run_results.json'
    run_results_path = Path(metadata_dir) / "run_results.json"

    # Convert 'run_results.json' to dict
    run_results_dict = json_to_dict(json_path=run_results_path)

    # If in dry run mode, print the test results and exit
    if dry_run:
        print(run_results_dict)
        raise typer.Exit(0)

    # Create and return the request information for test results
    endpoint = f"{luma_url}/api/v1/dbt/run_results/"
    request_info = RequestInfo(
        url=endpoint,
        method="POST",
        payload=run_results_dict,
        verify=False,
    )

    response, ingestion_uuid = perform_ingestion_request(request_info)
    if not response.ok:
        raise typer.Exit(1)

    if follow and ingestion_uuid:
        ingestion_status = None

        with console.status("Waiting...", spinner="dots") as spinner:
            for _ in range(30):
                ingestion_status = check_ingestion_status(luma_url, ingestion_uuid)
                if ingestion_status == IngestionStatus.successful.value:
                    response = check_ingestion_results(luma_url, ingestion_uuid)
                    print()
                    print(f"Ingestion results for ID {ingestion_uuid}:")
                    print()
                    print(response)
                    return

                if ingestion_status == IngestionStatus.failed.value:
                    print()
                    print(f"Ingestion failed for ID {ingestion_uuid}")
                    return

                if ingestion_status == IngestionStatus.pending.value:
                    time.sleep(1)

        if ingestion_status != IngestionStatus.successful.value:
            print(
                f"Ingestion did not complete successfully within the wait period. Status: {ingestion_status}"
            )


# Run the application
if __name__ == "__main__":
    app()
