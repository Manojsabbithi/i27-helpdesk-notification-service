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

        subject, plain_body, html_body = build_email(event_type, recipient_name, event.ticket_id)

        # In-app notification
        db.add(Notification(
            user_id=recipient_id,
            ticket_id=event.ticket_id,
            event_type=event_type,
            title=subject,
            message=plain_body,
            is_read=False
        ))

        try:
            send_email(
                to_email=recipient_email,
                subject=subject,
                plain_body=plain_body,
                html_body=html_body
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

def _render_email(name, ticket_id, subject, heading, message, button_text, button_url):
    plain_body = f"""Hello {name},

{heading}

{message}

Ticket ID: {ticket_id}

{button_text}: {button_url}

Regards,
i27 Helpdesk Team
https://i27academy.com
"""

    html_body = f"""<html>
  <body style="margin:0;padding:0;font-family:Inter,system-ui,Arial,sans-serif;background:#eef2ff;color:#0f172a;">
    <table width="100%" cellpadding="0" cellspacing="0" role="presentation">
      <tr>
        <td align="center" style="padding:32px 16px;">
          <table width="600" cellpadding="0" cellspacing="0" style="background:#ffffff;border-radius:24px;overflow:hidden;box-shadow:0 24px 80px rgba(15,23,42,0.08);">
            <tr>
              <td style="padding:36px;">
                <p style="margin:0;font-size:12px;font-weight:700;letter-spacing:0.16em;text-transform:uppercase;color:#6366f1;">i27 Helpdesk</p>
                <h1 style="margin:20px 0 12px;font-size:28px;line-height:1.1;color:#0f172a;">{heading}</h1>
                <p style="margin:0 0 28px;font-size:16px;line-height:1.7;color:#475569;">Hi {name}, {message}</p>
                <table width="100%" cellpadding="0" cellspacing="0" style="border:1px solid #e2e8f0;border-radius:18px;background:#f8fbff;">
                  <tr>
                    <td style="padding:24px;">
                      <p style="margin:0 0 8px;font-size:12px;font-weight:700;text-transform:uppercase;letter-spacing:0.12em;color:#0f172a;">Ticket</p>
                      <p style="margin:0;font-size:20px;font-weight:700;color:#111827;">#{ticket_id}</p>
                    </td>
                  </tr>
                </table>
                <p style="margin:28px 0 0;"><a href="{button_url}" style="display:inline-block;padding:14px 24px;background:#4338ca;color:#ffffff;border-radius:12px;text-decoration:none;font-weight:600;">{button_text}</a></p>
              </td>
            </tr>
            <tr>
              <td style="padding:24px 36px;background:#f8fafc;color:#64748b;font-size:13px;text-align:center;">
                <span style="display:block;">i27 Helpdesk • <a href="https://i27academy.com" style="color:#4338ca;text-decoration:none;">i27academy.com</a></span>
              </td>
            </tr>
          </table>
        </td>
      </tr>
    </table>
  </body>
</html>"""

    return subject, plain_body, html_body


def build_email(event_type, name, ticket_id):
    ticket_url = f"https://i27academy.com/tickets/{ticket_id}"

    if event_type == "TICKET_CREATED":
        return _render_email(
            name=name,
            ticket_id=ticket_id,
            subject=f"[i27 Helpdesk] Ticket Created • #{ticket_id}",
            heading="Your ticket is now live",
            message="Your support request has been received and our team is ready to help.",
            button_text="View Ticket",
            button_url=ticket_url,
        )

    if event_type == "TICKET_ASSIGNED_AGENT":
        return _render_email(
            name=name,
            ticket_id=ticket_id,
            subject=f"[i27 Helpdesk] New ticket assigned • #{ticket_id}",
            heading="A ticket was assigned to you",
            message="A new support ticket requires your attention. Please review the details and respond promptly.",
            button_text="Open Ticket",
            button_url=ticket_url,
        )

    if event_type == "TICKET_ASSIGNED_ADMIN":
        return _render_email(
            name=name,
            ticket_id=ticket_id,
            subject=f"[i27 Helpdesk] Ticket assigned • #{ticket_id}",
            heading="A ticket is awaiting admin review",
            message="A ticket has been assigned and needs administrative oversight.",
            button_text="Review Ticket",
            button_url=ticket_url,
        )

    if event_type == "TICKET_STATUS_CHANGED":
        return _render_email(
            name=name,
            ticket_id=ticket_id,
            subject=f"[i27 Helpdesk] Ticket status updated • #{ticket_id}",
            heading="Your ticket status has changed",
            message="The status of your ticket has been updated. Check the latest progress in the portal.",
            button_text="View Status",
            button_url=ticket_url,
        )

    if event_type == "TICKET_COMMENT_ADDED":
        return _render_email(
            name=name,
            ticket_id=ticket_id,
            subject=f"[i27 Helpdesk] New comment on ticket • #{ticket_id}",
            heading="A new comment was added",
            message="There’s a fresh comment on your ticket. Open the ticket to read the update and reply if needed.",
            button_text="View Comment",
            button_url=ticket_url,
        )

    return _render_email(
        name=name,
        ticket_id=ticket_id,
        subject=f"[i27 Helpdesk] Ticket update • #{ticket_id}",
        heading="Ticket update available",
        message="An update was made to your ticket. Check the portal for details.",
        button_text="View Ticket",
        button_url=ticket_url,
    )
