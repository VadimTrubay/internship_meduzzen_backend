from app.repository.base_repository import BaseRepository
from app.models.company_model import Company


class CompanyRepository(BaseRepository):
    def __init__(self, session):
        super().__init__(session=session, model=Company)
