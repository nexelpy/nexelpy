# tests/unit/mediator/test_cookies_manager.py
import pytest
from unittest.mock import MagicMock
from nexelpy import CookiesManager
from nexelpy.mediator.request_proxy.request_object import set_request, reset_request
from starlette.requests import Request


def test_set_cookie():
    cm = CookiesManager()
    cm.set_Cookie("theme", "dark", max_age=3600)
    assert len(cm._cookies_list) == 1
    c = cm._cookies_list[0]
    assert c["key"] == "theme"
    assert c["value"] == "dark"
    assert c["max_age"] == 3600


def test_set_cookie_empty_key_raises():
    cm = CookiesManager()
    with pytest.raises(ValueError, match="cookie key is required"):
        cm.set_Cookie("", "x")


def test_delete_cookie_explicit_keys():
    cm = CookiesManager()
    cm.delete_Cookie("a", "b")
    assert len(cm._cookies_list) == 2
    for c in cm._cookies_list:
        assert c["max_age"] == 0
        assert c["value"] == ""


def test_delete_cookie_from_request_context():
    scope = {"type": "http", "method": "GET", "path": "/",
             "headers": [(b"cookie", b"a=1; b=2")], "query_string": b"", "app": None}
    req = Request(scope)
    token = set_request(req)
    try:
        cm = CookiesManager()
        cm.delete_Cookie()
        keys = sorted(c["key"] for c in cm._cookies_list)
        assert keys == ["a", "b"]
    finally:
        reset_request(token)


def test_delete_cookie_outside_context_silently_noop():
    cm = CookiesManager()
    cm.delete_Cookie()
    assert cm._cookies_list == []


def test_set_cookies_from_list_writes_response_and_clears():
    cm = CookiesManager()
    cm.set_Cookie("k", "v")
    resp = MagicMock()
    cm._setCookiesFromList(resp)
    resp.set_cookie.assert_called_once()
    assert cm._cookies_list == []


def test_set_cookies_skips_none_values():
    cm = CookiesManager()
    cm.set_Cookie("k", "v", max_age=None) 
    resp = MagicMock()
    cm._setCookiesFromList(resp)
    kwargs = resp.set_cookie.call_args.kwargs
    assert "max_age" not in kwargs