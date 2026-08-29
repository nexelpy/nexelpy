from __future__ import annotations

from typing import Any, Optional

from .helpers import css_value, python_to_css_name


class KeyframeStep:
    def __init__(self, context, step_name: Any):
        self.context = context
        self.step_name = str(step_name)

    def _add_prop(self, css_property: str, value: Optional[Any] = None, **variants: Any) -> "KeyframeStep":
        if value is not None:
            self.context.keyframe_rules.setdefault("base", {}).setdefault(self.step_name, {})[css_property] = css_value(value)
        for variant_name, variant_value in variants.items():
            if variant_value is not None:
                self.context.keyframe_rules.setdefault(variant_name, {}).setdefault(self.step_name, {})[css_property] = css_value(variant_value)
        return self

    def __getattr__(self, name: str):
        css_property = python_to_css_name(name)

        def dynamic_method(value: Optional[Any] = None, **variants: Any) -> "KeyframeStep":
            return self._add_prop(css_property, value, **variants)

        return dynamic_method
