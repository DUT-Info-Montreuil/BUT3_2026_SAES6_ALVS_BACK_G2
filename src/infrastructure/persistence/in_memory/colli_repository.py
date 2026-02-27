# src/infrastructure/persistence/in_memory/colli_repository.py
"""Implémentation In-Memory du repository Colli pour les tests."""

from typing import Optional, List, Dict
from uuid import UUID

from src.domain.collaboration.entities.colli import Colli
from src.domain.collaboration.value_objects.colli_status import ColliStatus
from src.domain.collaboration.repositories.colli_repository import IColliRepository


class InMemoryColliRepository(IColliRepository):
    """
    Implémentation In-Memory du repository Colli.
    
    Utilisé pour:
    - Tests unitaires
    - Tests d'intégration sans base de données
    - Développement local rapide
    """
    
    def __init__(self):
        self._store: Dict[UUID, Colli] = {}
    
    def save(self, colli: Colli) -> Colli:
        """Persiste un Colli en mémoire."""
        self._store[colli.id] = colli
        return colli
    
    def find_by_id(self, colli_id: UUID) -> Optional[Colli]:
        """Récupère un Colli par son ID."""
        return self._store.get(colli_id)
    
    def find_all(self, page: int = 1, per_page: int = 20) -> List[Colli]:
        """Récupère tous les Collis avec pagination."""
        all_collis = list(self._store.values())
        start = (page - 1) * per_page
        end = start + per_page
        return all_collis[start:end]
    
    def find_by_status(self, status: ColliStatus, page: int = 1, per_page: int = 20) -> List[Colli]:
        """Récupère les Collis par statut avec pagination."""
        filtered = [c for c in self._store.values() if c.status == status]
        start = (page - 1) * per_page
        end = start + per_page
        return filtered[start:end]
    
    def find_by_creator(self, creator_id: UUID) -> List[Colli]:
        """Récupère les Collis d'un créateur."""
        return [c for c in self._store.values() if c.creator_id == creator_id]
    
    def delete(self, colli: Colli) -> bool:
        """Supprime un Colli."""
        if colli.id in self._store:
            del self._store[colli.id]
            return True
        return False
    
    def count(self) -> int:
        """Compte le nombre total de Collis."""
        return len(self._store)
    
    def count_by_status(self, status: ColliStatus) -> int:
        """Compte les Collis par statut."""
        return len([c for c in self._store.values() if c.status == status])
    
    def clear(self) -> None:
        """Vide le store (utile pour les tests)."""
        self._store.clear()
