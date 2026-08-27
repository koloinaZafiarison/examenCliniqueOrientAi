from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
# from backend.config import settings

# Use psycopg (v3) driver instead of psycopg2 to avoid
# UnicodeDecodeError with libpq 18.x on Windows
SQLALCHEMY_DATABASE_URL = "postgresql://postgres:Dovahkiin150@localhost:5432/OrientAi"

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    """Dependency that provides a database session per request."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Create all tables defined in the models."""
    Base.metadata.create_all(bind=engine)

