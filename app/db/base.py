from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base
import os

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise RuntimeError(
        "DATABASE_URL environment variable is not set. "
        "Set DATABASE_URL to a valid SQLAlchemy URL, e.g. mysql+pymysql://user:pass@host:port/db"
    )

engine = create_engine(DATABASE_URL, pool_pre_ping=True)
Base = declarative_base()
