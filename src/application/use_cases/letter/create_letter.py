# src/application/use_cases/letter/create_letter.py
"""Use Case: Créer une lettre dans un COLLI."""

from dataclasses import dataclass
from uuid import UUID

from src.domain.collaboration.entities.letter import Letter
from src.domain.collaboration.repositories.letter_repository import ILetterRepository
from src.domain.collaboration.repositories.colli_repository import IColliRepository
from src.application.dtos.letter_dto import (
    CreateTextLetterCommand,
    CreateFileLetterCommand,
    LetterResponseDTO
)
from src.application.exceptions import (
    NotFoundException,
    ForbiddenException,
    ValidationException
)


class CreateTextLetterUseCase:
    """
    Use Case: Créer une lettre texte.
    
    Règles métier:
    - Le COLLI doit exister et être actif
    - L'utilisateur doit être membre du COLLI
    - Le contenu doit faire au moins 10 caractères
    """
    
    def __init__(
        self,
        letter_repository: ILetterRepository,
        colli_repository: IColliRepository
    ):
        self._letter_repo = letter_repository
        self._colli_repo = colli_repository
    
    def execute(self, command: CreateTextLetterCommand) -> LetterResponseDTO:
        """Exécute la création d'une lettre texte."""
        # Vérifier que le COLLI existe
        colli = self._colli_repo.find_by_id(command.colli_id)
        if not colli:
            raise NotFoundException(f"COLLI {command.colli_id} introuvable")
        
        # Vérifier que le COLLI est actif
        if not colli.is_active:
            raise ForbiddenException("Le COLLI n'est pas actif")
        
        # Vérifier que l'utilisateur est membre
        if not colli.is_member(command.sender_id):
            raise ForbiddenException("Vous n'êtes pas membre de ce COLLI")
        
        # Créer la lettre
        try:
            letter = Letter.create_text_letter(
                colli_id=command.colli_id,
                sender_id=command.sender_id,
                content=command.content
            )
        except Exception as e:
            raise ValidationException(str(e))
        
        # Persister
        saved_letter = self._letter_repo.save(letter)
        
        return LetterResponseDTO.from_entity(saved_letter)


class CreateFileLetterUseCase:
    """
    Use Case: Créer une lettre fichier.
    
    Règles métier:
    - Le COLLI doit exister et être actif
    - L'utilisateur doit être membre du COLLI
    - Le fichier doit avoir été uploadé
    """
    
    def __init__(
        self,
        letter_repository: ILetterRepository,
        colli_repository: IColliRepository
    ):
        self._letter_repo = letter_repository
        self._colli_repo = colli_repository
    
    def execute(self, command: CreateFileLetterCommand) -> LetterResponseDTO:
        """Exécute la création d'une lettre fichier."""
        # Vérifier que le COLLI existe
        colli = self._colli_repo.find_by_id(command.colli_id)
        if not colli:
            raise NotFoundException(f"COLLI {command.colli_id} introuvable")
        
        # Vérifier que le COLLI est actif
        if not colli.is_active:
            raise ForbiddenException("Le COLLI n'est pas actif")
        
        # Vérifier que l'utilisateur est membre
        if not colli.is_member(command.sender_id):
            raise ForbiddenException("Vous n'êtes pas membre de ce COLLI")
        
        # Créer la lettre
        try:
            letter = Letter.create_file_letter(
                colli_id=command.colli_id,
                sender_id=command.sender_id,
                file_url=command.file_url,
                file_name=command.file_name,
                description=command.description
            )
        except Exception as e:
            raise ValidationException(str(e))
        
        # Persister
        saved_letter = self._letter_repo.save(letter)
        
        return LetterResponseDTO.from_entity(saved_letter)