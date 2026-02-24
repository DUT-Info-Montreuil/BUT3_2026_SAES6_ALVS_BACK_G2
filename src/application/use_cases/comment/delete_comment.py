# src/application/use_cases/comment/delete_comment.py
"""Use Case: Supprimer un commentaire."""

from uuid import UUID

from src.application.exceptions import ForbiddenException, NotFoundException
from src.domain.collaboration.repositories.colli_repository import IColliRepository
from src.domain.collaboration.repositories.comment_repository import ICommentRepository
from src.domain.collaboration.repositories.letter_repository import ILetterRepository


class DeleteCommentUseCase:
    """
    Use Case: Supprimer un commentaire.

    Règles métier:
    - Seul l'auteur ou un modérateur peut supprimer
    """

    def __init__(
        self,
        comment_repository: ICommentRepository,
        letter_repository: ILetterRepository,
        colli_repository: IColliRepository
    ):
        self._comment_repo = comment_repository
        self._letter_repo = letter_repository
        self._colli_repo = colli_repository

    def execute(self, comment_id: UUID, user_id: UUID) -> bool:
        """Supprime un commentaire."""
        # Vérifier que le commentaire existe
        comment = self._comment_repo.find_by_id(comment_id)
        if not comment:
            raise NotFoundException(f"Commentaire {comment_id} introuvable")

        # Récupérer la lettre et le COLLI pour vérifier les droits
        letter = self._letter_repo.find_by_id(comment.letter_id)
        colli = self._colli_repo.find_by_id(letter.colli_id) if letter else None

        is_moderator = colli and colli.is_manager(user_id) if colli else False

        if not comment.can_user_delete(user_id, is_moderator):
            raise ForbiddenException(
                "Seul l'auteur ou un modérateur peut supprimer ce commentaire"
            )

        return self._comment_repo.delete(comment)
