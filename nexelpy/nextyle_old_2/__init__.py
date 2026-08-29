from __future__ import annotations

from .context_renderer import ContextRenderer
from .keyframe_renderer import KeyframeRenderer
from .selector_renderer import SelectorRenderer


class CSSRenderer:
    def __init__(self, nextyle):
        self.nextyle = nextyle
        self.selector_renderer = SelectorRenderer()
        self.keyframe_renderer = KeyframeRenderer()
        self.context_renderer = ContextRenderer(nextyle, self.selector_renderer, self.keyframe_renderer)

    def generate(self) -> str:
        css = self.context_renderer.render_context(self.nextyle.stylesheet.root)
        return css.rstrip() + "\n" if css else ""
