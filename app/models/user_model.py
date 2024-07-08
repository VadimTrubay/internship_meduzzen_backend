from sqlalchemy import Column, String, Boolean
from sqlalchemy.orm import validates
from bcrypt import hashpw, gensalt

from app.models.base_model import BaseModel


class User(BaseModel):
    __tablename__ = "users"

    username = Column(String(50), unique=True, nullable=False)
    email = Column(String(50), unique=True, nullable=False)
    hashed_password = Column(String)
    is_admin = Column(Boolean, nullable=False, default=False)

    @validates("hashed_password")
    def validate_hashed_password(self, key, hashed_password):
        return hashpw(hashed_password.encode("utf-8"), gensalt()).decode("utf-8")

    def set_password(self, password):
        self.hashed_password = hashpw(password.encode("utf-8"), gensalt()).decode(
            "utf-8"
        )
