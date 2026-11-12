import pytest
from nexelpy import Nextyle


@pytest.fixture
def nextyle(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    (tmp_path / ".nexelpy").touch()
    f = tmp_path / "style.py"
    f.touch()
    return f


def test_pseudo_class_hover(nextyle, tmp_path):
    with Nextyle(nextyle) as y:
        y.select(".btn").color("red").hover().color("blue")
    css = (tmp_path / "style.css").read_text()
    assert ".btn {" in css
    assert ".btn:hover {" in css


def test_pseudo_chain_focus_active(nextyle, tmp_path):
    with Nextyle(nextyle) as y:
        y.select("input").focus().outline("2px").active().outline("none")
    css = (tmp_path / "style.css").read_text()
    assert "input:focus {" in css
    assert "input:focus:active {" in css


def test_pseudo_element_before(nextyle, tmp_path):
    with Nextyle(nextyle) as y:
        y.select(".x").pseudo("::before").content('""')
    css = (tmp_path / "style.css").read_text()
    assert ".x::before {" in css


def test_pseudo_with_string_input(nextyle, tmp_path):
    with Nextyle(nextyle) as y:
        y.select(".x").pseudo("hover").color("red")
    css = (tmp_path / "style.css").read_text()
    assert ".x:hover {" in css


def test_pseudo_with_colon_input(nextyle, tmp_path):
    with Nextyle(nextyle) as y:
        y.select(".x").pseudo(":focus").color("blue")
    css = (tmp_path / "style.css").read_text()
    assert ".x:focus {" in css


def test_render_group_returns_none_when_no_rules(nextyle):
    from nexelpy.criptyle.nextyle.select import Select
    s = Select(".x", Nextyle(nextyle))
    assert s.render_group("base") is None


def test_dynamic_css_property_via_getattr(nextyle, tmp_path):
    with Nextyle(nextyle) as y:
        y.select(".x").made_up_property("value")
    css = (tmp_path / "style.css").read_text()
    assert "made-up-property: value;" in css


def test_scope_selector_with_ampersand(nextyle, tmp_path):
    with Nextyle(nextyle) as y:
        with y.scoping(".scope"):
            y.select("&.active").color("red")
    css = (tmp_path / "style.css").read_text()
    assert ".scope.active {" in css


def test_multiple_media_kwargs(nextyle, tmp_path):
    with Nextyle(nextyle) as y:
        y.select(".x").color("red", sm="blue", md="green", lg="black")
    css = (tmp_path / "style.css").read_text()
    assert "color: red;" in css
    assert "@media (min-width: 640px)" in css
    assert "color: blue;" in css
    assert "@media (min-width: 768px)" in css
    assert "color: green;" in css
    assert "@media (min-width: 1024px)" in css
    assert "color: black;" in css