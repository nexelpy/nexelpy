import pytest
from unittest.mock import MagicMock
from nexelpy.view.restApi import RestApi
from nexelpy.mediator.request_proxy.request_object import set_request, reset_request
from starlette.requests import Request

@pytest.fixture
def mock_request():
    scope = {
        "type": "http",
        "method": "GET",
        "path": "/",
        "app": MagicMock(root_Path="/tmp")
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