import uuid
from typing import List, Optional

from pydantic import BaseModel, ConfigDict


class BaseCompanySchema(BaseModel):
    id: uuid.UUID
    name: str
    description: str
    visible: bool

    model_config = ConfigDict(from_attributes=True)


class CompanySchema(BaseCompanySchema):
    owner_id: uuid.UUID


class CompanyCreateRequest(BaseModel):
    name: str
    description: str
    visible: Optional[bool] = True


class CompanyUpdateRequest(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    visible: Optional[bool] = None


class CompanyDetailResponse(CompanySchema):
    owner_id: uuid.UUID

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": "123r4567-e89b-12dt-a456-426614174567",
                "name": "Company name",
                "description": "Description company",
                "visible": True,
                "owner_id": "123e4567-e89b-12d3-a456-426614174000",
            }
        },
    )


class CompaniesListResponse(BaseModel):
    companies: List[CompanySchema]
    total_count: int

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "companies": [
                    {
                        "id": "123e4567-e89b-12d3-a456-426614174000",
                        "name": "Company name",
                        "description": "Description company",
                        "visible": True,
                        "owner_id": "123e4567-e89b-12d3-a456-426614174000",
                    },
                    {
                        "id": "223e4567-e89b-12d3-a456-426614174001",
                        "name": "Company name",
                        "description": "Description company",
                        "visible": False,
                        "owner_id": "123e4567-e89b-12d3-a456-426614174001",
                    },
                ],
                "total_count": 0,
            }
        },
        strict=True,
    )
