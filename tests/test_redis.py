def test_redis(client):
    response = client.get("/test_redis")
    assert response.status_code == 200
    assert response.json()["message"] == "Redis connection test successful"
