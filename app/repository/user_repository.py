from app.repository.base_repository import BaseRepository
from app.models.user_model import User


class UserRepository(BaseRepository):
    def __init__(self, session):
        super().__init__(session=session, model=User)
