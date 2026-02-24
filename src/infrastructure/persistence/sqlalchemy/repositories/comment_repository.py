# src/infrastructure/persistence/sqlalchemy/repositories/comment_repository.py
"""Implémentation SQLAlchemy du repository Comment."""

from typing import List, Optional
from uuid import UUID

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from src.application.exceptions import PersistenceException
from src.domain.collaboration.entities.comment import Comment
from src.domain.collaboration.repositories.comment_repository import ICommentRepository
from src.infrastructure.persistence.sqlalchemy.mappers.comment_mapper import CommentMapper
from src.infrastructure.persistence.sqlalchemy.models.comment_model import CommentModel


class SQLAlchemyCommentRepository(ICommentRepository):
    """
    Implémentation SQLAlchemy du repository Comment.
    """

    def __init__(self, session: Session):
        self._session = session

    def save(self, comment: Comment) -> Comment:
        """Persiste un commentaire."""
        try:
            existing = self._session.query(CommentModel).filter_by(id=comment.id).first()

            if existing:
                CommentMapper.update_model(existing, comment)
                self._session.flush()
                return comment
            else:
                model = CommentMapper.to_model(comment)
                self._session.add(model)
                self._session.flush()
                return comment

        except IntegrityError as e:
            self._session.rollback()
            raise PersistenceException(f"Erreur d'intégrité: {e}")

    def find_by_id(self, comment_id: UUID) -> Optional[Comment]:
        """Récupère un commentaire par ID."""
        model = self._session.query(CommentModel).filter_by(id=comment_id).first()
        if model:
            return CommentMapper.to_entity(model)
        return None

    def find_by_letter(self, letter_id: UUID, page: int = 1, per_page: int = 50) -> List[Comment]:
        """Récupère les commentaires d'une lettre avec pagination."""
        offset = (page - 1) * per_page
        models = self._session.query(CommentModel)\
            .filter_by(letter_id=letter_id)\
            .order_by(CommentModel.created_at.asc())\
            .offset(offset)\
            .limit(per_page)\
            .all()
        return [CommentMapper.to_entity(m) for m in models]

    def find_by_sender(self, sender_id: UUID) -> List[Comment]:
        """Récupère les commentaires d'un utilisateur."""
        models = self._session.query(CommentModel)\
            .filter_by(sender_id=sender_id)\
            .order_by(CommentModel.created_at.desc())\
            .all()
        return [CommentMapper.to_entity(m) for m in models]

    def delete(self, comment: Comment) -> bool:
        """Supprime un commentaire."""
        model = self._session.query(CommentModel).filter_by(id=comment.id).first()
        if model:
            self._session.delete(model)
            self._session.flush()
            return True
        return False

    def count_by_letter(self, letter_id: UUID) -> int:
        """Compte les commentaires d'une lettre."""
        return self._session.query(CommentModel).filter_by(letter_id=letter_id).count()
