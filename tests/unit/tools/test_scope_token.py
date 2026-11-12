# tests/unit/tools/test_scope_token.py
import pytest
from pathlib import Path
from nexelpy.criptyle.sharedClasses.scopeToken import _make_scope_token


def test_token_is_deterministic():
    a = _make_scope_token("/a/b/c.py")
    b = _make_scope_token("/a/b/c.py")
    assert a == b


def test_token_differs_for_different_paths():
    assert _make_scope_token("/a/b.py") != _make_scope_token("/a/c.py")


def test_token_length():
    assert len(_make_scope_token("/x.py")) == 5


def test_token_is_lowercase_alnum():
    t = _make_scope_token("/x.py")
    assert t == t.lower()
    assert t.isalnum()


@pytest.mark.parametrize("path", ["/a.py", "relative.py", Path("/tmp/x.py")])
def test_token_accepts_various_types(path):
    t = _make_scope_token(path)
    assert isinstance(t, str) and len(t) == 5