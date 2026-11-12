# tests/unit/mediator/test_header_builders.py
import pytest
from nexelpy.mediator.headerBuilder.hstsHeaderBuilder import HSTSHeaderBuilder
from nexelpy.mediator.headerBuilder.cspHeaderBuilder import CSPHeaderBuilder
from nexelpy.mediator.headerBuilder.permissionsPolicyHeaderBuilder import PermissionsPolicyHeaderBuilder
from nexelpy.mediator.headerBuilder.clearSiteDataHeaderBuilder import ClearSiteDataHeaderBuilder
from nexelpy.mediator.headerBuilder.cacheControlHeaderBuilder import CacheControlHeaderBuilder
from nexelpy.mediator.headerBuilder.referrerPolicyHeaderBuilder import ReferrerPolicyHeaderBuilder
from nexelpy.mediator.headerBuilder.xFrameOptionsHeaderBuilder import XFrameOptionsHeaderBuilder
from nexelpy.mediator.headerBuilder.xContentTypeOptionsHeaderBuilder import XContentTypeOptionsHeaderBuilder
from nexelpy.mediator.headerBuilder.originAgentClusterHeaderBuilder import OriginAgentClusterHeaderBuilder
from nexelpy.mediator.headerBuilder.crossOriginOpenerPolicyHeaderBuilder import CrossOriginOpenerPolicyHeaderBuilder
from nexelpy.mediator.headerBuilder.crossOriginEmbedderPolicyHeaderBuilder import CrossOriginEmbedderPolicyHeaderBuilder
from nexelpy.mediator.headerBuilder.crossOriginResourcePolicyHeaderBuilder import CrossOriginResourcePolicyHeaderBuilder


# ---------------- HSTS ----------------
@pytest.mark.parametrize(
    "kwargs,expected",
    [
        ({}, "max-age=31536000; includeSubDomains"),
        ({"max_age": 60}, "max-age=60; includeSubDomains"),
        ({"include_subdomains": False}, "max-age=31536000"),
        ({"preload": True}, "max-age=31536000; includeSubDomains; preload"),
        ({"max_age": 0, "include_subdomains": False, "preload": False}, "max-age=0"),
    ],
    ids=["default", "short", "no_subdomains", "preload", "minimal"],
)
def test_hsts(kwargs, expected):
    assert HSTSHeaderBuilder(**kwargs).build_header() == {"Strict-Transport-Security": expected}


# ---------------- X-Frame-Options ----------------
@pytest.mark.parametrize("policy,expected", [
    ("DENY", "DENY"),
    ("deny", "DENY"),
    ("sameorigin", "SAMEORIGIN"),
    ("allow-from https://x.com", "ALLOW-FROM HTTPS://X.COM"),
])
def test_x_frame_options(policy, expected):
    assert XFrameOptionsHeaderBuilder(policy).build_header() == {"X-Frame-Options": expected}


def test_x_frame_options_default():
    assert XFrameOptionsHeaderBuilder().build_header() == {"X-Frame-Options": "DENY"}


# ---------------- X-Content-Type-Options ----------------
def test_x_content_type_options():
    assert XContentTypeOptionsHeaderBuilder().build_header() == {
        "X-Content-Type-Options": "nosniff"
    }


# ---------------- Origin-Agent-Cluster ----------------
def test_origin_agent_cluster():
    assert OriginAgentClusterHeaderBuilder().build_header() == {"Origin-Agent-Cluster": "?1"}


# ---------------- Referrer-Policy ----------------
def test_referrer_policy_default():
    assert ReferrerPolicyHeaderBuilder().build_header() == {
        "Referrer-Policy": "strict-origin-when-cross-origin"
    }


def test_referrer_policy_custom():
    assert ReferrerPolicyHeaderBuilder("no-referrer").build_header() == {
        "Referrer-Policy": "no-referrer"
    }


# ---------------- COOP / COEP / CORP ----------------
@pytest.mark.parametrize("cls,header,default", [
    (CrossOriginOpenerPolicyHeaderBuilder, "Cross-Origin-Opener-Policy", "same-origin"),
    (CrossOriginEmbedderPolicyHeaderBuilder, "Cross-Origin-Embedder-Policy", "require-corp"),
    (CrossOriginResourcePolicyHeaderBuilder, "Cross-Origin-Resource-Policy", "same-origin"),
])
def test_cross_origin_defaults(cls, header, default):
    assert cls().build_header() == {header: default}


@pytest.mark.parametrize("cls,header", [
    (CrossOriginOpenerPolicyHeaderBuilder, "Cross-Origin-Opener-Policy"),
    (CrossOriginEmbedderPolicyHeaderBuilder, "Cross-Origin-Embedder-Policy"),
    (CrossOriginResourcePolicyHeaderBuilder, "Cross-Origin-Resource-Policy"),
])
def test_cross_origin_custom(cls, header):
    assert cls("unsafe-none").build_header() == {header: "unsafe-none"}


