# src/domain/collaboration/entities/comment.py
"""
Entity Comment - Commentaire sur une Letter.

Un Comment est une réponse d'un membre à une Letter dans un COLLI.
"""

from dataclasses import dataclass, field
from datetime import datetime
from uuid import UUID, uuid4

from src.domain.shared.domain_exception import DomainException


class CommentValidationException(DomainException):
    """Exception pour les erreurs de validation de commentaire."""
    pass


class CannotEditCommentException(DomainException):
    """Exception quand le commentaire ne peut pas être modifié."""
    pass


@dataclass
class Comment:
    """
    Entity pour les commentaires.

    Invariants:
    - Le contenu ne peut pas être vide
    - Seul l'auteur peut modifier son commentaire
    """
    id: UUID
    letter_id: UUID
    sender_id: UUID
    content: str
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)

    @classmethod
    def create(
        cls,
        letter_id: UUID,
        sender_id: UUID,
        content: str
    ) -> "Comment":
        """
        Factory pour créer un commentaire.

        Args:
            letter_id: ID de la lettre parente.
            sender_id: ID de l'utilisateur qui commente.
            content: Contenu du commentaire.

        Returns:
            Comment: Nouveau commentaire.
        """
        if not content or len(content.strip()) < 1:
            raise CommentValidationException(
                "Le contenu du commentaire est obligatoire"
            )

        if len(content.strip()) > 5000:
            raise CommentValidationException(
                "Le commentaire ne peut pas dépasser 5000 caractères"
            )

        return cls(
            id=uuid4(),
            letter_id=letter_id,
            sender_id=sender_id,
            content=content.strip()
        )

    def update_content(self, new_content: str, editor_id: UUID) -> None:
        """
        Met à jour le contenu du commentaire.

        Args:
            new_content: Nouveau contenu.
            editor_id: ID de l'utilisateur qui modifie.

        Raises:
            CannotEditCommentException: Si l'utilisateur n'est pas l'auteur.
        """
        if editor_id != self.sender_id:
            raise CannotEditCommentException(
                "Seul l'auteur peut modifier son commentaire"
            )

        if not new_content or len(new_content.strip()) < 1:
            raise CommentValidationException(
                "Le contenu du commentaire est obligatoire"
            )

        self.content = new_content.strip()
        self._touch()

    def can_user_edit(self, user_id: UUID) -> bool:
        """Vérifie si l'utilisateur peut modifier le commentaire."""
        return user_id == self.sender_id

    def can_user_delete(self, user_id: UUID, is_moderator: bool = False) -> bool:
        """
        Vérifie si l'utilisateur peut supprimer le commentaire.

        Un utilisateur peut supprimer si:
        - Il est l'auteur du commentaire
        - Il est modérateur du COLLI
        """
        return user_id == self.sender_id or is_moderator

    def _touch(self) -> None:
        """Met à jour updated_at."""
        self.updated_at = datetime.utcnow()

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Comment):
            return False
        return self.id == other.id

    def __hash__(self) -> int:
        return hash(self.id)
