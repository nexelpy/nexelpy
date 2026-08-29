from __future__ import annotations

import re
from pathlib import Path
from typing import Any, Dict, Optional, Tuple

from .context import CSSContext, ContextManager, FontFaceContextManager
from .keyframes import KeyframeStep
from .renderer import CSSRenderer
from .select import Select
from ..sharedClasses.nextyle_nexcript_path_control import NexetyleNexcriptPathControl


class Nextyle(NexetyleNexcriptPathControl):
    DEFAULT_MEDIA_QUERIES = {
        "sm": "@media (min-width: 640px)",
        "md": "@media (min-width: 768px)",
        "lg": "@media (min-width: 1024px)",
        "xl": "@media (min-width: 1280px)",
        "ul": "@media (min-width: 1536px)",
    }

    _RAW_URL_PATTERN = re.compile(r'url\(\s*(["\']?)(.*?)\1\s*\)')

    def __init__(self, file: str | Path, export_path: Optional[str | Path] = None, layer_order: Optional[Tuple[str, ...]] = None, **custom_media_queries):
        super().__init__(file)
        self.scope_token = self.scoping_token
        self.export_file = self._resolve_file_path(export_path) if export_path else self.file_path.with_suffix(".css")
        self.media_queries = self.DEFAULT_MEDIA_QUERIES.copy()
        self.media_queries.update(custom_media_queries)
        self.layer_order = layer_order or ()
        self.global_raw_css = []
        self.root_context = CSSContext(parent=self, context_type="root")
        self.context_stack = [self.root_context]
        self.href = "/" + self.export_file.relative_to(self.project_root).as_posix()
        self.renderer = CSSRenderer(self)

    @property
    def current_context(self) -> CSSContext:
        return self.context_stack[-1]

    def _push_context(self, context_type: str, value: str = "", extra: Optional[Dict[str, Any]] = None) -> CSSContext:
        context = CSSContext(parent=self, context_type=context_type, value=value, extra=extra)
        self.current_context.actions.append(("context", context))
        self.context_stack.append(context)
        return context

    def _pop_context(self) -> None:
        self.context_stack.pop()

    def _get_active_scope_selector(self) -> str:
        selectors = [context.value.strip() for context in self.context_stack if context.context_type in {"nexel-scoping", "nexel-scoping-auto"} and context.value.strip()]
        return " ".join(selectors)

    def url(self, path: str, format: Optional[str] = None) -> str:
        result = f'url("{self._url(path)}")'
        if format is not None:
            result += f' format("{format}")'
        return result

    def _resolve_raw_urls(self, raw_css: str) -> str:
        def replacer(match: re.Match) -> str:
            original_path = match.group(2).strip()
            if original_path.startswith(("http://", "https://", "data:", "//", "/")):
                return match.group(0)
            return f'url("{self._url(original_path)}")'
        return self._RAW_URL_PATTERN.sub(replacer, raw_css)

    def select(self, selector_name: str) -> Select:
        selector = Select(selector_name=selector_name, parent_nextyle=self, scope_selector=self._get_active_scope_selector())
        self.current_context.actions.append(selector)
        return selector

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
        return ContextManager(self, "keyframes", self._make_keyframe_name(name, scope))

    def _make_keyframe_name(self, name: str, scope: bool = True) -> str:
        return f"{name}--{self.scope_token}" if scope else name

    def property(self, name: str) -> ContextManager:
        return ContextManager(self, "property", name)

    def vars(self, selector: str = ":root") -> ContextManager:
        return ContextManager(self, "vars", selector)

    def scope(self, root_selector: str, to: Optional[str] = None) -> ContextManager:
        value = f"({root_selector})" if to is None else f"({root_selector}) to ({to})"
        return ContextManager(self, "scope", value)

    def scoping(self, selector: Optional[str] = None) -> ContextManager:
        context_type = "nexel-scoping-auto" if selector is None else "nexel-scoping"
        selector = f'[data-scoping="{self.scope_token}"]' if selector is None else selector
        return ContextManager(self, context_type, selector)

    def starting_style(self) -> ContextManager:
        return ContextManager(self, "starting-style")

    def page(self, selector: str = "") -> ContextManager:
        return ContextManager(self, "page", selector)

    def src(self, *sources: Any) -> "Nextyle":
        self.current_context.declarations["src"] = ", ".join(str(source) for source in sources)
        return self

    def step(self, value: Any) -> KeyframeStep:
        return KeyframeStep(self.current_context, value)

    def import_file(self, target: str) -> "Nextyle":
        self.current_context.actions.append(f"@import {target};")
        return self


    def add_var(self, **variables: Any) -> "Nextyle":
        for name, value in variables.items():
            name = name if name.startswith("--") else f"--{name}"
            self.current_context.declarations[name] = str(value)
        return self

    def __getattr__(self, name: str):
        css_property_name = name.replace("_", "-")

        def context_declaration(value: Any = None):
            value = "true" if value is True else "false" if value is False else value
            value = f'"{value}"' if self.current_context.context_type == "property" and css_property_name == "syntax" else value
            self.current_context.declarations[css_property_name] = str(value)
            return self

        return context_declaration

    def add_raw_css(self, raw_css: Optional[str] = None, **kwargs: str) -> "Nextyle":
        if raw_css is not None:
            resolved = self._resolve_raw_urls(raw_css.strip())
            self.current_context.actions.append(("raw", "base", resolved))
        for media_key, content in kwargs.items():
            resolved = self._resolve_raw_urls(content.strip())
            self.current_context.actions.append(("raw", media_key, resolved))
        return self

    def add_global_raw_css(self, raw_css: str) -> "Nextyle":
        resolved = self._resolve_raw_urls(raw_css.strip())
        self.global_raw_css.append(resolved)
        return self

    def generate_css(self) -> str:
        return self.renderer.generate()



    def export(self) -> None:
        css_content = self.generate_css()
        self.export_file.parent.mkdir(parents=True, exist_ok=True)
        self.export_file.write_text(css_content, encoding="utf-8")

    def __enter__(self) -> "Nextyle":
        return self

    def __exit__(self, exc_type, exc_value, traceback) -> bool:
        if exc_type is None:
            self.export()
        return False


