# nexelpy/registration_builder.py

from pathlib import Path
from typing import List, Dict, Optional
from rich.console import Console
from .moduleScanner import ModuleScanner
from .moduleInspector import ModuleInspector
from .moduleRunHasDecorator import ModuleRunHasDecorator
from .registry import RouteRegistry

console = Console()


class RegistrationBuilder:

    def __init__(self, file: Path | str):

        self._file = Path(file).resolve()
        self._root = self._file.parent
        self._registry = RouteRegistry()
        self._scanned_modules: List[str] = []
        self._inspected_modules: List[str] = []
        self._registered_routes: List[Dict] = []

    def run(self) -> List[Dict]:

        scanner = ModuleScanner(self._file)
        self._scanned_modules = scanner.run()
        console.print(f"[bold][NexelPy Scanner][/bold] [blue]Scanned modules : [/blue]{len(self._scanned_modules)} ")
        # print(self._scanned_modules)

   
        inspector = ModuleInspector(self._file, self._scanned_modules)
        self._inspected_modules = inspector.run()
        console.print(f"[bold][NexelPy Inspector][/bold] [blue]modules with AutoRegister :[/blue] {len(self._inspected_modules)} ")
        # print(self._inspected_modules)

        runner = ModuleRunHasDecorator(self._inspected_modules)
        runner.run()

        self._registered_routes = self._registry.get_all()

        self._log_routes()

        return self._registered_routes

    def _validate_routes(self) -> None:
        seen = set()
        for item in self._registered_routes:
            path = item.get("path")
            if path in seen:
                console.print(f"[yellow]Warning: Duplicate route found: {path}[/yellow]")
            seen.add(path)

    def _log_routes(self) -> None:
        count = len(self._registered_routes)
        console.print(f"[bold][NexelPy Registration][/bold] [green]registered routes: {count}[/green]")
        
        if count == 0:
            console.print("[yellow]  No routes registered![/yellow]")
            return

        # for idx, item in enumerate(self._registered_routes, 1):
        #     methods = ", ".join(item.get("method", []))
        #     path = item.get("path", "")
        #     handler = item.get("handler", {}).__name__ if item.get("handler") else "unknown"
        #     module = item.get("module", "unknown")
        #     console.print(f"  {idx}. [{methods}] {path} -> {handler} ({module})")

    def get_routes(self) -> List[Dict]:
        return self._registered_routes

    def get_route_by_path(self, path: str) -> Optional[Dict]:
        for item in self._registered_routes:
            if item.get("path") == path:
                return item
        return None