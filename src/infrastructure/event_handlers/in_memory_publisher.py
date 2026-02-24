# src/infrastructure/event_handlers/in_memory_publisher.py
"""Implémentation In-Memory du publisher d'événements."""

import logging
from typing import Callable, Dict, List, Type

from src.application.interfaces.event_publisher import IEventPublisher
from src.domain.collaboration.events import DomainEvent

logger = logging.getLogger(__name__)


class InMemoryEventPublisher(IEventPublisher):
    """
    Publisher d'événements en mémoire.

    Utilisé pour:
    - Développement local
    - Tests
    - Exécution synchrone des handlers

    En production, utiliser un publisher asynchrone (Redis, RabbitMQ, etc.)
    """

    def __init__(self):
        self._handlers: Dict[Type[DomainEvent], List[Callable]] = {}
        self._published_events: List[DomainEvent] = []  # Pour les tests

    def subscribe(
        self,
        event_type: Type[DomainEvent],
        handler: Callable[[DomainEvent], None]
    ) -> None:
        """
        Abonne un handler à un type d'événement.

        Args:
            event_type: Le type d'événement à écouter.
            handler: La fonction à appeler quand l'événement est publié.
        """
        if event_type not in self._handlers:
            self._handlers[event_type] = []
        self._handlers[event_type].append(handler)

    def publish(self, event: DomainEvent) -> None:
        """
        Publie un événement.

        Args:
            event: L'événement à publier.
        """
        self._published_events.append(event)

        event_type = type(event)
        handlers = self._handlers.get(event_type, [])

        for handler in handlers:
            try:
                handler(event)
            except Exception as e:
                logger.error(
                    f"Erreur dans le handler {handler.__name__} "
                    f"pour l'événement {event_type.__name__}: {e}"
                )

    def publish_all(self, events: List[DomainEvent]) -> None:
        """Publie plusieurs événements."""
        for event in events:
            self.publish(event)

    # Méthodes utilitaires pour les tests

    def get_published_events(self) -> List[DomainEvent]:
        """Retourne tous les événements publiés (pour les tests)."""
        return self._published_events.copy()

    def clear(self) -> None:
        """Vide les événements publiés (pour les tests)."""
        self._published_events.clear()

    def get_events_of_type(self, event_type: Type[DomainEvent]) -> List[DomainEvent]:
        """Retourne les événements d'un type spécifique."""
        return [e for e in self._published_events if isinstance(e, event_type)]
