# src/domain/collaboration/repositories/colli_repository.py
"""Interface (Port) pour le repository Colli."""

from abc import ABC, abstractmethod
from typing import List, Optional
from uuid import UUID

from src.domain.collaboration.entities.colli import Colli
from src.domain.collaboration.value_objects.colli_status import ColliStatus


class IColliRepository(ABC):
    """
    Interface (Port) pour le repository Colli.

    Cette interface définit le contrat que toute implémentation
    (SQLAlchemy, MongoDB, InMemory) doit respecter.

    Règles :
    - Aucune dépendance à l'infrastructure (pas de SQLAlchemy, pas de Flask)
    - Travaille uniquement avec des entités du domaine
    - Les méthodes retournent des entités, jamais des modèles ORM
    """

    @abstractmethod
    def save(self, colli: Colli) -> Colli:
        """
        Persiste un Colli (création ou mise à jour).

        Args:
            colli: L'entité Colli à persister.

        Returns:
            Colli: L'entité persistée.
        """
        pass

    @abstractmethod
    def find_by_id(self, colli_id: UUID) -> Optional[Colli]:
        """
        Récupère un Colli par son identifiant.

        Args:
            colli_id: L'identifiant unique du Colli.

        Returns:
            Optional[Colli]: Le Colli trouvé ou None.
        """
        pass

    @abstractmethod
    def find_all(self, page: int = 1, per_page: int = 20) -> List[Colli]:
        """
        Récupère tous les Collis avec pagination.

        Args:
            page: Numéro de page (1-indexed).
            per_page: Nombre d'éléments par page.

        Returns:
            List[Colli]: Liste des Collis.
        """
        pass

    @abstractmethod
    def find_by_status(self, status: ColliStatus) -> List[Colli]:
        """
        Récupère tous les Collis ayant un statut donné.

        Args:
            status: Le statut à filtrer.

        Returns:
            List[Colli]: Liste des Collis correspondants.
        """
        pass

    @abstractmethod
    def find_by_creator(self, creator_id: UUID) -> List[Colli]:
        """
        Récupère tous les Collis créés par un utilisateur.

        Args:
            creator_id: L'identifiant du créateur.

        Returns:
            List[Colli]: Liste des Collis créés par cet utilisateur.
        """
        pass

    @abstractmethod
    def delete(self, colli: Colli) -> bool:
        """
        Supprime un Colli.

        Args:
            colli: L'entité à supprimer.

        Returns:
            bool: True si supprimé, False sinon.
        """
        pass

    @abstractmethod
    def count(self) -> int:
        """Retourne le nombre total de Collis."""
        pass

    @abstractmethod
    def count_by_status(self, status: ColliStatus) -> int:
        """Retourne le nombre de Collis ayant un statut donné."""
        pass
