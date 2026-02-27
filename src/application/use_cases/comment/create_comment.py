# src/application/use_cases/comment/create_comment.py
"""Use Case: Créer un commentaire sur une lettre."""

from uuid import UUID

from src.domain.collaboration.entities.comment import Comment
from src.domain.collaboration.repositories.comment_repository import ICommentRepository
from src.domain.collaboration.repositories.letter_repository import ILetterRepository
from src.domain.collaboration.repositories.colli_repository import IColliRepository
from src.application.dtos.comment_dto import CreateCommentCommand, CommentResponseDTO
from src.application.exceptions import (
    NotFoundException,
    ForbiddenException,
    ValidationException
)


class CreateCommentUseCase:
    """
    Use Case: Créer un commentaire sur une lettre.
    
    Règles métier:
    - La lettre doit exister
    - L'utilisateur doit être membre du COLLI de la lettre
    - Le contenu ne peut pas être vide
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
    
    def execute(self, command: CreateCommentCommand) -> CommentResponseDTO:
        """Exécute la création d'un commentaire."""
        # Vérifier que la lettre existe
        letter = self._letter_repo.find_by_id(command.letter_id)
        if not letter:
            raise NotFoundException(f"Lettre {command.letter_id} introuvable")
        
        # Vérifier que le COLLI de la lettre est accessible
        colli = self._colli_repo.find_by_id(letter.colli_id)
        if not colli:
            raise NotFoundException("COLLI de la lettre introuvable")
        
        # Vérifier que l'utilisateur est membre du COLLI
        if not colli.is_member(command.sender_id):
            raise ForbiddenException("Vous devez être membre du COLLI pour commenter")
        
        # Créer le commentaire
        try:
            comment = Comment.create(
                letter_id=command.letter_id,
                sender_id=command.sender_id,
                content=command.content,
                parent_comment_id=command.parent_comment_id
            )
        except Exception as e:
            raise ValidationException(str(e))
        
        # Persister
        saved_comment = self._comment_repo.save(comment)
        
        return CommentResponseDTO.from_entity(saved_comment)
