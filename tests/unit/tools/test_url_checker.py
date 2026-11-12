import pytest
from nexelpy.mediator.registerations.url_checker import UrlChecker

def test_url_valid():
    ok, path = UrlChecker.check("/users", "")
    assert ok is True
    assert path == "/users"

def test_url_valid_with_prefix():
    ok, path = UrlChecker.check("/profile", "/api")
    assert ok is True
    assert path == "/api/profile"

def test_url_missing_leading_slash():
    ok, msg = UrlChecker.check("users", "")
    assert ok is False
    assert "must start with '/'" in msg

def test_url_prefix_ends_with_slash():
    ok, msg = UrlChecker.check("/profile", "/api/")
    assert ok is False
    assert "must not end with '/'" in msg

def test_url_double_slash():
    ok, msg = UrlChecker.check("//users", "")
    assert ok is False
    assert "double slash" in msg