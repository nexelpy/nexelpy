from pathlib import Path
from rich.console import Console
import sys
from datetime import datetime

console = Console()


class ModuleScanner:

    EXCLUDED_DIRS = {"__pycache__", ".git", ".venv", "venv", "env", "node_modules", "__nexelpy__"}

    def __init__(self, file: Path):
        self._file = file.resolve() if file else None
        self._root = self._file.parent if self._file else None
        self._scan_python_file = []

    def run(self) -> list:
        if not self._file:
            console.print(
                f"\n[yellow]{datetime.now().strftime('%H:%M:%S')}[/yellow] [bold red](nexelpy error Scanner)[/bold red] \n"
                "       root_progect is not set in MainApp \n"
                "       [green]True syntax:[/green] MainApp(__file__)\n"
            )
            sys.exit(1)

        self._scan_python_file = []

        for py_file in self._root.rglob("*.py"):
            if any(part in self.EXCLUDED_DIRS for part in py_file.parts):
                continue

            if py_file == self._file:
                continue

            try:
                relative_path = py_file.relative_to(self._root)
            except ValueError:
                continue

            module_parts = list(relative_path.with_suffix("").parts)

            if module_parts and module_parts[-1] == "__init__":
                module_parts.pop()

            module_name = ".".join(module_parts)

            if module_name:
                self._scan_python_file.append(module_name)

        return self._scan_python_file