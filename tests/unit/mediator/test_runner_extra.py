import logging
import pytest
from unittest.mock import patch, MagicMock
from nexelpy.mediator.mainAppHelper.runner import run_app, UvicornAccessFilter


@pytest.fixture
def prod_app():
    app = MagicMock()
    app._is_parent = False
    app.is_local = True
    app.file = "/tmp/main.py"
    app.ignore_watch_dirs = []
    app.manual_routes = [{"path": "/a"}]
    app.AutoRegister_list = [{"path": "/b"}, {"path": "/c"}]
    return app


def test_run_app_prod_calls_uvicorn(prod_app):
    with patch("nexelpy.mediator.mainAppHelper.runner.uvicorn.run") as mock_uvicorn:
        run_app(prod_app, host="0.0.0.0", port=9000)
        mock_uvicorn.assert_called_once_with(prod_app, host="0.0.0.0", port=9000)


def test_run_app_dev_parent_uses_reloader(prod_app):
    prod_app._is_parent = True

    with patch("nexelpy.mediator.reloader.Reloader") as mock_reloader_cls:
        mock_instance = MagicMock()
        mock_reloader_cls.return_value = mock_instance
        run_app(prod_app)
        mock_instance.run.assert_called_once()


def test_run_app_prints_registered_counts(prod_app, capsys):
    with patch("nexelpy.mediator.mainAppHelper.runner.uvicorn.run"):
        run_app(prod_app)
    out = capsys.readouterr().out
    assert "registered manual routes" in out or "manual routes" in out


def test_uvicorn_access_filter_drops_well_known():
    f = UvicornAccessFilter()
    record = logging.LogRecord(
        name="uvicorn.access",
        level=logging.INFO,
        pathname="",
        lineno=0,
        msg="GET /.well-known/foo",
        args=(),
        exc_info=None,
    )
    assert f.filter(record) is False


def test_uvicorn_access_filter_keeps_normal():
    f = UvicornAccessFilter()
    record = logging.LogRecord(
        name="uvicorn.access",
        level=logging.INFO,
        pathname="",
        lineno=0,
        msg="GET /index",
        args=(),
        exc_info=None,
    )
    assert f.filter(record) is True