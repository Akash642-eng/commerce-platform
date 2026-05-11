from pydantic import BaseModel

class NotificationCreate(BaseModel):
    user_id: str
    message: str
    type: str