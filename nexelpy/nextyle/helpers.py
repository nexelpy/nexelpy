from __future__ import annotations

from typing import Any


def python_to_css_name(name: str) -> str:
    return name.replace("_", "-")


def css_value(value: Any) -> str:
    if isinstance(value, bool):
        return "true" if value else "false"

    return str(value)


def indent_css(css: str, level: int = 1) -> str:
    prefix = "    " * level

    return "\n".join(
        f"{prefix}{line}" if line.strip() else ""
        for line in css.splitlines()
    )
