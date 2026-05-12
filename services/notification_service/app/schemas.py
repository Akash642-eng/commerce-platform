from pydantic import BaseModel

from datetime import datetime


class NotificationCreate(BaseModel):

    user_id: str

    message: str

    type: str


class NotificationResponse(BaseModel):

    id: int

    user_id: str

    message: str

    type: str

    is_read: bool

    created_at: datetime

    class Config:

        from_attributes = True