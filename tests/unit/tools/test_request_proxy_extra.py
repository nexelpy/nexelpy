import pytest
from nexelpy.mediator.request_proxy.requestProxy import RequestProxy
from nexelpy.mediator.request_proxy.request_object import set_request, reset_request
from starlette.requests import Request


@pytest.fixture
def proxy_json():
    scope = {
        "type": "http", "method": "POST", "path": "/u",
        "path_params": {},
        "query_string": b"",
        "headers": [(b"content-type", b"application/json")],
        "server": ("t", 80), "scheme": "http", "app": None,
    }
    async def receive():
        return {"type": "http.request", "body": b'{"a": 1, "b": 2}', "more_body": False}
    req = Request(scope, receive)
    token = set_request(req)
    try:
        yield RequestProxy()
    finally:
        reset_request(token)


@pytest.fixture
def proxy_stream():
    scope = {
        "type": "http", "method": "POST", "path": "/",
        "path_params": {}, "query_string": b"",
        "headers": [],
        "server": ("t", 80), "scheme": "http", "app": None,
    }
    chunks = [b"one", b"two", b"three"]
    idx = {"i": 0}

    async def receive():
        i = idx["i"]
        if i < len(chunks):
            idx["i"] += 1
            return {"type": "http.request", "body": chunks[i], "more_body": i < len(chunks) - 1}
        return {"type": "http.disconnect"}

    req = Request(scope, receive)
    token = set_request(req)
    try:
        yield RequestProxy()
    finally:
        reset_request(token)


@pytest.mark.asyncio
async def test_json_whole_and_key(proxy_json):
    assert await proxy_json.json("a") == 1
    assert await proxy_json.json("a", "b") == [1, 2]
    data = await proxy_json.json()
    assert data == {"a": 1, "b": 2}


@pytest.mark.asyncio
async def test_body_returns_bytes(proxy_json):
    body = await proxy_json.body()
    assert isinstance(body, bytes)
    assert b'"a": 1' in body


@pytest.mark.asyncio
async def test_body_uses_cached_when_present():
    scope = {
        "type": "http", "method": "POST", "path": "/",
        "path_params": {}, "query_string": b"",
        "headers": [], "server": ("t", 80), "scheme": "http", "app": None,
        "cached_body": b"cached-content",
    }
    req = Request(scope)
    token = set_request(req)
    try:
        p = RequestProxy()
        assert await p.body() == b"cached-content"
    finally:
        reset_request(token)


@pytest.mark.asyncio
async def test_stream_yields_chunks(proxy_stream):
    chunks = []
    async for c in proxy_stream.stream():
        chunks.append(c)
    assert b"one" in b"".join(chunks)
    assert b"two" in b"".join(chunks)