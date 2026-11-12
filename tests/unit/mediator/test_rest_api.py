# tests/unit/mediator/test_rest_api.py
import pytest
from unittest.mock import MagicMock
from pathlib import Path
from nexelpy.view.restApi import RestApi
from nexelpy.mediator.request_proxy.request_object import set_request, reset_request
from starlette.requests import Request


@pytest.fixture
def mock_request():
    scope = {
        "type": "http",
        "method": "GET",
        "path": "/",
        "headers": [],
        "query_string": b"",
        "app": MagicMock(root_Path=str(Path(__file__).resolve().parent)),
    }
    req = Request(scope)
    token = set_request(req)
    yield req
    reset_request(token)


@pytest.fixture
def api(mock_request):
    return RestApi(__file__)


def test_rest_api_json(api):
    response = api.RESPONSE_json(status_code=200, message="success", data={"id": 1})
    assert response.status_code == 200
    assert response.media_type == "application/json"
    assert b'"message":"success"' in response.body


def test_rest_api_text(api):
    response = api.RESPONSE_text("Hello, World!")
    assert response.status_code == 200
    assert response.body == b"Hello, World!"


def test_rest_api_no_content(api):
    response = api.RESPONSE_no_content()
    assert response.status_code == 204


def test_rest_api_redirect(api):
    response = api.RESPONSE_redirect("/login")
    assert response.status_code == 307
    assert response.headers["location"] == "/login"


def test_rest_api_file_not_found(api):
    response = api.RESPONSE_file("not_exists.txt")
    assert response.status_code == 404



def test_rest_api_json_with_headers(api):
    api.Headers.add_raw_header(X__Custom="yes")
    r = api.RESPONSE_json(ok=True)
    assert r.headers["x-custom"] == "yes"


def test_rest_api_text_with_cookie(api):
    api.set_Cookie("k", "v")
    r = api.RESPONSE_text("x")
    assert "k=v" in r.headers.get("set-cookie", "")


def test_rest_api_redirect_custom_status(api):
    r = api.RESPONSE_redirect("/x", status_code=308)
    assert r.status_code == 308


def test_rest_api_html_missing(api):
    r = api.RESPONSE_html("nope.html")
    assert r.status_code == 404


def test_rest_api_streaming(api):
    async def gen():
        yield b"a"
        yield b"b"

    r = api.RESPONSE_streaming(gen(), media_type="application/octet-stream")
    assert r.media_type == "application/octet-stream"
    assert r.status_code == 200


def test_rest_api_file_success(api, tmp_path):
    from nexelpy.view.pathBuilder import PathBuilder
    (tmp_path / "hello.txt").write_text("hi")
    api._PathBuilder = PathBuilder(file_path=tmp_path / "x.py", root=tmp_path)
    r = api.RESPONSE_file("hello.txt", media_type="text/plain") 
    assert r.status_code == 200
    assert r.media_type == "text/plain"