import pytest
from nexelpy.mediator.registerations.url_checker import UrlChecker


@pytest.mark.parametrize("route,prefix,expected", [
    (None, None, ""),
    ("", "", ""),
    ("/x", "", "/x"),
    ("", "/api", "/api"),
    ("/x", "/api", "/api/x"),
    ("/", "/api", "/api/"),
], ids=[
    "both_none", "both_empty", "route_only", "prefix_only",
    "both_present", "root_route",
])
def test_valid_combinations(route, prefix, expected):
    ok, result = UrlChecker.check(route, prefix)
    assert ok is True
    assert result == expected

def test_root_prefix_rejected():
    ok, msg = UrlChecker.check("", "/")
    assert ok is False
    assert "must not end with '/'" in msg
    
def test_route_non_string_fails():
    ok, msg = UrlChecker.check(123, "")
    assert ok is False
    assert "route must be a string" in msg


def test_prefix_non_string_fails():
    ok, msg = UrlChecker.check("/x", 123)
    assert ok is False
    assert "prefix must be a string" in msg


def test_prefix_missing_leading_slash():
    ok, msg = UrlChecker.check("/x", "api")
    assert ok is False
    assert "prefix must start with '/'" in msg


def test_route_with_query_is_not_rejected():
    ok, result = UrlChecker.check("/x?y=1", "")
    assert ok is True
    assert result == "/x?y=1"


def test_double_slash_detected_in_combined():
    ok, msg = UrlChecker.check("//x", "/api")
    assert ok is False
    assert "double slash" in msg