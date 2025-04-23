from typing import List, Optional
from uuid import UUID
from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.base import get_db
from app.db.repositories.ticket_repository import ticket_repository
from app.schemas.ticket import Ticket, TicketCreate, TicketUpdate, TicketWithMessages
from app.schemas.message import Message, MessageCreate
from app.services.auth_service import auth_service

class TicketService:
    @staticmethod
    async def create_ticket(
        db: Session,
        ticket_in: TicketCreate,
        current_user: UUID
    ) -> Ticket:
        """Create a new support ticket"""
        # Extract data from TicketCreate
        ticket_data = ticket_in.dict()
        
        # Create the ticket using the repository (pass user_id directly)
        return ticket_repository.create(db, obj_in={**ticket_data, "user_id": current_user})
    
    @staticmethod
    async def get_user_tickets(
        db: Session,
        current_user: UUID,
        skip: int = 0,
        limit: int = 100
    ) -> List[Ticket]:
        """Get all tickets for a user"""
        return ticket_repository.get_by_user_id(db, user_id=current_user)
    
    @staticmethod
    async def get_ticket(
        db: Session,
        ticket_id: UUID,
        current_user: UUID
    ) -> Optional[TicketWithMessages]:
        """Get a specific ticket with its messages"""
        ticket = ticket_repository.get(db, id=ticket_id)
        
        if not ticket:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Ticket not found"
            )
        
        # Check if user has access to this ticket
        if str(ticket.user_id) != str(current_user) and current_user.role != "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enough permissions"
            )
        
        messages = ticket_repository.get_messages(db, ticket_id=ticket_id)
        
        return TicketWithMessages(
            **ticket.__dict__,
            messages=messages
        )
    
    @staticmethod
    async def add_message(
        db: Session,
        ticket_id: UUID,
        message: MessageCreate,
        current_user: UUID
    ) -> Message:
        """Add a message to a ticket"""
        ticket = ticket_repository.get(db, id=ticket_id)
        
        if not ticket:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Ticket not found"
            )
        
        # Check if user has access to this ticket
        if str(ticket.user_id) != str(current_user) and current_user.role != "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enough permissions"
            )
        
        return ticket_repository.add_message(db, ticket_id=ticket_id, message=message)

ticket_service = TicketService()