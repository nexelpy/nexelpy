import pytest
from starlette.testclient import TestClient
from nexelpy import Nexelpy, Route, View
from nexelpy.mediator.request_proxy.request_object import set_request, reset_request
from starlette.requests import Request
from pathlib import Path
from nexelpy.mediator.reDirect import redirect_now

class MockApp:
    def __init__(self):
        self.root_Path = str(Path(__file__).parent)
        self.secretKey = b"test_secret_key_1234567890123456"
        self.is_local = True

@pytest.fixture(scope="module")
def app():
    app = Nexelpy(__file__)
    
    @app.route("/hello")
    async def hello():
        x = View(__file__)
        x.h1("Hello Test")
        return x.RESPONSE()

    @app.route("/error")
    async def error_route():
        raise ValueError("Test Error")

    @app.route("/redirect-test")
    async def redirect_route():
        redirect_now("/hello")

    return app

@pytest.fixture(scope="module")
def client(app):
    return TestClient(app, raise_server_exceptions=False) 

@pytest.fixture
def mock_request():
    mock_app = MockApp()
    scope = {
        "type": "http",
        "method": "GET",
        "path": "/",
        "headers": [(b"host", b"testserver")],
        "query_string": b"name=test&age=20",
        "app": mock_app
    }
    
    async def receive():
        return {"type": "http.request", "body": b'{"key": "value"}'}
    
    req = Request(scope, receive)
    token = set_request(req)
    yield req
    reset_request(token)