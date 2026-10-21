from app import app


def test_unknown_route_returns_404_not_500():
    client = app.test_client()

    response = client.get("/this-route-does-not-exist")

    assert response.status_code == 404
    payload = response.get_json()
    assert isinstance(payload, dict)
    assert payload.get("detail")


def test_missing_favicon_returns_404_not_500():
    client = app.test_client()

    response = client.get("/favicon.ico")

    assert response.status_code == 404
    payload = response.get_json()
    assert isinstance(payload, dict)
    assert payload.get("detail")
