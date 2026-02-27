# src/infrastructure/persistence/in_memory/notification_repository.py
"""Repository in-memory pour les notifications."""

from typing import List, Optional
from uuid import UUID

from src.domain.notification.entities.notification import Notification


class InMemoryNotificationRepository:
    """
    Implementation in-memory du repository de notifications.
    
    Pour le developpement et les tests.
    """
    
    def __init__(self):
        self._notifications: dict[UUID, Notification] = {}
    
    def save(self, notification: Notification) -> None:
        """Sauvegarde une notification."""
        self._notifications[notification.id] = notification
    
    def find_by_id(self, notification_id: UUID) -> Optional[Notification]:
        """Trouve une notification par son ID."""
        return self._notifications.get(notification_id)
    
    def find_by_user(
        self, 
        user_id: UUID, 
        unread_only: bool = False,
        limit: int = 50
    ) -> List[Notification]:
        """Trouve les notifications d'un utilisateur."""
        notifications = [
            n for n in self._notifications.values()
            if n.user_id == user_id
        ]
        
        if unread_only:
            notifications = [n for n in notifications if not n.read]
        
        # Trier par date (plus recent en premier)
        notifications.sort(key=lambda n: n.created_at, reverse=True)
        
        return notifications[:limit]
    
    def count_unread(self, user_id: UUID) -> int:
        """Compte les notifications non lues."""
        return len([
            n for n in self._notifications.values()
            if n.user_id == user_id and not n.read
        ])
    
    def mark_as_read(self, notification_id: UUID) -> bool:
        """Marque une notification comme lue."""
        notification = self.find_by_id(notification_id)
        if notification:
            notification.mark_as_read()
            return True
        return False
    
    def mark_all_as_read(self, user_id: UUID) -> int:
        """Marque toutes les notifications d'un utilisateur comme lues."""
        count = 0
        for notification in self._notifications.values():
            if notification.user_id == user_id and not notification.read:
                notification.mark_as_read()
                count += 1
        return count
    
    def delete(self, notification_id: UUID) -> bool:
        """Supprime une notification."""
        if notification_id in self._notifications:
            del self._notifications[notification_id]
            return True
        return False
    
    def find_all(self) -> List[Notification]:
        """Retourne toutes les notifications."""
        return list(self._notifications.values())
