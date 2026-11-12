import pytest
from nexelpy.mediator.request_proxy.requestProxy import RequestProxy
from nexelpy.mediator.request_proxy.request_object import set_request, reset_request
from starlette.requests import Request
from starlette.datastructures import URL, Headers

@pytest.fixture
def mock_proxy():
    scope = {
        "type": "http",
        "method": "POST",
        "path": "/test/42",
        "path_params": {"id": "42"},
        "query_string": b"name=ali&age=25",
        "headers": [
            (b"content-type", b"application/x-www-form-urlencoded"),
            (b"user-agent", b"pytest")
        ],
        "server": ("testserver", 80),
        "scheme": "http",            
        "app": None
    }
    
    async def receive():
        return {"type": "http.request", "body": b"username=admin&password=123", "more_body": False}
        
    req = Request(scope, receive)
    token = set_request(req)
    
    proxy = RequestProxy()
    yield proxy
    reset_request(token)

@pytest.mark.asyncio
async def test_proxy_method_and_url(mock_proxy):
    assert await mock_proxy.method() == "POST"
    url = await mock_proxy.url()
    assert isinstance(url, URL)
    assert str(url) == "http://testserver/test/42?name=ali&age=25"

@pytest.mark.asyncio
async def test_proxy_args(mock_proxy):
    args = await mock_proxy.args()
    assert args["name"] == "ali"
    assert await mock_proxy.args("age") == "25"

@pytest.mark.asyncio
async def test_proxy_path_params(mock_proxy):
    assert await mock_proxy.path_params("id") == "42"

@pytest.mark.asyncio
async def test_proxy_form(mock_proxy):
    form = await mock_proxy.form()
    assert form["username"] == "admin"
    assert await mock_proxy.form("password") == "123"

@pytest.mark.asyncio
async def test_proxy_headers(mock_proxy):
    headers = await mock_proxy.headers()
    assert isinstance(headers, Headers)
    assert await mock_proxy.headers("user-agent") == "pytest"

@pytest.mark.asyncio
async def test_proxy_app(mock_proxy):
    app = await mock_proxy.app()
    assert app is None

@pytest.mark.asyncio
async def test_proxy_set_state(mock_proxy):
    mock_proxy.set_state(custom_key="custom_value")
    req = mock_proxy._get_original_request()
    assert req.state.custom_key == "custom_value"