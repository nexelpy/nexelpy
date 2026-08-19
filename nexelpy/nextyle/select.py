from __future__ import annotations

from typing import TYPE_CHECKING, Any, Dict, Optional, Tuple

from .helpers import python_to_css_name

if TYPE_CHECKING:
    from .nextyleBuilder import Nextyle


RuleKey = Tuple[str, str]


class Select:
    def __init__(
        self,
        selector_name: str,
        parent_nextyle: "Nextyle",
        pseudo_suffix: str = "",
        rules: Optional[
            Dict[RuleKey, Dict[str, str]]
        ] = None,
    ):
        self.selector_name = selector_name
        self.parent = parent_nextyle
        self.pseudo_suffix = pseudo_suffix

        # تمام pseudo-viewها همین dictionary را share می‌کنند.
        self.rules = rules if rules is not None else {}

    def _add_prop(
        self,
        css_prop: str,
        base_val: Optional[Any] = None,
        **kwargs,
    ):
        if base_val is not None:
            self.rules.setdefault(
                ("base", self.pseudo_suffix),
                {},
            )[css_prop] = str(base_val)

        for media_key, value in kwargs.items():
            if value is None:
                continue

            self.rules.setdefault(
                (media_key, self.pseudo_suffix),
                {},
            )[css_prop] = str(value)

        return self

    @staticmethod
    def _make_css_method(css_property_name: str):
        def method(
            self: "Select",
            value: Optional[Any] = None,
            **kwargs,
        ):
            return self._add_prop(
                css_property_name,
                value,
                **kwargs,
            )

        method.__name__ = css_property_name.replace("-", "_")
        method.__doc__ = (
            f"Set CSS '{css_property_name}' property."
        )

        return method

    def __getattr__(self, name: str):
        """
        Fallback برای propertyهایی که هنوز در css_Property نیستند.
        """

        css_property_name = python_to_css_name(name)

        def dynamic_method(
            value: Optional[Any] = None,
            **kwargs,
        ):
            return self._add_prop(
                css_property_name,
                value,
                **kwargs,
            )

        return dynamic_method

    # --------------------------------------------------------
    # Pseudo
    # --------------------------------------------------------

    def pseudo(self, pseudo_name: str) -> "Select":
        pseudo_name = pseudo_name.strip()

        if not pseudo_name.startswith(":"):
            pseudo_name = f":{pseudo_name}"

        return Select(
            selector_name=self.selector_name,
            parent_nextyle=self.parent,
            pseudo_suffix=(
                f"{self.pseudo_suffix}{pseudo_name}"
            ),
            rules=self.rules,
        )

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

    # --------------------------------------------------------
    # Render rule belonging to one media group
    # --------------------------------------------------------

    def render_group(
        self,
        group_name: str,
    ) -> Optional[str]:
        blocks = []

        for (
            rule_group,
            pseudo_suffix,
        ), properties in self.rules.items():

            if rule_group != group_name:
                continue

            if not properties:
                continue

            lines = [
                f"{self.selector_name}{pseudo_suffix} {{"
            ]

            for prop, value in properties.items():
                lines.append(
                    f"    {prop}: {value};"
                )

            lines.append("}")

            blocks.append("\n".join(lines))

        if not blocks:
            return None

        return "\n\n".join(blocks)


# Dynamic property methods برای runtime و autocomplete
from .cssProperty import css_Property as CSS_PROPERTIES


for css_property in CSS_PROPERTIES:
    method_name = css_property.replace("-", "_")

    setattr(
        Select,
        method_name,
        Select._make_css_method(css_property),
    )
