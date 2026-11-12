# tests/integration/test_middleware_flow.py

import pytest
from starlette.testclient import TestClient

from nexelpy import Nexelpy, Middleware, View
from nexelpy.mediator.middleware_builder.registry import MiddlewareRegistry
from nexelpy.mediator.middleware_builder.errors import MiddlewareError


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture(autouse=True)
def clear_middleware_registry():
    MiddlewareRegistry().clear()
    yield
    MiddlewareRegistry().clear()


@pytest.fixture
def make_app(tmp_path):
    def _make():
        main = tmp_path / "main.py"
        main.write_text("")
        return Nexelpy(str(main)), str(main)
    return _make


# ---------------------------------------------------------------------------
# 1.
# ---------------------------------------------------------------------------

def test_middleware_runs_around_handler(tmp_path):
    """m1-in → m2-in → handler → m2-out → m1-out"""
    order = []

    @Middleware(name="m1")
    class M1:
        def __init__(self, app):
            self.app = app

        async def __call__(self, scope, receive, send):
            order.append("m1-in")
            await self.app(scope, receive, send)
            order.append("m1-out")

    @Middleware(name="m2", after="m1")
    class M2:
        def __init__(self, app):
            self.app = app

        async def __call__(self, scope, receive, send):
            order.append("m2-in")
            await self.app(scope, receive, send)
            order.append("m2-out")

    main = tmp_path / "main.py"
    main.write_text("")
    app = Nexelpy(str(main))

    @app.route("/x")
    async def handler():
        order.append("handler")
        x = View(str(main))
        x.p("ok")
        return x.RESPONSE()

    r = TestClient(app).get("/x")

    assert r.status_code == 200
    assert order == ["m1-in", "m2-in", "handler", "m2-out", "m1-out"]


# ---------------------------------------------------------------------------
# 2.
# ---------------------------------------------------------------------------

def test_middleware_chain_of_three(tmp_path):
    """a → b → c (b after a, c after b) """
    order = []

    def make(name):
        class _M:
            def __init__(self, app):
                self.app = app

            async def __call__(self, scope, receive, send):
                order.append(f"{name}-in")
                await self.app(scope, receive, send)
                order.append(f"{name}-out")
        _M.__name__ = f"M_{name}"
        return _M

    Middleware(name="a")(make("a"))
    Middleware(name="b", after="a")(make("b"))
    Middleware(name="c", after="b")(make("c"))

    main = tmp_path / "main.py"
    main.write_text("")
    app = Nexelpy(str(main))

    @app.route("/y")
    async def handler():
        order.append("handler")
        x = View(str(main))
        x.p("hi")
        return x.RESPONSE()

    TestClient(app).get("/y")

    assert order == [
        "a-in", "b-in", "c-in",
        "handler",
        "c-out", "b-out", "a-out",
    ]


# ---------------------------------------------------------------------------
# 3. 
# ---------------------------------------------------------------------------

def test_ordering_independent_of_registration_order(tmp_path):

    order = []

    @Middleware(name="m2", after="m1")
    class M2:
        def __init__(self, app):
            self.app = app

        async def __call__(self, scope, receive, send):
            order.append("m2")
            await self.app(scope, receive, send)

    @Middleware(name="m1")
    class M1:
        def __init__(self, app):
            self.app = app

        async def __call__(self, scope, receive, send):
            order.append("m1")
            await self.app(scope, receive, send)

    main = tmp_path / "main.py"
    main.write_text("")
    app = Nexelpy(str(main))

    @app.route("/z")
    async def handler():
        x = View(str(main))
        x.p("x")
        return x.RESPONSE()

    TestClient(app).get("/z")

    assert order.index("m1") < order.index("m2")


# ---------------------------------------------------------------------------
# 4. Short-circuit
# ---------------------------------------------------------------------------

