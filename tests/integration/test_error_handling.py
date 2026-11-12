def test_redirect_exception(client):
    response = client.get("/redirect-test", follow_redirects=False)
    assert response.status_code == 307
    assert response.headers["location"] == "/hello"