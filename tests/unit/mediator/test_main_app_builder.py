import os
import pytest
from unittest.mock import patch, MagicMock
from pathlib import Path
from nexelpy.mediator.mainAppBuilder import MainAppBuilder


@pytest.fixture
def main_file(tmp_path):
    f = tmp_path / "main.py"
    f.write_text("")
    return f


def _build(tmp_path, monkeypatch, **kwargs):
    monkeypatch.chdir(tmp_path)
    (tmp_path / ".nexelpy").touch()
    # _is_parent=False so it goes through the child/prod path
    with patch.object(MainAppBuilder, "_signal_ready"):
        with patch(
            "nexelpy.mediator.mainAppBuilder.setup_routes",
            return_value={"routes": [], "middleware_modules": []},
        ):
            with patch("nexelpy.mediator.mainAppBuilder.setup_middlewares"):
                return MainAppBuilder(file=str(tmp_path / "main.py"), **kwargs)


def test_basic_attributes(tmp_path, monkeypatch):
    app = _build(tmp_path, monkeypatch)
    assert app.file == str(tmp_path / "main.py")
    assert app.root_Path == str(tmp_path)
    assert app.AutoRegister_list == []
    assert app.manual_routes == []
    assert app.Middleware_modules == []


def test_secret_key_from_param(tmp_path, monkeypatch):
    from cryptography.fernet import Fernet

    key = Fernet.generate_key()
    app = _build(tmp_path, monkeypatch, secretKey=key)
    assert app.secretKey == key


def test_secret_key_from_env(tmp_path, monkeypatch):
    monkeypatch.setenv("NEXELPY_SECRET_KEY", "env-key-value")
    app = _build(tmp_path, monkeypatch)
    assert app.secretKey == b"env-key-value"


def test_ignore_watch_dirs_default_empty(tmp_path, monkeypatch):
    app = _build(tmp_path, monkeypatch)
    assert app.ignore_watch_dirs == []


def test_ignore_watch_dirs_explicit(tmp_path, monkeypatch):
    app = _build(tmp_path, monkeypatch, ignore_watch_dirs=["build", "dist"])
    assert app.ignore_watch_dirs == ["build", "dist"]


def test_signal_ready_creates_file(tmp_path, monkeypatch):
    ready_path = tmp_path / "ready.marker"
    monkeypatch.setenv("NEXELPY_READY_FILE", str(ready_path))

    with patch(
        "nexelpy.mediator.mainAppBuilder.setup_routes",
        return_value={"routes": [], "middleware_modules": []},
    ):
        with patch("nexelpy.mediator.mainAppBuilder.setup_middlewares"):
            MainAppBuilder(file=str(tmp_path / "main.py"))

    assert ready_path.exists()


def test_signal_ready_ignores_errors(tmp_path, monkeypatch):
    monkeypatch.setenv("NEXELPY_READY_FILE", "/nonexistent/path/ready.marker")
    app = _build(tmp_path, monkeypatch)
    app._signal_ready()  # must not raise


def test_route_decorator_adds_manual_route(tmp_path, monkeypatch):
    app = _build(tmp_path, monkeypatch)

    @app.route("/x")
    async def handler():
        return "ok"

    assert len(app.manual_routes) == 1
    assert app.manual_routes[0]["path"] == "/x"
    assert app.manual_routes[0]["methods"] == ["GET"]


def test_route_decorator_with_methods(tmp_path, monkeypatch):
    app = _build(tmp_path, monkeypatch)

    @app.route("/y", methods=["GET", "POST"])
    async def handler():
        return "ok"

    assert app.manual_routes[0]["methods"] == ["GET", "POST"]


def test_route_decorator_with_prefix(tmp_path, monkeypatch):
    app = _build(tmp_path, monkeypatch)

    @app.route("/users", prefix="/api")
    async def handler():
        return "ok"

    assert app.manual_routes[0]["path"] == "/api/users"


def test_route_decorator_sync_raises(tmp_path, monkeypatch):
    app = _build(tmp_path, monkeypatch)

    with pytest.raises(TypeError, match="must be async"):
        @app.route("/bad")
        def handler():
            return "no"


def test_route_decorator_returns_function(tmp_path, monkeypatch):
    app = _build(tmp_path, monkeypatch)

    async def handler():
        return "ok"

    result = app.route("/z")(handler)
    assert result is handler


def test_add_manual_route_method(tmp_path, monkeypatch):
    app = _build(tmp_path, monkeypatch)

    async def handler():
        return "ok"

    app.add_manual_route(route="/m", methods=["POST"], func=handler)
    assert app.manual_routes[0]["path"] == "/m"
    assert app.manual_routes[0]["methods"] == ["POST"]


def test_run_sets_local_and_session_flags(tmp_path, monkeypatch):
    app = _build(tmp_path, monkeypatch)
    app.is_local = False
    app.session_secure = True

    with patch("nexelpy.mediator.mainAppBuilder.run_app") as mock_run:
        app.run(host="0.0.0.0", port=9000)
        mock_run.assert_called_once()
        assert app.is_local is True
        assert app.session_secure is False


def test_mount_statics_false(tmp_path, monkeypatch):
    with patch.object(MainAppBuilder, "_signal_ready"):
        with patch(
            "nexelpy.mediator.mainAppBuilder.setup_routes",
            return_value={"routes": [], "middleware_modules": []},
        ):
            with patch("nexelpy.mediator.mainAppBuilder.setup_middlewares"):
                with patch("nexelpy.mediator.mainAppBuilder.setup_statics") as mock_static:
                    MainAppBuilder(
                        file=str(tmp_path / "main.py"),
                        mountStatics=False,
                    )
                    args, kwargs = mock_static.call_args
                    assert kwargs.get("mount_statics", args[2] if len(args) > 2 else None) is False