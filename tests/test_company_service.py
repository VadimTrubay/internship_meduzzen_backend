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
