import pytest
from nexelpy.mediator.registerations.decorators import Route, registry
from nexelpy.mediator.registerations.registry import RouteRegistry

@pytest.fixture(autouse=True)
def clear_registry():
    RouteRegistry().clear()
    yield
    RouteRegistry().clear()

def test_route_registration_success():
    @Route("/test")
    async def handler():
        pass
    
    routes = registry.get_all()
    assert len(routes) == 1
    assert routes[0]["path"] == "/test"
    assert routes[0]["handler"] == handler
    assert routes[0]["methods"] == ["GET"]

def test_route_with_prefix():
    @Route("/users", prefix="/api")
    async def handler():
        pass
    
    routes = registry.get_all()
    assert routes[0]["path"] == "/api/users"

def test_route_with_multiple_methods():
    @Route("/submit", methods=["GET", "POST"])
    async def handler():
        pass
    
    routes = registry.get_all()
    assert routes[0]["methods"] == ["GET", "POST"]

def test_route_sync_function_error(capsys):
    with pytest.raises(SystemExit) as exc_info:
        @Route("/sync")
        def sync_handler():
            pass
    
    assert exc_info.value.code == 1
    captured = capsys.readouterr()
    assert "Handler must be async" in captured.out

def test_route_invalid_path_error(capsys):
    with pytest.raises(SystemExit) as exc_info:
        @Route("invalid-path")  
        async def handler():
            pass
    
    assert exc_info.value.code == 1
    captured = capsys.readouterr()
    assert "route must start with '/'" in captured.out

def test_route_duplicate_error(capsys):
    @Route("/duplicate")
    async def handler1():
        pass

    with pytest.raises(SystemExit) as exc_info:
        @Route("/duplicate")
        async def handler2():
            pass
    
    assert exc_info.value.code == 1
    captured = capsys.readouterr()
    assert "Duplicate route detected" in captured.out