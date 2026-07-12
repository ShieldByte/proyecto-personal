from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Base de datos SQLite local (archivo mes.db en la raíz del backend)
DATABASE_URL = "sqlite:///./mes.db"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}  # Necesario para SQLite con FastAPI
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    """Dependencia que provee una sesión de BD por request."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()