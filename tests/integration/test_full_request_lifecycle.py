# tests/integration/test_full_request_lifecycle.py
import pytest
from starlette.testclient import TestClient
from nexelpy import Nexelpy, View, RestApi, CookiesManager


def test_view_with_cookies_and_headers(tmp_path):
    main = tmp_path / "main.py"; main.write_text("")
    app = Nexelpy(str(main))

    @app.route("/page")
    async def page():
        x = View(str(main))
        x.set_Cookie("sid", "abc")
        x.Headers.add_raw_header(X__Custom="yes")
        x.h1("hi")
        return x.RESPONSE()

    c = TestClient(app)
    r = c.get("/page")
    assert r.status_code == 200
    assert "sid=abc" in r.headers["set-cookie"]
    assert r.headers["x-custom"] == "yes"
    assert "<h1>hi</h1>" in r.text


def test_rest_api_with_headers_and_cookie(tmp_path):
    main = tmp_path / "main.py"; main.write_text("")
    app = Nexelpy(str(main))

    @app.route("/api")
    async def api():
        a = RestApi(str(main))
        a.Headers.add_raw_header(X__Api="1")
        a.set_Cookie("k", "v")
        return a.RESPONSE_json(ok=True)

    c = TestClient(app)
    r = c.get("/api")
    assert r.json() == {"ok": True}
    assert r.headers["x-api"] == "1"
    assert "k=v" in r.headers["set-cookie"]