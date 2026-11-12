# tests/integration/test_form_payload.py
import pytest
from starlette.testclient import TestClient
from nexelpy import Nexelpy, RestApi


def test_real_form_parsing(tmp_path):
    main = tmp_path / "main.py"; main.write_text("")
    app = Nexelpy(str(main))

    @app.route("/submit", methods=["POST"])
    async def submit():
        api = RestApi(str(main))
        username = await api.REQUEST.form("username")
        return api.RESPONSE_json(username=username)

    c = TestClient(app)
    r = c.post("/submit", data={"username": "ali"})
    assert r.status_code == 200
    assert r.json() == {"username": "ali"}