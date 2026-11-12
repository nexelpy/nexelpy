import pytest
from pathlib import Path
from nexelpy import Nextyle


@pytest.fixture
def nextyle(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    (tmp_path / ".nexelpy").touch()
    f = tmp_path / "style.py"
    f.touch()
    return f


def _css(tmp_path):
    return (tmp_path / "style.css").read_text()


def test_layer_context(nextyle, tmp_path):
    with Nextyle(nextyle) as y:
        with y.layer("base"):
            y.select("body").color("red")
    css = _css(tmp_path)
    assert "@layer base {" in css
    assert "color: red;" in css


def test_supports_context(nextyle, tmp_path):
    with Nextyle(nextyle) as y:
        with y.supports("(display: grid)"):
            y.select(".grid").display("grid")
    css = _css(tmp_path)
    assert "@supports (display: grid)" in css
    assert "display: grid;" in css


def test_container_context_with_name(nextyle, tmp_path):
    with Nextyle(nextyle) as y:
        with y.container("(min-width: 400px)", name="card"):
            y.select(".x").padding("10px")
    css = _css(tmp_path)
    assert "@container card (min-width: 400px)" in css


def test_container_context_without_name(nextyle, tmp_path):
    with Nextyle(nextyle) as y:
        with y.container("(min-width: 400px)"):
            y.select(".x").padding("10px")
    css = _css(tmp_path)
    assert "@container (min-width: 400px)" in css


def test_scope_context(nextyle, tmp_path):
    with Nextyle(nextyle) as y:
        with y.scope(".card", to=".card-content"):
            y.select("p").color("gray")
    css = _css(tmp_path)
    assert "@scope (.card) to (.card-content)" in css


def test_scope_context_without_to(nextyle, tmp_path):
    with Nextyle(nextyle) as y:
        with y.scope(".card"):
            y.select("p").color("gray")
    css = _css(tmp_path)
    assert "@scope (.card)" in css


def test_property_context(nextyle, tmp_path):
    with Nextyle(nextyle) as y:
        with y.property("--my-color"):
            y.syntax("<color>")
            y.inherits(False)
            y.initial_value("red")
    css = _css(tmp_path)
    assert "@property --my-color" in css
    assert 'syntax: "<color>";' in css
    assert "inherits: false;" in css
    assert "initial-value: red;" in css


def test_vars_context(nextyle, tmp_path):
    with Nextyle(nextyle) as y:
        with y.vars(":root"):
            y.add_var(primary="#f00", secondary="#0f0")
    css = _css(tmp_path)
    assert ":root {" in css
    assert "--primary: #f00;" in css
    assert "--secondary: #0f0;" in css


def test_vars_add_var_with_dashes(nextyle, tmp_path):
    with Nextyle(nextyle) as y:
        with y.vars(":root"):
            y.add_var(**{"--already": "1"})
    assert "--already: 1;" in _css(tmp_path)


def test_page_context_with_selector(nextyle, tmp_path):
    with Nextyle(nextyle) as y:
        with y.page(":first"):
            y.margin("1cm")
            y.size("A4")
    css = _css(tmp_path)
    assert "@page :first" in css
    assert "margin: 1cm;" in css
    assert "size: A4;" in css


def test_page_context_without_selector(nextyle, tmp_path):
    with Nextyle(nextyle) as y:
        with y.page():
            y.margin("1cm")
    assert "@page {" in _css(tmp_path)


def test_starting_style_context(nextyle, tmp_path):
    with Nextyle(nextyle) as y:
        with y.starting_style():
            y.select(".fade").opacity("0")
        y.select(".fade").transition("opacity 0.3s").opacity("1")
    css = _css(tmp_path)
    assert "@starting-style {" in css
    assert "opacity: 0;" in css
    assert "transition: opacity 0.3s;" in css
    assert "opacity: 1;" in css


def test_import_css(nextyle, tmp_path):
    with Nextyle(nextyle) as y:
        y.import_css("/static/base.css")
    assert "@import /static/base.css;" in _css(tmp_path)


def test_media_context_standalone(nextyle, tmp_path):
    with Nextyle(nextyle) as y:
        with y.media("(min-width: 1024px)"):
            y.select(".hero").font_size("3rem")
    css = _css(tmp_path)
    assert "@media (min-width: 1024px)" in css
    assert "font-size: 3rem;" in css


def test_attr_stores_tag_attributes(nextyle):
    with Nextyle(nextyle) as y:
        y.attr(data_theme="dark")
    assert y._tag_attrs == {"data_theme": "dark"}


def test_raw_css(nextyle, tmp_path):
    with Nextyle(nextyle) as y:
        y.raw_css("body { color: red; }")
    assert "body { color: red; }" in _css(tmp_path)


def test_raw_css_media_kwargs(nextyle, tmp_path):
    with Nextyle(nextyle) as y:
        y.raw_css(sm=".x { color: blue; }")
    css = _css(tmp_path)
    assert "@media (min-width: 640px)" in css
    assert ".x { color: blue; }" in css


def test_raw_css_resolves_urls(nextyle, tmp_path):
    with Nextyle(nextyle) as y:
        y.raw_css('body { background: url("./bg.png"); }')
    css = _css(tmp_path)
    assert 'url("/bg.png")' in css


def test_raw_css_keeps_absolute_urls(nextyle, tmp_path):
    with Nextyle(nextyle) as y:
        y.raw_css('body { background: url("https://x.com/a.png"); }')
    assert "https://x.com/a.png" in _css(tmp_path)


def test_add_global_raw_css(nextyle, tmp_path):
    with Nextyle(nextyle) as y:
        y.add_global_raw_css("* { box-sizing: border-box; }")
    css = _css(tmp_path)
    assert "* { box-sizing: border-box; }" in css


def test_layer_order_presets(nextyle, tmp_path):
    with Nextyle(nextyle, layer_order=("reset", "base", "components")) as y:
        y.select("body").margin("0")
    css = _css(tmp_path)
    assert "@layer reset, base, components;" in css


def test_custom_media_query(nextyle, tmp_path):
    with Nextyle(nextyle, xxl="@media (min-width: 1920px)") as y:
        y.select(".x").color("red", xxl="blue")
    css = _css(tmp_path)
    assert "@media (min-width: 1920px)" in css
    assert "color: blue;" in css


def test_src_for_font_face(nextyle, tmp_path):
    with Nextyle(nextyle) as y:
        with y.font_face("MyFont"):
            y.src(y.url("./f.woff2", format="woff2"))
            y.font_weight("400")
    css = _css(tmp_path)
    assert "@font-face {" in css
    assert 'font-family: "MyFont";' in css
    assert 'src: url("/f.woff2") format("woff2");' in css
    assert "font-weight: 400;" in css


def test_scoping_with_explicit_selector(nextyle, tmp_path):
    with Nextyle(nextyle) as y:
        with y.scoping(".custom-scope"):
            y.select("p").color("red")
    css = _css(tmp_path)
    assert ".custom-scope p" in css
    assert "color: red;" in css


def test_scoping_ampersand_selector(nextyle, tmp_path):
    with Nextyle(nextyle) as y:
        with y.scoping(".root"):
            y.select("&").color("red")
    css = _css(tmp_path)
    assert ".root {" in css


def test_scoping_nested(nextyle, tmp_path):
    with Nextyle(nextyle) as y:
        with y.scoping(".a"):
            with y.scoping(".b"):
                y.select("p").color("red")
    css = _css(tmp_path)
    assert ".a .b p" in css


def test_generate_css_without_export(nextyle):
    y = Nextyle(nextyle)
    y.select("body").color("red")
    css = y.generate_css()
    assert "body {" in css
    assert "color: red;" in css
    assert not (nextyle.with_suffix(".css")).exists()