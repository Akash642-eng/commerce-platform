from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from .. import models, schemas
from ..logger import log_event

router = APIRouter(
    prefix="/support",
    tags=["Support"]
)


@router.post("/ticket", response_model=schemas.TicketResponse)
def create_ticket(
    ticket: schemas.TicketCreate,
    db: Session = Depends(get_db)
):
    new_ticket = models.SupportTicket(
        user_id=ticket.user_id,
        subject=ticket.subject,
        description=ticket.description,
        status="OPEN"
    )

    db.add(new_ticket)
    db.commit()
    db.refresh(new_ticket)

    log_event(
        service="support-service",
        trace_id=f"ticket-{new_ticket.id}",
        message="Support ticket created",
        data={
            "ticket_id": new_ticket.id,
            "user_id": ticket.user_id
        }
    )

    return new_ticket


@router.post("/message", response_model=schemas.MessageResponse)
def add_message(
    msg: schemas.MessageCreate,
    db: Session = Depends(get_db)
):
    ticket = db.query(models.SupportTicket).filter(
        models.SupportTicket.id == msg.ticket_id
    ).first()

    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")

    new_msg = models.SupportMessage(**msg.dict())

    db.add(new_msg)
    db.commit()
    db.refresh(new_msg)

    log_event(
        service="support-service",
        trace_id=f"ticket-{msg.ticket_id}",
        message="Support message added",
        data={
            "ticket_id": msg.ticket_id,
            "sender_id": msg.sender_id
        }
    )

    return new_msg


@router.get("/tickets", response_model=list[schemas.TicketResponse])
def get_tickets(db: Session = Depends(get_db)):
    return db.query(models.SupportTicket).all()


@router.get("/ticket/{ticket_id}", response_model=schemas.TicketResponse)
def get_ticket(ticket_id: int, db: Session = Depends(get_db)):
    ticket = db.query(models.SupportTicket).filter(
        models.SupportTicket.id == ticket_id
    ).first()

    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")

    return ticket


@router.put("/ticket/{ticket_id}/status")
def update_ticket_status(
    ticket_id: int,
    status_update: schemas.TicketStatusUpdate,
    db: Session = Depends(get_db)
):
    ticket = db.query(models.SupportTicket).filter(
        models.SupportTicket.id == ticket_id
    ).first()

    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")

    ticket.status = status_update.status

    db.commit()

    log_event(
        service="support-service",
        trace_id=f"ticket-{ticket.id}",
        message="Ticket status updated",
        data={
            "ticket_id": ticket.id,
            "status": ticket.status
        }
    )

    return {
        "message": "Ticket status updated",
        "ticket_id": ticket.id,
        "status": ticket.status
    }


@router.get("/ticket/{ticket_id}/messages",
            response_model=list[schemas.MessageResponse])
def get_ticket_messages(ticket_id: int, db: Session = Depends(get_db)):
    messages = db.query(models.SupportMessage).filter(
        models.SupportMessage.ticket_id == ticket_id
    ).all()

    return messages