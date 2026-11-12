# tests/unit/mediator/test_wraper_handler.py
import pytest
from unittest.mock import patch, MagicMock
from nexelpy.mediator.wraper_handler import wraper_handler, _find_user_frame
from nexelpy.mediator.reDirect import RedirectException
from starlette.requests import Request


@pytest.fixture
def req_dev():
    scope = {"type": "http", "method": "GET", "path": "/",
             "app": MagicMock(is_local=True, file="x.py")}
    return Request(scope)


@pytest.fixture
def req_prod():
    scope = {"type": "http", "method": "GET", "path": "/",
             "app": MagicMock(is_local=False, file="x.py")}
    return Request(scope)


@pytest.mark.asyncio
async def test_redirect_propagates(req_dev):
    async def h():
        raise RedirectException("/x")
    with pytest.raises(RedirectException):
        await wraper_handler(h)(req_dev)


@pytest.mark.asyncio
async def test_dev_mode_renders_error(req_dev):
    async def h():
        raise ValueError("boom")
    with patch("nexelpy.mediator.wraper_handler.show_error_in_view") as m:
        m.return_value = "page"
        r = await wraper_handler(h)(req_dev)
    assert r == "page"
    info = m.call_args.args[0]
    assert info["Error"].__class__ is ValueError


@pytest.mark.asyncio
async def test_prod_mode_reraises(req_prod):
    async def h():
        raise ValueError("boom")
    with pytest.raises(ValueError):
        await wraper_handler(h)(req_prod)


@pytest.mark.asyncio
async def test_prod_mode_logs(req_prod, caplog):
    import logging
    caplog.set_level(logging.ERROR, logger="nexelpy.handler")
    async def h():
        raise RuntimeError("x")
    with pytest.raises(RuntimeError):
        await wraper_handler(h)(req_prod)
    assert any("Unhandled" in r.message for r in caplog.records)


@pytest.mark.asyncio
async def test_dev_fallback_when_render_fails(req_dev):
    async def h():
        raise ValueError("y")
    with patch("nexelpy.mediator.wraper_handler.show_error_in_view",
               side_effect=RuntimeError("render failed")):
        with pytest.raises(ValueError):
            await wraper_handler(h)(req_dev)


def test_find_user_frame_returns_user_code():
    try:
        raise ValueError("t")
    except ValueError as e:
        f = _find_user_frame(e.__traceback__)
    assert "test_wraper_handler" in f.filename