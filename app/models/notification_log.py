from sqlalchemy import Column, BigInteger, String, Enum, TIMESTAMP
from sqlalchemy.sql import func
from app.db.base import Base


class NotificationLog(Base):
    __tablename__ = "notification_log"

    id = Column(BigInteger, primary_key=True, index=True)
    ticket_id = Column(BigInteger, nullable=True)
    notification_type = Column(Enum("EMAIL"), nullable=True)
    recipient = Column(String(255), nullable=True)
    status = Column(Enum("SENT", "FAILED"), nullable=True)
    sent_at = Column(TIMESTAMP, server_default=func.now())