# ---------------- Cache-Control ----------------
def test_cache_default():
    h = CacheControlHeaderBuilder()
    v = h.build_header()["Cache-Control"]
    assert v.startswith("no-cache")
    assert "max-age=31536000" in v


def test_cache_no_max_age():
    h = CacheControlHeaderBuilder(max_age=0)
    v = h.build_header()["Cache-Control"]
    assert "max-age" not in v


def test_cache_extra_parts():
    h = CacheControlHeaderBuilder(
        cache_control="public",
        max_age=100,
        s_maxage=200,
        stale_while_revalidate=30,
        stale_if_error=60,
        extra="immutable",
    )
    v = h.build_header()["Cache-Control"]
    for token in ["public", "max-age=100", "s-maxage=200",
                  "stale-while-revalidate=30", "stale-if-error=60", "immutable"]:
        assert token in v


def test_cache_empty_falls_back_to_no_cache():
    h = CacheControlHeaderBuilder(cache_control="", max_age=0)
    assert h.build_header()["Cache-Control"] == "no-cache"


# ---------------- Clear-Site-Data ----------------
def test_clear_site_data_wildcard():
    assert ClearSiteDataHeaderBuilder("*").build_header() == {
        "Clear-Site-Data": '"*"'
    }


def test_clear_site_data_types():
    h = ClearSiteDataHeaderBuilder("cache", "cookies")
    assert h.build_header() == {"Clear-Site-Data": '"cache", "cookies"'}


def test_clear_site_data_empty():
    assert ClearSiteDataHeaderBuilder().build_header() == {}


# ---------------- Permissions-Policy ----------------
def test_permissions_policy_empty():
    assert PermissionsPolicyHeaderBuilder().build_header() == {}


def test_permissions_policy_empty_allowlist():
    pp = PermissionsPolicyHeaderBuilder().add("camera")
    assert pp.build_header() == {"Permissions-Policy": "camera=()"}


def test_permissions_policy_star():
    pp = PermissionsPolicyHeaderBuilder().add("geolocation", "*")
    assert pp.build_header() == {"Permissions-Policy": "geolocation=*"}


def test_permissions_policy_list():
    pp = PermissionsPolicyHeaderBuilder().add("geolocation", ["self", "https://x.com"])
    assert pp.build_header() == {
        "Permissions-Policy": "geolocation=(self https://x.com)"
    }


def test_permissions_policy_scalar_becomes_list():
    pp = PermissionsPolicyHeaderBuilder().add("geolocation", "self")
    assert pp.build_header() == {"Permissions-Policy": "geolocation=(self)"}


def test_permissions_policy_multiple_features_joined():
    pp = (PermissionsPolicyHeaderBuilder()
          .add("camera")
          .add("geolocation", "*")
          .add("usb", ["self"]))
    v = pp.build_header()["Permissions-Policy"]
    assert "camera=()" in v
    assert "geolocation=*" in v
    assert "usb=(self)" in v
    assert v.count(",") == 2


# ---------------- CSP ----------------
def test_csp_empty():
    assert CSPHeaderBuilder().build_header() == {}


def test_csp_simple():
    b = CSPHeaderBuilder().add("default-src", "'self'")
    assert b.build_header() == {"Content-Security-Policy": "default-src 'self'"}


def test_csp_origin_extraction():
    b = CSPHeaderBuilder().add("script-src", "https://cdn.example.com/path?x=1")
    v = b.build_header()["Content-Security-Policy"]
    assert "https://cdn.example.com" in v
    assert "/path" not in v


def test_csp_quoted_preserved():
    b = CSPHeaderBuilder().add("script-src", "'unsafe-inline'")
    assert "script-src 'unsafe-inline'" in b.build_header()["Content-Security-Policy"]


def test_csp_multiple_directives():
    b = (CSPHeaderBuilder()
         .add("default-src", "'self'")
         .add("img-src", "'self'", "data:")
         .add("script-src", "'self'", "https://cdn.x.com"))
    v = b.build_header()["Content-Security-Policy"]
    for part in ["default-src 'self'", "img-src 'self' data:", "script-src 'self' https://cdn.x.com"]:
        assert part in v
    assert v.count(";") == 2


def test_csp_add_appends_to_existing_directive():
    b = (CSPHeaderBuilder()
         .add("script-src", "'self'")
         .add("script-src", "'unsafe-inline'"))
    v = b.build_header()["Content-Security-Policy"]
    assert v == "script-src 'self' 'unsafe-inline'"


def test_csp_no_origin_mode_keeps_raw():
    b = CSPHeaderBuilder().add("script-src", "https://cdn.x.com/foo.js", origin=False)
    v = b.build_header()["Content-Security-Policy"]
    assert "https://cdn.x.com/foo.js" in v


def test_csp_directive_with_empty_sources_skipped():
    b = CSPHeaderBuilder()
    b.directives["foo"] = []
    assert b.build_header() == {}