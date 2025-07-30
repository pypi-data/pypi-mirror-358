"""Ingest dbt metadata into Luma."""

from enum import Enum
from pathlib import Path
import time

from rich import print
from rich.console import Console
from rich.panel import Panel
import typer

from lumaCLI.models.dbt import DBTManifest
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


app = typer.Typer(no_args_is_help=True, pretty_exceptions_show_locals=False)
console = Console()


class IngestionStatus(Enum):
    successful = 0
    failed = 1
    pending = 2


@app.command()
def ingest(  # noqa: C901
    metadata_dir: Path = MetadataDir,
    luma_url: str = LumaURL,
    dry_run: bool = DryRun,
    follow: bool = Follow,
) -> None:
    """Ingest a bundle of JSON files into Luma.

    The files (manifest.json, catalog.json, sources.json, run_results.json) should be
    located in the specified directory.

    manifest.json and catalog.json are required.

    Uses the current working directory if 'metadata_dir' is not specified.
    """
    # Define JSON paths.
    manifest_json_path = metadata_dir / "manifest.json"
    catalog_json_path = metadata_dir / "catalog.json"
    sources_json_path = metadata_dir / "sources.json"
    run_results_json_path = metadata_dir / "run_results.json"

    # Ensure required files exist.
    if not manifest_json_path.is_file():
        print(Panel(f"[red]{manifest_json_path.absolute()} is not a file[/red]"))
        raise typer.Exit(1)
    if not catalog_json_path.is_file():
        print(Panel(f"[red]{catalog_json_path.absolute()} is not a file[/red]"))
        raise typer.Exit(1)

    # Convert each JSON to dict.
    manifest = json_to_dict(json_path=manifest_json_path)
    catalog = json_to_dict(json_path=catalog_json_path)
    sources = json_to_dict(json_path=sources_json_path)
    run_results = json_to_dict(json_path=run_results_json_path)

    # Validate the manifest.
    # DBTManifest.model_validate(manifest)

    # Bundle the artifacts.
    artifacts_bundle = {
        "manifest_json": manifest,
        "catalog_json": catalog,
        "sources_json": sources,
        "run_results_json": run_results,
    }

    # If in dry run mode, print the bundle and exit.
    if dry_run:
        print(artifacts_bundle)
        raise typer.Exit(0)

    # Send ingestion request.
    endpoint = f"{luma_url}/api/v1/dbt/"
    response, ingestion_uuid = perform_ingestion_request(
        url=endpoint,
        method="POST",
        payload=artifacts_bundle,
        verify=False,
    )
    if not response.ok:
        raise typer.Exit(1)

    # Wait until ingestion is complete.
    if follow and ingestion_uuid:
        ingestion_status = None

        with console.status("Waiting...", spinner="dots"):
            for _ in range(30):
                ingestion_status = check_ingestion_status(
                    luma_url, ingestion_uuid, verify=False
                )
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
) -> None:
    """Send 'run_results.json' file located in the specified directory to Luma.

    The command will fail if the 'run_results.json' file is not present in metadata_dir.
    The current working directory is used if 'metadata_dir' is not specified.
    """
    run_results_path = Path(metadata_dir) / "run_results.json"
    run_results_dict = json_to_dict(json_path=run_results_path)

    # If in dry run mode, print the test results and exit.
    if dry_run:
        print(run_results_dict)
        raise typer.Exit(0)

    # Send ingestion request.
    endpoint = f"{luma_url}/api/v1/dbt/run_results/"
    response, ingestion_uuid = perform_ingestion_request(
        url=endpoint,
        method="POST",
        payload=run_results_dict,
        verify=False,
    )
    if not response.ok:
        raise typer.Exit(1)

    if follow and ingestion_uuid:
        ingestion_status = None

        with console.status("Waiting...", spinner="dots"):
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


# Run the application.
if __name__ == "__main__":
    app()
