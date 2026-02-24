# src/infrastructure/persistence/sqlalchemy/database.py
"""Configuration de la base de données SQLAlchemy."""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session, declarative_base
from contextlib import contextmanager
from typing import Generator

from src.infrastructure.config.settings import get_settings


# Base pour tous les modèles SQLAlchemy
Base = declarative_base()


def create_engine_from_config():
    """Crée l'engine SQLAlchemy depuis la configuration."""
    settings = get_settings()
    
    # Configuration selon le type de base
    if settings.DATABASE_URL.startswith('sqlite'):
        engine = create_engine(
            settings.DATABASE_URL,
            connect_args={"check_same_thread": False},
            echo=settings.DEBUG
        )
    else:
        # PostgreSQL ou autre
        engine = create_engine(
            settings.DATABASE_URL,
            pool_size=5,
            max_overflow=10,
            pool_pre_ping=True,
            echo=settings.DEBUG
        )
    
    return engine


def create_session_factory(engine=None):
    """Crée une factory de sessions."""
    if engine is None:
        engine = create_engine_from_config()
    
    session_factory = sessionmaker(
        bind=engine,
        autocommit=False,
        autoflush=False
    )
    
    return session_factory


def get_scoped_session(session_factory=None):
    """Crée une session scopée (thread-safe)."""
    if session_factory is None:
        session_factory = create_session_factory()
    
    return scoped_session(session_factory)


@contextmanager
def get_db_session() -> Generator:
    """
    Context manager pour obtenir une session de base de données.
    
    Usage:
        with get_db_session() as session:
            result = session.query(Model).all()
    """
    Session = create_session_factory()
    session = Session()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def init_db(engine=None):
    """Initialise la base de données (crée les tables)."""
    if engine is None:
        engine = create_engine_from_config()
    
    # Import des modèles pour que SQLAlchemy les détecte
    from src.infrastructure.persistence.sqlalchemy.models import colli_model, user_model, letter_model, comment_model
    
    Base.metadata.create_all(bind=engine)
    return engine
