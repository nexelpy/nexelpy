import pytest
from unittest.mock import MagicMock
from pathlib import Path
import asyncio

from nexelpy.view.pluginBuilder import PluginBuilder
from nexelpy.mediator.request_proxy.request_object import set_request, reset_request
from starlette.requests import Request


def _make_request(root):
    scope = {
        "type": "http",
        "method": "GET",
        "path": "/",
        "headers": [],
        "query_string": b"",
        "app": MagicMock(root_Path=str(root)),
    }
    return Request(scope)


@pytest.fixture
def plugin(tmp_path):
    main = tmp_path / "main.py"
    main.touch()
    token = set_request(_make_request(tmp_path))
    try:
        yield PluginBuilder(str(main))
    finally:
        reset_request(token)


def test_init_sets_skeleton(plugin):
    body = plugin.elementsContainer.build_tag
    assert "<!DOCTYPE html/>" in body
    assert "<html>" in body
    assert "<head>" in body
    assert "<body>" in body


def test_scoping_returns_div_with_token(plugin):
    tag = plugin.scoping("x")
    assert tag.tagName == "div"
    assert tag.attribute["data-scoping"] == plugin.scoping_token


def test_url_resolves_relative(plugin):
    url = plugin.url("./style.css")
    assert url.startswith("/")
    assert url.endswith("style.css")


def test_url_returns_non_dot_unchanged(plugin):
    assert plugin.url("/static/x.js") == "/static/x.js"


def test_redirect_raises(plugin):
    from nexelpy.mediator.reDirect import RedirectException

    with pytest.raises(RedirectException) as exc:
        plugin.redirect("/login")
    assert exc.value.url == "/login"
    assert exc.value.status_code == 307


def test_redirect_with_custom_status(plugin):
    from nexelpy.mediator.reDirect import RedirectException

    with pytest.raises(RedirectException) as exc:
        plugin.redirect("/x", status_code=308)
    assert exc.value.status_code == 308


def test_redirect_with_query_params(plugin):
    from nexelpy.mediator.reDirect import RedirectException

    with pytest.raises(RedirectException) as exc:
        plugin.redirect("/login", next="/home", code=42, skip=None)
    assert "next=%2Fhome" in exc.value.url
    assert "code=42" in exc.value.url
    assert "skip" not in exc.value.url


def test_redirect_with_existing_query(plugin):
    from nexelpy.mediator.reDirect import RedirectException

    with pytest.raises(RedirectException) as exc:
        plugin.redirect("/x?a=1", b=2)
    assert exc.value.url.startswith("/x?a=1&")
    assert "b=2" in exc.value.url


def test_response_stores_data_and_returns_self(plugin):
    result = plugin.RESPONSE("first", "second")
    assert result is plugin
    assert plugin._plugin_return_func_data == ("first", "second")


def test_import_plugin_merges_body_head_and_cookies(tmp_path):
    main = tmp_path / "main.py"
    main.touch()
    token = set_request(_make_request(tmp_path))
    try:
        parent = PluginBuilder(str(main))

        child = PluginBuilder(str(main))
        child.element("script", parent=child.headTag, src="/child.js")
        child.element("p", "child", parent=child.bodyTag)
        child.set_Cookie("from_child", "yes")
        child.RESPONSE("only_one")

        result = parent.importPlugin(child)

        assert result == "only_one"
        assert any(
            getattr(c, "attribute", {}).get("src") == "/child.js"
            for c in parent.headTag.children
        )
        assert any(
            getattr(c, "text", "") == "child" for c in parent.bodyTag.children
        )
        assert any(c["key"] == "from_child" for c in parent._cookies_list)
    finally:
        reset_request(token)


def test_import_plugin_returns_tuple_when_multiple(tmp_path):
    main = tmp_path / "main.py"
    main.touch()
    token = set_request(_make_request(tmp_path))
    try:
        parent = PluginBuilder(str(main))
        child = PluginBuilder(str(main))
        child.RESPONSE("a", "b")
        result = parent.importPlugin(child)
        assert result == ("a", "b")
    finally:
        reset_request(token)


def test_import_plugin_with_explicit_parent(tmp_path):
    main = tmp_path / "main.py"
    main.touch()
    token = set_request(_make_request(tmp_path))
    try:
        parent = PluginBuilder(str(main))
        target = parent.element("section")
        child = PluginBuilder(str(main))
        child.element("span", "inner", parent=child.bodyTag)
        child.RESPONSE("done")
        parent.importPlugin(child, parent=target)
        assert any(
            getattr(c, "tagName", None) == "span" for c in target.children
        )
    finally:
        reset_request(token)

