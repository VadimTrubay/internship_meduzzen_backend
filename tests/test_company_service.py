import pytest
from unittest.mock import AsyncMock
from uuid import uuid4

from app.schemas.companies import CompanySchema, CompanyResponseSchema
from app.schemas.users import UserSchema
from app.services.company_service import CompanyService
from app.exept.custom_exceptions import CompanyNotFound


@pytest.fixture
def company_service():
    session = AsyncMock()
    repository = AsyncMock()
    return CompanyService(session=session, repository=repository)


@pytest.mark.asyncio
async def test_create_company_success(company_service):
    company_data = {
        "name": "testname",
        "description": "testdescription",
        "visible": False,
    }
    current_user_id = uuid4()
    company_service.repository.create_company_with_owner.return_value = CompanySchema(
        id=uuid4(),
        name="testname",
        description="testdescription",
        visible=False,
        owner_id=current_user_id,
    )

    company = await company_service.create_company(company_data, current_user_id)
    assert company.name == company_data["name"]
    assert company.description == company_data["description"]


@pytest.mark.asyncio
async def test_get_companies_success(company_service):
    user_id = uuid4()
    current_user = UserSchema(
        id=user_id,
        email="testuser@example.com",
        username="testuser",
        password="testpassword",
    )
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
    company_service.repository.get_many.return_value = companies_data
    companies = await company_service.get_companies(0, 10, current_user)

    assert len(companies) == 2
    assert companies[0].name == "company1"
    assert companies[1].name == "company2"


@pytest.mark.asyncio
async def test_get_company_by_id_success(company_service):
    company_id = uuid4()
    user_id = uuid4()

    current_user = UserSchema(
        id=user_id,
        email="testuser@example.com",
        username="testuser",
        password="testpassword",
    )
    company_service.repository.get_one.return_value = CompanySchema(
        id=company_id,
        name="company",
        email="company1@example.com",
        description="description",
        visible=True,
        owner_id=user_id,
    )

    company = await company_service.get_company_by_id(company_id, current_user)
    assert company.id == company_id


@pytest.mark.asyncio
async def test_get_company_by_id_not_found(company_service):
    company_id = uuid4()
    user_id = uuid4()
    current_user = UserSchema(
        id=user_id,
        email="testuser@example.com",
        username="testuser",
        password="testpassword",
    )
    company_service.repository.get_one.return_value = None

    with pytest.raises(CompanyNotFound):
        await company_service.get_company_by_id(company_id, current_user)


@pytest.mark.asyncio
async def test_update_company_success(company_service):
    company_id = uuid4()
    user_id = uuid4()
    company_data = {"name": "updatedname", "description": "updateddescription"}
    company_service.repository.get_one.return_value = CompanySchema(
        id=company_id,
        name="company",
        description="description",
        visible=True,
        owner_id=user_id,
    )
    company_service.repository.update_one.return_value = CompanySchema(
        id=company_id,
        name="updatedname",
        description="updateddescription",
        visible=True,
        owner_id=user_id,
    )

    company = await company_service.update_company(company_data, user_id, company_id)
    assert company.name == company_data["name"]


@pytest.mark.asyncio
async def test_delete_company_success(company_service):
    company_id = uuid4()
    user_id = uuid4()
    company_service.repository.get_one.return_value = CompanySchema(
        id=company_id,
        name="company",
        description="description",
        visible=True,
        owner_id=user_id,
    )
    company_service.repository.delete_one.return_value = CompanySchema(
        id=company_id,
        name="company",
        description="description",
        visible=True,
        owner_id=user_id,
    )
    response = CompanyResponseSchema(
        id=company_id,
        name="company",
        description="description",
    )
    company = await company_service.delete_company(company_id, user_id)
    assert company == response
