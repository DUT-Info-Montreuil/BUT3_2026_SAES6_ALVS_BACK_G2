# tests/unit/application/use_cases/test_letter_use_cases.py
"""Tests unitaires pour les Use Cases Letter."""

import pytest
from uuid import uuid4, UUID

from src.application.use_cases.letter.create_letter import CreateTextLetterUseCase, CreateFileLetterUseCase
from src.application.use_cases.letter.get_letters import GetLettersForColliUseCase, GetLetterByIdUseCase
from src.application.use_cases.letter.delete_letter import DeleteLetterUseCase
from src.application.dtos.letter_dto import CreateTextLetterCommand, CreateFileLetterCommand
from src.application.use_cases.colli.create_colli import CreateColliUseCase, CreateColliCommand
from src.application.use_cases.colli.approve_colli import ApproveColliUseCase, ApproveColliCommand
from src.application.use_cases.colli.membership import JoinColliUseCase, AcceptMemberUseCase
from src.application.exceptions import NotFoundException, ForbiddenException
from src.infrastructure.persistence.in_memory.letter_repository import InMemoryLetterRepository
from src.infrastructure.persistence.in_memory.comment_repository import InMemoryCommentRepository
from src.infrastructure.persistence.in_memory.colli_repository import InMemoryColliRepository
from src.infrastructure.persistence.in_memory.user_repository import InMemoryUserRepository


class MockEventPublisher:
    def publish(self, event): pass
    def publish_all(self, events): pass


def to_uuid(id_str):
    """Convertit un ID string en UUID si nécessaire."""
    if isinstance(id_str, UUID):
        return id_str
    return UUID(id_str) if id_str else None


class TestCreateTextLetterUseCase:
    """Tests pour CreateTextLetterUseCase."""

    def _setup_colli(self, colli_repo):
        """Crée un COLLI actif avec un membre."""
        creator_id = uuid4()
        member_id = uuid4()

        create_uc = CreateColliUseCase(colli_repo)
        approve_uc = ApproveColliUseCase(colli_repo, MockEventPublisher())
        join_uc = JoinColliUseCase(colli_repo)
        accept_uc = AcceptMemberUseCase(colli_repo)

        colli = create_uc.execute(CreateColliCommand(
            name="Test COLLI", theme="Test", description=None, creator_id=creator_id
        ))
        colli_uuid = to_uuid(colli.id)
        approve_uc.execute(ApproveColliCommand(colli_id=colli_uuid, approver_id=uuid4()))
        join_uc.execute(colli_uuid, member_id)
        accept_uc.execute(colli_uuid, member_id, creator_id)

        return colli, creator_id, member_id
    
    def test_create_text_letter_success(self):
        """Doit créer une lettre texte."""
        colli_repo = InMemoryColliRepository()
        letter_repo = InMemoryLetterRepository()
        colli, creator_id, member_id = self._setup_colli(colli_repo)
        
        use_case = CreateTextLetterUseCase(letter_repo, colli_repo)
        
        result = use_case.execute(CreateTextLetterCommand(
            colli_id=to_uuid(colli.id),
            sender_id=member_id,
            content="Ceci est le contenu de ma lettre."
        ))
        
        assert result is not None
        assert result.letter_type == "text"
        assert result.content == "Ceci est le contenu de ma lettre."
    
    def test_create_letter_by_creator(self):
        """Le créateur peut aussi créer une lettre."""
        colli_repo = InMemoryColliRepository()
        letter_repo = InMemoryLetterRepository()
        colli, creator_id, member_id = self._setup_colli(colli_repo)
        
        use_case = CreateTextLetterUseCase(letter_repo, colli_repo)
        
        result = use_case.execute(CreateTextLetterCommand(
            colli_id=to_uuid(colli.id),
            sender_id=creator_id,
            content="Lettre du créateur."
        ))
        
        assert result is not None
    
    def test_create_letter_nonexistent_colli(self):
        """Doit lever NotFoundException si COLLI inexistant."""
        colli_repo = InMemoryColliRepository()
        letter_repo = InMemoryLetterRepository()
        
        use_case = CreateTextLetterUseCase(letter_repo, colli_repo)
        
        with pytest.raises(NotFoundException):
            use_case.execute(CreateTextLetterCommand(
                colli_id=uuid4(),
                sender_id=uuid4(),
                content="Ceci est un contenu suffisamment long."
            ))
    
    def test_create_letter_not_member(self):
        """Doit lever ForbiddenException si non-membre."""
        colli_repo = InMemoryColliRepository()
        letter_repo = InMemoryLetterRepository()
        colli, creator_id, member_id = self._setup_colli(colli_repo)
        
        use_case = CreateTextLetterUseCase(letter_repo, colli_repo)
        
        with pytest.raises(ForbiddenException):
            use_case.execute(CreateTextLetterCommand(
                colli_id=to_uuid(colli.id),
                sender_id=uuid4(),  # Non-membre
                content="Ceci est un contenu suffisamment long."
            ))


