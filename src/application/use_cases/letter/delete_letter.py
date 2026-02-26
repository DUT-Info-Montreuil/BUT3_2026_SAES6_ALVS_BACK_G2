# src/application/use_cases/letter/delete_letter.py
"""Use Case: Supprimer une lettre."""

from uuid import UUID

from src.domain.collaboration.repositories.letter_repository import ILetterRepository
from src.domain.collaboration.repositories.colli_repository import IColliRepository
from src.domain.identity.repositories.user_repository import IUserRepository
from src.application.exceptions import NotFoundException, ForbiddenException


class DeleteLetterUseCase:
    """
    Use Case: Supprimer une lettre.

    Règles métier:
    - L'auteur, un manager du COLLI, ou un admin peut supprimer
    """

    def __init__(
        self,
        letter_repository: ILetterRepository,
        colli_repository: IColliRepository,
        user_repository: IUserRepository = None
    ):
        self._letter_repo = letter_repository
        self._colli_repo = colli_repository
        self._user_repo = user_repository

    def execute(self, letter_id: UUID, user_id: UUID) -> bool:
        """Supprime une lettre."""
        # Vérifier que la lettre existe
        letter = self._letter_repo.find_by_id(letter_id)
        if not letter:
            raise NotFoundException(f"Lettre {letter_id} introuvable")

        # Vérifier les droits
        colli = self._colli_repo.find_by_id(letter.colli_id)
        is_author = letter.sender_id == user_id
        is_manager = colli and colli.is_manager(user_id) if colli else False

        # Vérifier si l'utilisateur est admin
        is_admin = False
        if self._user_repo:
            user = self._user_repo.find_by_id(user_id)
            is_admin = user and user.role.value == 'admin' if user else False

        if not is_author and not is_manager and not is_admin:
            raise ForbiddenException(
                "Seul l'auteur, un manager ou un admin peut supprimer cette lettre"
            )

        return self._letter_repo.delete(letter)
