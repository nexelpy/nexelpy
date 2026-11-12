# tests/unit/criptyle/test_helpers.py
import pytest
from nexelpy.criptyle.nextyle.helpers import python_to_css_name, css_value, indent_css


@pytest.mark.parametrize("inp,out", [
    ("background_color", "background-color"),
    ("color", "color"),
    ("_", "-"),
    ("a_b_c", "a-b-c"),
])
def test_python_to_css_name(inp, out):
    assert python_to_css_name(inp) == out


@pytest.mark.parametrize("inp,out", [
    (True, "true"),
    (False, "false"),
    (1, "1"),
    (1.5, "1.5"),
    ("x", "x"),
])
def test_css_value(inp, out):
    assert css_value(inp) == out


def test_indent_css_one_level():
    assert indent_css("a\nb") == "    a\n    b"


def test_indent_css_skips_empty_lines():
    assert indent_css("a\n\nb") == "    a\n\n    b"


def test_indent_css_two_levels():
    assert indent_css("x", level=2) == "        x"