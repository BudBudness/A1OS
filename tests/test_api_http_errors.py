from app import app


def test_unknown_route_returns_404_not_500():
    client = app.test_client()

    response = client.get("/this-route-does-not-exist")

    assert response.status_code == 404
    assert response.get_json() == {"detail": "The requested URL was not found on the server. If you entered the URL manually please check your spelling and try again."}


def test_missing_favicon_returns_404_not_500():
    client = app.test_client()

    response = client.get("/favicon.ico")

    assert response.status_code == 404
    assert response.get_json()["detail"]
