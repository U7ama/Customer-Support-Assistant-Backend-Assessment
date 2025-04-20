from typing import Optional
from uuid import UUID
from datetime import datetime
from pydantic import BaseModel, Field

class MessageBase(BaseModel):
    content: Optional[str] = None
    is_ai: Optional[bool] = False
    
class MessageCreate(MessageBase):
    content: str = Field(..., min_length=1)
    is_ai: bool = False
    
class MessageInDB(MessageBase):
    id: UUID
    ticket_id: UUID
    created_at: datetime
    
    class Config:
        from_attributes = True
        
class Message(MessageInDB):
    pass