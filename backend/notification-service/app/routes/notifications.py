from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from fastapi import status

from sqlalchemy.orm import Session

from ..database import get_db
from .. import models
from .. import schemas

from ..producer import publish_event
from ..metrics import notifications_created

router = APIRouter(
    prefix="/notifications",
    tags=["Notifications"]
)

# --------------------------------
# CREATE NOTIFICATION
# --------------------------------
@router.post(
    "/",
    response_model=schemas.NotificationCreate
)
def create_notification(
    notification: schemas.NotificationCreate,
    db: Session = Depends(get_db)
):

    new_notification = models.Notification(
        user_id=notification.user_id,
        message=notification.message,
        type=notification.type
    )

    db.add(new_notification)
    db.commit()
    db.refresh(new_notification)

    notifications_created.inc()

    publish_event(
        "notifications",
        {
            "user_id": notification.user_id,
            "message": notification.message,
            "type": notification.type
        }
    )

    return new_notification


# --------------------------------
# GET USER NOTIFICATIONS
# --------------------------------
@router.get(
    "/{user_id}"
)
def get_notifications(
    user_id: str,
    db: Session = Depends(get_db)
):

    notifications = db.query(
        models.Notification
    ).filter(
        models.Notification.user_id == user_id
    ).all()

    return notifications


# --------------------------------
# MARK AS READ
# --------------------------------
@router.put(
    "/{notification_id}/read"
)
def mark_as_read(
    notification_id: int,
    db: Session = Depends(get_db)
):

    notification = db.query(
        models.Notification
    ).filter(
        models.Notification.id == notification_id
    ).first()

    if not notification:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notification not found"
        )

    notification.is_read = True

    db.commit()

    return {
        "message": "Notification marked as read"
    }