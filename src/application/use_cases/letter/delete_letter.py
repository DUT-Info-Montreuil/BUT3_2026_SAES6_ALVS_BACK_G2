# src/application/use_cases/letter/delete_letter.py
"""Use Case: Supprimer une lettre."""

from uuid import UUID

from src.domain.collaboration.repositories.letter_repository import ILetterRepository
from src.domain.collaboration.repositories.colli_repository import IColliRepository
from src.application.exceptions import NotFoundException, ForbiddenException


class DeleteLetterUseCase:
    """
    Use Case: Supprimer une lettre.
    
    Règles métier:
    - Seul l'auteur ou un manager du COLLI peut supprimer
    """
    
    def __init__(
        self,
        letter_repository: ILetterRepository,
        colli_repository: IColliRepository
    ):
        self._letter_repo = letter_repository
        self._colli_repo = colli_repository
    
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
        
        if not is_author and not is_manager:
            raise ForbiddenException(
                "Seul l'auteur ou un manager peut supprimer cette lettre"
            )
        
        return self._letter_repo.delete(letter)