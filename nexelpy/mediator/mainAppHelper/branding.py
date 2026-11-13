from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.align import Align
import os

console = Console()

def print_branding(root_path: str, has_node: bool, has_secret_key: bool = True) -> None:
    """
    Print the NexelPy logo, Node.js status, watcher message, and secret key warning.
    Used only in the parent (dev-mode) process.
    """
    logo_text = Text("nexelpy", style="bold purple", justify="center")
    panel = Panel(
        Align.center(logo_text),
        border_style="purple",
        width=80,
        padding=(0, 1),
    )
    console.print(panel)

    if has_node:
        console.print(
            "[bold][NexelPy][/bold] [green]✓ Node.js found. "
            "(TS/JS features are available)[/green]"
        )
    else:
        console.print(
            "[bold][NexelPy][/bold] [yellow]⚠ Node.js not found.[/yellow] "
            "[dim]If you don't use .ts files, you can ignore this. "
            "To use NexCript, install Node.js from nodejs.org[/dim]"
        )

    if not has_secret_key and not os.getenv("_NEXELPY_KEY_WARNED"):
        console.print(
            "[dim yellow]⚠ NEXELPY_SECRET_KEY is not set. Using a random key. "
            "SECRET_KEY will reset on each restart.[/dim yellow]"
        )
        os.environ["_NEXELPY_KEY_WARNED"] = "1"

    console.print(
        f"[bold][NexelPy Registration][/bold] [yellow]watching:[/yellow] "
        f"{root_path} [yellow]directory (Python files only)[/yellow]"
    )