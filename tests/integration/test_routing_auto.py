def test_get_route(client):
    response = client.get("/hello")
    assert response.status_code == 200
    assert "<h1>Hello Test</h1>" in response.text

def test_404_route(client):
    response = client.get("/not-exists")
    assert response.status_code == 404