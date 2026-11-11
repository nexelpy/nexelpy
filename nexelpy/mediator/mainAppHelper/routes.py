from typing import Any, Callable, Iterable
from ..registerations.regestrationBuilder import RegistrationBuilder
from ..registerations.url_checker import UrlChecker
from ..wraper_handler import wraper_handler
import inspect


def setup_routes(app, file: str) -> dict:
    """Scan the project and return {'routes': [...], 'middleware_modules': [...]}."""
    return RegistrationBuilder(file).run()


def register_root_list(app, routes: list) -> None:
    """Register the scanned routes on the Starlette app."""
    for reg in routes:
        app.add_route(
            reg["path"],
            wraper_handler(reg["handler"]),
            methods=reg["methods"],
        )


def add_manual_route(
    app,
    route: str = "",
    prefix: str = "",
    methods: str | Iterable[str] | None = None,
    func: Callable[..., Any] | None = None,
) -> Callable[..., Any]:
    """Add a route manually (used by `add_manual_route` and `@app.route`)."""
    if func is None or not callable(func):
        raise TypeError("func must be a callable function")

    is_valid, full_path = UrlChecker.check(route, prefix)
    if not is_valid:
        raise ValueError(full_path)

    if methods is None:
        methods = ["GET"]
    elif isinstance(methods, str):
        methods = [methods.upper()]
    else:
        methods = [item.upper() for item in methods]

    route_data = {
        "path": full_path,
        "methods": methods,
        "handler": func,
        "module": func.__module__,
        "file": func.__code__.co_filename,
        "line": func.__code__.co_firstlineno,
        "route": route,
        "prefix": prefix,
    }
    app.manual_routes.append(route_data)
    app.add_route(full_path, wraper_handler(func), methods=methods)

    # Move static mount to the end of the route list
    for index, r in enumerate(app.routes):
        if getattr(r, "name", None) == "static":
            app.routes.append(app.routes.pop(index))
            break

    return func