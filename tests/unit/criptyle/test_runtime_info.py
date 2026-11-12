# tests/unit/criptyle/test_runtime_info.py
import pytest
from unittest.mock import patch, MagicMock
from nexelpy.criptyle.nexcript.runtime_info import RuntimeInfo


@pytest.fixture(autouse=True)
def reset_singleton():
    RuntimeInfo._instance = None
    yield
    RuntimeInfo._instance = None


def test_no_node(monkeypatch):
    monkeypatch.setattr("shutil.which", lambda _: None)
    info = RuntimeInfo()
    assert info.has_node is False
    assert info.can_transpile_ts is False


@pytest.mark.parametrize("version,ok", [
    ("v22.6.0", True),
    ("v22.5.0", False),
    ("v23.0.0", True),
    ("v20.0.0", False),
    ("v22.10.3", True),
])
def test_node_version_gate(monkeypatch, version, ok):
    monkeypatch.setattr("shutil.which", lambda _: "/usr/bin/node")
    fake = MagicMock(stdout=version + "\n")
    monkeypatch.setattr("subprocess.run", lambda *a, **k: fake)
    info = RuntimeInfo()
    assert info.has_node is True
    assert info.node_version == version
    assert info.node_version_ok is ok
    assert info.can_transpile_ts is ok


def test_subprocess_failure_marks_not_ok(monkeypatch):
    monkeypatch.setattr("shutil.which", lambda _: "/usr/bin/node")
    def boom(*a, **k):
        raise OSError("nope")
    monkeypatch.setattr("subprocess.run", boom)
    info = RuntimeInfo()
    assert info.has_node is True
    assert info.node_version_ok is False


def test_singleton_returns_same_instance(monkeypatch):
    monkeypatch.setattr("shutil.which", lambda _: None)
    a = RuntimeInfo()
    b = RuntimeInfo()
    assert a is b