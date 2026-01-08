"""
Rich logging system with visibility into every step.

Provides:
- Colored console output
- Progress tracking
- Step-by-step visibility
- Performance metrics
"""

import logging
from rich.console import Console
from rich.logging import RichHandler
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn
from rich.panel import Panel
from rich.table import Table
from contextlib import contextmanager
import time
from typing import Dict, Any

# Global console for rich output
console = Console()

# Progress tracker
_active_progress = None


def setup_logging(level: str = "INFO", colorize: bool = True):
    """Setup rich logging."""
    
    if colorize:
        logging.basicConfig(
            level=level,
            format="%(message)s",
            handlers=[RichHandler(
                console=console,
                rich_tracebacks=True,
                show_time=True,
                show_path=False
            )]
        )
    else:
        logging.basicConfig(
            level=level,
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )


def log_step(step_name: str, details: str = ""):
    """Log a processing step with rich formatting."""
    console.print(f"\n[bold cyan]→ {step_name}[/bold cyan]")
    if details:
        console.print(f"  [dim]{details}[/dim]")


def log_success(message: str):
    """Log success message."""
    console.print(f"[bold green]✓[/bold green] {message}")


def log_warning(message: str):
    """Log warning message."""
    console.print(f"[bold yellow]⚠[/bold yellow] {message}")


def log_error(message: str):
    """Log error message."""
    console.print(f"[bold red]✗[/bold red] {message}")


def log_info(message: str):
    """Log info message."""
    console.print(f"[blue]ℹ[/blue] {message}")


def show_provider_info(provider_type: str, provider_name: str):
    """Show which provider is being used."""
    panel = Panel(
        f"[bold]{provider_name}[/bold]",
        title=f"[cyan]{provider_type.upper()} Provider[/cyan]",
        border_style="cyan"
    )
    console.print(panel)


def show_config_summary(config: Dict[str, Any]):
    """Display configuration summary."""
    table = Table(title="Active Configuration", show_header=True)
    table.add_column("Provider Type", style="cyan")
    table.add_column("Active Provider", style="green")
    table.add_column("Status", style="yellow")
    
    for key, value in config.items():
        if isinstance(value, dict) and 'provider' in value:
            table.add_row(
                key.upper(),
                value['provider'],
                "✓ Loaded"
            )
    
    console.print(table)


@contextmanager
def step_progress(description: str):
    """Show progress for a step."""
    global _active_progress
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        console=console,
        transient=True
    ) as progress:
        _active_progress = progress
        task = progress.add_task(description, total=None)
        
        start_time = time.time()
        try:
            yield progress
        finally:
            elapsed = time.time() - start_time
            progress.update(task, completed=100)
            console.print(f"[dim]  Completed in {elapsed:.2f}s[/dim]")
            _active_progress = None


def log_metrics(metrics: Dict[str, Any], title: str = "Metrics"):
    """Display metrics in a table."""
    table = Table(title=title, show_header=True)
    table.add_column("Metric", style="cyan")
    table.add_column("Value", style="green")
    
    for key, value in metrics.items():
        table.add_row(key, str(value))
    
    console.print(table)


def log_comparison(provider1: str, provider2: str, results: Dict[str, tuple]):
    """Compare results from two providers."""
    table = Table(title="Provider Comparison", show_header=True)
    table.add_column("Metric", style="cyan")
    table.add_column(provider1, style="yellow")
    table.add_column(provider2, style="green")
    
    for metric, (val1, val2) in results.items():
        table.add_row(metric, str(val1), str(val2))
    
    console.print(table)
