from pydantic import BaseModel

class TicketCreate(BaseModel):
    user_id: str
    subject: str
    description: str


class MessageCreate(BaseModel):
    ticket_id: int
    sender_id: str
    message: str