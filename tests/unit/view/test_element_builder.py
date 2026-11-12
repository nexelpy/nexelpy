# tests/unit/view/test_element_builder.py
import pytest
from nexelpy.view.elementBuilder import ElementBuilder


class Dummy(ElementBuilder):
    def __init__(self):
        super().__init__()
        self.bodyTag = self.element("body", parent=self.elementsContainer)


def test_element_creates_tag_and_sets_builder():
    d = Dummy()
    t = d.element("div", "x")
    assert t.builder is d
    assert "<div>x</div>" in d.elementsContainer.build_tag


def test_default_parent_is_body():
    d = Dummy()
    t = d.div("hello")
    assert t.parent is d.bodyTag


def test_explicit_parent():
    d = Dummy()
    sec = d.section()
    p = d.p("text", parent=sec)
    assert p.parent is sec


def test_stack_used_as_parent():
    d = Dummy()
    sec = d.section()
    d._parent_stack.append(sec)
    try:
        p = d.p("x")
        assert p.parent is sec
    finally:
        d._parent_stack.pop()


def test_self_closing_tag():
    d = Dummy()
    img = d.img(src="/x.png")
    assert img.selfClose is True
    assert "<img src='/x.png'/>" in img.build_tag


def test_all_normal_tags_exist():
    from nexelpy.view.elementBuilder import NORMAL_TAGS
    d = Dummy()
    for tag in NORMAL_TAGS:
        method = getattr(d, tag, None)
        assert callable(method), f"missing tag method: {tag}"


def test_all_self_closing_tags_exist():
    from nexelpy.view.elementBuilder import SELF_CLOSING_TAGS
    d = Dummy()
    for tag in SELF_CLOSING_TAGS:
        assert callable(getattr(d, tag))


def test_raw_returns_rawhtml():
    d = Dummy()
    r = d.raw("<custom/>")
    assert r.html == "<custom/>"
    assert "<custom/>" in d.elementsContainer.build_tag