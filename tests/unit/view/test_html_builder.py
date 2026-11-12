# tests/unit/view/test_html_builder.py
from nexelpy.view.htmlBuilder import HTMLBuilder


def test_doctype_and_skeleton():
    h = HTMLBuilder(title="T")
    out = h.render()
    assert out.startswith("<!DOCTYPE html/>")
    assert "<html>" in out
    assert "<head>" in out
    assert "<body>" in out


def test_title_set():
    h = HTMLBuilder(title="My Page")
    assert "<title>My Page</title>" in h.render()


def test_default_title():
    h = HTMLBuilder()
    assert "<title>NexelPy</title>" in h.render()


def test_meta_charset_present():
    h = HTMLBuilder()
    assert "charset='UTF-8'" in h.render()


def test_custom_body_content():
    h = HTMLBuilder()
    h.h1("Welcome")
    assert "<h1>Welcome</h1>" in h.render()


def test_head_analyzer_dedupes():
    h = HTMLBuilder(title="A")
    h.element("title", "B", parent=h.headTag)
    out = h.render()
    assert out.count("<title>") == 1