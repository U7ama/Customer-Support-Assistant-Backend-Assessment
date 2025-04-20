from typing import Optional
from uuid import UUID
from pydantic import BaseModel, EmailStr, Field

class UserBase(BaseModel):
    email: Optional[EmailStr] = None
    
class UserCreate(UserBase):
    email: EmailStr
    password: str = Field(..., min_length=8)
    
class UserUpdate(UserBase):
    password: Optional[str] = Field(None, min_length=8)
    
class UserInDB(UserBase):
    id: UUID
    role: str
    is_active: bool
    
    class Config:
        from_attributes = True
        
class User(UserInDB):
    pass

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    
class TokenPayload(BaseModel):
    sub: Optional[str] = None