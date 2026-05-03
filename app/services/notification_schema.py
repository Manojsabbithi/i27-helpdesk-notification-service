from pydantic import BaseModel
from typing import Optional

class NotificationEvent(BaseModel):
    event_type: str
    ticket_id: int
    actor_id: int
    actor_role: str
    recipient_id: Optional[int] = None   # ✅ THIS FIXES 422
