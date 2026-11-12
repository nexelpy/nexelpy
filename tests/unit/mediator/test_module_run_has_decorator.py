import pytest
import sys
import types
from nexelpy.mediator.registerations.moduleRunHasDecorator import ModuleRunHasDecorator


def test_imports_valid_module(monkeypatch):
    mod = types.ModuleType("fake_ok_module")
    sys.modules["fake_ok_module"] = mod
    try:
        ModuleRunHasDecorator(["fake_ok_module"]).run()
    finally:
        del sys.modules["fake_ok_module"]


def test_handles_missing_module(capsys):
    ModuleRunHasDecorator(["does.not.exist"]).run()
    out = capsys.readouterr().out
    assert "Import Error" in out
    assert "does.not.exist" in out


def test_handles_broken_module(tmp_path, monkeypatch, capsys):
    broken = types.ModuleType("broken_module")
    sys.modules["broken_module"] = broken
    monkeypatch.setattr(
        "importlib.import_module",
        lambda name: (_ for _ in ()).throw(ValueError("boom")),
    )
    try:
        ModuleRunHasDecorator(["broken_module"]).run()
    finally:
        del sys.modules["broken_module"]
    out = capsys.readouterr().out
    assert "Import Error" in out
    assert "boom" in out


def test_empty_list_does_nothing(capsys):
    ModuleRunHasDecorator([]).run()
    assert capsys.readouterr().out == ""


def test_continues_after_failure(capsys):
    ModuleRunHasDecorator(["missing1", "missing2"]).run()
    out = capsys.readouterr().out
    assert "missing1" in out
    assert "missing2" in out