<<<<<<< Updated upstream
import pytest
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4
from app.services.company_service import CompanyService
from app.repository.company_repository import CompanyRepository
from app.schemas.companies import (
    CompanyCreateRequest,
    CompanyUpdateRequest,
    CompanySchema,
)
from app.exept.custom_exceptions import CompanyNotFound, NotOwner


@pytest.mark.asyncio
class TestCompanyService:
    @pytest.fixture
    def company_service(self):
        session = MagicMock()
        repository = MagicMock()
        return CompanyService(session=session, repository=repository)

    @pytest.fixture
    def valid_company_data(self):
        return {
            "description": "A description",
            "id": uuid4(),
            "name": "Test Company",
            "owner_id": uuid4(),
            "visible": True,
        }

    # async def test_create_company(self, company_service, valid_company_data):
    #     company_service.repository.create_company_with_owner = AsyncMock(return_value=valid_company_data)
    #
    #     create_request = CompanyCreateRequest(
    #         name="Test Company",
    #         description="A description",
    #         visible=True
    #     )
    #
    #     result = await company_service.create_company(create_request, uuid4())
    #
    #     expected_result = CompanySchema(**valid_company_data)
    #     assert result == expected_result
    #     company_service.repository.create_company_with_owner.assert_called_once()

    # async def test_get_company_or_raise_success(self, company_service, valid_company_data):
    #     company_service.repository.get_one = AsyncMock(return_value=valid_company_data)
    #
    #     result = await company_service._get_company_or_raise(valid_company_data["id"])
    #
    #     expected_result = CompanySchema(**valid_company_data)
    #     print(expected_result)
    #     assert result == expected_result

    # async def test_validate_company_success(self, company_service, valid_company_data):
    #     company_service._get_company_or_raise = AsyncMock(return_value=valid_company_data)
    #     company_service.repository.is_user_company_owner = AsyncMock(return_value=True)
    #
    #     result = await company_service.validate_company(uuid4(), valid_company_data["id"])
    #
    #     expected_result = CompanySchema(**valid_company_data)
    #     assert result == expected_result
    #
    # async def test_update_company(self, company_service, valid_company_data):
    #     updated_data = {
    #         "name": "Updated Company",
    #         "description": "Updated description",
    #         "visible": False
    #     }
    #     company_service.repository.update_one = AsyncMock(return_value=valid_company_data)
    #     company_service._get_company_or_raise = AsyncMock(return_value=valid_company_data)
    #
    #     update_request = CompanyUpdateRequest(**updated_data)
    #
    #     result = await company_service.update_company(update_request, uuid4(), valid_company_data["id"])
    #
    #     expected_result = CompanySchema(**valid_company_data)
    #     assert result == expected_result
    #
    # async def test_delete_company(self, company_service, valid_company_data):
    #     company_service.repository.delete_company = AsyncMock()
    #     company_service._get_company_or_raise = AsyncMock(return_value=valid_company_data)
    #
    #     result = await company_service.delete_company(valid_company_data["id"], uuid4())
    #
    #     assert result == {"message": "Company deleted", "id": valid_company_data["id"]}
    #     company_service.repository.delete_company.assert_called_once()
=======
import unittest
from unittest.mock import AsyncMock
from uuid import uuid4

from app.schemas.companies import (
    CompanySchema,
)
from app.services.company_service import CompanyService
from app.exept.custom_exceptions import CompanyNotFound


class TestCompanyService(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.session = AsyncMock()
        self.repository = AsyncMock()
        self.company_service = CompanyService(
            session=self.session, repository=self.repository
        )

    async def test_create_company_success(self):
        company_data = {
            "name": "testname",
            "description": "testdescription",
            "visible": False,
        }
        current_user_id = uuid4()
        self.repository.create_company_with_owner.return_value = CompanySchema(
            id=uuid4(),
            name="testname",
            description="testdescription",
            visible=False,
            owner_id=current_user_id,
        )

        company = await self.company_service.create_company(
            company_data, current_user_id
        )
        self.assertEqual(company.name, company_data["name"])
        self.assertEqual(company.description, company_data["description"])

    async def test_get_companies_success(self):
        companies_data = [
            CompanySchema(
                id=uuid4(),
                name="company1",
                email="company1@example.com",
                description="description1",
                visible=True,
                owner_id=uuid4(),
            ),
            CompanySchema(
                id=uuid4(),
                name="company2",
                email="company2@example.com",
                description="description2",
                visible=False,
                owner_id=uuid4(),
            ),
        ]
        self.repository.get_many.return_value = companies_data
        companies = await self.company_service.get_companies(0, 10)

        self.assertEqual(len(companies), 2)
        self.assertEqual(companies[0].name, "company1")
        self.assertEqual(companies[1].name, "company2")

    async def test_get_company_by_id_success(self):
        company_id = uuid4()
        user_id = uuid4()
        self.repository.get_one.return_value = CompanySchema(
            id=company_id,
            name="company",
            email="company1@example.com",
            description="description",
            visible=True,
            owner_id=user_id,
        )

        company = await self.company_service.get_company_by_id(company_id)
        self.assertEqual(company.id, company_id)

    async def test_get_company_by_id_not_found(self):
        company_id = uuid4()
        user_id = uuid4()
        self.repository.get_one.return_value = None

        with self.assertRaises(CompanyNotFound):
            await self.company_service.get_company_by_id(company_id)

    async def test_update_company_success(self):
        company_id = uuid4()
        user_id = uuid4()
        company_data = {"name": "updatedname", "description": "updateddescription"}
        self.repository.get_one.return_value = CompanySchema(
            id=company_id,
            name="company",
            description="description",
            visible=True,
            owner_id=user_id,
        )
        self.repository.update_one.return_value = CompanySchema(
            id=company_id,
            name="updatedname",
            description="updateddescription",
            visible=True,
            owner_id=user_id,
        )

        company = await self.company_service.update_company(
            company_data, user_id, company_id
        )
        self.assertEqual(company.name, company_data["name"])

    async def test_delete_company_success(self):
        company_id = uuid4()
        user_id = uuid4()
        self.repository.get_one.return_value = CompanySchema(
            id=company_id,
            name="company",
            description="description",
            visible=True,
            owner_id=user_id,
        )
        self.repository.delete_one.return_value = CompanySchema(
            id=company_id,
            name="company",
            description="description",
            visible=True,
            owner_id=user_id,
        )
        response = {"message": "Company deleted", "id": company_id}
        company = await self.company_service.delete_company(company_id, user_id)
        self.assertEqual(company, response)
>>>>>>> Stashed changes
