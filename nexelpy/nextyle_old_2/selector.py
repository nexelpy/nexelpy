from __future__ import annotations

from typing import TYPE_CHECKING, Any, Optional

from .helpers import css_value, python_to_css_name
from .nodes import SelectorNode

if TYPE_CHECKING:
    from .nextyle import Nextyle


class Select:
    def __init__(self, node: SelectorNode, parent_nextyle: "Nextyle", pseudo_suffix: str = ""):
        self.node = node
        self.parent = parent_nextyle
        self.pseudo_suffix = pseudo_suffix

    def _add_prop(self, css_property: str, value: Optional[Any] = None, **variants: Any) -> "Select":
        if value is not None:
            self.node.rules.setdefault(("base", self.pseudo_suffix), {})[css_property] = css_value(value)
        for variant_name, variant_value in variants.items():
            if variant_value is not None:
                self.node.rules.setdefault((variant_name, self.pseudo_suffix), {})[css_property] = css_value(variant_value)
        return self

    def __getattr__(self, name: str):
        css_property = python_to_css_name(name)

        def dynamic_method(value: Optional[Any] = None, **variants: Any) -> "Select":
            return self._add_prop(css_property, value, **variants)

        return dynamic_method

    def pseudo(self, pseudo_name: str) -> "Select":
        pseudo_name = pseudo_name.strip()
        pseudo_name = pseudo_name if pseudo_name.startswith(":") else f":{pseudo_name}"
        return Select(node=self.node, parent_nextyle=self.parent, pseudo_suffix=f"{self.pseudo_suffix}{pseudo_name}")

    def hover(self) -> "Select":
        return self.pseudo("hover")

    def focus(self) -> "Select":
        return self.pseudo("focus")

    def focus_visible(self) -> "Select":
        return self.pseudo("focus-visible")

    def focus_within(self) -> "Select":
        return self.pseudo("focus-within")

    def active(self) -> "Select":
        return self.pseudo("active")

    def disabled(self) -> "Select":
        return self.pseudo("disabled")

    def enabled(self) -> "Select":
        return self.pseudo("enabled")

    def checked(self) -> "Select":
        return self.pseudo("checked")

    def visited(self) -> "Select":
        return self.pseudo("visited")

    def first_child(self) -> "Select":
        return self.pseudo("first-child")

    def last_child(self) -> "Select":
        return self.pseudo("last-child")

    def first_of_type(self) -> "Select":
        return self.pseudo("first-of-type")

    def last_of_type(self) -> "Select":
        return self.pseudo("last-of-type")

    def before(self) -> "Select":
        return self.pseudo("::before")

    def after(self) -> "Select":
        return self.pseudo("::after")

    def placeholder(self) -> "Select":
        return self.pseudo("::placeholder")

    def selection(self) -> "Select":
        return self.pseudo("::selection")

    def marker(self) -> "Select":
        return self.pseudo("::marker")
