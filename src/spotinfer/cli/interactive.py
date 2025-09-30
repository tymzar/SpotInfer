"""
SpotInfer - Interactive Mode.

Interactive CLI mode for guided instance selection and job setup.
"""

from pathlib import Path
from typing import List, Optional

import inquirer
import typer
from rich.console import Console
from rich.panel import Panel
from rich.prompt import IntPrompt, Prompt
from rich.table import Table

from ..prepare.offers import InstanceSelectionService

app = typer.Typer(name="interactive", help="Interactive mode for guided setup")
console = Console()


class InteractiveContext:
    """Context object to hold state during interactive session."""

    def __init__(self):
        self.input_file: Optional[Path] = None
        self.selected_instance = None
        self.gpu_requirements: Optional[str] = None
        self.budget_limit: Optional[float] = None


def get_arrow_key_input(options: List[str], prompt: str = "Select an option") -> str:
    """Get user input using inquirer for arrow key navigation."""
    if not options:
        return ""

    # Check if we're in an interactive terminal
    import sys

    if not sys.stdin.isatty():
        # Fallback to numbered selection for non-interactive environments
        console.print(f"\n{prompt}:")
        for i, option in enumerate(options, 1):
            console.print(f"  {i}. {option}")

        choice = IntPrompt.ask(
            "Select option",
            choices=[str(i) for i in range(1, len(options) + 1)],
            default="1",
        )

        selected = options[int(choice) - 1]
        console.print(f"[green]✓ Selected: {selected}[/green]")
        return selected

    try:
        questions = [
            inquirer.List("choice", message=prompt, choices=options, carousel=True)
        ]

        answers = inquirer.prompt(questions)
        if answers:
            selected = answers["choice"]
            console.print(f"[green]✓ Selected: {selected}[/green]")
            return selected
        else:
            # User cancelled (Ctrl+C)
            raise typer.Exit(1)

    except Exception:
        # Fallback to numbered selection if inquirer fails
        console.print(
            "[yellow]Warning: Interactive selection failed, using fallback[/yellow]"
        )
        console.print(f"\n{prompt}:")
        for i, option in enumerate(options, 1):
            console.print(f"  {i}. {option}")

        choice = IntPrompt.ask(
            "Select option",
            choices=[str(i) for i in range(1, len(options) + 1)],
            default="1",
        )

        selected = options[int(choice) - 1]
        console.print(f"[green]✓ Selected: {selected}[/green]")
        return selected


