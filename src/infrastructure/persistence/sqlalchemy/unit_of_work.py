# src/infrastructure/persistence/sqlalchemy/unit_of_work.py
"""Unit of Work Pattern pour la gestion des transactions."""

from typing import Optional

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from src.infrastructure.persistence.sqlalchemy.repositories.colli_repository import (
    SQLAlchemyColliRepository,
)
from src.infrastructure.persistence.sqlalchemy.repositories.user_repository import (
    SQLAlchemyUserRepository,
)


class UnitOfWork:
    """
    Unit of Work Pattern pour la gestion des transactions atomiques.

    Avantages:
    - Transactions atomiques (tout réussit ou tout échoue)
    - Rollback automatique en cas d'erreur
    - Point unique de commit
    - Lazy loading des repositories

    Usage:
        with UnitOfWork(session_factory) as uow:
            user = uow.users.find_by_email_str("test@example.com")
            colli = uow.collis.find_by_id(colli_id)
            colli.approve()
            uow.collis.save(colli)
            uow.commit()
    """

    def __init__(self, session_factory):
        self._session_factory = session_factory
        self._session: Optional[Session] = None

        # Repositories (lazy loaded)
        self._collis: Optional[SQLAlchemyColliRepository] = None
        self._users: Optional[SQLAlchemyUserRepository] = None

    def __enter__(self) -> "UnitOfWork":
        """Démarre une nouvelle transaction."""
        self._session = self._session_factory()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Ferme la transaction (rollback si erreur)."""
        if exc_type:
            self.rollback()
        self._session.close()

    @property
    def collis(self) -> SQLAlchemyColliRepository:
        """Accès au repository Colli (lazy loading)."""
        if self._collis is None:
            self._collis = SQLAlchemyColliRepository(self._session)
        return self._collis

    @property
    def users(self) -> SQLAlchemyUserRepository:
        """Accès au repository User (lazy loading)."""
        if self._users is None:
            self._users = SQLAlchemyUserRepository(self._session)
        return self._users

    def commit(self) -> None:
        """Commit la transaction."""
        try:
            self._session.commit()
        except SQLAlchemyError:
            self.rollback()
            raise

    def rollback(self) -> None:
        """Rollback la transaction."""
        self._session.rollback()

    def flush(self) -> None:
        """Flush les changements en attente (sans commit)."""
        self._session.flush()
