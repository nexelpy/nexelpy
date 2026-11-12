import pytest
from nexelpy import Nextyle


@pytest.fixture
def nextyle(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    (tmp_path / ".nexelpy").touch()
    f = tmp_path / "style.py"
    f.touch()
    return f


def test_keyframe_dynamic_property_via_getattr(nextyle, tmp_path):
    with Nextyle(nextyle) as y:
        with y.keyframes("k"):
            y.step("0%").custom_property("value")
    css = (tmp_path / "style.css").read_text()
    assert "custom-property: value;" in css


def test_keyframe_step_supports_chain(nextyle):
    with Nextyle(nextyle) as y:
        with y.keyframes("k"):
            step = y.step("0%")
            result = step.opacity("0").transform("scale(1)")
            assert result is step