class TestCreateFileLetterUseCase:
    """Tests pour CreateFileLetterUseCase."""

    def _setup_colli(self, colli_repo):
        creator_id = uuid4()
        member_id = uuid4()

        create_uc = CreateColliUseCase(colli_repo)
        approve_uc = ApproveColliUseCase(colli_repo, MockEventPublisher())
        join_uc = JoinColliUseCase(colli_repo)
        accept_uc = AcceptMemberUseCase(colli_repo)

        colli = create_uc.execute(CreateColliCommand(
            name="Test COLLI", theme="Test", description=None, creator_id=creator_id
        ))
        colli_uuid = to_uuid(colli.id)
        approve_uc.execute(ApproveColliCommand(colli_id=colli_uuid, approver_id=uuid4()))
        join_uc.execute(colli_uuid, member_id)
        accept_uc.execute(colli_uuid, member_id, creator_id)

        return colli, creator_id, member_id
    
    def test_create_file_letter_success(self):
        """Doit créer une lettre fichier."""
        colli_repo = InMemoryColliRepository()
        letter_repo = InMemoryLetterRepository()
        colli, creator_id, member_id = self._setup_colli(colli_repo)
        
        use_case = CreateFileLetterUseCase(letter_repo, colli_repo)
        
        result = use_case.execute(CreateFileLetterCommand(
            colli_id=to_uuid(colli.id),
            sender_id=member_id,
            file_url="https://example.com/document.pdf",
            file_name="document.pdf",
            description="Un document important"
        ))
        
        assert result is not None
        assert result.letter_type == "file"
        assert result.file_url == "https://example.com/document.pdf"


class TestGetLettersForColliUseCase:
    """Tests pour GetLettersForColliUseCase."""

    def _setup_colli(self, colli_repo):
        creator_id = uuid4()
        member_id = uuid4()

        create_uc = CreateColliUseCase(colli_repo)
        approve_uc = ApproveColliUseCase(colli_repo, MockEventPublisher())
        join_uc = JoinColliUseCase(colli_repo)
        accept_uc = AcceptMemberUseCase(colli_repo)

        colli = create_uc.execute(CreateColliCommand(
            name="Test COLLI", theme="Test", description=None, creator_id=creator_id
        ))
        colli_uuid = to_uuid(colli.id)
        approve_uc.execute(ApproveColliCommand(colli_id=colli_uuid, approver_id=uuid4()))
        join_uc.execute(colli_uuid, member_id)
        accept_uc.execute(colli_uuid, member_id, creator_id)

        return colli, creator_id, member_id
    
    def test_get_letters_empty(self):
        """Doit retourner une liste vide."""
        colli_repo = InMemoryColliRepository()
        letter_repo = InMemoryLetterRepository()
        comment_repo = InMemoryCommentRepository()
        colli, creator_id, member_id = self._setup_colli(colli_repo)
        
        use_case = GetLettersForColliUseCase(letter_repo, comment_repo, colli_repo, InMemoryUserRepository())
        result = use_case.execute(to_uuid(colli.id), member_id, page=1, per_page=20)
        
        assert result.total == 0
        assert result.items == []
    
    def test_get_letters_with_data(self):
        """Doit lister les lettres."""
        colli_repo = InMemoryColliRepository()
        letter_repo = InMemoryLetterRepository()
        comment_repo = InMemoryCommentRepository()
        colli, creator_id, member_id = self._setup_colli(colli_repo)
        colli_uuid = to_uuid(colli.id)
        
        create_uc = CreateTextLetterUseCase(letter_repo, colli_repo)
        for i in range(3):
            create_uc.execute(CreateTextLetterCommand(
                colli_id=colli_uuid,
                sender_id=member_id,
                content=f"Lettre de test numéro {i} suffisamment longue"
            ))
        
        get_uc = GetLettersForColliUseCase(letter_repo, comment_repo, colli_repo, InMemoryUserRepository())
        result = get_uc.execute(colli_uuid, member_id, page=1, per_page=20)
        
        assert result.total == 3
        assert len(result.items) == 3
    
    def test_get_letters_not_member(self):
        """Doit lever ForbiddenException si non-membre."""
        colli_repo = InMemoryColliRepository()
        letter_repo = InMemoryLetterRepository()
        comment_repo = InMemoryCommentRepository()
        colli, creator_id, member_id = self._setup_colli(colli_repo)
        
        use_case = GetLettersForColliUseCase(letter_repo, comment_repo, colli_repo, InMemoryUserRepository())
        
        with pytest.raises(ForbiddenException):
            use_case.execute(to_uuid(colli.id), uuid4(), page=1, per_page=20)


