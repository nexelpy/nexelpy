import sys
from datetime import datetime
from rich.console import Console

console = Console()


class MiddlewareError(Exception):
    """Raised when middleware registration or ordering fails."""
    pass


def nexel_middleware_error(message: str) -> None:
    """
    Print a middleware error with NexelPy's rich style, then exit.
    """
    now = datetime.now().strftime("%H:%M:%S")
    console.print(
        f"\n[yellow]{now}[/yellow] "
        f"[bold red](nexelpy Middleware Error)[/bold red]"
    )
    for line in message.split("\n"):
        console.print(f"         [blue]{line}[/blue]")
    console.print()
    sys.exit(1)