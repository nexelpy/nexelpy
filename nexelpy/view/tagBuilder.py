from typing import Any

class TagBuilder:
    def __init__(self, tagName:str="NoName", text:str="", selfClose:bool=False, props:str="", parent=None, **attributes:dict[str, Any]):
        super().__init__()
        self.tagName = tagName
        self.selfClose = selfClose
        self.text = str(text)
        self.props = props
        self.attribute = attributes
        self.value = None
        self.children:list["TagBuilder"] = []
        self.builder = None

        self.parent = parent
        if self.parent:
            self.parent.children.append(self)

    @property
    def build_tag(self):
        tag = self.tagName
        attrs = " ".join(f'{k.lower().replace("__","-")}="{str(v).replace("\"","\'")}"' for k, v in self.attribute.items()) if self.attribute else ""
        vla = self.props
        if self.selfClose:
            return f"<{tag}{(' ' + attrs) if attrs else ''}{(' ' + vla) if vla else ''}/>"
        content = (self.text or "") + self.content
        open_tag = f"<{tag}{(' ' + attrs) if attrs else ''}{(' ' + vla) if vla else ''}>"
        return f"{open_tag}{content}</{tag}>"

    @property
    def content(self):
        return "".join(child.build_tag for child in self.children)
    
    # ------------------------ WITH -----------------------------
    def __enter__(self):
        if self.builder:
            self.builder._parent_stack.append(self)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.builder:
            self.builder._parent_stack.pop()

# -----------------------------------------------------------
# ------------------------ RawHTML --------------------------
# -----------------------------------------------------------
class RawHTML:
    def __init__(self, html, parent=None):
        self.html = html
        self.parent = parent
        if self.parent:
            self.parent.children.append(self)
        self.builder = None

    @property
    def build_tag(self):
        return self.html
    

