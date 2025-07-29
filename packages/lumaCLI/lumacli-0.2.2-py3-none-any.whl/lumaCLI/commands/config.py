from pathlib import Path

import typer
from rich import print

from lumaCLI.utils import get_config, init_config, send_config
from lumaCLI.utils.options import ConfigDir, DryRun, Force, LumaURL

app = typer.Typer(
    name="config", no_args_is_help=True, pretty_exceptions_show_locals=False
)

@app.command(help="Initialize the configuration.")
def init(config_dir: Path = ConfigDir, force: bool = Force):
    """
    Initializes and overwrites the configuration at the specified directory if 'force' is True. 
    Raises FileExistsError if the configuration already exists and 'force' is not True.
    """
    try:
        init_config(config_dir=config_dir, force=force)
        print(f"[green]Config initialized at[/green] {config_dir}")
    except FileExistsError:
        print(
            f"[red]Error![/red] [red]Config files already exist at[/red] {config_dir}\n"
            f"[yellow]If you want to override run with flag [/yellow][red]--force/-f[/red]"
        )
        raise typer.Exit(1)


@app.command(help="Display the current configuration information.")
def show(config_dir: Path = ConfigDir):
    """
    Displays the current configuration from the specified directory. 
    """
    try:
        config = get_config(config_dir=config_dir)
        print(config)
    except FileNotFoundError:
        print(
            "[red]Error![/red] [red]Config files not found at[/red] {config_dir}\n"
            "[yellow]To generate config files use [/yellow][white]'luma config init'[/white]"
        )
        raise typer.Exit(1)


@app.command(help="Send the current configuration information to luma")
def send(config_dir: Path = ConfigDir, luma_url: str = LumaURL, dry_run: bool = DryRun):
    """
    Sends the current configuration to the specified Luma URL. In dry run mode, 
    the configuration is printed but not sent.
    """
    try:
        config = get_config(config_dir=config_dir)

        if dry_run:
            print(config.dict())
            return

        if config:
            response = send_config(config=config, luma_url=luma_url)
            if not response.ok:
                raise typer.Exit(1)
        else:
            print(
                f"[red]No Config detected under {config_dir}[/red]\n"
                f"[yellow]To generate config files use [/yellow][white]'luma config init'[/white]"
            )

    except FileNotFoundError:
        print(
            f"[red]Error![/red] [red]Config files not found at[/red] {config_dir}\n"
            f"[yellow]To generate config files use [/yellow][white]'luma config init'[/white]"
        )
        raise typer.Exit(1)
