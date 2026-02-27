# src/infrastructure/services/notification_service.py
"""Service de notification integrant les push WebSocket."""

from typing import Optional
from uuid import UUID
from datetime import datetime

from src.domain.notification.entities.notification import Notification, NotificationType
from src.infrastructure.persistence.in_memory.notification_repository import InMemoryNotificationRepository


class NotificationService:
    """
    Service centralise pour la gestion des notifications.
    
    Cree les notifications en base ET les envoie en temps reel via WebSocket.
    """
    
    def __init__(self, notification_repo: InMemoryNotificationRepository = None):
        self._repo = notification_repo or InMemoryNotificationRepository()
    
    def create_notification(
        self,
        user_id: UUID,
        notification_type: NotificationType,
        title: str,
        message: str,
        related_entity_id: Optional[UUID] = None,
        related_entity_type: Optional[str] = None
    ) -> Notification:
        """
        Cree une notification et l'envoie en temps reel.
        
        Args:
            user_id: ID de l'utilisateur destinataire
            notification_type: Type de notification
            title: Titre
            message: Message
            related_entity_id: ID de l'entite liee (optionnel)
            related_entity_type: Type de l'entite liee (optionnel)
            
        Returns:
            Notification creee
        """
        # Creer la notification
        notification = Notification(
            user_id=user_id,
            type=notification_type,
            title=title,
            message=message,
            related_entity_id=related_entity_id,
            related_entity_type=related_entity_type
        )
        
        # Sauvegarder en base
        self._repo.save(notification)
        
        # Envoyer en temps reel via WebSocket
        try:
            from src.infrastructure.websocket import push_notification
            push_notification(str(user_id), notification.to_dict())
        except Exception:
            # WebSocket peut ne pas etre disponible (tests, etc.)
            pass
        
        return notification
    
    def notify_new_letter(
        self,
        colli_id: UUID,
        colli_name: str,
        letter_id: UUID,
        author_name: str,
        member_ids: list[UUID]
    ):
        """Notifie les membres d'un COLLI d'une nouvelle lettre."""
        for member_id in member_ids:
            self.create_notification(
                user_id=member_id,
                notification_type=NotificationType.NEW_LETTER,
                title="Nouvelle lettre",
                message=f"{author_name} a ecrit une nouvelle lettre dans {colli_name}",
                related_entity_id=letter_id,
                related_entity_type="letter"
            )
    
    def notify_new_comment(
        self,
        letter_id: UUID,
        letter_author_id: UUID,
        comment_author_name: str
    ):
        """Notifie l'auteur d'une lettre d'un nouveau commentaire."""
        self.create_notification(
            user_id=letter_author_id,
            notification_type=NotificationType.NEW_COMMENT,
            title="Nouveau commentaire",
            message=f"{comment_author_name} a commente votre lettre",
            related_entity_id=letter_id,
            related_entity_type="letter"
        )
    
    def notify_colli_approved(
        self,
        colli_id: UUID,
        colli_name: str,
        creator_id: UUID
    ):
        """Notifie le createur qu'un COLLI a ete approuve."""
        self.create_notification(
            user_id=creator_id,
            notification_type=NotificationType.COLLI_APPROVED,
            title="COLLI approuve !",
            message=f"Votre COLLI '{colli_name}' a ete approuve par un moderateur",
            related_entity_id=colli_id,
            related_entity_type="colli"
        )
    
    def notify_colli_rejected(
        self,
        colli_id: UUID,
        colli_name: str,
        creator_id: UUID,
        reason: str = None
    ):
        """Notifie le createur qu'un COLLI a ete rejete."""
        message = f"Votre COLLI '{colli_name}' a ete rejete"
        if reason:
            message += f": {reason}"
        
        self.create_notification(
            user_id=creator_id,
            notification_type=NotificationType.COLLI_REJECTED,
            title="COLLI rejete",
            message=message,
            related_entity_id=colli_id,
            related_entity_type="colli"
        )
    
    def notify_user_joined(
        self,
        colli_id: UUID,
        colli_name: str,
        new_member_name: str,
        creator_id: UUID
    ):
        """Notifie le createur qu'un utilisateur a rejoint son COLLI."""
        self.create_notification(
            user_id=creator_id,
            notification_type=NotificationType.USER_JOINED,
            title="Nouveau membre",
            message=f"{new_member_name} a rejoint votre COLLI '{colli_name}'",
            related_entity_id=colli_id,
            related_entity_type="colli"
        )


# Instance globale
_notification_service: Optional[NotificationService] = None


def get_notification_service() -> NotificationService:
    """Retourne l'instance du service de notifications."""
    global _notification_service
    if _notification_service is None:
        _notification_service = NotificationService()
    return _notification_service
