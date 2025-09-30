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

app = typer.Typer(name="offers", help="List available instance offers")
console = Console()


@app.command()
def list(
    gpu_type: Optional[str] = typer.Option(
        None,
        "--gpu-type",
        "-g",
        help="Filter by GPU type (case-insensitive, e.g., v100, RTX4090, a100)",
    ),
    spot_only: bool = typer.Option(
        False, "--spot", "-s", help="Show spot pricing only"
    ),
    cheapest: bool = typer.Option(
        False, "--cheapest", "-c", help="Show only the cheapest offer"
    ),
    limit: int = typer.Option(10, "--limit", "-l", help="Limit number of results"),
    client_id: Optional[str] = typer.Option(
        None, "--client-id", help="Datacrunch client ID (overrides env var)"
    ),
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
                console.print(
                    "\n[yellow]Tip: Use spotinfer offers gpu-types to see all types[/yellow]"  # noqa: E501
                )
            else:
                console.print(
                    "[yellow]No offers found matching your criteria.[/yellow]"
                )
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

            if gpu_description and gpu_count > 0:
                # Extract GPU type from description (e.g., "1x Tesla V100 16GB" ->
                # "V100")
                import re

                patterns = [
                    r"(B300)\s+SXM6",  # e.g., "B300 SXM6"
                    r"(B200)\s+SXM6",  # e.g., "B200 SXM6"
                    r"(H200)\s+SXM5",  # e.g., "H200 SXM5"
                    r"(H100)\s+SXM5",  # e.g., "H100 SXM5"
                    r"(A100)\s+SXM4",  # e.g., "A100 SXM4"
                    r"(RTX\s+PRO)\s+6000",  # e.g., "RTX PRO 6000"
                    r"(RTX\s+6000)\s+Ada",  # e.g., "RTX 6000 Ada"
                    r"(RTX\s+A6000)",  # e.g., "RTX A6000"
                    r"(Tesla\s+V100)",  # e.g., "Tesla V100"
                    r"(L40S)",  # e.g., "L40S"
                ]

                gpu_type = "Unknown"
                for pattern in patterns:
                    match = re.search(pattern, gpu_description)
                    if match:
                        gpu_type = match.group(1)
                        break

                gpu_display = f"{gpu_count}x{gpu_type}" if gpu_count > 1 else gpu_type
            else:
                gpu_display = "CPU Only"

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
                savings = (
                    (offer.price_per_hour - offer.spot_price_per_hour)
                    / offer.price_per_hour
                ) * 100
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
            console.print(
                "\n[yellow]Showing first results. Use --limit to see more.[/yellow]"
            )

    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(1)


@app.command()
def gpu_types(
    client_id: Optional[str] = typer.Option(
        None, "--client-id", help="Datacrunch client ID (overrides env var)"
    ),
    client_secret: Optional[str] = typer.Option(
        None, "--client-secret", help="Datacrunch client secret (overrides env var)"
    ),
):
    """List available GPU types."""
    try:
        service = OffersService(client_id=client_id, client_secret=client_secret)
        gpu_types = service.get_available_gpu_types()

        if not gpu_types:
            console.print("[yellow]No GPU types found.[/yellow]")
            return

        # Create a simple list
        text = Text("Available GPU Types:", style="bold")
        console.print(text)

        for gpu_type in gpu_types:
            console.print(f"  • {gpu_type}")

    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(1)
