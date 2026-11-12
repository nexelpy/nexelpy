import pytest
from unittest.mock import patch, MagicMock
from pathlib import Path
from starlette.requests import Request
from nexelpy.mediator.request_proxy.request_object import set_request, reset_request
from nexelpy.mediator.show_error_in_view import show_error_in_view


def _setup_request(tmp_path):
    scope = {
        "type": "http",
        "method": "GET",
        "path": "/",
        "headers": [],
        "query_string": b"",
        "app": MagicMock(root_Path=str(tmp_path)),
    }
    return set_request(Request(scope))


class FakeResponse:
    status_code = 200
    body = b""
    media_type = "text/html"
    headers = {}


@pytest.mark.asyncio
async def test_renders_page_with_error_info(tmp_path):
    main = tmp_path / "main.py"
    main.touch()
    (tmp_path / ".nexelpy").touch()

    error_info = {
        "Time": "12:00:00",
        "Error": ValueError("boom"),
        "Module path": "/app/x.py",
        "Line number": 42,
        "Code": "raise ValueError",
    }

    captured = {}

    def fake_response(self):
        captured["html"] = self.elementsContainer.content
        return FakeResponse()

    token = _setup_request(tmp_path)
    try:
        with patch("nexelpy.view.pageBuilder.PageBilder.RESPONSE", new=fake_response):
            response = await show_error_in_view(error_info, file=str(main))
    finally:
        reset_request(token)

    html = captured["html"]
    assert "NexelPy error" in html
    assert "Time : 12:00:00" in html
    assert "Error : boom" in html
    assert "Line number : 42" in html
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_renders_with_empty_info(tmp_path):
    main = tmp_path / "main.py"
    main.touch()

    captured = {}

    def fake_response(self):
        captured["html"] = self.elementsContainer.content
        return FakeResponse()

    token = _setup_request(tmp_path)
    try:
        with patch("nexelpy.view.pageBuilder.PageBilder.RESPONSE", new=fake_response):
            await show_error_in_view({}, file=str(main))
    finally:
        reset_request(token)

    assert "NexelPy error" in captured["html"]