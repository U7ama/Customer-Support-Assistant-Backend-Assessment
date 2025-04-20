from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_active_user, get_current_admin_user
from app.db.base import get_db
from app.db.repositories.ticket_repository import ticket_repository
from app.services.ticket_service import ticket_service
from app.services.ai_service import ai_service
from app.schemas.auth import User
from app.schemas.ticket import Ticket, TicketCreate, TicketUpdate, TicketWithMessages
from app.schemas.message import Message, MessageCreate

router = APIRouter()

@router.get("/", response_model=List[Ticket])
async def get_tickets(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get all tickets for the current user
    """
    return await ticket_service.get_user_tickets(
        db, current_user.id, skip=skip, limit=limit
    )

@router.post("/", response_model=Ticket)
async def create_ticket(
    ticket_in: TicketCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Create a new ticket
    """
    return await ticket_service.create_ticket(db, ticket_in, current_user.id)

@router.get("/{ticket_id}", response_model=TicketWithMessages)
async def get_ticket(
    ticket_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get a specific ticket with messages
    """
    return await ticket_service.get_ticket(db, ticket_id, current_user.id)

@router.post("/{ticket_id}/messages", response_model=Message)
async def add_message(
    ticket_id: UUID,
    message: MessageCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Add a message to a ticket
    """
    return await ticket_service.add_message(db, ticket_id, message, current_user.id)

@router.get("/{ticket_id}/ai-response")
async def get_ai_response(
    ticket_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Stream an AI response for a ticket using Server-Sent Events
    """
    ticket = ticket_repository.get(db, id=ticket_id)
    if not ticket:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ticket not found"
        )
    
    # Check if user has access to this ticket
    if str(ticket.user_id) != str(current_user.id) and current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    messages = ticket_repository.get_messages(db, ticket_id=ticket_id)
    
    async def event_generator():
        async for chunk in ai_service.stream_response(ticket, messages):
            yield f"data: {chunk}\n\n"
        
        # Save the complete response to the database after streaming
        complete_response = await ai_service.generate_response(ticket, messages)
        ai_message = MessageCreate(content=complete_response, is_ai=True)
        ticket_repository.add_message(db, ticket_id=ticket_id, message=ai_message)
        
        yield "data: [DONE]\n\n"
    
    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream"
    )