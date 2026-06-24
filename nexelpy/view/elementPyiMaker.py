from pathlib import Path
from typing import Any, Optional

SELF_CLOSING_TAGS = [
    "area", "base", "br", "col", "embed",
    "hr", "img", "link", "meta",
    "param", "source", "track", "wbr",
]

SPECIAL_TAGS = {
    "script": "code",
    "style": "css",
}

NORMAL_TAGS = [
    "address", "article", "aside", "footer","script","style",
    "h1", "h2", "h3", "h4", "h5", "h6", "hgroup", "main", "nav", "section",
    "blockquote", "dd", "div", "dl", "dt", "figcaption", "figure",
    "li", "menu", "ol", "p", "pre", "ul",
    "a", "abbr", "b", "bdi", "bdo", "cite", "code", "data", "dfn",
    "em", "i", "kbd", "mark", "q", "rp", "rt", "ruby", "s", "samp",
    "small", "span", "strong", "sub", "sup", "time", "u", "var",
    "audio", "canvas", "video",
    "iframe", "object", "picture",
    "noscript",
    "caption", "colgroup", "table", "tbody", "td", "tfoot", "th", "thead", "tr",
    "button", "datalist", "fieldset", "label", "legend", "meter",
    "optgroup", "option", "output", "progress", "select", "textarea",
    "details", "dialog", "summary",
    "Del", "ins",
]

all_tags = NORMAL_TAGS + SELF_CLOSING_TAGS

header = f'''# pyi for elements
from typing import Union, Optional, Any
from .tagBuilder import TagBuilder, RawHTML

class ElementBuilder:
    def __init__(self) -> None: ...
    def raw(self, html: str, parent: Optional[TagBuilder] = None) -> RawHTML: ...
    def element(self, tagName: str = "empty-tag", text: Any = "", selfClose: bool = False, props: str = "", parent: Optional[TagBuilder] = None, **attributes: Any) -> TagBuilder: ...
'''

methods = []

for tag in all_tags:
    if tag in SPECIAL_TAGS:
        # تگ‌های خاص با پارامتر متفاوت
        param_name = SPECIAL_TAGS[tag]
        methods.append(f'    def {tag}(self, {param_name}: Any = "", props: str = "", parent: Optional[TagBuilder] = None, **attributes: Any) -> TagBuilder: ...')
    else:
        # تگ‌های معمولی با پارامتر 'text'
        methods.append(f'    def {tag}(self, text: Any = "", props: str = "", parent: Optional[TagBuilder] = None, **attributes: Any) -> TagBuilder: ...')

content = header + "\n" + "\n".join(methods) + "\n"

file_path = Path(__file__).parent / "elementBuilder.pyi"
file_path.write_text(content, encoding="utf-8")
print(f"elementBuilder.pyi generated at {file_path}")





# BASE_ATTRIBUTES = [
#     "id: Optional[str] = None",
#     "Class: Optional[str] = None",
#     "style: Optional[str] = None",
#     "title: Optional[str] = None",
#     "lang: Optional[str] = None",
#     "dir: Optional[str] = None",
#     "tabindex: Optional[int] = None",
#     "accesskey: Optional[str] = None",
#     "draggable: Optional[bool] = None",
#     "spellcheck: Optional[bool] = None",
#     "contenteditable: Optional[bool] = None",
#     "translate: Optional[bool] = None",

#     "src: Optional[str] = None",
#     "href: Optional[str] = None",
#     "alt: Optional[str] = None",
#     "download: Optional[Union[str, bool]] = None",
#     "rel: Optional[str] = None",
#     "target: Optional[str] = None",
#     "type: Optional[str] = None",

#     "name: Optional[str] = None",
#     "value: Optional[str] = None",
#     "placeholder: Optional[str] = None",
#     "required: Optional[bool] = None",
#     "autofocus: Optional[bool] = None",
#     "maxlength: Optional[int] = None",
#     "minlength: Optional[int] = None",
#     "size: Optional[int] = None",
#     "multiple: Optional[bool] = None",
#     "accept: Optional[str] = None",
#     "pattern: Optional[str] = None",
#     "min: Optional[Union[int, float]] = None",
#     "max: Optional[Union[int, float]] = None",
#     "step: Optional[Union[int, float]] = None",

#     "onclick: Optional[str] = None",
#     "ondblclick: Optional[str] = None",
#     "onmousedown: Optional[str] = None",
#     "onmouseup: Optional[str] = None",
#     "onmouseover: Optional[str] = None",
#     "onmouseout: Optional[str] = None",
#     "onmousemove: Optional[str] = None",
#     "onkeydown: Optional[str] = None",
#     "onkeyup: Optional[str] = None",
#     "onkeypress: Optional[str] = None",
#     "onchange: Optional[str] = None",
#     "oninput: Optional[str] = None",
#     "onsubmit: Optional[str] = None",
#     "onreset: Optional[str] = None",
#     "onfocus: Optional[str] = None",
#     "onblur: Optional[str] = None",
#     "onload: Optional[str] = None",
#     "onerror: Optional[str] = None",
#     "onscroll: Optional[str] = None",
#     "onresize: Optional[str] = None",

#     "colspan: Optional[int] = None",
#     "rowspan: Optional[int] = None",
#     "scope: Optional[str] = None",

#     "controls: Optional[bool] = None",
#     "autoplay: Optional[bool] = None",
#     "loop: Optional[bool] = None",
#     "muted: Optional[bool] = None",
#     "poster: Optional[str] = None",
#     "preload: Optional[str] = None",
#     "playsinline: Optional[bool] = None",

#     "allow: Optional[str] = None",
#     "allowfullscreen: Optional[bool] = None",
#     "sandbox: Optional[str] = None",

#     "async_: Optional[bool] = None",
#     "defer: Optional[bool] = None",
#     "crossorigin: Optional[str] = None",
#     "integrity: Optional[str] = None",
#     "loading: Optional[str] = None",
#     "decoding: Optional[str] = None",
#     "fetchpriority: Optional[str] = None",
# ]

