from .tagBuilder import TagBuilder,RawHTML

class ElementBuilder():
    def __init__(self):
        super().__init__()
        self._parent_stack = []
        self.elementsContainer = TagBuilder(tagName="elementsContainer")
        # self.elementsContainer.builder = self

    def _setParent(self, parent=None):
        if parent is not None:
            return parent
        stack = self._parent_stack
        return stack[-1] if stack else self.BODY_tag
    
    def raw(self, html, parent=None):
        node = RawHTML(html, parent=self._setParent(parent))
        node.builder = self
        return node

    def element(self, tagName="empty", text="", selfClose=False, props="", parent=None, **attributes):
        tag = TagBuilder(tagName=tagName, text=text, selfClose=selfClose, props=props,parent=self._setParent(parent), **attributes)
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
    "script","iframe","video","audio","a","style","title",
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