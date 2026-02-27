# src/infrastructure/persistence/sqlalchemy/repositories/colli_repository.py
"""Implémentation SQLAlchemy du repository Colli."""

from typing import Optional, List
from uuid import UUID

from sqlalchemy.orm import Session, joinedload
from sqlalchemy.exc import IntegrityError

from src.domain.collaboration.entities.colli import Colli
from src.domain.collaboration.value_objects.colli_status import ColliStatus
from src.domain.collaboration.repositories.colli_repository import IColliRepository
from src.infrastructure.persistence.sqlalchemy.models.colli_model import ColliModel
from src.infrastructure.persistence.sqlalchemy.mappers.colli_mapper import ColliMapper
from src.application.exceptions import PersistenceException


class SQLAlchemyColliRepository(IColliRepository):
    """
    Implémentation SQLAlchemy du repository Colli.
    
    Utilise joinedload pour éviter les problèmes N+1.
    """
    
    def __init__(self, session: Session):
        self._session = session
    
    def save(self, colli: Colli) -> Colli:
        """Persiste un Colli."""
        try:
            existing = self._session.query(ColliModel)\
                .options(joinedload(ColliModel.members))\
                .filter_by(id=colli.id)\
                .first()
            
            if existing:
                # Update
                ColliMapper.update_model(existing, colli)
                self._session.flush()
                return colli
            else:
                # Create
                model = ColliMapper.to_model(colli)
                self._session.add(model)
                self._session.flush()
                return colli
                
        except IntegrityError as e:
            self._session.rollback()
            raise PersistenceException(f"Erreur d'intégrité: {e}")
    
    def find_by_id(self, colli_id: UUID) -> Optional[Colli]:
        """Récupère un Colli avec ses membres (eager loading)."""
        model = self._session.query(ColliModel)\
            .options(joinedload(ColliModel.members))\
            .filter_by(id=colli_id)\
            .first()
        if model:
            return ColliMapper.to_entity(model)
        return None
    
    def find_all(self, page: int = 1, per_page: int = 20) -> List[Colli]:
        """Récupère tous les Collis avec pagination."""
        offset = (page - 1) * per_page
        models = self._session.query(ColliModel)\
            .options(joinedload(ColliModel.members))\
            .order_by(ColliModel.created_at.desc())\
            .offset(offset)\
            .limit(per_page)\
            .all()
        return ColliMapper.to_entity_list(models)
    
    def find_by_status(self, status: ColliStatus) -> List[Colli]:
        """Récupère les Collis par statut."""
        models = self._session.query(ColliModel)\
            .options(joinedload(ColliModel.members))\
            .filter_by(status=status.value)\
            .order_by(ColliModel.created_at.desc())\
            .all()
        return ColliMapper.to_entity_list(models)
    
    def find_by_creator(self, creator_id: UUID) -> List[Colli]:
        """Récupère les Collis d'un créateur."""
        models = self._session.query(ColliModel)\
            .options(joinedload(ColliModel.members))\
            .filter_by(creator_id=creator_id)\
            .order_by(ColliModel.created_at.desc())\
            .all()
        return ColliMapper.to_entity_list(models)
    
    def delete(self, colli: Colli) -> bool:
        """Supprime un Colli."""
        model = self._session.query(ColliModel).filter_by(id=colli.id).first()
        if model:
            self._session.delete(model)
            self._session.flush()
            return True
        return False
    
    def count(self) -> int:
        """Compte les Collis."""
        return self._session.query(ColliModel).count()
    
    def count_by_status(self, status: ColliStatus) -> int:
        """Compte les Collis par statut."""
        return self._session.query(ColliModel)\
            .filter_by(status=status.value)\
            .count()
