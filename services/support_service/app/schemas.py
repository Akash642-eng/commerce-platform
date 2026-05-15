from datetime import datetime

from pydantic import BaseModel


class TicketCreate(BaseModel):

    user_id: str

    subject: str

    description: str


class TicketStatusUpdate(BaseModel):

    status: str


class MessageCreate(BaseModel):

    ticket_id: int

    sender_id: str

    message: str


class TicketResponse(BaseModel):

    id: int

    user_id: str

    subject: str

    description: str

    status: str

    created_at: datetime

    class Config:

        from_attributes = True


class MessageResponse(BaseModel):

    id: int

    ticket_id: int

    sender_id: str

    message: str

    created_at: datetime

    class Config:

        from_attributes = True
