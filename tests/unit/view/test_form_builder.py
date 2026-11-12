from nexelpy import View
from nexelpy.mediator.request_proxy.request_object import set_request, reset_request
from starlette.requests import Request
import pytest
from pathlib import Path

class MockApp:
    def __init__(self):
        self.root_Path = str(Path(__file__).parent)
        self.secretKey = b"test_secret_key_1234567890123456"

@pytest.fixture
def view_instance():
    mock_app = MockApp()
    scope = {
        "type": "http", 
        "method": "GET", 
        "path": "/", 
        "headers": [], 
        "query_string": b"",
        "app": mock_app
    }
    req = Request(scope)
    token = set_request(req)
    
    x = View(__file__)
    yield x
    
    reset_request(token)

def test_form_input(view_instance):
    x = view_instance
    tag = x.input(type="text", name="username")
    assert "type='text'" in tag.build_tag
    assert "name='username'" in tag.build_tag

def test_form_submit(view_instance):
    x = view_instance
    tag = x.submit("Send")
    assert "type='submit'" in tag.build_tag
    assert "value='Send'" in tag.build_tag