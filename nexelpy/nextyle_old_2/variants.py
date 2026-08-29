from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Variant:
    name: str
    wrapper: str = ""

    @property
    def is_base(self) -> bool:
        return self.name == "base"

    def wrap(self, css: str, indent) -> str:
        if self.is_base:
            return css
        return f"{self.wrapper} {{\n{indent(css)}\n}}"


class VariantRegistry:
    def __init__(self, media_queries: dict[str, str] | None = None):
        self._variants: dict[str, Variant] = {"base": Variant(name="base")}
        for name, condition in (media_queries or {}).items():
            self.register_media(name, condition)

    def register_media(self, name: str, condition: str) -> None:
        wrapper = condition if condition.startswith("@media") else f"@media {condition}"
        self._variants[name] = Variant(name=name, wrapper=wrapper)

    def register(self, name: str, wrapper: str) -> None:
        self._variants[name] = Variant(name=name, wrapper=wrapper)

    def get(self, name: str) -> Variant:
        return self._variants[name]

    def items(self):
        return self._variants.items()

    def names(self) -> tuple[str, ...]:
        return tuple(self._variants)
