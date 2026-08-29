from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class RawCSSNode:
    content: str
    variant: str = "base"


@dataclass
class SelectorNode:
    selector: str
    scope_selector: str = ""
    rules: dict[tuple[str, str], dict[str, str]] = field(default_factory=dict)


@dataclass
class ContextNode:
    context_type: str
    value: str = ""
    extra: dict[str, Any] = field(default_factory=dict)
    actions: list[Any] = field(default_factory=list)
    declarations: dict[str, str] = field(default_factory=dict)
    keyframe_rules: dict[str, dict[str, dict[str, str]]] = field(default_factory=dict)