def test_import_plugin_without_response_raises(tmp_path):
    main = tmp_path / "main.py"
    main.touch()
    token = set_request(_make_request(tmp_path))
    try:
        parent = PluginBuilder(str(main))
        child = PluginBuilder(str(main))
        child.element("p", "content", parent=child.bodyTag)

        with pytest.raises(TypeError, match="NoneType"):
            parent.importPlugin(child)
    finally:
        reset_request(token)

def test_import_plugin_returns_single_value_when_one_arg(tmp_path):
    main = tmp_path / "main.py"
    main.touch()
    token = set_request(_make_request(tmp_path))
    try:
        parent = PluginBuilder(str(main))
        child = PluginBuilder(str(main))
        child.RESPONSE("payload")
        assert parent.importPlugin(child) == "payload"
    finally:
        reset_request(token)


def test_import_plugin_merges_multiple_children(tmp_path):
    main = tmp_path / "main.py"
    main.touch()
    token = set_request(_make_request(tmp_path))
    try:
        parent = PluginBuilder(str(main))
        child = PluginBuilder(str(main))
        child.element("p", "one", parent=child.bodyTag)
        child.element("p", "two", parent=child.bodyTag)
        child.element("p", "three", parent=child.bodyTag)
        child.RESPONSE("x")

        parent.importPlugin(child)

        texts = [getattr(c, "text", "") for c in parent.bodyTag.children]
        assert texts == ["one", "two", "three"]
    finally:
        reset_request(token)


def test_import_plugin_merges_cookies(tmp_path):
    main = tmp_path / "main.py"
    main.touch()
    token = set_request(_make_request(tmp_path))
    try:
        parent = PluginBuilder(str(main))
        parent.set_Cookie("parent_cookie", "1")

        child = PluginBuilder(str(main))
        child.set_Cookie("child_cookie", "2")
        child.set_Cookie("another", "3")
        child.RESPONSE("x")

        parent.importPlugin(child)

        keys = [c["key"] for c in parent._cookies_list]
        assert "parent_cookie" in keys
        assert "child_cookie" in keys
        assert "another" in keys
    finally:
        reset_request(token)


@pytest.mark.asyncio
async def test_import_plugin_with_awaited_plugin(tmp_path):
    main = tmp_path / "main.py"
    main.touch()
    token = set_request(_make_request(tmp_path))
    try:
        parent = PluginBuilder(str(main))

        async def make_plugin():
            p = PluginBuilder(str(main))
            p.element("h1", "from-async", parent=p.bodyTag)
            p.RESPONSE("ok")
            return p

        child = await make_plugin()
        result = parent.importPlugin(child)

        assert result == "ok"
        assert any(
            getattr(c, "text", "") == "from-async" for c in parent.bodyTag.children
        )
    finally:
        reset_request(token)


@pytest.mark.asyncio
async def test_import_plugin_with_db_await_inside(tmp_path):
    main = tmp_path / "main.py"
    main.touch()
    token = set_request(_make_request(tmp_path))
    try:
        parent = PluginBuilder(str(main))

        async def make_plugin():
            p = PluginBuilder(str(main))
            data = await asyncio.sleep(0, result="db-result")
            p.element("p", data, parent=p.bodyTag)
            p.RESPONSE("done")
            return p

        child = await make_plugin()
        result = parent.importPlugin(child)

        assert result == "done"
        assert any(
            getattr(c, "text", "") == "db-result" for c in parent.bodyTag.children
        )
    finally:
        reset_request(token)


@pytest.mark.asyncio
async def test_import_plugin_multiple_async_plugins(tmp_path):
    main = tmp_path / "main.py"
    main.touch()
    token = set_request(_make_request(tmp_path))
    try:
        parent = PluginBuilder(str(main))

        async def make_section(text):
            p = PluginBuilder(str(main))
            p.element("section", text, parent=p.bodyTag)
            p.RESPONSE(text)
            return p

        for i in range(3):
            child = await make_section(f"section-{i}")
            parent.importPlugin(child)

        texts = [getattr(c, "text", "") for c in parent.bodyTag.children]
        assert texts == ["section-0", "section-1", "section-2"]
    finally:
        reset_request(token)


def test_import_plugin_does_not_mutate_source(tmp_path):
    main = tmp_path / "main.py"
    main.touch()
    token = set_request(_make_request(tmp_path))
    try:
        parent = PluginBuilder(str(main))
        child = PluginBuilder(str(main))
        child.element("p", "keep", parent=child.bodyTag)
        child.RESPONSE("x")
        original_count = len(child.bodyTag.children)

        parent.importPlugin(child)

        assert len(child.bodyTag.children) == original_count
    finally:
        reset_request(token)