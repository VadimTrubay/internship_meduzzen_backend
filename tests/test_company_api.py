import unittest
from unittest.mock import AsyncMock
from uuid import uuid4

from app.schemas.companies import (
    CompanySchema,
)
from app.services.company_service import CompanyService
from app.exept.custom_exceptions import CompanyNotFound, NotOwner


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
        mock_company = CompanySchema(
            id=uuid4(),
            name="testname",
            description="testdescription",
            visible=False,
        )
        self.repository.create_company_with_owner.return_value = mock_company

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
                description="description1",
                visible=True,
            ),
            CompanySchema(
                id=uuid4(),
                name="company2",
                description="description2",
                visible=False,
            ),
        ]
        self.repository.get_many.return_value = companies_data
        self.repository.get_count.return_value = 2
        user_id = uuid4()

        companies = await self.company_service.get_companies(0, 10, user_id)
        self.assertEqual(companies.total_count, 2)

    async def test_get_company_by_id_success(self):
        company_id = uuid4()
        user_id = uuid4()
        self.repository.get_one.return_value = CompanySchema(
            id=company_id,
            name="company",
            description="description",
            visible=True,
        )

        company = await self.company_service.get_company_by_id(company_id, user_id)
        self.assertEqual(company.id, company_id)

    async def test_get_company_by_id_not_found(self):
        company_id = uuid4()
        user_id = uuid4()
        self.repository.get_one.return_value = None

        with self.assertRaises(CompanyNotFound):
            await self.company_service.get_company_by_id(company_id, user_id)

    async def test_update_company_success(self):
        company_id = uuid4()
        user_id = uuid4()
        company_data = {"name": "updatedname", "description": "updateddescription"}
        self.repository.get_one.return_value = CompanySchema(
            id=company_id,
            name="company",
            description="description",
            visible=True,
        )
        self.repository.update_one.return_value = CompanySchema(
            id=company_id,
            name="updatedname",
            description="updateddescription",
            visible=True,
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
        )

        response = await self.company_service.delete_company(company_id, user_id)
        self.assertEqual(response, {"message": "Company deleted"})
