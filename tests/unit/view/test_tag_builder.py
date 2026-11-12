# tests/unit/view/test_tag_builder.py
import pytest
from nexelpy.view.tagBuilder import TagBuilder, RawHTML


# ---------------- base ----------------
def test_tag_simple():
    assert TagBuilder("div", "hello").build_tag == "<div>hello</div>"


def test_tag_attributes():
    tag = TagBuilder("a", "click", href="/home", Class="link")
    assert tag.build_tag == "<a href='/home' class='link'>click</a>"


def test_tag_self_closing():
    tag = TagBuilder("img", selfClose=True, src="/logo.png")
    assert tag.build_tag == "<img src='/logo.png'/>"


def test_tag_no_attrs():
    assert TagBuilder("br", selfClose=True).build_tag == "<br/>"


def test_tag_empty_text():
    assert TagBuilder("div").build_tag == "<div></div>"


def test_tag_props_injected():
    assert TagBuilder("div", props="data-x=1").build_tag == "<div data-x=1></div>"


# ---------------- children ----------------
def test_nested_children():
    parent = TagBuilder("div")
    child = TagBuilder("span", "x", parent=parent)
    assert parent.build_tag == "<div><span>x</span></div>"


def test_multiple_children_order_preserved():
    p = TagBuilder("ul")
    TagBuilder("li", "a", parent=p)
    TagBuilder("li", "b", parent=p)
    assert p.build_tag == "<ul><li>a</li><li>b</li></ul>"


def test_deep_nesting():
    root = TagBuilder("div")
    a = TagBuilder("section", parent=root)
    b = TagBuilder("p", "hi", parent=a)
    assert root.build_tag == "<div><section><p>hi</p></section></div>"


# ---------------- escape ----------------
def test_text_not_escaped_but_attrs_are():
    tag = TagBuilder("div", text="<b>x</b>", title='a"b')
    assert "<b>x</b>" in tag.build_tag
    assert 'title=\'a&quot;b\'' in tag.build_tag


def test_attribute_with_apostrophe_escaped_as_entity():
    tag = TagBuilder("div", title="it's")
    # escape(quote=True) -> &#x27;
    assert "&#x27;" in tag.build_tag


def test_list_attribute_serialized_as_json():
    tag = TagBuilder("div", data_items=["a", "b"])
    # json.dumps -> ["a", "b"]
    assert "&#x22;" in tag.build_tag or "[" in tag.build_tag


def test_dict_attribute_serialized_as_json():
    tag = TagBuilder("div", data_map={"a": 1})
    assert "{" in tag.build_tag


# ---------------- name normalization ----------------
def test_class_alias():
    tag = TagBuilder("div", Class="x")
    assert "class='x'" in tag.build_tag


def test_double_underscore_becomes_dash():
    tag = TagBuilder("div", aria__label="hi")
    assert "aria-label='hi'" in tag.build_tag


# ---------------- context manager ----------------
def test_with_context_manager_pushes_stack():
    class FakeBuilder:
        def __init__(self):
            self._parent_stack = []

    p = TagBuilder("div")
    b = FakeBuilder()
    p.builder = b
    with p:
        assert b._parent_stack == [p]
    assert b._parent_stack == []


def test_raw_html():
    r = RawHTML("<p>raw</p>")
    assert r.build_tag == "<p>raw</p>"


def test_raw_html_with_parent():
    p = TagBuilder("div")
    RawHTML("<span>x</span>", parent=p)
    assert p.build_tag == "<div><span>x</span></div>"