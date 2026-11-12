import pytest
from nexelpy import Nextyle


@pytest.fixture
def nextyle(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    (tmp_path / ".nexelpy").touch()
    f = tmp_path / "style.py"
    f.touch()
    return f


def test_keyframe_media_queries(nextyle, tmp_path):
    with Nextyle(nextyle) as y:
        with y.keyframes("fade-in"):
            y.step("0%").opacity("0", sm="0.5")
            y.step("100%").opacity("1", sm="1")
    css = (tmp_path / "style.css").read_text()
    assert "@keyframes fade-in--" in css
    assert "0% {" in css
    assert "opacity: 0;" in css
    assert "@media (min-width: 640px)" in css
    assert "opacity: 0.5;" in css


def test_keyframe_unscoped_name(nextyle, tmp_path):
    with Nextyle(nextyle) as y:
        with y.keyframes("spin", scope=False):
            y.step("0%").rotate("0deg")
            y.step("100%").rotate("360deg")
    css = (tmp_path / "style.css").read_text()
    assert "@keyframes spin {" in css


def test_keyframe_step_returns_step(nextyle):
    y = Nextyle(nextyle)
    with y.keyframes("k"):
        step = y.step("50%")
        assert step is not None
        step.opacity("0.5").transform("scale(1)")


def test_keyframe_multiple_properties(nextyle, tmp_path):
    with Nextyle(nextyle) as y:
        with y.keyframes("pulse"):
            y.step("0%").opacity("1").scale("1")
            y.step("50%").opacity("0.5").scale("1.1")
            y.step("100%").opacity("1").scale("1")
    css = (tmp_path / "style.css").read_text()
    assert css.count("opacity:") == 3
    assert css.count("scale:") == 3


def test_keyframe_merge_overrides(nextyle, tmp_path):
    with Nextyle(nextyle) as y:
        with y.keyframes("k"):
            y.step("0%").opacity("0").opacity("1")
    css = (tmp_path / "style.css").read_text()
    step_block = css.split("0% {")[1].split("}")[0]
    assert "opacity: 1;" in step_block