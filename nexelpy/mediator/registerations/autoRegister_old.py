from __future__ import annotations
import sys
import inspect
from datetime import datetime
from typing import Callable, Iterable, Any
from rich.console import Console
from .. import _Global_nexelpy_var

console = Console()

# ==========================================================
# Central Error Printer (Fail-Fast)
# ==========================================================

def nexel_error(source: str, **info: Any) -> None:
    now = datetime.now()
    console.print(
        f"\n[yellow]{now.strftime('%H:%M:%S')}[/yellow] "
        f"[bold red](nexelpy {source})[/bold red]")
    for key, value in info.items():
        console.print(f"         [blue]{key}:[/blue] {value}")
    console.print()
    sys.exit(1)

# ==========================================================
# URL Checker (No Exceptions, Clean Validation)
# ==========================================================

class UrlChecker:

    @staticmethod
    def check(route: Any, prefix: Any) -> tuple[bool, str]:
        prefix = prefix or ""

        if not isinstance(route, str):
            return False, "route must be a string"

        if not isinstance(prefix, str):
            return False, "prefix must be a string"

        if not route.startswith("/"):
            return False, "route must start with '/'"

        if prefix:
            if not prefix.startswith("/"):
                return False, "prefix must start with '/'"

            if prefix.endswith("/"):
                return False, "prefix must not end with '/'"

        full_path = prefix + route

        if "//" in full_path:
            return False, "double slash detected in final url"

        return True, full_path

# ==========================================================
# AutoRegister Decorator (Strict / Fail-Fast)
# ==========================================================

def AutoRegister(route: str = "/",method: Iterable[str] | None = ["GET"],prefix: str | None = "",) -> Callable:

    def decorator(func: Callable) -> Callable:

        module = func.__module__

        try:
            line = inspect.getsourcelines(func)[1]
        except Exception:
            line = None

        # --------------------------------------------------
        # 1) Async Check
        # --------------------------------------------------
        if not inspect.iscoroutinefunction(func):
            nexel_error("AutoRegister",type="SyncFunctionError",module=module,line=line,handler=func.__name__,message="Handler must be async (use async def)")

        # --------------------------------------------------
        # 2) Route Validation
        # --------------------------------------------------
        ok, result = UrlChecker.check(route, prefix)

        if not ok:
            nexel_error("AutoRegister",type="InvalidRouteError",module=module,line=line,route=route,prefix=prefix,handler=func.__name__,message=result)

        full_path = result

        # --------------------------------------------------
        # 3) Duplicate Route Check
        # --------------------------------------------------
        for item in _Global_nexelpy_var.AutoRegister_list:

            if item["path"] == full_path:
                nexel_error("AutoRegister",type="DuplicateRouteError",path=full_path,new_module=module,new_line=line,old_module=item["module"],old_line=item["line"],message="Duplicate route detected")

        # --------------------------------------------------
        # 4) Register Route
        # --------------------------------------------------
        _Global_nexelpy_var.AutoRegister_list.append(
            {"path": full_path,
             "method": list(method),
             "handler": func,
             "module": module,
             "line": line,
             "route":route ,
             "prefix" :prefix})

        return func

    return decorator
