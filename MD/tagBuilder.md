# TagBuilder class

### init args:
```python
def __init__(self, tagName="NoName", text="", textEnd="",selfClose=False,props="", parent=None,**attributes):
```
| arg | type | description |
|-----|------|-------------|
| tagName | `str` | set tag name |
| text | `str` | set innerText for this tag |
| textEnd | `str` | append text to end of the childrens in this tag<br>example:```<p>text<span>text</span>endText</p>```|
|selfClose|`bool`|set tag mode . self close like `<img href=google.com/>` or normal tag like `<p>this is paragraph<p/>`|
|props|`str`|set no value attribute for tag.example: `required selected disabled`|
|parent|`obj` of TagBuilder|append this tag to child of parent.|
|attributes|`dict`|set any attribute for this tag.<br>for use: `Class="bg-red",id="myid",name="username",type="text"`<br>result: `<input class=bg-red id=myid name=username type=text />`
----
### build_tag:
build_tag method create tree object of the tag with chidren
```python
@property
def build_tag(self):
    tag = self.tagName
    attrs = " ".join(f'{k.replace("_", "-").lower()}={v}' for k, v in self.attribute.items()) if self.attribute else ""
    vla = self.props
    # build self-closing tag
    if self.selfClose:
        return f"<{tag}{(' ' + attrs) if attrs else ''}{(' ' + vla) if vla else ''}/>"
    # build normal tag
    content = ((self.text or "") + self.content + (self.textEnd or ""))
    open_tag = f"<{tag}{(' ' + attrs) if attrs else ''}{(' ' + vla) if vla else ''}>"
    return f"{open_tag}{content}</{tag}>"
```
### content:
content method export tree objects as a string
```python
@property
def content(self):
    html_parts = []
    for child in self.children:
        html_parts.append(child.build_tag)
    return "".join(html_parts)
```
### with:
below methods make contex manager for objects of TagBuilder
```python
_parent_stack = [] 
def __enter__(self):
        TagBuilder._parent_stack.append(self)
        return self

def __exit__(self, exc_type, exc_val, exc_tb):
    TagBuilder._parent_stack.pop()

@classmethod
def get_current_parent(cls):
    return cls._parent_stack[-1] if cls._parent_stack else None
```
*example :*
```python
with TagBuilder(tagName="div"):
    TagBuilder(tagName="p",text="contex Manager")
```
*result :*
```html
<div>
    <p>contex Manager<p/>
<div/>
```
