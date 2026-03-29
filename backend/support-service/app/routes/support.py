from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ..database import get_db
from .. import models, schemas

router = APIRouter(prefix="/support", tags=["Support"])

@router.post("/ticket")
def create_ticket(ticket: schemas.TicketCreate, db: Session = Depends(get_db)):
    new_ticket = models.SupportTicket(
        user_id=ticket.user_id,
        subject=ticket.subject,
        description=ticket.description,
        status="OPEN"
    )
    db.add(new_ticket)
    db.commit()
    db.refresh(new_ticket)
    return new_ticket


@router.post("/message")
def add_message(msg: schemas.MessageCreate, db: Session = Depends(get_db)):
    new_msg = models.SupportMessage(**msg.dict())
    db.add(new_msg)
    db.commit()
    db.refresh(new_msg)
    return new_msg


@router.get("/tickets")
def get_tickets(db: Session = Depends(get_db)):
    return db.query(models.SupportTicket).all()