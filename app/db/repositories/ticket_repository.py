from typing import List, Optional
from sqlalchemy.orm import Session
from uuid import UUID
from app.db.repositories.base import BaseRepository
from app.db.models import Ticket, Message
from app.schemas.ticket import TicketCreate, TicketUpdate
from app.schemas.message import MessageCreate

class TicketRepository(BaseRepository[Ticket, TicketCreate, TicketUpdate]):
    def get_by_user_id(self, db: Session, *, user_id: UUID) -> List[Ticket]:
        return db.query(Ticket).filter(Ticket.user_id == user_id).all()
    
    def add_message(self, db: Session, *, ticket_id: UUID, message: MessageCreate) -> Message:
        db_message = Message(**message.dict(), ticket_id=ticket_id)
        db.add(db_message)
        db.commit()
        db.refresh(db_message)
        return db_message
    
    def get_messages(self, db: Session, *, ticket_id: UUID) -> List[Message]:
        return db.query(Message).filter(Message.ticket_id == ticket_id).order_by(Message.created_at).all()

ticket_repository = TicketRepository(Ticket)