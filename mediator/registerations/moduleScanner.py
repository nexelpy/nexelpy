
from pathlib import Path
from rich.console import Console
from .. import _Global_nexelpy_var
import sys
from datetime import datetime

console = Console()


class ModuleScanner:
    EXCLUDED_DIRS = {
        "__pycache__", ".git", ".venv", "venv", "env", "node_modules", "__nexelpy__"}

    def __init__(self):
        self.entry_file = (
            Path(_Global_nexelpy_var.root_progect).resolve()
            if _Global_nexelpy_var.root_progect else None
        )
        self.root = self.entry_file.parent if self.entry_file else None

    def run(self):
        if not self.entry_file:
            console.print(
                f"\n[yellow]{datetime.now().strftime('%H:%M:%S')}[/yellow] [bold red](nexelpy error Scanner)[/bold red] \n"
                "       root_progect is not set in MainApp \n"
                "       [green]True syntax:[/green] MainApp(__file__)\n"
            )
            sys.exit(1)

        _Global_nexelpy_var.scan_python_file = []

        for file in self.root.rglob("*.py"):
            if any(part in self.EXCLUDED_DIRS for part in file.parts):
                continue

            if file.resolve() == self.entry_file:
                continue

            relative_path = file.relative_to(self.root)
            module_parts = list(relative_path.with_suffix("").parts)

            if module_parts and module_parts[-1] == "__init__":
                module_parts.pop()

            module_name = ".".join(module_parts)

            if module_name:
                _Global_nexelpy_var.scan_python_file.append(module_name)
