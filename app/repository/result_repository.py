from app.models.result_model import Result
from app.repository.base_repository import BaseRepository


class ResultRepository(BaseRepository):
    def __init__(self, session):
        super().__init__(session=session, model=Result)
