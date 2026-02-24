# src/application/use_cases/comment/update_comment.py
"""Use Case: Mise a jour d'un commentaire."""

from dataclasses import dataclass
from uuid import UUID

from src.application.dtos.comment_dto import CommentResponseDTO
from src.application.exceptions import ForbiddenException, NotFoundException, ValidationException
from src.domain.collaboration.repositories.comment_repository import ICommentRepository


@dataclass
class UpdateCommentCommand:
    """Commande pour mettre a jour un commentaire."""
    comment_id: UUID
    user_id: UUID
    content: str


class UpdateCommentUseCase:
    """
    Met a jour un commentaire existant.

    Seul l'auteur peut modifier son commentaire.
    """

    def __init__(self, comment_repository: ICommentRepository):
        self._comment_repo = comment_repository

    def execute(self, command: UpdateCommentCommand) -> CommentResponseDTO:
        """Execute la mise a jour du commentaire."""
        if not command.content or not command.content.strip():
            raise ValidationException("Le contenu ne peut pas etre vide")

        comment = self._comment_repo.find_by_id(command.comment_id)
        if not comment:
            raise NotFoundException(f"Commentaire {command.comment_id} non trouve")

        # Verifier les permissions (auteur uniquement)
        if comment.author_id != command.user_id:
            raise ForbiddenException("Seul l'auteur peut modifier ce commentaire")

        # Mettre a jour le contenu
        comment.content = command.content.strip()

        self._comment_repo.save(comment)

        return CommentResponseDTO.from_entity(comment)
