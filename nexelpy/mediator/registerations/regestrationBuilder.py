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
        self._route_modules: List[str] = []
        self._middleware_modules: List[str] = []
        self._registered_routes: List[Dict] = []

    def run(self) -> Dict:
        """
        Returns:
            {
                "routes": [...],
                "middleware_modules": [...],
            }
        """
        scanner = ModuleScanner(self._file)
        self._scanned_modules = scanner.run()
        console.print(
            f"[bold][NexelPy Scanner][/bold] [blue]Scanned modules : [/blue]"
            f"{len(self._scanned_modules)}"
        )

        inspector = ModuleInspector(self._file, self._scanned_modules)
        inspected = inspector.run()
        self._route_modules = inspected["route_modules"]
        self._middleware_modules = inspected["middleware_modules"]

        console.print(
            f"[bold][NexelPy Inspector][/bold] [blue]modules with Route :[/blue] "
            f"{len(self._route_modules)}"
        )
        console.print(
            f"[bold][NexelPy Inspector][/bold] [blue]modules with Middleware :[/blue] "
            f"{len(self._middleware_modules)}"
        )

        if self._middleware_modules:
            runner_middleware = ModuleRunHasDecorator(self._middleware_modules)
            runner_middleware.run()

        if self._route_modules:
            runner_route = ModuleRunHasDecorator(self._route_modules)
            runner_route.run()

        self._registered_routes = self._registry.get_all()
        self._log_routes()

        return {
            "routes": self._registered_routes,
            "middleware_modules": self._middleware_modules,
        }

    def _log_routes(self) -> None:
        count = len(self._registered_routes)
        if count == 0:
            console.print("[yellow]  No routes registered![/yellow]")

    def get_routes(self) -> List[Dict]:
        return self._registered_routes

    def get_route_by_path(self, path: str) -> Optional[Dict]:
        for item in self._registered_routes:
            if item.get("path") == path:
                return item
        return None