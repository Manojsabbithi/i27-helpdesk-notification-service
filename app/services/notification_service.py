from sqlalchemy.orm import Session
import requests
import os

from app.models.notifications import Notification
from app.models.notification_log import NotificationLog
from app.utils.email_sender import send_email


AUTH_SERVICE_URL = os.environ["AUTH_SERVICE_URL"]
TICKET_SERVICE_URL = os.environ["TICKET_SERVICE_URL"]

if not AUTH_SERVICE_URL:
    raise RuntimeError("AUTH_SERVICE_URL environment variable is not set")
if not TICKET_SERVICE_URL:
    raise RuntimeError("TICKET_SERVICE_URL environment variable is not set")


# =====================================================
# 🧠 Helper → Fetch user details
# =====================================================
def get_user(user_id: int):
    if not user_id:
        return None
    try:
        resp = requests.get(f"{AUTH_SERVICE_URL}/auth/users/{user_id}")
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        print(f"Failed to fetch user {user_id}: {e}")
        return None


# =====================================================
# 🧠 Helper → Fetch ticket details
# =====================================================
def get_ticket(ticket_id: int):
    try:
        resp = requests.get(f"{TICKET_SERVICE_URL}/tickets/{ticket_id}")
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        print(f"Failed to fetch ticket {ticket_id}: {e}")
        return {}


# =====================================================
# 🔔 Core Event Processor
# =====================================================
def process_event(event, db: Session):

    event_type = event.event_type.strip().upper()
    print("Processing event:", event_type)

    recipients = []   # list of dicts → {id, email, name}

    # =====================================================
    # 🎫 TICKET CREATED → STUDENT
    # =====================================================
    if event_type == "TICKET_CREATED":
        user = get_user(event.recipient_id)
        recipients.append(user)

    # =====================================================
    # 🧑‍💼 ASSIGNED → AGENT
    # =====================================================
    elif event_type == "TICKET_ASSIGNED_AGENT":
        user = get_user(event.recipient_id)
        recipients.append(user)

    # =====================================================
    # 👑 ASSIGNED → ADMIN (copy)
    # =====================================================
    elif event_type == "TICKET_ASSIGNED_ADMIN":
        user = get_user(event.recipient_id)
        recipients.append(user)

    # =====================================================
    # 🔄 STATUS CHANGED → STUDENT
    # =====================================================
    elif event_type == "TICKET_STATUS_CHANGED":
        user = get_user(event.recipient_id)
        recipients.append(user)

    # =====================================================
    # 💬 COMMENT ADDED → STUDENT + AGENT + ADMIN
    # =====================================================
    elif event_type == "TICKET_COMMENT_ADDED":

        ticket = get_ticket(event.ticket_id)

        # 🎓 Student
        recipients.append(get_user(ticket.get("createdBy")))

        # 🧑‍💼 Agent (if assigned)
        if ticket.get("assignedTo"):
            recipients.append(get_user(ticket.get("assignedTo")))

        # 👑 Admin (single admin for now – scalable later)
        # Assuming admin ID = 1
        recipients.append(get_user(1))

    else:
        print("Unknown event type:", event_type)
        return {"status": "IGNORED"}

    # =====================================================
    # 📧 Send emails (one by one)
    # =====================================================
    valid_recipients = [u for u in recipients if u is not None]

    for user in valid_recipients:

        recipient_id = user["id"]
        recipient_email = user["email"]
        recipient_name = user.get("fullName", "User")

        subject, body = build_email(event_type, recipient_name, event.ticket_id)

        # In-app notification
        db.add(Notification(
            user_id=recipient_id,
            ticket_id=event.ticket_id,
            event_type=event_type,
            title=subject,
            message=body,
            is_read=False
        ))

        try:
            send_email(
                to_email=recipient_email,
                subject=subject,
                body=body
            )
            status = "SENT"
            print(f"Email sent to {recipient_email}")

        except Exception as e:
            print("Email send failed:", e)
            status = "FAILED"

        db.add(NotificationLog(
            ticket_id=event.ticket_id,
            recipient=recipient_email,
            status=status
        ))

    db.commit()
    return {"status": "DONE"}


# =====================================================
# ✉️ Email Templates
# =====================================================
def build_email(event_type, name, ticket_id):

    if event_type == "TICKET_CREATED":
        return (
            "[i27 Helpdesk] Ticket Created Successfully",
            f"""Hello {name},

🎫 Your support ticket has been created successfully.

Ticket ID: {ticket_id}

—  
Regards,  
i27 Helpdesk Team
https://i27academy.com
"""
        )

    if event_type == "TICKET_ASSIGNED_AGENT":
        return (
            "[i27 Helpdesk] Ticket Assigned to You",
            f"""Hello {name},

🧑‍💼 A support ticket has been assigned to you.

Ticket ID: {ticket_id}

Please review and take action.

—  
Regards,  
i27 Helpdesk Team
"""
        )

    if event_type == "TICKET_ASSIGNED_ADMIN":
        return (
            "[i27 Helpdesk] Ticket Assigned",
            f"""Hello {name},

✅ A ticket has been assigned successfully.

Ticket ID: {ticket_id}

—  
Regards,  
i27 Helpdesk Team
"""
        )

    if event_type == "TICKET_STATUS_CHANGED":
        return (
            "[i27 Helpdesk] Ticket Status Updated",
            f"""Hello {name},

📢 Your ticket status has been updated.

Ticket ID: {ticket_id}

—  
Regards,  
i27 Helpdesk Team
"""
        )

    if event_type == "TICKET_COMMENT_ADDED":
        return (
            "[i27 Helpdesk] New Comment on Ticket",
            f"""Hello {name},

💬 A new comment was added on Ticket ID: {ticket_id}

Please log in to view and respond.

—  
Regards,  
i27 Helpdesk Team
"""
        )

    return "[i27 Helpdesk]", "You have a new notification."
