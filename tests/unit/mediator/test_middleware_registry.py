import pytest
from nexelpy.mediator.middleware_builder.registry import MiddlewareRegistry
from nexelpy.mediator.middleware_builder.decorator import Middleware
from nexelpy.mediator.middleware_builder.errors import MiddlewareError

@pytest.fixture(autouse=True)
def clear_registry():
    MiddlewareRegistry().clear()
    yield
    MiddlewareRegistry().clear()

def test_middleware_registration():
    @Middleware(name="test_mw")
    class TestMW: pass
    
    registry = MiddlewareRegistry()
    assert len(registry._middlewares) == 1
    assert registry._middlewares[0][0] == "test_mw"

def test_middleware_duplicate_name():
    @Middleware(name="duplicate")
    class First: pass

    with pytest.raises(MiddlewareError, match="already registered"):
        @Middleware(name="duplicate")
        class Second: pass

def test_middleware_ordering():
    @Middleware(name="first")
    class First: pass

    @Middleware(name="second", after="first")
    class Second: pass

    @Middleware(name="third", after="second")
    class Third: pass

    ordered = MiddlewareRegistry().get_ordered()
    assert [m.__name__ for m in ordered] == ["First", "Second", "Third"]

def test_middleware_ordering_mixed():
    @Middleware(name="b", after="a")
    class B: pass

    @Middleware(name="a")
    class A: pass

    @Middleware(name="c", after="b")
    class C: pass

    ordered = MiddlewareRegistry().get_ordered()
    assert [m.__name__ for m in ordered] == ["A", "B", "C"]

def test_middleware_circular_dependency(capsys):
    @Middleware(name="a", after="b")
    class A: pass

    @Middleware(name="b", after="a")
    class B: pass

    with pytest.raises(SystemExit) as exc_info:
        MiddlewareRegistry().get_ordered()
    
    assert exc_info.value.code == 1
    captured = capsys.readouterr()
    assert "Cannot resolve middleware order" in captured.out

def test_middleware_missing_after_target(capsys):
    @Middleware(name="a", after="non_existent")
    class A: pass

    with pytest.raises(SystemExit) as exc_info:
        MiddlewareRegistry().get_ordered()
    
    assert exc_info.value.code == 1
    captured = capsys.readouterr()
    assert "Unresolved middlewares" in captured.out