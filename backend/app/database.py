"""Configuración de SQLAlchemy, motor SQLite y dependencia de sesión."""

from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, declarative_base, sessionmaker

from app.config import URL_BASE_DATOS

argumentos_conexion = (
    {"check_same_thread": False} if URL_BASE_DATOS.startswith("sqlite") else {}
)

engine = create_engine(
    URL_BASE_DATOS,
    connect_args=argumentos_conexion,
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)

Base = declarative_base()


def get_db() -> Generator[Session, None, None]:
    """Provee una sesión de base de datos por petición y garantiza su cierre."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
