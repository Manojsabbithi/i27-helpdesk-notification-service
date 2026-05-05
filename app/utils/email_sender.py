import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


def send_email(to_email: str, subject: str, plain_body: str, html_body: str | None = None):

    # 🔥 READ ENV VARS AT RUNTIME (NOT AT IMPORT)
    SMTP_HOST = os.environ["SMTP_HOST"]
    SMTP_PORT = int(os.environ["SMTP_PORT"])
    SMTP_USER = os.environ["SMTP_USER"]
    SMTP_PASSWORD = os.environ["SMTP_PASSWORD"]

    if not SMTP_HOST or not SMTP_USER or not SMTP_PASSWORD:
        raise RuntimeError("SMTP configuration missing")

    msg = MIMEMultipart("alternative")
    msg["From"] = SMTP_USER
    msg["To"] = to_email
    msg["Subject"] = subject
    msg.attach(MIMEText(plain_body, "plain"))

    if html_body:
        msg.attach(MIMEText(html_body, "html"))

    server = smtplib.SMTP(SMTP_HOST, SMTP_PORT)
    try:
        server.ehlo()
        server.starttls()
        server.ehlo()
        server.login(SMTP_USER, SMTP_PASSWORD)
        server.send_message(msg)
        print(f"📧 Email sent to {to_email}")
    finally:
        server.quit()
