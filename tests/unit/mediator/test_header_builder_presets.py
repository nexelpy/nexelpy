import pytest
from nexelpy.mediator.headerBuilder.headerBuilder import HeaderBuilder


def _hdrs(preset_name):
    hb = HeaderBuilder()
    getattr(hb, preset_name)()
    return hb.build_header()


@pytest.mark.parametrize("preset,checks", [
    ("set_strict", {
        "X-Frame-Options": "SAMEORIGIN",
        "X-Content-Type-Options": "nosniff",
        "Referrer-Policy": "strict-origin-when-cross-origin",
        "Cross-Origin-Opener-Policy": "same-origin",
        "Cross-Origin-Embedder-Policy": "require-corp",
        "Cross-Origin-Resource-Policy": "same-origin",
    }),
    ("set_super_strict", {
        "X-Frame-Options": "DENY",
        "Referrer-Policy": "no-referrer",
        "Cache-Control": "no-store, max-age=0",
        "Cross-Origin-Opener-Policy": "same-origin",
        "Cross-Origin-Embedder-Policy": "require-corp",
        "Cross-Origin-Resource-Policy": "same-origin",
    }),
    ("set_normal", {
        "X-Frame-Options": "SAMEORIGIN",
        "Cross-Origin-Opener-Policy": "same-origin-allow-popups",
        "Cross-Origin-Resource-Policy": "cross-origin",
    }),
    ("set_relaxed", {
        "Referrer-Policy": "unsafe-url",
        "Cross-Origin-Embedder-Policy": "unsafe-none",
        "Origin-Agent-Cluster": "?0",
        "Cross-Origin-Resource-Policy": "cross-origin",
    }),
])
def test_preset_has_expected_keys(preset, checks):
    h = _hdrs(preset)
    for k, v in checks.items():
        assert h[k] == v


def test_add_raw_header_translates_double_underscore():
    hb = HeaderBuilder()
    hb.add_raw_header(X__Custom__Thing="value")
    assert hb.build_header()["X-Custom-Thing"] == "value"


def test_raw_header_overrides_builder_value():
    hb = HeaderBuilder()
    hb.frame_options("DENY")            # builder
    hb.add_raw_header(X__Frame__Options="SAMEORIGIN")  # raw wins
    assert hb.build_header()["X-Frame-Options"] == "SAMEORIGIN"


def test_multiple_builders_merge():
    hb = HeaderBuilder()
    hb.frame_options("DENY")
    hb.content_type_options()
    hb.referrer_Policy("no-referrer")
    headers = hb.build_header()
    assert headers["X-Frame-Options"] == "DENY"
    assert headers["X-Content-Type-Options"] == "nosniff"
    assert headers["Referrer-Policy"] == "no-referrer"


def test_build_is_idempotent():
    hb = HeaderBuilder()
    hb.set_normal()
    a = hb.build_header()
    b = hb.build_header()
    assert a == b


def test_csp_builder_accessible():
    hb = HeaderBuilder()
    hb.csp.add("default-src", "'self'")
    h = hb.build_header()
    assert "Content-Security-Policy" in h


def test_permissions_policy_accessible():
    hb = HeaderBuilder()
    hb.permissions_Policy.add("camera")
    h = hb.build_header()
    assert "Permissions-Policy" in h