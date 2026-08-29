from __future__ import annotations

from typing import Optional

from ..helpers import indent_css
from ..nodes import ContextNode, RawCSSNode, SelectorNode
from .keyframe_renderer import KeyframeRenderer
from .selector_renderer import SelectorRenderer


class CSSRenderer:
    def __init__(self, nextyle):
        self.nextyle = nextyle
        self.selector_renderer = SelectorRenderer()
        self.keyframe_renderer = KeyframeRenderer()

    def render_declarations(self, declarations: dict[str, str], level: int = 1) -> str:
        prefix = "    " * level
        return "\n".join(f"{prefix}{property_name}: {value};" for property_name, value in declarations.items())

    def render_declaration_context(self, context: ContextNode, header: str) -> str:
        declarations = self.render_declarations(context.declarations)
        return f"{header} {{\n{declarations}\n}}" if declarations else ""

    def render_context_actions(self, context: ContextNode, variant_name: str = "base") -> list[str]:
        blocks = []

        for action in context.actions:
            if isinstance(action, RawCSSNode) and action.variant == variant_name:
                blocks.append(action.content)

            if isinstance(action, SelectorNode):
                css = self.selector_renderer.render(action, variant_name)

                if css:
                    blocks.append(css)

            if isinstance(action, ContextNode) and variant_name == "base":
                css = self.render_context(action)

                if css:
                    blocks.append(css)

        return blocks

    def render_media_aware_context(self, context: ContextNode) -> str:
        blocks = []
        base_blocks = self.render_context_actions(context, "base")

        if base_blocks:
            blocks.append("\n\n".join(base_blocks))

        for variant_name, variant in self.nextyle.variants.items():
            if variant_name == "base":
                continue

            variant_blocks = self.render_context_actions(context, variant_name)

            if variant_blocks:
                blocks.append(variant.wrap("\n\n".join(variant_blocks), indent_css))

        return "\n\n".join(blocks)

    def render_root(self, context: ContextNode) -> str:
        blocks = []

        if self.nextyle.stylesheet.global_raw_css:
            blocks.extend(self.nextyle.stylesheet.global_raw_css)

        if self.nextyle.layer_order:
            blocks.append(f"@layer {', '.join(self.nextyle.layer_order)};")

        content = self.render_media_aware_context(context)

        if content:
            blocks.append(content)

        return "\n\n".join(blocks)

    def render_media(self, context: ContextNode) -> str:
        content = self.render_media_aware_context(context)
        value = context.value.strip()
        header = value if value.startswith("@media") else f"@media {value}"
        return f"{header} {{\n{indent_css(content)}\n}}" if content else ""

    def render_supports(self, context: ContextNode) -> str:
        content = self.render_media_aware_context(context)
        return f"@supports {context.value} {{\n{indent_css(content)}\n}}" if content else ""

    def render_container(self, context: ContextNode) -> str:
        content = self.render_media_aware_context(context)
        return f"@container {context.value} {{\n{indent_css(content)}\n}}" if content else ""

    def render_layer(self, context: ContextNode) -> str:
        content = self.render_media_aware_context(context)
        return f"@layer {context.value} {{\n{indent_css(content)}\n}}" if content else ""

    def render_scope(self, context: ContextNode) -> str:
        content = self.render_media_aware_context(context)
        return f"@scope {context.value} {{\n{indent_css(content)}\n}}" if content else ""

    def render_starting_style(self, context: ContextNode) -> str:
        content = self.render_media_aware_context(context)
        return f"@starting-style {{\n{indent_css(content)}\n}}" if content else ""

    def render_font_face(self, context: ContextNode) -> str:
        return self.render_declaration_context(context, "@font-face")

    def render_property(self, context: ContextNode) -> str:
        return self.render_declaration_context(context, f"@property {context.value}")

    def render_vars(self, context: ContextNode) -> str:
        return self.render_declaration_context(context, context.value)

    def render_page(self, context: ContextNode) -> str:
        header = f"@page {context.value.strip()}" if context.value.strip() else "@page"
        return self.render_declaration_context(context, header)

    def render_keyframes(self, context: ContextNode) -> str:
        return self.keyframe_renderer.render(context, self.nextyle.variants)

    def render_scoping(self, context: ContextNode) -> str:
        return self.render_media_aware_context(context)

    def render_context(self, context: ContextNode) -> str:
        renderers = {
            "root": self.render_root,
            "media": self.render_media,
            "supports": self.render_supports,
            "container": self.render_container,
            "layer": self.render_layer,
            "scope": self.render_scope,
            "starting-style": self.render_starting_style,
            "font-face": self.render_font_face,
            "property": self.render_property,
            "vars": self.render_vars,
            "page": self.render_page,
            "keyframes": self.render_keyframes,
            "nexel-scoping": self.render_scoping,
            "nexel-scoping-auto": self.render_scoping,
        }

        return renderers[context.context_type](context)

    def generate(self) -> str:
        css = self.render_context(self.nextyle.stylesheet.root)
        return f"{css.rstrip()}\n" if css else ""