def test_middleware_short_circuits_handler(tmp_path):

    handler_ran = {"value": False}

    @Middleware(name="blocker")
    class Blocker:
        def __init__(self, app):
            self.app = app

        async def __call__(self, scope, receive, send):
            from starlette.responses import PlainTextResponse
            response = PlainTextResponse("blocked", status_code=403)
            await response(scope, receive, send)

    main = tmp_path / "main.py"
    main.write_text("")
    app = Nexelpy(str(main))

    @app.route("/secret")
    async def handler():
        handler_ran["value"] = True
        x = View(str(main))
        x.p("ok")
        return x.RESPONSE()

    r = TestClient(app).get("/secret")

    assert r.status_code == 403
    assert r.text == "blocked"
    assert handler_ran["value"] is False


# ---------------------------------------------------------------------------
# 5
# ---------------------------------------------------------------------------

def test_middleware_injects_response_header(tmp_path):
    @Middleware(name="hdr")
    class HeaderInjector:
        def __init__(self, app):
            self.app = app

        async def __call__(self, scope, receive, send):
            async def send_wrapper(message):
                if message["type"] == "http.response.start":
                    headers = list(message.get("headers", []))
                    headers.append((b"x-injected", b"yes"))
                    message = {**message, "headers": headers}
                await send(message)

            await self.app(scope, receive, send_wrapper)

    main = tmp_path / "main.py"
    main.write_text("")
    app = Nexelpy(str(main))

    @app.route("/h")
    async def handler():
        x = View(str(main))
        x.p("ok")
        return x.RESPONSE()

    r = TestClient(app).get("/h")

    assert r.status_code == 200
    assert r.headers["x-injected"] == "yes"


# ---------------------------------------------------------------------------
# 6.
# ---------------------------------------------------------------------------

def test_no_middleware_still_works(tmp_path):
    main = tmp_path / "main.py"
    main.write_text("")
    app = Nexelpy(str(main))

    @app.route("/plain")
    async def handler():
        x = View(str(main))
        x.p("hello")
        return x.RESPONSE()

    r = TestClient(app).get("/plain")
    assert r.status_code == 200
    assert "<p>hello</p>" in r.text


# ---------------------------------------------------------------------------
# 7.
# ---------------------------------------------------------------------------

def test_middleware_applies_to_all_routes(tmp_path):
    hits = []

    @Middleware(name="tracker")
    class Tracker:
        def __init__(self, app):
            self.app = app

        async def __call__(self, scope, receive, send):
            if scope["type"] == "http":
                hits.append(scope["path"])
            await self.app(scope, receive, send)

    main = tmp_path / "main.py"
    main.write_text("")
    app = Nexelpy(str(main))

    @app.route("/a")
    async def a():
        x = View(str(main))
        x.p("A")
        return x.RESPONSE()

    @app.route("/b")
    async def b():
        x = View(str(main))
        x.p("B")
        return x.RESPONSE()

    client = TestClient(app)
    client.get("/a")
    client.get("/b")

    assert hits == ["/a", "/b"]


# ---------------------------------------------------------------------------
# 8.
# ---------------------------------------------------------------------------

def test_registry_isolated_between_tests(tmp_path):
    order = []

    @Middleware(name="only_this_test")
    class OnlyMe:
        def __init__(self, app):
            self.app = app

        async def __call__(self, scope, receive, send):
            order.append("only")
            await self.app(scope, receive, send)

    main = tmp_path / "main.py"
    main.write_text("")
    app = Nexelpy(str(main))

    @app.route("/iso")
    async def handler():
        x = View(str(main))
        x.p("x")
        return x.RESPONSE()

    TestClient(app).get("/iso")

    assert order == ["only"]


# ---------------------------------------------------------------------------
# 9
# ---------------------------------------------------------------------------

def test_duplicate_middleware_name_in_new_app(tmp_path):
    @Middleware(name="dup")
    class First:
        def __init__(self, app):
            self.app = app

        async def __call__(self, scope, receive, send):
            await self.app(scope, receive, send)

    with pytest.raises(MiddlewareError, match="already registered"):
        @Middleware(name="dup")
        class Second:
            def __init__(self, app):
                self.app = app

            async def __call__(self, scope, receive, send):
                await self.app(scope, receive, send)