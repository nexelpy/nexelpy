from __future__ import annotations

from ..helpers import indent_css


class KeyframeRenderer:
    def merge_rules(self, current_rules: dict[str, dict[str, str]], overrides: dict[str, dict[str, str]]) -> dict[str, dict[str, str]]:
        merged = {step_name: declarations.copy() for step_name, declarations in current_rules.items()}

        for step_name, declarations in overrides.items():
            merged.setdefault(step_name, {}).update(declarations)

        return merged

    def render_definition(self, name: str, rules: dict[str, dict[str, str]]) -> str:
        blocks = []

        for step_name, declarations in rules.items():
            lines = [f"{step_name} {{"]
            lines.extend(f"    {property_name}: {value};" for property_name, value in declarations.items())
            lines.append("}")
            blocks.append("\n".join(lines))

        content = "\n\n".join(blocks)
        return f"@keyframes {name} {{\n{indent_css(content)}\n}}" if content else ""

    def render(self, context, variants) -> str:
        blocks = []
        effective_rules = self.merge_rules({}, context.keyframe_rules.get("base", {}))
        base_css = self.render_definition(context.value, effective_rules)

        if base_css:
            blocks.append(base_css)

        for variant_name, variant in variants.items():
            if variant_name == "base":
                continue

            overrides = context.keyframe_rules.get(variant_name, {})
            effective_rules = self.merge_rules(effective_rules, overrides)

            if not overrides:
                continue

            css = self.render_definition(context.value, effective_rules)

            if css:
                blocks.append(variant.wrap(css, indent_css))

        return "\n\n".join(blocks)
