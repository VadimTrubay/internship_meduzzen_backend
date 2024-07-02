def test_health_check(client):
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["detail"] == "ok"
    assert response.json()["result"] == "working"

