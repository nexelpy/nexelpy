from __future__ import annotations

from typing import TYPE_CHECKING, Any, Dict, Optional, Tuple

from .cssProperty import css_Property as CSS_PROPERTIES
from .helpers import python_to_css_name

if TYPE_CHECKING:
    from .nextyleBuilder import Nextyle

RuleKey = Tuple[str, str]

class Select:
    def __init__(self, selector_name: str, parent_nextyle: "Nextyle", pseudo_suffix: str = "", rules: Optional[Dict[RuleKey, Dict[str, str]]] = None, scope_selector: str = ""):
        self.selector_name = selector_name
        self.parent = parent_nextyle
        self.pseudo_suffix = pseudo_suffix
        self.scope_selector = scope_selector
        self.rules = rules if rules is not None else {}

    def _add_prop(self, css_prop: str, base_val: Optional[Any] = None, **kwargs) -> "Select":
        if base_val is not None:
            self.rules.setdefault(("base", self.pseudo_suffix), {})[css_prop] = str(base_val)
        for media_key, value in kwargs.items():
            if value is not None:
                self.rules.setdefault((media_key, self.pseudo_suffix), {})[css_prop] = str(value)
        return self

    @staticmethod
    def _make_css_method(css_property_name: str):
        def method(self: "Select", value: Optional[Any] = None, **kwargs) -> "Select":
            return self._add_prop(css_property_name, value, **kwargs)
        method.__name__ = css_property_name.replace("-", "_")
        return method

    @staticmethod
    def _make_pseudo_method(pseudo_target: str):
        def method(self: "Select") -> "Select":
            return self.pseudo(pseudo_target)
        method.__name__ = pseudo_target.lstrip(":").replace("-", "_")
        return method

    def __getattr__(self, name: str):
        css_property_name = python_to_css_name(name)
        def dynamic_method(value: Optional[Any] = None, **kwargs) -> "Select":
            return self._add_prop(css_property_name, value, **kwargs)
        return dynamic_method

    def pseudo(self, pseudo_name: str) -> "Select":
        pseudo_name = pseudo_name.strip()
        pseudo_name = pseudo_name if pseudo_name.startswith(":") else f":{pseudo_name.replace('_', '-')}"
        return Select(selector_name=self.selector_name, parent_nextyle=self.parent, pseudo_suffix=f"{self.pseudo_suffix}{pseudo_name}", rules=self.rules, scope_selector=self.scope_selector)

    def _render_selector(self, pseudo_suffix: str) -> str:
        selector = self.selector_name.strip()
        if not self.scope_selector:
            return f"{selector}{pseudo_suffix}"
        if selector in ("&", ":self", ""):
            return f"{self.scope_selector}{pseudo_suffix}"
        if selector.startswith("&"):
            return f"{self.scope_selector}{selector[1:]}{pseudo_suffix}"
        return f"{self.scope_selector} {selector}{pseudo_suffix}"

    def render_group(self, group_name: str) -> Optional[str]:
        blocks = []
        for (rule_group, pseudo_suffix), properties in self.rules.items():
            if rule_group != group_name or not properties:
                continue
            lines = [f"{self._render_selector(pseudo_suffix)} {{"]
            for prop, value in properties.items():
                lines.append(f"    {prop}: {value};")
            lines.append("}")
            blocks.append("\n".join(lines))
        return "\n\n".join(blocks) if blocks else None

#--------------------------------------------------------------------------------------------------------

for css_property in CSS_PROPERTIES:
    setattr(Select, css_property.replace("-", "_"), Select._make_css_method(css_property))

#--------------------------------------------------------------------------------------------------------

PSEUDO_ELEMENTS_AND_CLASSES = ["hover","focus","focus_visible","focus_within","active","disabled","enabled","checked",
    "visited","first_child","last_child","first_of_type","last_of_type","::before","::after","::placeholder","::selection","::marker",]

for pseudo_item in PSEUDO_ELEMENTS_AND_CLASSES:
    method_name = pseudo_item.lstrip(":").replace("-", "_")
    setattr(Select, method_name, Select._make_pseudo_method(pseudo_item))
