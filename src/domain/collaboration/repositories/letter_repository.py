# src/domain/collaboration/repositories/letter_repository.py
"""Interface (Port) pour le repository Letter."""

from abc import ABC, abstractmethod
from typing import Optional, List
from uuid import UUID

from src.domain.collaboration.entities.letter import Letter


class ILetterRepository(ABC):
    """Interface pour le repository Letter."""
    
    @abstractmethod
    def save(self, letter: Letter) -> Letter:
        """Persiste une lettre."""
        pass
    
    @abstractmethod
    def find_by_id(self, letter_id: UUID) -> Optional[Letter]:
        """Récupère une lettre par ID."""
        pass
    
    @abstractmethod
    def find_by_colli(
        self,
        colli_id: UUID,
        page: int = 1,
        per_page: int = 20
    ) -> List[Letter]:
        """Récupère les lettres d'un COLLI avec pagination."""
        pass
    
    @abstractmethod
    def find_by_sender(self, sender_id: UUID) -> List[Letter]:
        """Récupère les lettres d'un utilisateur."""
        pass
    
    @abstractmethod
    def delete(self, letter: Letter) -> bool:
        """Supprime une lettre."""
        pass
    
    @abstractmethod
    def count_by_colli(self, colli_id: UUID) -> int:
        """Compte les lettres d'un COLLI."""
        pass
