import pytest
from unittest.mock import patch
from nexelpy.mediator.mainAppHelper.branding import print_branding


def _capture_output(fn, *args, **kwargs):
    captured = []
    with patch(
        "nexelpy.mediator.mainAppHelper.branding.console"
    ) as mock_console:
        mock_console.print = lambda *a, **k: captured.append(a)
        fn(*args, **kwargs)
    return captured


def test_prints_logo_panel():
    captured = _capture_output(print_branding, "/project", has_node=True)
    assert len(captured) >= 1


def test_node_present_message():
    captured = _capture_output(print_branding, "/project", has_node=True)
    combined = " ".join(str(c) for c in captured)
    assert "Node.js found" in combined
    assert "TypeScript" in combined or "TS/JS" in combined


def test_node_missing_message():
    captured = _capture_output(print_branding, "/project", has_node=False)
    combined = " ".join(str(c) for c in captured)
    assert "Node.js not found" in combined
    assert "nodejs.org" in combined


def test_watching_message_includes_root():
    captured = _capture_output(print_branding, "/my/project", has_node=True)
    combined = " ".join(str(c) for c in captured)
    assert "/my/project" in combined
    assert "watching" in combined