from typing import Optional
from sqlalchemy.orm import Session
from app.db.repositories.base import BaseRepository
from app.db.models import User
from app.schemas.auth import UserCreate, UserUpdate

class UserRepository(BaseRepository[User, UserCreate, UserUpdate]):
    def get_by_email(self, db: Session, *, email: str) -> Optional[User]:
        return db.query(User).filter(User.email == email).first()

user_repository = UserRepository(User)