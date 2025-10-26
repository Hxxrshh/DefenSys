from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
import os

# Use DATABASE_URL environment variable when running in containers; fall back to local default for dev
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    # Temporarily using SQLite for testing - switch to PostgreSQL for production
    # "postgresql://defensys_user:defensys_password@localhost:5432/defensys_db"
    "sqlite:///./defensys.db"
)

# Create engine with the configured URL
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
