from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.align import Align

console = Console()


def print_branding(root_path: str, has_node: bool) -> None:
    """
    Print the NexelPy logo, Node.js status, and watcher message.
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

    console.print(
        f"[bold][NexelPy Registration][/bold] [yellow]watching:[/yellow] "
        f"{root_path} [yellow]directory (Python files only)[/yellow]"
    )