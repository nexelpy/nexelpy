from rich.console import Console
import logging
import uvicorn

console = Console()


class UvicornAccessFilter(logging.Filter):
    def filter(self, record):
        msg = record.getMessage()
        return not any(p in msg for p in ["/.well-known/"])


def run_app(app, host: str = "127.0.0.1", port: int = 8000) -> None:
    """
    Run the app:
    - In dev-parent: spawn reloader.
    - In dev-child / prod: run uvicorn.
    """
    # Parent (dev watcher)
    if app._is_parent:
        from ..reloader import Reloader
        Reloader(
            entry_file=app.file,
            extra_ignore_dirs=app.ignore_watch_dirs,
        ).run()
        return

    # Child / prod
    console.print("=" * 80)
    console.print(
        f"[bold][NexelPy MainApp][/bold] [blue]registered manual routes:[/blue] "
        f"{len(app.manual_routes)}"
    )
    console.print(
        f"[bold][NexelPy Registration][/bold] [green]registered routes: "
        f"{len(app.AutoRegister_list) + len(app.manual_routes)}[/green]"
    )
    logging.getLogger("uvicorn.access").addFilter(UvicornAccessFilter())
    uvicorn.run(app, host=host, port=port)