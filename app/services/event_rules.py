EVENT_RULES = {

    "TICKET_CREATED": {
        "title": "New Support Ticket",
        "message": "A new ticket has been created by a student.",
        "roles": ["ADMIN"],          # 👈 NOT STUDENT
        "channels": ["EMAIL"]
    },

    "TICKET_ASSIGNED": {
        "title": "Ticket Assigned",
        "message": "A ticket has been assigned to you.",
        "roles": ["AGENT"],
        "channels": ["EMAIL"]
    },

    "COMMENT_BY_STUDENT": {
        "title": "New Student Comment",
        "message": "A student added a new comment.",
        "roles": ["AGENT"],
        "channels": []
    },

    "COMMENT_BY_AGENT": {
        "title": "New Agent Reply",
        "message": "Support agent replied to your ticket.",
        "roles": ["STUDENT"],
        "channels": []
    }
}
