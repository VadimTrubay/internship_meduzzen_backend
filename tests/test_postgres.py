def test_postgres(client):
    response = client.get("/test_postgres")
    assert response.status_code == 200
    assert response.json()["postgres_status"] == "Postgres connection test successful"
