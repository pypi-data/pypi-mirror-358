from lumaCLI.luma import app
from typer.testing import CliRunner

runner = CliRunner()


def test_ingest_v1_7(METADATA_DIR_V1_7):
    result = runner.invoke(
        app,
        [
            "dbt",
            "ingest",
            "--metadata-dir",
            METADATA_DIR_V1_7 / "model_metadata",
            "--luma-url",
            "http://localhost:8000",
            "--dry-run",
        ],
    )
    assert result.exit_code == 0
