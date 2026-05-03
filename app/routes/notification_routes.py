from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.services.notification_schema import NotificationEvent
from app.services.notification_service import process_event

router = APIRouter(prefix="/notifications", tags=["Notifications"])


@router.post("/event")
def notify(event: NotificationEvent, db: Session = Depends(get_db)):
    print("🔥 EVENT RECEIVED:", event.dict())
    return process_event(event, db)
