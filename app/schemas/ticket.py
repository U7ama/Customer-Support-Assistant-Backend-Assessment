from typing import List, Optional
from uuid import UUID
from datetime import datetime
from pydantic import BaseModel, Field
from app.schemas.message import Message

class TicketBase(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    
class TicketCreate(TicketBase):
    title: str = Field(..., min_length=3, max_length=100)
    description: str = Field(..., min_length=10)
    
class TicketUpdate(TicketBase):
    pass

class TicketInDB(TicketBase):
    id: UUID
    user_id: UUID
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True
        
class Ticket(TicketInDB):
    pass

class TicketWithMessages(Ticket):
    messages: List[Message] = []