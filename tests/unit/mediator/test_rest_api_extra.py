import pytest
from unittest.mock import MagicMock, patch
from pathlib import Path
from nexelpy.view.restApi import RestApi
from nexelpy.mediator.request_proxy.request_object import set_request, reset_request
from starlette.requests import Request


def _make_request(root, path="/"):
    scope = {
        "type": "http",
        "method": "GET",
        "path": path,
        "headers": [],
        "query_string": b"",
        "app": MagicMock(root_Path=str(root)),
    }
    return Request(scope)


@pytest.fixture
def api(tmp_path):
    main = tmp_path / "main.py"
    main.touch()
    token = set_request(_make_request(tmp_path))
    try:
        yield RestApi(str(main))
    finally:
        reset_request(token)


def test_response_file_with_custom_media_type(api, tmp_path):
    (tmp_path / "x.bin").write_bytes(b"\x00\x01")
    r = api.RESPONSE_file("x.bin", media_type="application/octet-stream")
    assert r.status_code == 200
    assert r.media_type == "application/octet-stream"


def test_response_file_with_download_name(api, tmp_path):
    (tmp_path / "x.txt").write_text("data")
    r = api.RESPONSE_file("x.txt", download_name="renamed.txt", disposition="attachment")
    assert r.status_code == 200
    assert "attachment" in r.headers.get("content-disposition", "")


def test_response_file_inline_disposition(api, tmp_path):
    (tmp_path / "x.txt").write_text("data")
    r = api.RESPONSE_file("x.txt", download_name="x.txt", disposition="inline")
    assert "inline" in r.headers.get("content-disposition", "")

def test_response_file_disposition_without_filename_has_no_header(api, tmp_path):
    (tmp_path / "x.txt").write_text("data")
    r = api.RESPONSE_file("x.txt", disposition="inline")
    assert "content-disposition" not in r.headers

def test_response_file_with_background_task(api, tmp_path):
    (tmp_path / "x.txt").write_text("data")
    called = {"n": 0}

    def task():
        called["n"] += 1

    r = api.RESPONSE_file("x.txt", background_task=task)
    assert r.status_code == 200
    assert r.background is not None


def test_response_html_returns_file(api, tmp_path):
    (tmp_path / "page.html").write_text("<html><body>hi</body></html>")
    r = api.RESPONSE_html("page.html")
    assert r.status_code == 200
    assert r.media_type == "text/html"


def test_response_html_missing(api):
    r = api.RESPONSE_html("missing.html")
    assert r.status_code == 404


def test_response_html_with_custom_status(api, tmp_path):
    (tmp_path / "p.html").write_text("<h1>ok</h1>")
    r = api.RESPONSE_html("p.html", status_code=201)
    assert r.status_code == 201


def test_response_html_jinja_renders(api, tmp_path):
    (tmp_path / "tmpl.html").write_text("<h1>{{ name }}</h1>")
    r = api.RESPONSE_html_jinja("tmpl.html", name="ali")
    assert r.status_code == 200
    assert b"ali" in r.body


def test_response_html_jinja_missing(api):
    r = api.RESPONSE_html_jinja("missing.html")
    assert r.status_code == 404


def test_response_json_with_status_and_data(api):
    r = api.RESPONSE_json(status_code=202, result="ok", n=5)
    assert r.status_code == 202
    assert b'"result":"ok"' in r.body
    assert b'"n":5' in r.body


def test_response_streaming_media_type(api):
    async def gen():
        yield b"a"

    r = api.RESPONSE_streaming(gen(), media_type="text/event-stream")
    assert r.media_type == "text/event-stream"


def test_response_streaming_with_background(api):
    async def gen():
        yield b"a"

    def bg():
        pass

    r = api.RESPONSE_streaming(gen(), background_task=bg)
    assert r.background is not None


def test_response_redirect_status_301(api):
    r = api.RESPONSE_redirect("/moved", status_code=301)
    assert r.status_code == 301


def test_response_redirect_status_302(api):
    r = api.RESPONSE_redirect("/tmp", status_code=302)
    assert r.status_code == 302


def test_response_cookie_via_set_cookie(api):
    api.set_Cookie("sid", "xyz", httponly=True)
    r = api.RESPONSE_json(ok=True)
    assert "sid=xyz" in r.headers["set-cookie"]
    assert "httponly" in r.headers["set-cookie"].lower()


def test_response_headers_persist_across_calls(api):
    api.Headers.add_raw_header(X__Trace="1")
    r1 = api.RESPONSE_json(a=1)
    r2 = api.RESPONSE_text("hi")
    assert r1.headers["x-trace"] == "1"
    assert r2.headers["x-trace"] == "1"