from __future__ import annotations

from typing import Any, Optional

from .nodes import ContextNode


class Stylesheet:
    def __init__(self):
        self.root = ContextNode(context_type="root")
        self.context_stack = [self.root]
        self.global_raw_css: list[str] = []

    @property
    def current_context(self) -> ContextNode:
        return self.context_stack[-1]

    def push_context(self, context_type: str, value: str = "", extra: Optional[dict[str, Any]] = None) -> ContextNode:
        context = ContextNode(context_type=context_type, value=value, extra=extra or {})
        self.current_context.actions.append(context)
        self.context_stack.append(context)
        return context

    def pop_context(self) -> ContextNode:
        return self.context_stack.pop()

    def append(self, node: Any) -> None:
        self.current_context.actions.append(node)

    def add_global_raw_css(self, raw_css: str) -> None:
        self.global_raw_css.append(raw_css)

    def active_scope_selector(self) -> str:
        selectors = [context.value.strip() for context in self.context_stack if context.context_type in {"nexel-scoping", "nexel-scoping-auto"} and context.value.strip()]
        return " ".join(selectors)
