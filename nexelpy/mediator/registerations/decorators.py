from __future__ import annotations
import sys
import inspect
from datetime import datetime
from typing import Callable, Iterable, Any
from rich.console import Console
from .registry import RouteRegistry
from .url_checker import UrlChecker

console = Console()
registry = RouteRegistry()


def nexel_error(source: str, **info: Any) -> None:
    now = datetime.now()
    console.print(
        f"\n[yellow]{now.strftime('%H:%M:%S')}[/yellow] "
        f"[bold red](nexelpy {source})[/bold red]"
    )
    for key, value in info.items():
        console.print(f"         [blue]{key}:[/blue] {value}")
    console.print()
    sys.exit(1)


def Route(route: str = "/", methods: Iterable[str] | None = ["GET"], prefix: str | None = ""):
    
    def decorator(func: Callable) -> Callable:
        module = func.__module__

        try:
            line = inspect.getsourcelines(func)[1]
        except Exception:
            line = None

        # --------------------------------------------------
        # --------------------------------------------------
        if not inspect.iscoroutinefunction(func):
            nexel_error(
                "Route",
                type="SyncFunctionError",
                module=module,
                line=line,
                handler=func.__name__,
                message="Handler must be async (use async def)")
        # --------------------------------------------------
        # --------------------------------------------------
        ok, result = UrlChecker.check(route, prefix)

        if not ok:
            nexel_error(
                "Route",
                type="InvalidRouteError",
                module=module,
                line=line,
                route=route,
                prefix=prefix,
                handler=func.__name__,
                message=result)

        full_path = result

        # --------------------------------------------------
        # --------------------------------------------------
        existing = registry.find_by_path(full_path)
        if existing:
            nexel_error(
                "Route",
                type="DuplicateRouteError",
                path=full_path,
                new_module=module,
                new_line=line,
                old_module=existing.get("module"),
                old_line=existing.get("line"),
                message="Duplicate route detected")

        # --------------------------------------------------
        # --------------------------------------------------
        registry.register({
            "path": full_path,
            "methods": list(methods) if methods else ["GET"],
            "handler": func,
            "module": module,
            "line": line,
            "route": route or "",
            "prefix": prefix or "",})
        return func

    return decorator