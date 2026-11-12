# tests/unit/view/test_vapi.py
import pytest
import json
from unittest.mock import MagicMock
from pathlib import Path
from nexelpy.view.vapi import Vapi
from nexelpy.mediator.request_proxy.request_object import set_request, reset_request
from starlette.requests import Request


@pytest.fixture
def vapi():
    scope = {
        "type": "http", "method": "GET", "path": "/",
        "headers": [], "query_string": b"",
        "app": MagicMock(root_Path=str(Path(__file__).resolve().parent)),
    }
    req = Request(scope)
    token = set_request(req)
    try:
        yield Vapi(__file__)
    finally:
        reset_request(token)


def test_vapi_response_shape(vapi):
    vapi.h1("Hello")
    vapi.set_Cookie("k", "v")
    r = vapi.RESPONSE(status_code=201, status_message="ok", user_id=42)
    assert r.status_code == 201
    body = json.loads(r.body)
    assert body["user_id"] == 42
    assert body["status_message"] == "ok"
    assert "<h1>Hello</h1>" in body["view"]
    assert "set-cookie" in r.headers


def test_vapi_response_default_status_message_is_empty(vapi):
    body = json.loads(vapi.RESPONSE().body)
    assert body["status_message"] == ""


def test_vapi_links_header_present(vapi):
    body = json.loads(vapi.RESPONSE(ok=True).body)
    assert "QE_links_header" in body


def test_vapi_extra_data_merges(vapi):
    body = json.loads(vapi.RESPONSE(a=1, b=2).body)
    assert body["a"] == 1 and body["b"] == 2