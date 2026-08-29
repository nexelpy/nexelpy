from __future__ import annotations

from pathlib import Path
from typing import Any, Optional

from .context import ContextManager, FontFaceContextManager
from .keyframes import KeyframeStep
from .nodes import RawCSSNode, SelectorNode
from .selector import Select
from .stylesheet import Stylesheet
from .url_resolver import URLResolver
from .variants import VariantRegistry
from .renderers import CSSRenderer
from ..sharedClasses.nextyle_nexcript_path_control import NexetyleNexcriptPathControl


class Nextyle(NexetyleNexcriptPathControl):
    DEFAULT_MEDIA_QUERIES = {
        "sm": "@media (min-width: 640px)",
        "md": "@media (min-width: 768px)",
        "lg": "@media (min-width: 1024px)",
        "xl": "@media (min-width: 1280px)",
        "ul": "@media (min-width: 1536px)",
    }

    def __init__(self, file: str | Path, export_path: Optional[str | Path] = None, layer_order: Optional[tuple[str, ...]] = None, **custom_media_queries: str):
        super().__init__(file)
        self.scope_token = self.scoping_token
        self.export_file = self._resolve_file_path(export_path) if export_path else self.file_path.with_suffix(".css")
        self.href = "/" + self.export_file.relative_to(self.project_root).as_posix()
        self.layer_order = layer_order or ()
        self.stylesheet = Stylesheet()
        self.variants = VariantRegistry(self.DEFAULT_MEDIA_QUERIES | custom_media_queries)
        self.url_resolver = URLResolver(self)
        self.renderer = CSSRenderer(self)

    @property
    def current_context(self):
        return self.stylesheet.current_context

    def url(self, path: str, format: Optional[str] = None) -> str:
        value = f'url("{self._url(path)}")'
        return f'{value} format("{format}")' if format is not None else value

    def select(self, selector: str) -> Select:
        node = SelectorNode(selector=selector, scope_selector=self.stylesheet.active_scope_selector())
        self.stylesheet.append(node)
        return Select(node=node, parent_nextyle=self)

    def media(self, condition: str) -> ContextManager:
        return ContextManager(self, "media", condition)

    def supports(self, condition: str) -> ContextManager:
        return ContextManager(self, "supports", condition)

    def container(self, condition: str, name: Optional[str] = None) -> ContextManager:
        value = f"{name} {condition}" if name else condition
        return ContextManager(self, "container", value)

    def layer(self, name: str) -> ContextManager:
        return ContextManager(self, "layer", name)

    def font_face(self, family_name: str) -> FontFaceContextManager:
        return FontFaceContextManager(self, family_name)

    def keyframes(self, name: str, scope: bool = True) -> ContextManager:
        value = self._make_keyframe_name(name, scope)
        return ContextManager(self, "keyframes", value)

    def property(self, name: str) -> ContextManager:
        return ContextManager(self, "property", name)

    def vars(self, selector: str = ":root") -> ContextManager:
        return ContextManager(self, "vars", selector)

    def scope(self, root_selector: str, to: Optional[str] = None) -> ContextManager:
        value = f"({root_selector})" if to is None else f"({root_selector}) to ({to})"
        return ContextManager(self, "scope", value)

    def scoping(self, selector: Optional[str] = None) -> ContextManager:
        context_type = "nexel-scoping-auto" if selector is None else "nexel-scoping"
        value = f'[data-scoping="{self.scope_token}"]' if selector is None else selector
        return ContextManager(self, context_type, value)

    def starting_style(self) -> ContextManager:
        return ContextManager(self, "starting-style")

    def page(self, selector: str = "") -> ContextManager:
        return ContextManager(self, "page", selector)

    def src(self, *sources: Any) -> "Nextyle":
        self.current_context.declarations["src"] = ", ".join(str(source) for source in sources)
        return self

    def step(self, value: Any) -> KeyframeStep:
        return KeyframeStep(self.current_context, value)

    def add_var(self, **variables: Any) -> "Nextyle":
        for name, value in variables.items():
            property_name = name if name.startswith("--") else f"--{name}"
            self.current_context.declarations[property_name] = str(value)
        return self

    def add_raw_css(self, raw_css: Optional[str] = None, **variants: str) -> "Nextyle":
        if raw_css is not None:
            content = self.url_resolver.resolve_raw_css(raw_css.strip())
            self.stylesheet.append(RawCSSNode(content=content))

        for variant_name, content in variants.items():
            resolved_content = self.url_resolver.resolve_raw_css(content.strip())
            self.stylesheet.append(RawCSSNode(content=resolved_content, variant=variant_name))

        return self

    def add_global_raw_css(self, raw_css: str) -> "Nextyle":
        content = self.url_resolver.resolve_raw_css(raw_css.strip())
        self.stylesheet.add_global_raw_css(content)
        return self

    def _make_keyframe_name(self, name: str, scope: bool = True) -> str:
        return f"{name}--{self.scope_token}" if scope else name

    def __getattr__(self, name: str):
        css_property = name.replace("_", "-")

        def context_declaration(value: Any = None) -> "Nextyle":
            value = "true" if value is True else "false" if value is False else value
            value = f'"{value}"' if self.current_context.context_type == "property" and css_property == "syntax" else value
            self.current_context.declarations[css_property] = str(value)
            return self

        return context_declaration

    def generate_css(self) -> str:
        return self.renderer.generate()

    def export(self) -> None:
        self.export_file.parent.mkdir(parents=True, exist_ok=True)
        self.export_file.write_text(self.generate_css(), encoding="utf-8")

    def __enter__(self) -> "Nextyle":
        return self

    def __exit__(self, exc_type, exc_value, traceback) -> bool:
        if exc_type is None:
            self.export()

        return False
