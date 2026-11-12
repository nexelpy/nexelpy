import pytest
from pathlib import Path
from nexelpy import Nexcript


@pytest.fixture
def project(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    (tmp_path / ".nexelpy").touch()
    f = tmp_path / "script.py"
    f.touch()
    return f


def test_default_export_path(project):
    n = Nexcript(project)
    assert n._export_file == project.with_suffix(".js")


def test_custom_export_path(project, tmp_path):
    n = Nexcript(project, export_path="out/custom.js")
    assert n._export_file == tmp_path / "out" / "custom.js"


def test_src_relative_to_project_root(project):
    n = Nexcript(project)
    assert n.src.startswith("/")
    assert n.src.endswith("script.js")


def test_add_script_returns_self(project):
    n = Nexcript(project)
    assert n.add_script("console.log(1)") is n


def test_add_script_js_auto(project, tmp_path):
    with Nexcript(project) as n:
        n.add_script("const x = 1;")
    content = (tmp_path / "script.js").read_text()
    assert "const x = 1;" in content


def test_add_script_ts_explicit(project, tmp_path, monkeypatch):
    from nexelpy.criptyle.nexcript.nexcriptBuilder import Nexcript as N
    monkeypatch.setattr(
        N,
        "_transpile_ts",
        lambda self, code: f"/*compiled*/ {code}",
    )
    with Nexcript(project) as n:
        n.add_script("let x: number = 1;", lang="ts")
    content = (tmp_path / "script.js").read_text()
    assert "/*compiled*/" in content


def test_no_export_on_exception(project, tmp_path):
    try:
        with Nexcript(project):
            raise RuntimeError("abort")
    except RuntimeError:
        pass
    assert not (tmp_path / "script.js").exists()


def test_transpile_ts_no_node_raises(project, monkeypatch):
    from nexelpy.criptyle.nexcript.runtime_info import RuntimeInfo

    RuntimeInfo._instance = None
    monkeypatch.setattr("shutil.which", lambda _: None)

    n = Nexcript(project)
    with pytest.raises(RuntimeError, match="Node.js"):
        n._transpile_ts("let x: number = 1;")


def test_transpile_ts_old_node_raises(project, monkeypatch):
    from nexelpy.criptyle.nexcript.runtime_info import RuntimeInfo
    from unittest.mock import MagicMock

    RuntimeInfo._instance = None
    monkeypatch.setattr("shutil.which", lambda _: "/usr/bin/node")
    fake = MagicMock(stdout="v20.0.0\n")
    monkeypatch.setattr("subprocess.run", lambda *a, **k: fake)

    n = Nexcript(project)
    with pytest.raises(RuntimeError, match=">= 22.6.0"):
        n._transpile_ts("let x: number = 1;")


def test_transpile_ts_subprocess_failure(project, monkeypatch):
    from nexelpy.criptyle.nexcript.runtime_info import RuntimeInfo
    from unittest.mock import MagicMock
    import subprocess

    RuntimeInfo._instance = None
    monkeypatch.setattr("shutil.which", lambda _: "/usr/bin/node")

    calls = {"n": 0}

    def fake_run(*a, **k):
        calls["n"] += 1
        if calls["n"] == 1:
            m = MagicMock(stdout="v22.10.0\n")
            return m
        raise subprocess.CalledProcessError(1, "node", stderr="syntax error")

    monkeypatch.setattr("subprocess.run", fake_run)

    n = Nexcript(project)
    with pytest.raises(RuntimeError, match="TypeScript compilation failed"):
        n._transpile_ts("let x: = 1;")


def test_render_joins_blocks(project, tmp_path):
    with Nexcript(project) as n:
        n.add_script("const a = 1;")
        n.add_script("const b = 2;")
    content = (tmp_path / "script.js").read_text()
    assert "const a = 1;" in content
    assert "const b = 2;" in content