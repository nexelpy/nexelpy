from .parentResolverBase import ParentResolverBase
from .tagBuilder import TagBuilder,RawHTML
from .pathBuilder import PathBuilder

class ElementBuilder(ParentResolverBase,PathBuilder):
    def __init__(self):
        super().__init__()
        self.elementsContainer = TagBuilder(tagName="elementsContainer")
        self.elementsContainer.builder = self
        
    def raw(self, html, parent=None):
        node = RawHTML(html, parent=self.setParent(parent))
        node.builder = self
        return node

    def element(self, tagName="empty", text="", selfClose=False, props="", parent=None, **attributes):
        self._normalize_paths(attributes)
        tag = TagBuilder(tagName=tagName, text=text, selfClose=selfClose, props=props,parent=self.setParent(parent), **attributes)
        tag.builder = self
        return tag



#--------------------------------------------------------------------------------------
def _make_tag_method(tag_name, self_close=False):
    def _method(self, text="", props="", parent=None, **attributes):
        return self.element(tagName=tag_name, text=text, props=props,
                            parent=parent, selfClose=self_close, **attributes)
    _method.__name__ = tag_name
    return _method


SELF_CLOSING_TAGS = [
    "img","source","track","link","area","base",
    "br", "col", "embed",
    "hr" , "input","meta",
    "param", "wbr",
]

NORMAL_TAGS = [
    "script","iframe","video","audio","a","style",
    "address", "article", "aside", "footer", "header", "h1", "h2", "h3",
    "h4", "h5", "h6", "hgroup", "main", "nav", "section",
    "blockquote", "dd", "div", "dl", "dt", "figcaption", "figure",
    "li", "menu", "ol", "p", "pre", "ul",
    "abbr", "b", "bdi", "bdo", "cite", "code", "data", "dfn",
    "em", "i", "kbd", "mark", "q", "rp", "rt", "ruby", "s", "samp",
    "small", "span", "strong", "sub", "sup", "time", "u", "var",
    "canvas",
    "object", "picture",
    "noscript",
    "caption", "colgroup", "table", "tbody", "td", "tfoot", "th", "thead", "tr",
    "button", "datalist", "fieldset", "form", "label", "legend", "meter",
    "optgroup", "option", "output", "progress", "select", "textarea",
    "details", "dialog", "summary",
    "del", "ins",
]

for tag in NORMAL_TAGS:
    setattr(ElementBuilder, tag, _make_tag_method(tag, self_close=False))

for tag in SELF_CLOSING_TAGS:
    setattr(ElementBuilder, tag, _make_tag_method(tag, self_close=True)) 