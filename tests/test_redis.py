def test_redis(client):
    response = client.get("/test_redis")
    assert response.status_code == 200
    assert response.json()["redis_status"] == "Redis connection test successful"
