import pytest
import time
from pathlib import Path
from nexelpy.mediator.reloader import Reloader


@pytest.fixture
def project(tmp_path):
    entry = tmp_path / "main.py"
    entry.write_text("print('x')")
    return entry


def test_ignore_dirs_includes_pycache(project):
    r = Reloader(entry_file=str(project))
    assert "__pycache__" in r.ignore_dirs


def test_extra_ignore_dirs(project):
    r = Reloader(entry_file=str(project), extra_ignore_dirs=["custom"])
    assert "custom" in r.ignore_dirs


def test_should_include_ignores_extra_dirs(project):
    extra = project.parent / "extra"
    extra.mkdir()
    (extra / "x.py").touch()
    r = Reloader(entry_file=str(project), extra_ignore_dirs=["extra"])
    assert r._should_include(extra / "x.py") is False


def test_should_include_ignores_non_py(project):
    r = Reloader(entry_file=str(project))
    assert r._should_include(project.parent / "x.txt") is False


def test_should_include_accepts_py(project):
    r = Reloader(entry_file=str(project))
    assert r._should_include(project) is True


def test_has_changes_detects_size_change(project):
    r = Reloader(entry_file=str(project))
    assert r._has_changes({"a.py": 10}, {"a.py": 20}) is True


def test_has_changes_detects_new_file(project):
    r = Reloader(entry_file=str(project))
    assert r._has_changes({"a.py": 10, "b.py": 20}, {"a.py": 10}) is True


def test_has_changes_detects_removed_file(project):
    r = Reloader(entry_file=str(project))
    assert r._has_changes({"a.py": 10}, {"a.py": 10, "b.py": 20}) is True


def test_has_changes_equal_returns_false(project):
    r = Reloader(entry_file=str(project))
    assert r._has_changes({"a.py": 10}, {"a.py": 10}) is False


def test_has_changes_empty_returns_false(project):
    r = Reloader(entry_file=str(project))
    assert r._has_changes({}, {}) is False


def test_snapshot_excludes_ignored(project):
    (project.parent / "__pycache__").mkdir()
    (project.parent / "__pycache__" / "x.py").touch()
    (project.parent / "keep.py").touch()
    r = Reloader(entry_file=str(project))
    snap = r._snapshot()
    assert not any("__pycache__" in k for k in snap)
    assert any(k.endswith("keep.py") for k in snap)


def test_make_ready_path_unique(project):
    r = Reloader(entry_file=str(project))
    p1 = r._make_ready_path()
    p2 = r._make_ready_path()
    assert p1 != p2
    assert "nexelpy_ready" in p1.name


def test_is_child_checks_env(monkeypatch):
    monkeypatch.setenv(Reloader.CHILD_ENV_KEY, "1")
    assert Reloader.is_child() is True
    monkeypatch.delenv(Reloader.CHILD_ENV_KEY)
    assert Reloader.is_child() is False