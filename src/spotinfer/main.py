"""
SpotInfer - A simple Python package for inference tasks.
"""

import typer

from .cli.interactive import app as interactive_app
from .cli.offers import app as offers_app

__version__ = "0.1.0"

app = typer.Typer(
    name="spotinfer",
    help="Run local notebooks/scripts on remote Datacrunch GPU instances",
    no_args_is_help=True,
    add_completion=False,
)

# Add subcommands
app.add_typer(offers_app, name="offers", help="List available instance offers")
app.add_typer(
    interactive_app, name="interactive", help="Interactive mode for guided setup"
)


@app.command()
def version():
    """Show version and exit."""
    typer.echo(f"SpotInfer {__version__}")


@app.callback()
def main():
    """SpotInfer - GPU instance management for ML workloads."""
    pass


def cli():
    """CLI entry point."""
    app()


if __name__ == "__main__":
    cli()
