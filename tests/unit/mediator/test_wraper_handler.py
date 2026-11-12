import pytest
from unittest.mock import patch, MagicMock
from nexelpy.mediator.wraper_handler import wraper_handler, _find_user_frame
from nexelpy.mediator.reDirect import RedirectException
from starlette.requests import Request

@pytest.fixture
def mock_request():
    scope = {
        "type": "http",
        "method": "GET",
        "path": "/",
        "app": MagicMock(is_local=True, file="test.py")
    }
    return Request(scope)

@pytest.mark.asyncio
async def test_wraper_handler_redirect(mock_request):
    async def handler():
        raise RedirectException("/login")

    endpoint = wraper_handler(handler)
    
    with pytest.raises(RedirectException):
        await endpoint(mock_request)

@pytest.mark.asyncio
async def test_wraper_handler_dev_mode(mock_request):
    async def handler():
        raise ValueError("Test Error")

    mock_request.scope["app"].devMode = True
    mock_request.scope["app"].is_local = True
    
    with patch("nexelpy.mediator.wraper_handler.show_error_in_view") as mock_view:
        mock_view.return_value = "Error Page"
        endpoint = wraper_handler(handler)
        response = await endpoint(mock_request)
        
        assert response == "Error Page"
        mock_view.assert_called_once()

@pytest.mark.asyncio
async def test_wraper_handler_prod_mode(mock_request):
    async def handler():
        raise ValueError("Test Error")

    mock_request.scope["app"].is_local = False
    
    endpoint = wraper_handler(handler)
    
    with pytest.raises(ValueError, match="Test Error"):
        await endpoint(mock_request)

def test_find_user_frame():
    try:
        raise ValueError("Test")
    except ValueError as e:
        frame = _find_user_frame(e.__traceback__)
        assert frame is not None
        assert "test_wraper_handler.py" in frame.filename