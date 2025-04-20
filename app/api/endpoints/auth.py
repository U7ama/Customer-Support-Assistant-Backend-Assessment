from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.db.base import get_db
from app.services.auth_service import auth_service
from app.schemas.auth import Token, UserCreate, User

router = APIRouter()

@router.post("/signup", response_model=User)
async def signup(
    user_data: UserCreate,
    db: Session = Depends(get_db)
):
    """
    Create new user
    """
    return await auth_service.create_user(db, user_data)

@router.post("/login", response_model=Token)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """
    OAuth2 compatible token login, get an access token for future requests
    """
    user = await auth_service.authenticate_user(
        db, form_data.username, form_data.password
    )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return await auth_service.create_access_token(user.id)