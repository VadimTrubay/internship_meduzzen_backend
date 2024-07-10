import unittest
from uuid import uuid4
from unittest.mock import AsyncMock

from fastapi.testclient import TestClient

from app.main import app
from app.schemas.users import UserSchema
from app.routers.users import get_user_service

client = TestClient(app)


class TestUserRoutes(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.user_service = AsyncMock()
        self.user_service.create_user.return_value = UserSchema(
            id=uuid4(),
            username="testuser",
            email="testuser@example.com",
            is_admin=False,
        )
        self.user_service.get_users.return_value = [
            UserSchema(
                id=uuid4(),
                username="testuser1",
                email="testuser1@example.com",
                is_admin=False,
            ),
            UserSchema(
                id=uuid4(),
                username="testuser2",
                email="testuser2@example.com",
                is_admin=False,
            ),
        ]
        self.user_service.get_user_by_id.return_value = UserSchema(
            id=uuid4(),
            username="testuser",
            email="testuser@example.com",
            is_admin=False,
        )
        self.user_service.update_user.return_value = UserSchema(
            id=uuid4(),
            username="updateduser",
            email="updateduser@example.com",
            is_admin=False,
        )
        self.user_service.delete_user.return_value = UserSchema(
            id=uuid4(),
            username="deleteduser",
            email="deleteduser@example.com",
            is_admin=False,
        )

        app.dependency_overrides[get_user_service] = lambda: self.user_service

    async def test_create_user(self):
        response = client.post(
            "/users/",
            json={
                "username": "testuser",
                "email": "testuser@example.com",
                "hashed_password": "hashedpassword",
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["username"], "testuser")

    async def test_get_all_users(self):
        response = client.get("/users/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()["users"]), 2)

    async def test_get_user_by_id(self):
        user_id = uuid4()
        response = client.get(f"/users/{user_id}")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["username"], "testuser")

    async def test_update_user(self):
        user_id = uuid4()
        response = client.patch(
            f"/users/{user_id}",
            json={
                "username": "updateduser",
                "email": "updateduser@example.com",
                "hashed_password": "updatehashedpassword",
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["username"], "updateduser")

    async def test_delete_user(self):
        user_id = uuid4()
        response = client.delete(f"/users/{user_id}")
        self.assertEqual(response.status_code, 200)
