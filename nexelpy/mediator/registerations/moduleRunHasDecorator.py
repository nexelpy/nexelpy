import importlib
import sys
from rich.console import Console
from datetime import datetime

console = Console()


class ModuleRunHasDecorator:
    def __init__(self, modules: list):
        self.modules = modules

    def run(self) -> None:
        for module_name in self.modules:
            try:
                importlib.import_module(module_name)
            except Exception as e:
                console.print(
                    f"\n[yellow]{datetime.now().strftime('%H:%M:%S')}[/yellow] "
                    f"[bold red](nexelpy Import Error):[/bold red]"
                )
                console.print(f"         [blue]module:[/blue] {module_name}")
                console.print(f"         [blue]error:[/blue] {str(e)}")
                console.print()
