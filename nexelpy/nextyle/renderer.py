from __future__ import annotations

from typing import Dict, List


class CSSRenderer:
    def __init__(self, nextyle):
        self.nextyle = nextyle

    @staticmethod
    def indent_css(
        css: str,
        level: int = 1,
    ) -> str:
        prefix = "    " * level

        return "\n".join(
            f"{prefix}{line}" if line.strip() else ""
            for line in css.splitlines()
        )

    @staticmethod
    def render_declarations(
        declarations: Dict[str, str],
        level: int = 1,
    ) -> str:
        prefix = "    " * level

        return "\n".join(
            f"{prefix}{prop}: {value};"
            for prop, value in declarations.items()
        )

    def render_context_actions(
        self,
        context,
        group_name: str = "base",
    ) -> List[str]:
        blocks = []

        for action in context.actions:

            if hasattr(action, "render_group"):
                rendered = action.render_group(group_name)

                if rendered:
                    blocks.append(rendered)

                continue

            if (
                isinstance(action, tuple)
                and action[0] == "raw"
                and action[1] == group_name
            ):
                blocks.append(action[2])
                continue

            if (
                isinstance(action, tuple)
                and action[0] == "context"
                and group_name == "base"
            ):
                child_context = action[1]
                rendered = self.render_context(
                    child_context
                )

                if rendered:
                    blocks.append(rendered)

        return blocks

    def render_media_aware_context(self, context) -> str:
        blocks = []

        base_blocks = self.render_context_actions(
            context,
            "base",
        )

        if base_blocks:
            blocks.append(
                "\n\n".join(base_blocks)
            )

        for media_key, media_rule in (
            self.nextyle.media_queries.items()
        ):
            media_blocks = self.render_context_actions(
                context,
                media_key,
            )

            if not media_blocks:
                continue

            inner_css = "\n\n".join(media_blocks)

            blocks.append(
                f"{media_rule} {{\n"
                f"{self.indent_css(inner_css)}\n"
                f"}}"
            )

        return "\n\n".join(blocks)

    def render_keyframes(self, context) -> str:
        blocks = []

        for step_name, declarations in (
            context.keyframe_rules.items()
        ):
            lines = [f"{step_name} {{"]

            for prop, value in declarations.items():
                lines.append(
                    f"    {prop}: {value};"
                )

            lines.append("}")

            blocks.append("\n".join(lines))

        if not blocks:
            return ""

        inner_css = "\n\n".join(blocks)

        return (
            f"@keyframes {context.value} {{\n"
            f"{self.indent_css(inner_css)}\n"
            f"}}"
        )

    def render_declaration_context(
        self,
        context,
        header: str,
    ) -> str:
        if not context.declarations:
            return ""

        declarations = self.render_declarations(
            context.declarations
        )

        return (
            f"{header} {{\n"
            f"{declarations}\n"
            f"}}"
        )

    def render_context(self, context) -> str:
        context_type = context.context_type

        if context_type == "root":
            blocks = []

            # @charset و global rawها باید اول باشند.
            if self.nextyle.global_raw_css:
                blocks.extend(
                    self.nextyle.global_raw_css
                )

            if self.nextyle.layer_order:
                blocks.append(
                    "@layer "
                    + ", ".join(
                        self.nextyle.layer_order
                    )
                    + ";"
                )

            content = self.render_media_aware_context(
                context
            )

            if content:
                blocks.append(content)

            return "\n\n".join(blocks)

        if context_type == "media":
            content = self.render_media_aware_context(
                context
            )

            if not content:
                return ""

            value = context.value.strip()

            if not value.startswith("@media"):
                value = f"@media {value}"

            return (
                f"{value} {{\n"
                f"{self.indent_css(content)}\n"
                f"}}"
            )

        if context_type == "supports":
            content = self.render_media_aware_context(
                context
            )

            if not content:
                return ""

            return (
                f"@supports {context.value} {{\n"
                f"{self.indent_css(content)}\n"
                f"}}"
            )

        if context_type == "container":
            content = self.render_media_aware_context(
                context
            )

            if not content:
                return ""

            return (
                f"@container {context.value} {{\n"
                f"{self.indent_css(content)}\n"
                f"}}"
            )

        if context_type == "layer":
            content = self.render_media_aware_context(
                context
            )

            if not content:
                return ""

            return (
                f"@layer {context.value} {{\n"
                f"{self.indent_css(content)}\n"
                f"}}"
            )

        if context_type == "scope":
            content = self.render_media_aware_context(
                context
            )

            if not content:
                return ""

            return (
                f"@scope {context.value} {{\n"
                f"{self.indent_css(content)}\n"
                f"}}"
            )

        if context_type == "starting-style":
            content = self.render_media_aware_context(
                context
            )

            if not content:
                return ""

            return (
                "@starting-style {\n"
                f"{self.indent_css(content)}\n"
                "}"
            )

        if context_type == "font-face":
            return self.render_declaration_context(
                context,
                "@font-face",
            )

        if context_type == "property":
            return self.render_declaration_context(
                context,
                f"@property {context.value}",
            )

        if context_type == "vars":
            return self.render_declaration_context(
                context,
                context.value,
            )

        if context_type == "page":
            header = "@page"

            if context.value.strip():
                header += f" {context.value.strip()}"

            return self.render_declaration_context(
                context,
                header,
            )

        if context_type == "keyframes":
            return self.render_keyframes(context)

        return ""

    def generate(self) -> str:
        css = self.render_context(
            self.nextyle.root_context
        )

        if not css:
            return ""

        return css.rstrip() + "\n"
