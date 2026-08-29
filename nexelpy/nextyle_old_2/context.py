from __future__ import annotations

from typing import TYPE_CHECKING, Any, Optional

if TYPE_CHECKING:
    from .nextyle import Nextyle


class ContextManager:
    def __init__(self, nextyle: "Nextyle", context_type: str, value: str = "", extra: Optional[dict[str, Any]] = None):
        self.nextyle = nextyle
        self.context_type = context_type
        self.value = value
        self.extra = extra

    def __enter__(self) -> "Nextyle":
        self.nextyle.stylesheet.push_context(self.context_type, self.value, self.extra)
        return self.nextyle

    def __exit__(self, exc_type, exc_value, traceback) -> bool:
        self.nextyle.stylesheet.pop_context()
        return False


class FontFaceContextManager:
    def __init__(self, nextyle: "Nextyle", family_name: str):
        self.nextyle = nextyle
        self.family_name = family_name

    def __enter__(self) -> "Nextyle":
        context = self.nextyle.stylesheet.push_context("font-face")
        context.declarations["font-family"] = f'"{self.family_name}"'
        return self.nextyle

    def __exit__(self, exc_type, exc_value, traceback) -> bool:
        self.nextyle.stylesheet.pop_context()
        return False
