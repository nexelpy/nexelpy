# tests/unit/tools/test_project_root.py
from pathlib import Path
from nexelpy.criptyle.sharedClasses.projectRoot import find_project_root


def test_finds_marker(tmp_path):
    (tmp_path / ".nexelpy").touch()
    sub = tmp_path / "a" / "b"
    sub.mkdir(parents=True)
    f = sub / "x.py"
    f.touch()
    assert find_project_root(f) == tmp_path


def test_fallback_to_parent_when_no_marker(tmp_path, monkeypatch):
    f = tmp_path / "x.py"
    f.touch()
    monkeypatch.setattr(Path, "exists", lambda self: self.name == ".nexelpy" and False)
    result = find_project_root(f)
    assert result == f.parent