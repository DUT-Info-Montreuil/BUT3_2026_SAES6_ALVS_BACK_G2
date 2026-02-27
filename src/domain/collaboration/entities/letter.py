# src/domain/collaboration/entities/letter.py
"""
Aggregate Root Letter - Publication dans un COLLI.

Une Letter est un post créé par un manager dans un COLLI.
Les membres peuvent y répondre via des Comments.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, List
from uuid import UUID, uuid4

from src.domain.collaboration.value_objects.letter_type import LetterType
from src.domain.collaboration.value_objects.file_attachment import FileAttachment
from src.domain.shared.domain_exception import DomainException


class LetterValidationException(DomainException):
    """Exception pour les erreurs de validation de lettre."""
    pass


class CannotEditLetterException(DomainException):
    """Exception quand la lettre ne peut pas être modifiée."""
    pass


@dataclass
class Letter:
    """
    Aggregate Root pour les lettres/publications.
    
    Invariants:
    - Une lettre TEXT doit avoir un content non vide
    - Une lettre FILE doit avoir une file_url
    - Seul le sender peut modifier sa lettre
    """
    id: UUID
    letter_type: LetterType
    colli_id: UUID
    sender_id: UUID
    content: Optional[str] = None
    file_url: Optional[str] = None
    file_name: Optional[str] = None
    title: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    
    # Events (pour publication après commit)
    _events: List = field(default_factory=list, repr=False)
    
    @classmethod
    def create_text_letter(
        cls,
        colli_id: UUID,
        sender_id: UUID,
        content: str,
        title: Optional[str] = None
    ) -> "Letter":
        """
        Factory pour créer une lettre texte.

        Args:
            colli_id: ID du COLLI parent.
            sender_id: ID de l'utilisateur qui envoie.
            content: Contenu texte de la lettre.
            title: Titre optionnel de la lettre.

        Returns:
            Letter: Nouvelle lettre texte.
        """
        if not content or len(content.strip()) < 10:
            raise LetterValidationException(
                "Le contenu doit faire au moins 10 caractères"
            )

        return cls(
            id=uuid4(),
            letter_type=LetterType.TEXT,
            colli_id=colli_id,
            sender_id=sender_id,
            content=content.strip(),
            title=title.strip() if title else None
        )
    
    @classmethod
    def create_file_letter(
        cls,
        colli_id: UUID,
        sender_id: UUID,
        file_url: str,
        file_name: str,
        description: Optional[str] = None,
        title: Optional[str] = None
    ) -> "Letter":
        """
        Factory pour créer une lettre avec fichier PDF.

        Args:
            colli_id: ID du COLLI parent.
            sender_id: ID de l'utilisateur qui envoie.
            file_url: URL du fichier uploadé.
            file_name: Nom original du fichier.
            description: Description optionnelle.
            title: Titre optionnel de la lettre.

        Returns:
            Letter: Nouvelle lettre fichier.
        """
        if not file_url:
            raise LetterValidationException("L'URL du fichier est obligatoire")

        return cls(
            id=uuid4(),
            letter_type=LetterType.FILE,
            colli_id=colli_id,
            sender_id=sender_id,
            file_url=file_url,
            file_name=file_name,
            content=description,
            title=title.strip() if title else None
        )
    
    def update_content(self, new_content: str, editor_id: UUID) -> None:
        """
        Met à jour le contenu de la lettre.
        
        Args:
            new_content: Nouveau contenu.
            editor_id: ID de l'utilisateur qui modifie.
            
        Raises:
            CannotEditLetterException: Si l'utilisateur n'est pas l'auteur.
        """
        if editor_id != self.sender_id:
            raise CannotEditLetterException(
                "Seul l'auteur peut modifier sa lettre"
            )
        
        if self.letter_type == LetterType.TEXT:
            if not new_content or len(new_content.strip()) < 10:
                raise LetterValidationException(
                    "Le contenu doit faire au moins 10 caractères"
                )
        
        self.content = new_content.strip() if new_content else None
        self._touch()
    
    def can_user_edit(self, user_id: UUID) -> bool:
        """Vérifie si l'utilisateur peut modifier la lettre."""
        return user_id == self.sender_id
    
    @property
    def is_text_letter(self) -> bool:
        """Vérifie si c'est une lettre texte."""
        return self.letter_type == LetterType.TEXT
    
    @property
    def is_file_letter(self) -> bool:
        """Vérifie si c'est une lettre fichier."""
        return self.letter_type == LetterType.FILE
    
    def _touch(self) -> None:
        """Met à jour updated_at."""
        self.updated_at = datetime.utcnow()
    
    def collect_events(self) -> List:
        """Récupère et vide les événements en attente."""
        events = self._events.copy()
        self._events.clear()
        return events
    
    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Letter):
            return False
        return self.id == other.id
    
    def __hash__(self) -> int:
        return hash(self.id)
