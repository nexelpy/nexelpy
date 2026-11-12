# tests/unit/mediator/test_registry_extra.py
import pytest
from nexelpy.mediator.registerations.registry import RouteRegistry


@pytest.fixture(autouse=True)
def clear():
    RouteRegistry().clear()
    yield
    RouteRegistry().clear()


def test_get_by_module_returns_matching_routes():
    reg = RouteRegistry()
    reg.register({"path": "/a", "module": "mod1", "handler": lambda: None, "methods": ["GET"]})
    reg.register({"path": "/b", "module": "mod1", "handler": lambda: None, "methods": ["POST"]})
    reg.register({"path": "/c", "module": "mod2", "handler": lambda: None, "methods": ["GET"]})

    results = reg.get_by_module("mod1")
    assert len(results) == 2
    assert {r["path"] for r in results} == {"/a", "/b"}


def test_get_by_module_empty():
    assert RouteRegistry().get_by_module("nonexistent") == []


def test_count_returns_number_of_routes():
    reg = RouteRegistry()
    assert reg.count() == 0
    reg.register({"path": "/a", "handler": lambda: None, "methods": ["GET"]})
    assert reg.count() == 1
    reg.register({"path": "/b", "handler": lambda: None, "methods": ["GET"]})
    assert reg.count() == 2