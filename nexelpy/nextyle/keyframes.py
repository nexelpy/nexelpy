from __future__ import annotations

from typing import Any, Dict, Optional


class KeyframeStep:
    def __init__(
        self,
        context,
        step_name: Any,
    ):
        self.context = context
        self.step_name = str(step_name)

    def _add_prop(
        self,
        css_prop: str,
        value: Optional[Any] = None,
        **kwargs,
    ):
        if value is not None:
            self.context.keyframe_rules.setdefault(
                self.step_name,
                {},
            )[css_prop] = str(value)

        return self

    @staticmethod
    def _make_css_method(css_property_name: str):
        def method(
            self: "KeyframeStep",
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
            f"Set keyframe CSS '{css_property_name}' property."
        )

        return method

    def __getattr__(self, name: str):
        css_property_name = name.replace("_", "-")

        def dynamic_method(value: Any = None):
            return self._add_prop(
                css_property_name,
                value,
            )

        return dynamic_method


from .cssProperty import css_Property as CSS_PROPERTIES


for css_property in CSS_PROPERTIES:
    method_name = css_property.replace("-", "_")

    setattr(
        KeyframeStep,
        method_name,
        KeyframeStep._make_css_method(css_property),
    )
