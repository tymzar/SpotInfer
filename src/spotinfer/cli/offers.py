"""
Offers CLI command.

List available Datacrunch instance offers with pricing.
"""

from typing import Optional

import typer
from rich.console import Console
from rich.table import Table
from rich.text import Text

from ..prepare.offers import OffersService
from ..utils.gpu import format_gpu_display

app = typer.Typer(name="offers", help="List available instance offers")
console = Console()


# pylint: disable=R0917
@app.command()
def list_offers(
    gpu_type: Optional[str] = typer.Option(
        None,
        "--gpu-type",
        "-g",
        help="Filter by GPU type (case-insensitive, e.g., v100, RTX4090, a100)",
    ),
    spot_only: bool = typer.Option(False, "--spot", "-s", help="Show spot pricing only"),
    cheapest: bool = typer.Option(False, "--cheapest", "-c", help="Show only the cheapest offer"),
    limit: int = typer.Option(10, "--limit", "-l", help="Limit number of results"),
    client_id: Optional[str] = typer.Option(None, "--client-id", help="Datacrunch client ID (overrides env var)"),
    client_secret: Optional[str] = typer.Option(
        None, "--client-secret", help="Datacrunch client secret (overrides env var)"
    ),
):
    """List available instance offers with pricing."""
    try:
        service = OffersService(client_id=client_id, client_secret=client_secret)

        if cheapest:
            offer = service.get_cheapest_offer(gpu_type=gpu_type, spot=spot_only)
            offers = [offer] if offer else []
        elif gpu_type:
            offers = service.filter_by_gpu_type(gpu_type)
        elif spot_only:
            offers = service.list_spot_offers()
        else:
            offers = service.list_all_offers()

        # Limit results
        offers = offers[:limit]

        if not offers:
            if gpu_type:
                console.print(f"[red]No offers found for GPU type: '{gpu_type}'[/red]")
                console.print("\n[blue]Available GPU types:[/blue]")
                available_types = service.get_available_gpu_types()
                for gpu_t in available_types:
                    console.print(f"  • {gpu_t}")
                console.print("\n[yellow]Tip: Use spotinfer offers gpu-types to see all types[/yellow]")
            else:
                console.print("[yellow]No offers found matching your criteria.[/yellow]")
            return

        # Create rich table
        table = Table(title="Available Instance Offers")
        table.add_column("Instance Type", style="cyan", no_wrap=True)
        table.add_column("GPU", style="green")
        table.add_column("vCPU", justify="right", style="blue")
        table.add_column("RAM", justify="right", style="blue")
        table.add_column("GPU RAM", justify="right", style="purple")
        table.add_column("On-Demand", justify="right", style="yellow")

        if not spot_only:
            table.add_column("Spot", justify="right", style="magenta")
            table.add_column("Savings", justify="right", style="green")

        for offer in offers:
            # Extract GPU info from description
            gpu_description = offer.gpu.get("description", "")
            gpu_count = offer.gpu.get("number_of_gpus", 0)
            gpu_display = format_gpu_display(gpu_description, gpu_count)

            # Extract CPU and memory info
            cpu_count = offer.cpu.get("number_of_cores", 0)
            memory_gb = offer.memory.get("size_in_gigabytes", 0)

            # Extract GPU memory info
            gpu_memory_gb = offer.gpu_memory.get("size_in_gigabytes", 0)
            gpu_memory_display = f"{gpu_memory_gb}GB" if gpu_memory_gb > 0 else "-"

            row = [
                offer.instance_type,
                gpu_display,
                str(cpu_count),
                f"{memory_gb}GB",
                gpu_memory_display,
                f"${offer.price_per_hour:.2f}",
            ]

            if not spot_only:
                savings = ((offer.price_per_hour - offer.spot_price_per_hour) / offer.price_per_hour) * 100
                row.extend(
                    [
                        f"${offer.spot_price_per_hour:.2f}",
                        f"{savings:.1f}%",
                    ]
                )

            table.add_row(*row)

        console.print(table)

        # Show summary
        if len(offers) == limit and not cheapest:
            console.print("\n[yellow]Showing first results. Use --limit to see more.[/yellow]")

    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(1)


@app.command()
def gpu_types(
    client_id: Optional[str] = typer.Option(None, "--client-id", help="Datacrunch client ID (overrides env var)"),
    client_secret: Optional[str] = typer.Option(
        None, "--client-secret", help="Datacrunch client secret (overrides env var)"
    ),
):
    """List available GPU types."""
    try:
        service = OffersService(client_id=client_id, client_secret=client_secret)
        available_gpu_types = service.get_available_gpu_types()

        if not available_gpu_types:
            console.print("[yellow]No GPU types found.[/yellow]")
            return

        # Create a simple list
        text = Text("Available GPU Types:", style="bold")
        console.print(text)

        for gpu_type in available_gpu_types:
            console.print(f"  • {gpu_type}")

    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(1)
