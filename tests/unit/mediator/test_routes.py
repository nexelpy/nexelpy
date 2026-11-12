import pytest
from unittest.mock import MagicMock, patch
from nexelpy.mediator.mainAppHelper.routes import (
    setup_routes,
    register_root_list,
    add_manual_route,
)


def test_setup_routes_calls_registration_builder(tmp_path):
    main = tmp_path / "main.py"
    main.touch()
    fake_result = {
        "routes": [{"path": "/a", "handler": lambda: None, "methods": ["GET"]}],
        "middleware_modules": [],
    }

    with patch(
        "nexelpy.mediator.mainAppHelper.routes.RegistrationBuilder"
    ) as mock_builder:
        mock_instance = MagicMock()
        mock_instance.run.return_value = fake_result
        mock_builder.return_value = mock_instance

        result = setup_routes(app=None, file=str(main))
        mock_builder.assert_called_once_with(str(main))
        assert result == fake_result


def test_register_root_list_adds_wrapped_routes():
    async def handler():
        return "x"

    app = MagicMock()
    routes = [
        {"path": "/a", "handler": handler, "methods": ["GET"]},
        {"path": "/b", "handler": handler, "methods": ["POST"]},
    ]

    with patch("nexelpy.mediator.mainAppHelper.routes.wraper_handler") as mock_wrap:
        mock_wrap.return_value = "wrapped"
        register_root_list(app, routes)
        assert app.add_route.call_count == 2
        assert mock_wrap.call_count == 2


def _make_app():
    app = MagicMock()
    app.routes = []
    app.manual_routes = []
    return app


def test_add_manual_route_with_defaults():
    app = _make_app()

    async def handler():
        return "x"

    with patch("nexelpy.mediator.mainAppHelper.routes.wraper_handler") as mock_wrap:
        mock_wrap.return_value = "wrapped"
        result = add_manual_route(app, route="/x", func=handler)
        assert result is handler
        assert app.manual_routes[-1]["path"] == "/x"
        assert app.manual_routes[-1]["methods"] == ["GET"]


def test_add_manual_route_with_methods_string():
    app = _make_app()

    async def handler():
        return "x"

    with patch("nexelpy.mediator.mainAppHelper.routes.wraper_handler") as mock_wrap:
        mock_wrap.return_value = "wrapped"
        add_manual_route(app, route="/x", methods="post", func=handler)
        assert app.manual_routes[-1]["methods"] == ["POST"]


def test_add_manual_route_with_methods_iterable():
    app = _make_app()

    async def handler():
        return "x"

    with patch("nexelpy.mediator.mainAppHelper.routes.wraper_handler") as mock_wrap:
        mock_wrap.return_value = "wrapped"
        add_manual_route(app, route="/x", methods=["get", "post"], func=handler)
        assert app.manual_routes[-1]["methods"] == ["GET", "POST"]


def test_add_manual_route_func_not_callable_raises():
    app = _make_app()
    with pytest.raises(TypeError, match="func must be a callable"):
        add_manual_route(app, route="/x", func=None)


def test_add_manual_route_invalid_path_raises():
    app = _make_app()

    async def handler():
        return "x"

    with pytest.raises(ValueError, match="must start with"):
        add_manual_route(app, route="bad-path", func=handler)


def test_add_manual_route_with_prefix():
    app = _make_app()

    async def handler():
        return "x"

    with patch("nexelpy.mediator.mainAppHelper.routes.wraper_handler") as mock_wrap:
        mock_wrap.return_value = "wrapped"
        add_manual_route(app, route="/u", prefix="/api", func=handler)
        assert app.manual_routes[-1]["path"] == "/api/u"
        assert app.manual_routes[-1]["prefix"] == "/api"


def test_add_manual_route_moves_static_to_end():
    from starlette.routing import Mount

    async def handler():
        return "x"

    app = _make_app()
    static_mount = Mount("/", app=MagicMock(), name="static")
    app.routes = [static_mount]

    with patch("nexelpy.mediator.mainAppHelper.routes.wraper_handler") as mock_wrap:
        mock_wrap.return_value = "wrapped"
        app.add_route.side_effect = lambda path, fn, methods: app.routes.append(
            Mount(path, app=fn, name="manual")
        )
        add_manual_route(app, route="/x", func=handler)
        assert app.routes[-1] is static_mount


def test_add_manual_route_records_metadata():
    app = _make_app()

    async def handler():
        return "x"

    with patch("nexelpy.mediator.mainAppHelper.routes.wraper_handler") as mock_wrap:
        mock_wrap.return_value = "wrapped"
        add_manual_route(app, route="/meta", func=handler)
        data = app.manual_routes[-1]
        assert data["handler"] is handler
        assert data["route"] == "/meta"
        assert data["module"] == handler.__module__
        assert "line" in data
        assert "file" in data