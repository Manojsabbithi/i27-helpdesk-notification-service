from pydantic import BaseModel

class NotificationEvent(BaseModel):
    event_type: str
    ticket_id: int
    actor_id: int
    recipient_email: str
