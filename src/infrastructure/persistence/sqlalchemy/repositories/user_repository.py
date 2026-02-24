# src/infrastructure/persistence/sqlalchemy/repositories/user_repository.py
"""Implémentation SQLAlchemy du repository User."""

from typing import List, Optional
from uuid import UUID

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from src.application.exceptions import PersistenceException
from src.domain.identity.entities.user import User
from src.domain.identity.repositories.user_repository import IUserRepository
from src.domain.identity.value_objects.email import Email
from src.infrastructure.persistence.sqlalchemy.mappers.user_mapper import UserMapper
from src.infrastructure.persistence.sqlalchemy.models.user_model import UserModel


class SQLAlchemyUserRepository(IUserRepository):
    """
    Implémentation SQLAlchemy du repository User.

    Utilise le UserMapper pour la conversion Entity ↔ Model.
    """

    def __init__(self, session: Session):
        self._session = session

    def save(self, user: User) -> User:
        """Persiste un utilisateur."""
        try:
            existing = self._session.query(UserModel).filter_by(id=user.id).first()

            if existing:
                # Update
                UserMapper.update_model(existing, user)
                self._session.flush()
                return user
            else:
                # Create
                model = UserMapper.to_model(user)
                self._session.add(model)
                self._session.flush()
                return user

        except IntegrityError as e:
            self._session.rollback()
            raise PersistenceException(f"Erreur d'intégrité: {e}")

    def find_by_id(self, user_id: UUID) -> Optional[User]:
        """Récupère un utilisateur par ID."""
        model = self._session.query(UserModel).filter_by(id=user_id).first()
        if model:
            return UserMapper.to_entity(model)
        return None

    def find_by_email(self, email: Email) -> Optional[User]:
        """Récupère un utilisateur par Email."""
        return self.find_by_email_str(str(email))

    def find_by_email_str(self, email: str) -> Optional[User]:
        """Récupère un utilisateur par email (string)."""
        model = self._session.query(UserModel).filter(
            UserModel.email.ilike(email)
        ).first()
        if model:
            return UserMapper.to_entity(model)
        return None

    def email_exists(self, email: str) -> bool:
        """Vérifie si un email existe."""
        return self._session.query(
            self._session.query(UserModel).filter(
                UserModel.email.ilike(email)
            ).exists()
        ).scalar()

    def find_all(self, page: int = 1, per_page: int = 20) -> List[User]:
        """Récupère tous les utilisateurs avec pagination."""
        offset = (page - 1) * per_page
        models = self._session.query(UserModel)\
            .order_by(UserModel.created_at.desc())\
            .offset(offset)\
            .limit(per_page)\
            .all()
        return [UserMapper.to_entity(m) for m in models]

    def delete(self, user: User) -> bool:
        """Supprime un utilisateur."""
        model = self._session.query(UserModel).filter_by(id=user.id).first()
        if model:
            self._session.delete(model)
            self._session.flush()
            return True
        return False

    def count(self) -> int:
        """Compte les utilisateurs."""
        return self._session.query(UserModel).count()