class TestGetLetterByIdUseCase:
    """Tests pour GetLetterByIdUseCase."""

    def _setup_colli(self, colli_repo):
        creator_id = uuid4()
        member_id = uuid4()

        create_uc = CreateColliUseCase(colli_repo)
        approve_uc = ApproveColliUseCase(colli_repo, MockEventPublisher())
        join_uc = JoinColliUseCase(colli_repo)
        accept_uc = AcceptMemberUseCase(colli_repo)

        colli = create_uc.execute(CreateColliCommand(
            name="Test COLLI", theme="Test", description=None, creator_id=creator_id
        ))
        colli_uuid = to_uuid(colli.id)
        approve_uc.execute(ApproveColliCommand(colli_id=colli_uuid, approver_id=uuid4()))
        join_uc.execute(colli_uuid, member_id)
        accept_uc.execute(colli_uuid, member_id, creator_id)

        return colli, creator_id, member_id
    
    def test_get_letter_success(self):
        """Doit récupérer une lettre."""
        colli_repo = InMemoryColliRepository()
        letter_repo = InMemoryLetterRepository()
        comment_repo = InMemoryCommentRepository()
        colli, creator_id, member_id = self._setup_colli(colli_repo)
        
        create_uc = CreateTextLetterUseCase(letter_repo, colli_repo)
        letter = create_uc.execute(CreateTextLetterCommand(
            colli_id=to_uuid(colli.id),
            sender_id=member_id,
            content="Ceci est un contenu suffisamment long."
        ))
        
        get_uc = GetLetterByIdUseCase(letter_repo, comment_repo, colli_repo, InMemoryUserRepository())
        result = get_uc.execute(to_uuid(letter.id), member_id)
        
        assert result.id == letter.id
    
    def test_get_nonexistent_letter(self):
        """Doit lever NotFoundException."""
        colli_repo = InMemoryColliRepository()
        letter_repo = InMemoryLetterRepository()
        comment_repo = InMemoryCommentRepository()
        
        use_case = GetLetterByIdUseCase(letter_repo, comment_repo, colli_repo, InMemoryUserRepository())
        
        with pytest.raises(NotFoundException):
            use_case.execute(uuid4(), uuid4())


class TestDeleteLetterUseCase:
    """Tests pour DeleteLetterUseCase."""

    def _setup_colli(self, colli_repo):
        creator_id = uuid4()
        member_id = uuid4()

        create_uc = CreateColliUseCase(colli_repo)
        approve_uc = ApproveColliUseCase(colli_repo, MockEventPublisher())
        join_uc = JoinColliUseCase(colli_repo)
        accept_uc = AcceptMemberUseCase(colli_repo)

        colli = create_uc.execute(CreateColliCommand(
            name="Test COLLI", theme="Test", description=None, creator_id=creator_id
        ))
        colli_uuid = to_uuid(colli.id)
        approve_uc.execute(ApproveColliCommand(colli_id=colli_uuid, approver_id=uuid4()))
        join_uc.execute(colli_uuid, member_id)
        accept_uc.execute(colli_uuid, member_id, creator_id)

        return colli, creator_id, member_id
    
    def test_delete_by_author(self):
        """L'auteur peut supprimer sa lettre."""
        colli_repo = InMemoryColliRepository()
        letter_repo = InMemoryLetterRepository()
        colli, creator_id, member_id = self._setup_colli(colli_repo)
        
        create_uc = CreateTextLetterUseCase(letter_repo, colli_repo)
        letter = create_uc.execute(CreateTextLetterCommand(
            colli_id=to_uuid(colli.id),
            sender_id=member_id,
            content="Ceci est un contenu suffisamment long."
        ))
        
        delete_uc = DeleteLetterUseCase(letter_repo, colli_repo)
        result = delete_uc.execute(to_uuid(letter.id), member_id)
        
        assert result is True
    
    def test_delete_by_manager(self):
        """Un manager peut supprimer une lettre."""
        colli_repo = InMemoryColliRepository()
        letter_repo = InMemoryLetterRepository()
        colli, creator_id, member_id = self._setup_colli(colli_repo)
        
        create_uc = CreateTextLetterUseCase(letter_repo, colli_repo)
        letter = create_uc.execute(CreateTextLetterCommand(
            colli_id=to_uuid(colli.id),
            sender_id=member_id,
            content="Ceci est un contenu suffisamment long."
        ))
        
        delete_uc = DeleteLetterUseCase(letter_repo, colli_repo)
        result = delete_uc.execute(to_uuid(letter.id), creator_id)  # Manager
        
        assert result is True
    
    def test_delete_by_random_user(self):
        """Un utilisateur random ne peut pas supprimer."""
        colli_repo = InMemoryColliRepository()
        letter_repo = InMemoryLetterRepository()
        colli, creator_id, member_id = self._setup_colli(colli_repo)
        
        create_uc = CreateTextLetterUseCase(letter_repo, colli_repo)
        letter = create_uc.execute(CreateTextLetterCommand(
            colli_id=to_uuid(colli.id),
            sender_id=member_id,
            content="Ceci est un contenu suffisamment long."
        ))
        
        delete_uc = DeleteLetterUseCase(letter_repo, colli_repo)
        
        with pytest.raises(ForbiddenException):
            delete_uc.execute(to_uuid(letter.id), uuid4())
