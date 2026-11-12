import pytest
from nexelpy.mediator.headerBuilder.headerBuilder import HeaderBuilder


def test_hsts_method_returns_builder_and_registers():
    hb = HeaderBuilder()
    builder = hb.hsts(max_age=60, include_subdomains=False)
    headers = hb.build_header()
    assert "Strict-Transport-Security" in headers
    assert headers["Strict-Transport-Security"] == "max-age=60"
    assert builder is not None


def test_cache_method_registers():
    hb = HeaderBuilder()
    hb.cache(cache_control="public", max_age=100)
    h = hb.build_header()
    assert "Cache-Control" in h
    assert "public" in h["Cache-Control"]
    assert "max-age=100" in h["Cache-Control"]


def test_frame_options_method_registers():
    hb = HeaderBuilder()
    hb.frame_options("SAMEORIGIN")
    assert hb.build_header()["X-Frame-Options"] == "SAMEORIGIN"


def test_content_type_options_method_registers():
    hb = HeaderBuilder()
    hb.content_type_options()
    assert hb.build_header()["X-Content-Type-Options"] == "nosniff"


def test_referrer_policy_method_registers():
    hb = HeaderBuilder()
    hb.referrer_Policy("no-referrer")
    assert hb.build_header()["Referrer-Policy"] == "no-referrer"


def test_cross_origin_methods_register():
    hb = HeaderBuilder()
    hb.cross_origin_opener("same-origin")
    hb.cross_origin_embedder("require-corp")
    hb.cross_origin_resource("same-origin")
    h = hb.build_header()
    assert h["Cross-Origin-Opener-Policy"] == "same-origin"
    assert h["Cross-Origin-Embedder-Policy"] == "require-corp"
    assert h["Cross-Origin-Resource-Policy"] == "same-origin"


def test_origin_agent_cluster_method_registers():
    hb = HeaderBuilder()
    hb.origin_agent_cluster()
    assert hb.build_header()["Origin-Agent-Cluster"] == "?1"


def test_clear_site_data_method_registers():
    hb = HeaderBuilder()
    hb.clear_site_data("cache", "cookies")
    h = hb.build_header()
    assert "Clear-Site-Data" in h
    assert '"cache"' in h["Clear-Site-Data"]


def test_clear_site_data_wildcard_method():
    hb = HeaderBuilder()
    hb.clear_site_data("*")
    assert hb.build_header()["Clear-Site-Data"] == '"*"'


def test_all_builders_combine():
    hb = HeaderBuilder()
    hb.hsts()
    hb.cache()
    hb.frame_options()
    hb.content_type_options()
    hb.referrer_Policy()
    hb.cross_origin_opener()
    hb.cross_origin_embedder()
    hb.cross_origin_resource()
    hb.origin_agent_cluster()
    hb.clear_site_data("cache")
    h = hb.build_header()
    for key in [
        "Strict-Transport-Security",
        "Cache-Control",
        "X-Frame-Options",
        "X-Content-Type-Options",
        "Referrer-Policy",
        "Cross-Origin-Opener-Policy",
        "Cross-Origin-Embedder-Policy",
        "Cross-Origin-Resource-Policy",
        "Origin-Agent-Cluster",
        "Clear-Site-Data",
    ]:
        assert key in h


def test_csp_and_permissions_policy_objects_present():
    hb = HeaderBuilder()
    assert hasattr(hb, "csp")
    assert hasattr(hb, "permissions_Policy")


def test_raw_header_overrides_specific_builder():
    hb = HeaderBuilder()
    hb.frame_options("SAMEORIGIN")
    hb.add_raw_header(X__Frame__Options="DENY")
    assert hb.build_header()["X-Frame-Options"] == "DENY"


def test_raw_header_overrides_super_strict_csp():
    hb = HeaderBuilder()
    hb.set_super_strict()
    hb.add_raw_header(Content__Security__Policy="default-src 'none'")
    assert hb.build_header()["Content-Security-Policy"] == "default-src 'none'"