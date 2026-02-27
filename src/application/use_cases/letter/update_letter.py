# src/application/use_cases/letter/update_letter.py
"""Use Case: Mise a jour d'une lettre."""

from dataclasses import dataclass
from uuid import UUID
from typing import Optional

from src.domain.collaboration.repositories.letter_repository import ILetterRepository
from src.application.dtos.letter_dto import LetterResponseDTO
from src.application.exceptions import NotFoundException, ForbiddenException


@dataclass
class UpdateLetterCommand:
    """Commande pour mettre a jour une lettre."""
    letter_id: UUID
    user_id: UUID
    content: Optional[str] = None
    description: Optional[str] = None


class UpdateLetterUseCase:
    """
    Met a jour une lettre existante.
    
    Seul l'auteur peut modifier sa lettre.
    """
    
    def __init__(self, letter_repository: ILetterRepository):
        self._letter_repo = letter_repository
    
    def execute(self, command: UpdateLetterCommand) -> LetterResponseDTO:
        """Execute la mise a jour de la lettre."""
        letter = self._letter_repo.find_by_id(command.letter_id)
        if not letter:
            raise NotFoundException(f"Lettre {command.letter_id} non trouvee")
        
        # Verifier les permissions (auteur uniquement)
        if letter.sender_id != command.user_id:
            raise ForbiddenException("Seul l'auteur peut modifier cette lettre")
        
        # Mettre a jour les champs fournis
        if command.content is not None:
            letter.content = command.content
        
        if command.description is not None:
            letter.description = command.description
        
        self._letter_repo.save(letter)
        
        return LetterResponseDTO.from_entity(letter)
