import pytest
from nexelpy.criptyle.nextyle.renderer import CSSRenderer


def test_indent_css_static():
    assert CSSRenderer.indent_css("a\nb", level=2) == "        a\n        b"


def test_render_declarations_static():
    out = CSSRenderer.render_declarations({"color": "red", "margin": "0"})
    assert "    color: red;" in out
    assert "    margin: 0;" in out


def test_merge_keyframe_rules_merges_steps():
    current = {"0%": {"opacity": "0"}, "100%": {"opacity": "1"}}
    overrides = {"0%": {"transform": "none"}}
    merged = CSSRenderer.merge_keyframe_rules(current, overrides)
    assert merged["0%"]["opacity"] == "0"
    assert merged["0%"]["transform"] == "none"
    assert merged["100%"]["opacity"] == "1"


def test_merge_keyframe_rules_adds_new_step():
    current = {"0%": {"opacity": "0"}}
    overrides = {"50%": {"opacity": "0.5"}}
    merged = CSSRenderer.merge_keyframe_rules(current, overrides)
    assert "50%" in merged
    assert merged["50%"]["opacity"] == "0.5"