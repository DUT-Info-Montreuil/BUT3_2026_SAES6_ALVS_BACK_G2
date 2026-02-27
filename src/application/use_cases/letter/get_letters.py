# src/application/use_cases/letter/get_letters.py
"""Use Case: Récupérer les lettres d'un COLLI."""

from uuid import UUID
from typing import List

from src.domain.collaboration.repositories.letter_repository import ILetterRepository
from src.domain.collaboration.repositories.comment_repository import ICommentRepository
from src.domain.collaboration.repositories.colli_repository import IColliRepository
from src.domain.identity.repositories.user_repository import IUserRepository
from src.application.dtos.letter_dto import LetterResponseDTO, LetterListResponseDTO
from src.application.exceptions import NotFoundException, ForbiddenException


def _build_sender_data(user_repository: IUserRepository, sender_id: UUID) -> dict | None:
    """Récupère les données du sender pour le DTO."""
    user = user_repository.find_by_id(sender_id)
    if user:
        return {
            'id': str(user.id),
            'first_name': user.first_name,
            'last_name': user.last_name,
        }
    return None


class GetLettersForColliUseCase:
    """Use Case: Lister les lettres d'un COLLI."""

    def __init__(
        self,
        letter_repository: ILetterRepository,
        comment_repository: ICommentRepository,
        colli_repository: IColliRepository,
        user_repository: IUserRepository
    ):
        self._letter_repo = letter_repository
        self._comment_repo = comment_repository
        self._colli_repo = colli_repository
        self._user_repo = user_repository

    def execute(
        self,
        colli_id: UUID,
        user_id: UUID,
        page: int = 1,
        per_page: int = 20
    ) -> LetterListResponseDTO:
        """Récupère les lettres paginées."""
        # Vérifier que le COLLI existe
        colli = self._colli_repo.find_by_id(colli_id)
        if not colli:
            raise NotFoundException(f"COLLI {colli_id} introuvable")

        # Vérifier que l'utilisateur est membre
        if not colli.is_member(user_id):
            raise ForbiddenException("Vous n'êtes pas membre de ce COLLI")

        # Récupérer les lettres
        letters = self._letter_repo.find_by_colli(colli_id, page, per_page)
        total = self._letter_repo.count_by_colli(colli_id)

        # Cache des senders pour éviter les requêtes dupliquées
        sender_cache: dict[UUID, dict | None] = {}

        # Convertir avec le nombre de commentaires et les données sender
        items = []
        for letter in letters:
            comment_count = self._comment_repo.count_by_letter(letter.id)
            if letter.sender_id not in sender_cache:
                sender_cache[letter.sender_id] = _build_sender_data(self._user_repo, letter.sender_id)
            items.append(LetterResponseDTO.from_entity(letter, comment_count, sender_cache[letter.sender_id]))

        return LetterListResponseDTO(
            items=items,
            total=total,
            page=page,
            per_page=per_page,
            has_more=(page * per_page) < total
        )


class GetLetterByIdUseCase:
    """Use Case: Récupérer une lettre par ID."""

    def __init__(
        self,
        letter_repository: ILetterRepository,
        comment_repository: ICommentRepository,
        colli_repository: IColliRepository,
        user_repository: IUserRepository
    ):
        self._letter_repo = letter_repository
        self._comment_repo = comment_repository
        self._colli_repo = colli_repository
        self._user_repo = user_repository

    def execute(self, letter_id: UUID, user_id: UUID) -> LetterResponseDTO:
        """Récupère une lettre."""
        letter = self._letter_repo.find_by_id(letter_id)
        if not letter:
            raise NotFoundException(f"Lettre {letter_id} introuvable")

        # Vérifier l'accès au COLLI
        colli = self._colli_repo.find_by_id(letter.colli_id)
        if colli and not colli.is_member(user_id):
            raise ForbiddenException("Vous n'êtes pas membre de ce COLLI")

        comment_count = self._comment_repo.count_by_letter(letter.id)
        sender_data = _build_sender_data(self._user_repo, letter.sender_id)
        return LetterResponseDTO.from_entity(letter, comment_count, sender_data)
