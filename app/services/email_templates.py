def ticket_event_email(event_type: str, ticket_id: int, role: str):
    subject = f"[i27 Helpdesk] Ticket Update – #{ticket_id}"

    if event_type == "TICKET_CREATED":
        title = "🎫 Ticket Created Successfully"
        message = (
            f"Your support ticket has been created successfully.\n\n"
            f"Ticket ID: {ticket_id}\n"
            f"Status: OPEN\n\n"
            f"Our support team will get back to you shortly."
        )

    elif event_type == "TICKET_ASSIGNED":
        title = "🧑‍💼 Ticket Assigned to You"
        message = (
            f"A support ticket has been assigned to you.\n\n"
            f"Ticket ID: {ticket_id}\n"
            f"Please review and take action."
        )

    elif event_type == "STATUS_CHANGED":
        title = "🔄 Ticket Status Updated"
        message = (
            f"The status of your ticket has been updated.\n\n"
            f"Ticket ID: {ticket_id}\n"
            f"Please check the dashboard for details."
        )

    else:
        title = "📢 Ticket Notification"
        message = f"An update occurred on Ticket ID: {ticket_id}"

    body = f"""
Hello,

{title}

{message}

—
Regards,
i27 Helpdesk Team
https://i27academy.com
"""

    return subject, body
