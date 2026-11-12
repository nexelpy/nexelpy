import pytest
from nexelpy.mediator.request_proxy.requestProxy import RequestProxy
from nexelpy.mediator.request_proxy.request_object import (
    set_request, reset_request, get_request,
)
from nexelpy.mediator.request_proxy import request_object
from starlette.requests import Request
from starlette.datastructures import Headers


@pytest.fixture
def proxy():
    scope = {
        "type": "http",
        "method": "POST",
        "path": "/u/42",
        "path_params": {"id": "42"},
        "query_string": b"a=1&b=2",
        "headers": [(b"x-test", b"v")],
        "server": ("testserver", 80),
        "scheme": "http",
        "app": None,
        "cached_body": b"k=v&z=w",
    }
    req = Request(scope)
    token = set_request(req)
    try:
        yield RequestProxy()
    finally:
        reset_request(token)


def test_get_request_without_context_raises():
    request_object._request_var.set(None)
    with pytest.raises(RuntimeError, match="not initialized"):
        get_request()


@pytest.mark.asyncio
async def test_method_and_url(proxy):
    assert await proxy.method() == "POST"
    assert str(await proxy.url()) == "http://testserver/u/42?a=1&b=2"


@pytest.mark.asyncio
async def test_args_single_and_multi(proxy):
    assert await proxy.args("a") == "1"
    assert await proxy.args("a", "b") == ["1", "2"]
    assert isinstance(await proxy.args(), dict)


@pytest.mark.asyncio
async def test_path_params(proxy):
    assert await proxy.path_params("id") == "42"


@pytest.mark.asyncio
async def test_headers(proxy):
    h = await proxy.headers()
    assert isinstance(h, Headers)
    assert await proxy.headers("x-test") == "v"


@pytest.mark.asyncio
async def test_form(proxy):
    assert await proxy.form("k") == "v"
    assert await proxy.form() == {"k": "v", "z": "w"}


@pytest.mark.asyncio
async def test_app(proxy):
    assert await proxy.app() is None


@pytest.mark.asyncio
async def test_scope_getters(proxy):
    assert await proxy.scope("path") == "/u/42"


def test_set_state(proxy):
    proxy.set_state(a=1, b=2)
    req = proxy._get_original_request()
    assert req.state.a == 1
    assert req.state.b == 2


@pytest.mark.asyncio
async def test_state_roundtrip(proxy):
    proxy.set_state(x=9)
    assert await proxy.state("x") == 9


@pytest.mark.asyncio
async def test_payload_dispatch(proxy):
    assert await proxy.payload("GET", "a") == "1"
    assert await proxy.payload("PATH", "id") == "42"
    assert await proxy.payload("POST", "k") == "v"
    with pytest.raises(ValueError, match="unsupported payload method"):
        await proxy.payload("NOPE")


def test_stream_returns_async_iterator(proxy):
    s = proxy.stream()
    assert hasattr(s, "__aiter__")

def test_scope_property(proxy):
    scope = proxy._scope
    assert isinstance(scope, dict)
    assert scope["path"] == "/u/42"


@pytest.mark.asyncio
async def test_client_returns_address_or_none(proxy):
    client = await proxy.client()
    assert client is None or hasattr(client, "host")


@pytest.mark.asyncio
async def test_cookies(proxy):
    result = await proxy.cookies()
    assert isinstance(result, dict)


@pytest.mark.asyncio
async def test_cookies_specific_key(proxy):
    assert await proxy.cookies("nonexistent") is None