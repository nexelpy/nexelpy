from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, Optional, Tuple

from .context import (
    CSSContext,
    ContextManager,
    FontFaceContextManager,
)

from .keyframes import KeyframeStep
from .resolver import URLResolver
from .renderer import CSSRenderer
from .select import Select


class Nextyle:
    DEFAULT_MEDIA_QUERIES = {
        "sm": "@media (min-width: 640px)",
        "md": "@media (min-width: 768px)",
        "lg": "@media (min-width: 1024px)",
        "xl": "@media (min-width: 1280px)",
        "ul": "@media (min-width: 1536px)",
    }

    def __init__(
        self,
        file: str,
        export_path: Optional[str] = None,
        layer_order: Optional[Tuple[str, ...]] = None,
        **custom_media_queries,
    ):
        self.file_path = Path(file).resolve()
        self.current_dir = self.file_path.parent
        self.project_root = self._find_project_root(
            self.file_path
        )

        if export_path:
            target = Path(export_path)

            if target.is_absolute():
                self.export_file = target
            else:
                self.export_file = (
                    self.current_dir / target
                ).resolve()
        else:
            self.export_file = (
                self.file_path.with_suffix(".css")
            )

        self.media_queries = (
            self.DEFAULT_MEDIA_QUERIES.copy()
        )
        self.media_queries.update(
            custom_media_queries
        )

        self.layer_order = layer_order or ()

        self.global_raw_css = []

        self.root_context = CSSContext(
            parent=self,
            context_type="root",
        )

        self.context_stack = [
            self.root_context
        ]

        self.url_resolver = URLResolver(
            current_dir=self.current_dir,
            project_root=self.project_root,
        )

        self.renderer = CSSRenderer(self)

    # --------------------------------------------------------
    # Paths
    # --------------------------------------------------------

    def _find_project_root(
        self,
        start_file: Path,
    ) -> Path:
        current = start_file.parent

        for parent in [current, *current.parents]:
            if (parent / ".nexelpy").exists():
                return parent

        return current

    # --------------------------------------------------------
    # Context stack
    # --------------------------------------------------------

    @property
    def current_context(self) -> CSSContext:
        return self.context_stack[-1]

    def _push_context(
        self,
        context_type: str,
        value: str = "",
        extra: Optional[Dict[str, Any]] = None,
    ) -> CSSContext:
        context = CSSContext(
            parent=self,
            context_type=context_type,
            value=value,
            extra=extra,
        )

        self.current_context.actions.append(
            ("context", context)
        )

        self.context_stack.append(context)

        return context

    def _pop_context(self):
        self.context_stack.pop()

    # --------------------------------------------------------
    # URL API
    # --------------------------------------------------------

    def url(
        self,
        path: str,
        format: Optional[str] = None,
    ) -> str:
        return self.url_resolver.url(
            path,
            format=format,
        )

    # --------------------------------------------------------
    # Select
    # --------------------------------------------------------

    def select(self, selector_name: str) -> Select:
        selector = Select(
            selector_name=selector_name,
            parent_nextyle=self,
        )

        self.current_context.actions.append(
            selector
        )

        return selector

    # --------------------------------------------------------
    # Context APIs
    # --------------------------------------------------------

    def media(self, condition: str):
        return ContextManager(
            self,
            "media",
            condition,
        )

    def supports(self, condition: str):
        return ContextManager(
            self,
            "supports",
            condition,
        )

    def container(
        self,
        condition: str,
        name: Optional[str] = None,
    ):
        value = condition

        if name:
            value = f"{name} {condition}"

        return ContextManager(
            self,
            "container",
            value,
        )

    def layer(self, name: str):
        return ContextManager(
            self,
            "layer",
            name,
        )

    def font_face(self, family_name: str):
        return FontFaceContextManager(
            self,
            family_name,
        )

    def keyframes(self, name: str):
        return ContextManager(
            self,
            "keyframes",
            name,
        )

    def property(self, name: str):
        return ContextManager(
            self,
            "property",
            name,
        )

    def vars(self, selector: str = ":root"):
        return ContextManager(
            self,
            "vars",
            selector,
        )

    def scope(
        self,
        root_selector: str,
        to: Optional[str] = None,
    ):
        value = f"({root_selector})"

        if to is not None:
            value += f" to ({to})"

        return ContextManager(
            self,
            "scope",
            value,
        )

    def starting_style(self):
        return ContextManager(
            self,
            "starting-style",
        )

    def page(self, selector: str = ""):
        return ContextManager(
            self,
            "page",
            selector,
        )

    # --------------------------------------------------------
    # Font-face
    # --------------------------------------------------------

    def src(self, *sources: Any):
        self.current_context.declarations["src"] = (
            ", ".join(str(source) for source in sources)
        )

        return self

    # --------------------------------------------------------
    # Keyframes
    # --------------------------------------------------------

    def from_(self):
        return KeyframeStep(
            self.current_context,
            "from",
        )

    def to(self):
        return KeyframeStep(
            self.current_context,
            "to",
        )

    def at(self, value):
        return KeyframeStep(
            self.current_context,
            value,
        )

    # --------------------------------------------------------
    # Variables
    # --------------------------------------------------------

    def add_var(self, **variables):
        for name, value in variables.items():
            if not name.startswith("--"):
                name = f"--{name}"

            self.current_context.declarations[name] = (
                str(value)
            )

        return self

    # --------------------------------------------------------
    # Context declarations
    # --------------------------------------------------------

    def __getattr__(self, name: str):
        css_property_name = name.replace("_", "-")

        def context_declaration(value: Any = None):
            if isinstance(value, bool):
                value = "true" if value else "false"

            elif (
                self.current_context.context_type == "property"
                and css_property_name == "syntax"
            ):
                value = f'"{value}"'

            self.current_context.declarations[
                css_property_name
            ] = str(value)

            return self

        return context_declaration

    # --------------------------------------------------------
    # Raw CSS
    # --------------------------------------------------------

    def add_raw_css(
        self,
        raw_css: Optional[str] = None,
        **kwargs,
    ):
        if raw_css is not None:
            resolved = (
                self.url_resolver.resolve_raw_urls(
                    raw_css.strip()
                )
            )

            self.current_context.actions.append(
                ("raw", "base", resolved)
            )

        for media_key, content in kwargs.items():
            resolved = (
                self.url_resolver.resolve_raw_urls(
                    content.strip()
                )
            )

            self.current_context.actions.append(
                ("raw", media_key, resolved)
            )

        return self

    def add_global_raw_css(self, raw_css: str):
        resolved = (
            self.url_resolver.resolve_raw_urls(
                raw_css.strip()
            )
        )

        self.global_raw_css.append(resolved)

        return self

    # --------------------------------------------------------
    # Rendering / export
    # --------------------------------------------------------

    def generate_css(self) -> str:
        return self.renderer.generate()

    def export(self):
        css_content = self.generate_css()

        self.export_file.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        self.export_file.write_text(
            css_content,
            encoding="utf-8",
        )

    def __enter__(self):
        return self

    def __exit__(
        self,
        exc_type,
        exc_value,
        traceback,
    ):
        if exc_type is None:
            self.export()

        return False
