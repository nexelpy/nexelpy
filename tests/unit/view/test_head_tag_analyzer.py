# tests/unit/view/test_head_tag_analyzer.py
from nexelpy.view.tagBuilder import TagBuilder
from nexelpy.view.headTagAnalyzer import HeadTagAnalyzer


def _head():
    return TagBuilder("head")


def test_title_dedupe():
    h = _head()
    TagBuilder("title", "A", parent=h)
    TagBuilder("title", "B", parent=h)
    HeadTagAnalyzer(h).analyze()
    assert len(h.children) == 1
    assert h.children[0].text == "B"


def test_meta_charset_key():
    h = _head()
    TagBuilder("meta", selfClose=True, parent=h, charset="UTF-8")
    HeadTagAnalyzer(h).analyze()
    assert len(h.children) == 1


def test_meta_same_name_dedupe():
    h = _head()
    TagBuilder("meta", selfClose=True, parent=h, name="description", content="a")
    TagBuilder("meta", selfClose=True, parent=h, name="description", content="b")
    HeadTagAnalyzer(h).analyze()
    assert len(h.children) == 1
    assert h.children[0].attribute["content"] == "b"


def test_script_src_key():
    h = _head()
    TagBuilder("script", parent=h, src="/a.js")
    TagBuilder("script", parent=h, src="/a.js")
    HeadTagAnalyzer(h).analyze()
    assert len(h.children) == 1


def test_inline_script_keyed_by_content():
    h = _head()
    TagBuilder("script", "console.log(1)", parent=h)
    TagBuilder("script", "console.log(1)", parent=h)
    HeadTagAnalyzer(h).analyze()
    assert len(h.children) == 1


def test_link_href_key():
    h = _head()
    TagBuilder("link", selfClose=True, parent=h, href="/a.css", rel="stylesheet")
    TagBuilder("link", selfClose=True, parent=h, href="/a.css", rel="stylesheet")
    HeadTagAnalyzer(h).analyze()
    assert len(h.children) == 1


def test_unknown_tag_preserved():
    h = _head()
    TagBuilder("base", selfClose=True, parent=h, href="/")
    HeadTagAnalyzer(h).analyze()
    assert len(h.children) == 1