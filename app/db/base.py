from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base
import os

DATABASE_URL = os.environ["DATABASE_URL"]

print("DEBUG DATABASE_URL =", repr(DATABASE_URL))

if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL environment variable is not set")

engine = create_engine(DATABASE_URL, pool_pre_ping=True)
Base = declarative_base()
