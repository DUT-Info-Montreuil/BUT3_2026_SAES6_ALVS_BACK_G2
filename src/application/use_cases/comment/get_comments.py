# src/application/use_cases/comment/get_comments.py
"""Use Case: Récupérer les commentaires d'une lettre."""

from uuid import UUID

from src.domain.collaboration.repositories.comment_repository import ICommentRepository
from src.domain.collaboration.repositories.letter_repository import ILetterRepository
from src.domain.collaboration.repositories.colli_repository import IColliRepository
from src.application.dtos.comment_dto import CommentResponseDTO, CommentListResponseDTO
from src.application.exceptions import NotFoundException, ForbiddenException


class GetCommentsForLetterUseCase:
    """Use Case: Lister les commentaires d'une lettre."""
    
    def __init__(
        self,
        comment_repository: ICommentRepository,
        letter_repository: ILetterRepository,
        colli_repository: IColliRepository
    ):
        self._comment_repo = comment_repository
        self._letter_repo = letter_repository
        self._colli_repo = colli_repository
    
    def execute(
        self,
        letter_id: UUID,
        user_id: UUID,
        page: int = 1,
        per_page: int = 50
    ) -> CommentListResponseDTO:
        """Récupère les commentaires paginés."""
        # Vérifier que la lettre existe
        letter = self._letter_repo.find_by_id(letter_id)
        if not letter:
            raise NotFoundException(f"Lettre {letter_id} introuvable")
        
        # Vérifier l'accès au COLLI
        colli = self._colli_repo.find_by_id(letter.colli_id)
        if colli and not colli.is_member(user_id):
            raise ForbiddenException("Vous n'êtes pas membre de ce COLLI")
        
        # Récupérer les commentaires
        comments = self._comment_repo.find_by_letter(letter_id, page, per_page)
        total = self._comment_repo.count_by_letter(letter_id)
        
        items = [CommentResponseDTO.from_entity(c) for c in comments]
        
        return CommentListResponseDTO(
            items=items,
            total=total,
            page=page,
            per_page=per_page,
            has_more=(page * per_page) < total
        )
