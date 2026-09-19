
from __future__ import annotations
from typing import TYPE_CHECKING, Any, Dict, Optional, Union

if TYPE_CHECKING:
    from .nextyleBuilder import Nextyle
    from .select import Select

class CSSContext:
    def __init__(self, parent: "Nextyle", context_type: str, value: str = "", extra: Optional[Dict[str, Any]] = None):
        self.parent = parent
        self.context_type = context_type
        self.value = value
        self.extra = extra or {}
        self.actions = []
        self.declarations = {}
        self.keyframe_rules = {}


class ContextManager:
    def __init__(self, parent: "Nextyle", context_type: str, value: str = "", extra: Optional[Dict[str, Any]] = None):
        self.parent = parent
        self.context_type = context_type
        self.value = value
        self.extra = extra or {}
        self.context: Optional[CSSContext] = None

    def __enter__(self) -> Union["Select", str, "Nextyle"]:
        from .select import Select
        self.context = self.parent._push_context(self.context_type, self.value, self.extra)
        if self.context_type in {"scoping", "nexel-scoping", "nexel-scoping-auto"}:
            scope_sel = self.value if self.value else f'[data-scoping="{self.parent.scope_token}"]'
            selector = Select("&", self.parent, scope_selector=scope_sel)
            self.context.actions.append(selector)
            return selector
        if self.context_type == "keyframes":
            return self.value
        return self.parent


    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> bool:
        self.parent._pop_context()
        return False


class FontFaceContextManager:
    def __init__(self, nextyle: "Nextyle", family_name: str):
        self.nextyle = nextyle
        self.family_name = family_name

    def __enter__(self):
        context = self.nextyle._push_context("font-face")
        context.declarations["font-family"] = f'"{self.family_name}"'
        return self.nextyle

    def __exit__(self, exc_type, exc_value, traceback):
        self.nextyle._pop_context()
        return False


