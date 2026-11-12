import pytest
from unittest.mock import MagicMock
from pathlib import Path
from nexelpy import View
from nexelpy.mediator.request_proxy.request_object import set_request, reset_request
from starlette.requests import Request


@pytest.fixture
def view(tmp_path):
    main = tmp_path / "main.py"
    main.touch()
    scope = {
        "type": "http", "method": "GET", "path": "/",
        "headers": [], "query_string": b"",
        "app": MagicMock(root_Path=str(tmp_path)),
    }
    token = set_request(Request(scope))
    try:
        yield View(str(main))
    finally:
        reset_request(token)


def test_form_with_action_and_method(view):
    f = view.form(action="/submit", method="POST")
    assert "action='/submit'" in f.build_tag
    assert "method='POST'" in f.build_tag


def test_form_with_attributes(view):
    f = view.form(action="/x", method="POST", enctype="multipart/form-data")
    assert "enctype='multipart/form-data'" in f.build_tag


def test_input_with_type_name_placeholder(view):
    tag = view.input(type="email", name="mail", placeholder="you@x.com")
    assert "type='email'" in tag.build_tag
    assert "name='mail'" in tag.build_tag
    assert "placeholder='you@x.com'" in tag.build_tag


def test_input_self_closing(view):
    tag = view.input(type="text", name="q")
    assert tag.selfClose is True
    assert tag.build_tag.endswith("/>")


def test_submit_has_type_and_value(view):
    tag = view.submit("Send")
    assert "type='submit'" in tag.build_tag
    assert "value='Send'" in tag.build_tag


def test_submit_with_extra_attributes(view):
    tag = view.submit("Go", name="action", Class="btn")
    assert "name='action'" in tag.build_tag
    assert "class='btn'" in tag.build_tag


def test_form_nested_input(view):
    form = view.form(action="/x", method="POST")
    view.input(type="text", name="n", parent=form)
    view.submit("Send", parent=form)
    html = form.build_tag
    assert "<form" in html
    assert "type='text'" in html
    assert "type='submit'" in html