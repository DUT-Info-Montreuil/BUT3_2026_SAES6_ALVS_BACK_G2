# src/infrastructure/persistence/sqlalchemy/repositories/letter_repository.py
"""Implémentation SQLAlchemy du repository Letter."""

from typing import Optional, List
from uuid import UUID

from sqlalchemy.orm import Session, joinedload
from sqlalchemy.exc import IntegrityError

from src.domain.collaboration.entities.letter import Letter
from src.domain.collaboration.repositories.letter_repository import ILetterRepository
from src.infrastructure.persistence.sqlalchemy.models.letter_model import LetterModel
from src.infrastructure.persistence.sqlalchemy.mappers.letter_mapper import LetterMapper
from src.application.exceptions import PersistenceException


class SQLAlchemyLetterRepository(ILetterRepository):
    """
    Implémentation SQLAlchemy du repository Letter.
    """
    
    def __init__(self, session: Session):
        self._session = session
    
    def save(self, letter: Letter) -> Letter:
        """Persiste une lettre."""
        try:
            existing = self._session.query(LetterModel).filter_by(id=letter.id).first()
            
            if existing:
                LetterMapper.update_model(existing, letter)
                self._session.flush()
                return letter
            else:
                model = LetterMapper.to_model(letter)
                self._session.add(model)
                self._session.flush()
                return letter
                
        except IntegrityError as e:
            self._session.rollback()
            raise PersistenceException(f"Erreur d'intégrité: {e}")
    
    def find_by_id(self, letter_id: UUID) -> Optional[Letter]:
        """Récupère une lettre par ID."""
        model = self._session.query(LetterModel).filter_by(id=letter_id).first()
        if model:
            return LetterMapper.to_entity(model)
        return None
    
    def find_by_colli(self, colli_id: UUID, page: int = 1, per_page: int = 20) -> List[Letter]:
        """Récupère les lettres d'un COLLI avec pagination."""
        offset = (page - 1) * per_page
        models = self._session.query(LetterModel)\
            .filter_by(colli_id=colli_id)\
            .order_by(LetterModel.created_at.desc())\
            .offset(offset)\
            .limit(per_page)\
            .all()
        return [LetterMapper.to_entity(m) for m in models]
    
    def find_by_sender(self, sender_id: UUID) -> List[Letter]:
        """Récupère les lettres d'un utilisateur."""
        models = self._session.query(LetterModel)\
            .filter_by(sender_id=sender_id)\
            .order_by(LetterModel.created_at.desc())\
            .all()
        return [LetterMapper.to_entity(m) for m in models]
    
    def delete(self, letter: Letter) -> bool:
        """Supprime une lettre."""
        model = self._session.query(LetterModel).filter_by(id=letter.id).first()
        if model:
            self._session.delete(model)
            self._session.flush()
            return True
        return False
    
    def count_by_colli(self, colli_id: UUID) -> int:
        """Compte les lettres d'un COLLI."""
        return self._session.query(LetterModel).filter_by(colli_id=colli_id).count()
