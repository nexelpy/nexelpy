from __future__ import annotations

from typing import Optional

from ..nodes import SelectorNode


class SelectorRenderer:
    def render(self, node: SelectorNode, variant_name: str) -> Optional[str]:
        blocks = []

        for (rule_variant, pseudo_suffix), declarations in node.rules.items():
            if rule_variant != variant_name or not declarations:
                continue
            selector = f"{node.selector.strip()}{pseudo_suffix}"
            selector = f"{node.scope_selector} {selector}" if node.scope_selector else selector
            lines = [f"{selector} {{"]
            lines.extend(f"    {property_name}: {value};" for property_name, value in declarations.items())
            lines.append("}")
            blocks.append("\n".join(lines))

        return "\n\n".join(blocks) if blocks else None
