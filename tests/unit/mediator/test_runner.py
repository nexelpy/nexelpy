import pytest
from unittest.mock import patch, MagicMock
from nexelpy.mediator.mainAppHelper.runner import run_app

@pytest.fixture
def mock_app():
    app = MagicMock()
    app._is_parent = False
    app.is_local = True
    app.file = "/tmp/main.py"
    app.ignore_watch_dirs = []
    app.manual_routes = []
    app.AutoRegister_list = []
    return app

def test_run_app_production(mock_app):
    mock_app._is_parent = False
    
    with patch("nexelpy.mediator.mainAppHelper.runner.uvicorn.run") as mock_uvicorn:
        run_app(mock_app, host="127.0.0.1", port=8000)
        
        mock_uvicorn.assert_called_once_with(mock_app, host="127.0.0.1", port=8000)

def test_run_app_dev_parent(mock_app):
    mock_app._is_parent = True
    
    with patch("nexelpy.mediator.reloader.Reloader") as mock_reloader:
        run_app(mock_app)
        
        mock_reloader.return_value.run.assert_called_once()