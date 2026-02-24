# src/application/interfaces/event_publisher.py
"""Interface pour la publication d'événements domaine."""

from abc import ABC, abstractmethod
from typing import List

from src.domain.collaboration.events import DomainEvent


class IEventPublisher(ABC):
    """
    Interface pour publier les événements du domaine.

    Permet de découpler les actions métier de leurs effets secondaires
    (notifications, webhooks, synchronisation, etc.).
    """

    @abstractmethod
    def publish(self, event: DomainEvent) -> None:
        """
        Publie un événement domaine.

        Args:
            event: L'événement à publier.
        """
        pass

    @abstractmethod
    def publish_all(self, events: List[DomainEvent]) -> None:
        """
        Publie plusieurs événements domaine.

        Args:
            events: Liste d'événements à publier.
        """
        pass
