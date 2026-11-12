# tests/unit/view/test_page_builder.py
import pytest
from unittest.mock import MagicMock
from pathlib import Path
from nexelpy.view.pageBuilder import PageBilder
from nexelpy.mediator.request_proxy.request_object import set_request, reset_request
from starlette.requests import Request


@pytest.fixture
def fake_request():
    scope = {
        "type": "http", "method": "GET", "path": "/",
        "headers": [], "query_string": b"",
        "app": MagicMock(root_Path=str(Path(__file__).resolve().parent)),
    }
    req = Request(scope)
    token = set_request(req)
    yield req
    reset_request(token)


def test_page_response_status_and_media_type(fake_request):
    x = PageBilder(__file__)
    x.h1("hello")
    r = x.RESPONSE()
    assert r.status_code == 200
    assert r.media_type == "text/html"
    assert b"<h1>hello</h1>" in r.body


def test_page_title(fake_request):
    x = PageBilder(__file__, title="Hi")
    assert b"<title>Hi</title>" in x.RESPONSE().body


def test_page_viewport_meta(fake_request):
    x = PageBilder(__file__)
    assert b"name='viewport'" in x.RESPONSE().body


def test_page_cookies_attached(fake_request):
    x = PageBilder(__file__)
    x.set_Cookie("session", "abc")
    r = x.RESPONSE()
    assert "session=abc" in r.headers["set-cookie"]