@app.command()
def run(
    client_id: Optional[str] = typer.Option(
        None, "--client-id", help="Datacrunch client ID"
    ),
    client_secret: Optional[str] = typer.Option(
        None, "--client-secret", help="Datacrunch client secret"
    ),
):
    """Run interactive mode for guided instance selection."""

    # Initialize context
    ctx = InteractiveContext()

    # Step 1: File Input (mocked for now)
    console.print(Panel.fit("Step 1: Input File Selection", style="bold blue"))
    input_file = Prompt.ask(
        "Enter path to your notebook/script", default="notebook.ipynb"
    )
    ctx.input_file = Path(input_file)

    # Mock file validation
    if not ctx.input_file.exists():
        console.print("[yellow]Note: File doesn't exist (mocked for demo)[/yellow]")

    console.print(f"[green]✓ Selected file: {ctx.input_file}[/green]")
    console.print()

    # Step 2: Instance Selection (real implementation)
    console.print(Panel.fit("Step 2: Instance Selection", style="bold blue"))

    try:
        # Initialize the instance selection service
        service = InstanceSelectionService(
            client_id=client_id, client_secret=client_secret
        )

        # Ask about GPU requirements
        console.print("Let's find the right instance for your workload...")

        # GPU type selection
        gpu_choice = get_arrow_key_input(["yes", "no"], "Do you need GPU acceleration?")

        if gpu_choice.lower() == "yes":
            # Show available GPU types with arrow key navigation
            gpu_types = service.get_available_gpu_types()
            selected_gpu = get_arrow_key_input(gpu_types, "Select GPU type")
            ctx.gpu_requirements = selected_gpu

            # Get offers for selected GPU
            offers = service.filter_by_gpu_type(selected_gpu)
        else:
            # CPU-only instances
            offers = service.list_all_offers()
            # Filter for CPU-only instances (no GPU)
            offers = [
                offer for offer in offers if offer.gpu.get("number_of_gpus", 0) == 0
            ]

        if not offers:
            console.print(
                "[red]No suitable instances found for your requirements.[/red]"
            )
            raise typer.Exit(1)

        # Ask about budget
        budget_choice = get_arrow_key_input(
            ["no", "yes"], "Do you have a budget limit?"
        )
        if budget_choice.lower() == "yes":
            ctx.budget_limit = float(
                Prompt.ask("Enter maximum hourly cost ($)", default="1.00")
            )
            # Filter offers by budget
            offers = [
                offer for offer in offers if offer.price_per_hour <= ctx.budget_limit
            ]

        if not offers:
            console.print("[red]No instances found within budget.[/red]")
            raise typer.Exit(1)

        # Show top offers
        console.print(f"\n[bold]Top {min(5, len(offers))} suitable instances:[/bold]")

        table = Table(title="Available Instances")
        table.add_column("Option", style="cyan", no_wrap=True)
        table.add_column("Instance Type", style="green")
        table.add_column("GPU", style="blue")
        table.add_column("vCPU", justify="right", style="blue")
        table.add_column("RAM", justify="right", style="blue")
        table.add_column("GPU RAM", justify="right", style="purple")
        table.add_column("On-Demand", justify="right", style="yellow")
        table.add_column("Spot", justify="right", style="magenta")
        table.add_column("Savings", justify="right", style="green")

        for i, offer in enumerate(offers[:5], 1):
            # Extract GPU info
            gpu_description = offer.gpu.get("description", "")
            gpu_count = offer.gpu.get("number_of_gpus", 0)

            if gpu_description and gpu_count > 0:
                import re

                patterns = [
                    r"(B300)\s+SXM6",
                    r"(B200)\s+SXM6",
                    r"(H200)\s+SXM5",
                    r"(H100)\s+SXM5",
                    r"(A100)\s+SXM4",
                    r"(RTX\s+PRO)\s+6000",
                    r"(RTX\s+6000)\s+Ada",
                    r"(RTX\s+A6000)",
                    r"(Tesla\s+V100)",
                    r"(L40S)",
                ]

                gpu_type_display = "Unknown"
                for pattern in patterns:
                    match = re.search(pattern, gpu_description)
                    if match:
                        gpu_type_display = match.group(1)
                        break

                gpu_display = (
                    f"{gpu_count}x{gpu_type_display}"
                    if gpu_count > 1
                    else gpu_type_display
                )
            else:
                gpu_display = "CPU Only"

            # Extract other specs
            cpu_count = offer.cpu.get("number_of_cores", 0)
            memory_gb = offer.memory.get("size_in_gigabytes", 0)
            gpu_memory_gb = offer.gpu_memory.get("size_in_gigabytes", 0)
            gpu_memory_display = f"{gpu_memory_gb}GB" if gpu_memory_gb > 0 else "-"

            # Calculate savings
            savings = (
                (offer.price_per_hour - offer.spot_price_per_hour)
                / offer.price_per_hour
            ) * 100

            table.add_row(
                str(i),
                offer.instance_type,
                gpu_display,
                str(cpu_count),
                f"{memory_gb}GB",
                gpu_memory_display,
                f"${offer.price_per_hour:.2f}",
                f"${offer.spot_price_per_hour:.2f}",
                f"{savings:.1f}%",
            )

        console.print(table)

        # Instance selection
        instance_choice = IntPrompt.ask(
            "Select instance",
            choices=[str(i) for i in range(1, min(6, len(offers) + 1))],
            default="1",
        )

        ctx.selected_instance = offers[int(instance_choice) - 1]

        # Pricing preference
        pricing_choice = get_arrow_key_input(
            ["spot", "on-demand"], "Pricing preference"
        )

        # Summary
        console.print()
        console.print(Panel.fit("Selection Summary", style="bold green"))
        console.print(f"📁 Input file: {ctx.input_file}")
        console.print(f"🖥️  Instance: {ctx.selected_instance.instance_type}")
        console.print(f"💰 Pricing: {pricing_choice}")

        if pricing_choice == "spot":
            hourly_cost = ctx.selected_instance.spot_price_per_hour
            savings = (
                (
                    ctx.selected_instance.price_per_hour
                    - ctx.selected_instance.spot_price_per_hour
                )
                / ctx.selected_instance.price_per_hour
            ) * 100
            console.print(f"💵 Cost: ${hourly_cost:.2f}/hour (saves {savings:.1f}%)")
        else:
            hourly_cost = ctx.selected_instance.price_per_hour
            console.print(f"💵 Cost: ${hourly_cost:.2f}/hour")

        # Confirmation
        proceed_choice = get_arrow_key_input(
            ["yes", "no"], "Proceed with this configuration?"
        )
        proceed = proceed_choice.lower() == "yes"
        if proceed:
            console.print("[green]✓ Configuration confirmed! Ready to proceed.[/green]")
            console.print(
                "[yellow]Note: This is a demo - provisioning not implemented.[/yellow]"
            )
        else:
            console.print("[yellow]Configuration cancelled.[/yellow]")

    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(1)
