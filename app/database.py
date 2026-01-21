"""
Управление подключением к базе данных
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from contextlib import contextmanager
from typing import Generator
from config import settings
from app.models import Base

# Создание engine с базовыми настройками
engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,  # Проверка соединения перед использованием
    echo=False  # Логирование SQL запросов
)

# Session factory
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

def get_db() -> Generator[Session, None, None]:
    """
    Dependency для получения сессии БД в FastAPI endpoints
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@contextmanager
def get_db_context():
    """
    Context manager для использования вне FastAPI
    """
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()

def init_db():
    """Создание всех таблиц"""
    Base.metadata.create_all(bind=engine)

def drop_db():
    """Удаление всех таблиц"""
    Base.metadata.drop_all(bind=engine)
