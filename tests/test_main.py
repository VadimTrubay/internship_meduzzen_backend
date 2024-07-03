def test_health_check(client):
    response = client.get("/")
    assert response.status_code == 200
    json_response = response.json()
    assert json_response.get("detail") == "ok"
    assert json_response.get("result") == "working"
