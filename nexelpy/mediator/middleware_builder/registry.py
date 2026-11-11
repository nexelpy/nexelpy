from __future__ import annotations
from typing import Optional
from .errors import MiddlewareError,nexel_middleware_error


class MiddlewareRegistry:
    _instance: Optional["MiddlewareRegistry"] = None

    def __new__(cls) -> "MiddlewareRegistry":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if not hasattr(self, "_middlewares"):
            self._middlewares: list[tuple[str, type, Optional[str]]] = []

    def register(self, name: str, cls: type, after: Optional[str] = None) -> None:
        if any(m[0] == name for m in self._middlewares):
            raise MiddlewareError(
                f"Middleware '{name}' is already registered. "
                f"Each middleware must have a unique name."
            )
        self._middlewares.append((name, cls, after))

    def clear(self) -> None:
        self._middlewares.clear()

    def get_ordered(self) -> list[type]:
        no_dep = [m for m in self._middlewares if m[2] is None]
        with_dep = [m for m in self._middlewares if m[2] is not None]

        ordered = list(no_dep)
        resolved = {m[0] for m in no_dep}
        pending = list(with_dep)

        while pending:
            progress = False
            for m in pending[:]:
                name, cls, after = m
                if after in resolved:
                    ordered.append(m)
                    resolved.add(name)
                    pending.remove(m)
                    progress = True

            if not progress:
                unresolved = [f"{m[0]} (after: {m[2]})" for m in pending]
                nexel_middleware_error(
                    "Cannot resolve middleware order. "
                    "This is usually caused by:\n"
                    "  - A circular dependency (A after B, B after A)\n"
                    "  - A missing 'after' target (the referenced middleware "
                    "is not registered/imported)\n"
                    f"Unresolved middlewares: {unresolved}"
    )

        return [m[1] for m in ordered]