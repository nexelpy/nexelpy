from __future__ import annotations

from typing import Dict, List


class CSSRenderer:
    def __init__(self, nextyle):
        self.nextyle = nextyle

    @staticmethod
    def indent_css(css: str, level: int = 1) -> str:
        prefix = "    " * level
        return "\n".join(f"{prefix}{line}" if line.strip() else "" for line in css.splitlines())

    @staticmethod
    def render_declarations(declarations: Dict[str, str], level: int = 1) -> str:
        prefix = "    " * level
        return "\n".join(f"{prefix}{prop}: {value};" for prop, value in declarations.items())

    @staticmethod
    def merge_keyframe_rules(current_rules, overrides):
        merged = {step_name: declarations.copy() for step_name, declarations in current_rules.items()}
        for step_name, declarations in overrides.items():
            merged.setdefault(step_name, {}).update(declarations)
        return merged

    def render_context_actions(self, context, group_name: str = "base") -> List[str]:
        blocks = []
        for action in context.actions:
            if hasattr(action, "render_group"):
                rendered = action.render_group(group_name)
                if rendered:
                    blocks.append(rendered)
                continue
            if isinstance(action, tuple) and action[0] == "raw" and action[1] == group_name:
                blocks.append(action[2])
                continue
            if isinstance(action, tuple) and action[0] == "context" and group_name == "base":
                rendered = self.render_context(action[1])
                if rendered:
                    blocks.append(rendered)
        return blocks

    def render_media_aware_context(self, context) -> str:
        blocks = []
        base_blocks = self.render_context_actions(context, "base")
        if base_blocks:
            blocks.append("\n\n".join(base_blocks))
        for media_key, media_rule in self.nextyle.media_queries.items():
            media_blocks = self.render_context_actions(context, media_key)
            if not media_blocks:
                continue
            inner_css = "\n\n".join(media_blocks)
            blocks.append(f"{media_rule} {{\n{self.indent_css(inner_css)}\n}}")
        return "\n\n".join(blocks)

    def render_keyframe_definition(self, name: str, rules) -> str:
        blocks = []
        for step_name, declarations in rules.items():
            lines = [f"{step_name} {{"]
            for prop, value in declarations.items():
                lines.append(f"    {prop}: {value};")
            lines.append("}")
            blocks.append("\n".join(lines))
        if not blocks:
            return ""
        content = "\n\n".join(blocks)
        return f"@keyframes {name} {{\n{self.indent_css(content)}\n}}"

    def render_keyframes(self, context) -> str:
        rules_by_query = context.keyframe_rules
        blocks = []
        effective_rules = self.merge_keyframe_rules({}, rules_by_query.get("base", {}))
        base_css = self.render_keyframe_definition(context.value, effective_rules)
        if base_css:
            blocks.append(base_css)
        for media_key, media_rule in self.nextyle.media_queries.items():
            overrides = rules_by_query.get(media_key, {})
            effective_rules = self.merge_keyframe_rules(effective_rules, overrides)
            if not overrides:
                continue
            keyframe_css = self.render_keyframe_definition(context.value, effective_rules)
            if keyframe_css:
                blocks.append(f"{media_rule} {{\n{self.indent_css(keyframe_css)}\n}}")
        return "\n\n".join(blocks)

    def render_declaration_context(self, context, header: str) -> str:
        if not context.declarations:
            return ""
        declarations = self.render_declarations(context.declarations)
        return f"{header} {{\n{declarations}\n}}"

    def render_context(self, context) -> str:
        context_type = context.context_type

        if context_type in {"nexel-scoping", "nexel-scoping-auto"}:
            return self.render_media_aware_context(context)

        if context_type == "root":
            blocks = []
            if self.nextyle.global_raw_css:
                blocks.extend(self.nextyle.global_raw_css)
            if self.nextyle.layer_order:
                blocks.append("@layer " + ", ".join(self.nextyle.layer_order) + ";")
            content = self.render_media_aware_context(context)
            if content:
                blocks.append(content)
            return "\n\n".join(blocks)

        if context_type == "media":
            content = self.render_media_aware_context(context)
            if not content:
                return ""
            value = context.value.strip()
            value = value if value.startswith("@media") else f"@media {value}"
            return f"{value} {{\n{self.indent_css(content)}\n}}"

        if context_type == "supports":
            content = self.render_media_aware_context(context)
            return f"@supports {context.value} {{\n{self.indent_css(content)}\n}}" if content else ""

        if context_type == "container":
            content = self.render_media_aware_context(context)
            return f"@container {context.value} {{\n{self.indent_css(content)}\n}}" if content else ""

        if context_type == "layer":
            content = self.render_media_aware_context(context)
            return f"@layer {context.value} {{\n{self.indent_css(content)}\n}}" if content else ""

        if context_type == "scope":
            content = self.render_media_aware_context(context)
            return f"@scope {context.value} {{\n{self.indent_css(content)}\n}}" if content else ""

        if context_type == "starting-style":
            content = self.render_media_aware_context(context)
            return f"@starting-style {{\n{self.indent_css(content)}\n}}" if content else ""

        if context_type == "font-face":
            return self.render_declaration_context(context, "@font-face")

        if context_type == "property":
            return self.render_declaration_context(context, f"@property {context.value}")

        if context_type == "vars":
            return self.render_declaration_context(context, context.value)

        if context_type == "page":
            header = f"@page {context.value.strip()}" if context.value.strip() else "@page"
            return self.render_declaration_context(context, header)

        if context_type == "keyframes":
            return self.render_keyframes(context)

        return ""

    def generate(self) -> str:
        css = self.render_context(self.nextyle.root_context)
        return css.rstrip() + "\n" if css else ""
