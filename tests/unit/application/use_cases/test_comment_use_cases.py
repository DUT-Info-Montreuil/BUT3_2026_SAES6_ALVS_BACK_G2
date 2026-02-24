# tests/unit/application/use_cases/test_comment_use_cases.py
"""Tests unitaires pour les Use Cases Comment."""

import pytest
from uuid import uuid4, UUID

from src.application.use_cases.comment.create_comment import CreateCommentUseCase
from src.application.use_cases.comment.get_comments import GetCommentsForLetterUseCase
from src.application.use_cases.comment.delete_comment import DeleteCommentUseCase
from src.application.dtos.comment_dto import CreateCommentCommand
from src.application.dtos.letter_dto import CreateTextLetterCommand
from src.application.use_cases.letter.create_letter import CreateTextLetterUseCase
from src.application.use_cases.colli.create_colli import CreateColliUseCase, CreateColliCommand
from src.application.use_cases.colli.approve_colli import ApproveColliUseCase, ApproveColliCommand
from src.application.use_cases.colli.membership import JoinColliUseCase, AcceptMemberUseCase
from src.application.exceptions import NotFoundException, ForbiddenException
from src.infrastructure.persistence.in_memory.letter_repository import InMemoryLetterRepository
from src.infrastructure.persistence.in_memory.comment_repository import InMemoryCommentRepository
from src.infrastructure.persistence.in_memory.colli_repository import InMemoryColliRepository


class MockEventPublisher:
    def publish(self, event): pass
    def publish_all(self, events): pass


def to_uuid(id_str):
    """Convertit un ID string en UUID si nécessaire."""
    if isinstance(id_str, UUID):
        return id_str
    return UUID(id_str) if id_str else None


class CommentTestBase:
    """Base pour les tests Comment avec setup COLLI + Letter."""
    
    def _setup(self):
        """Crée repos, COLLI actif et lettre."""
        colli_repo = InMemoryColliRepository()
        letter_repo = InMemoryLetterRepository()
        comment_repo = InMemoryCommentRepository()

        creator_id = uuid4()
        member_id = uuid4()

        create_colli = CreateColliUseCase(colli_repo)
        approve_colli = ApproveColliUseCase(colli_repo, MockEventPublisher())
        join_colli = JoinColliUseCase(colli_repo)
        accept_colli = AcceptMemberUseCase(colli_repo)

        colli = create_colli.execute(CreateColliCommand(
            name="Test COLLI", theme="Test", description=None, creator_id=creator_id
        ))
        colli_uuid = to_uuid(colli.id)
        approve_colli.execute(ApproveColliCommand(colli_id=colli_uuid, approver_id=uuid4()))
        join_colli.execute(colli_uuid, member_id)
        accept_colli.execute(colli_uuid, member_id, creator_id)

        create_letter = CreateTextLetterUseCase(letter_repo, colli_repo)
        letter = create_letter.execute(CreateTextLetterCommand(
            colli_id=colli_uuid,
            sender_id=member_id,
            content="Contenu de la lettre"
        ))
        
        return {
            'colli_repo': colli_repo,
            'letter_repo': letter_repo,
            'comment_repo': comment_repo,
            'colli': colli,
            'letter': letter,
            'creator_id': creator_id,
            'member_id': member_id
        }


class TestCreateCommentUseCase(CommentTestBase):
    """Tests pour CreateCommentUseCase."""
    
    def test_create_comment_success(self):
        """Doit créer un commentaire."""
        ctx = self._setup()
        use_case = CreateCommentUseCase(ctx['comment_repo'], ctx['letter_repo'], ctx['colli_repo'])
        
        result = use_case.execute(CreateCommentCommand(
            letter_id=to_uuid(ctx['letter'].id),
            sender_id=ctx['member_id'],
            content="Super lettre !"
        ))
        
        assert result is not None
        assert result.content == "Super lettre !"
    
    def test_create_comment_by_creator(self):
        """Le créateur peut commenter."""
        ctx = self._setup()
        use_case = CreateCommentUseCase(ctx['comment_repo'], ctx['letter_repo'], ctx['colli_repo'])
        
        result = use_case.execute(CreateCommentCommand(
            letter_id=to_uuid(ctx['letter'].id),
            sender_id=ctx['creator_id'],
            content="Commentaire du créateur"
        ))
        
        assert result is not None
    
    def test_create_comment_nonexistent_letter(self):
        """Doit lever NotFoundException si lettre inexistante."""
        ctx = self._setup()
        use_case = CreateCommentUseCase(ctx['comment_repo'], ctx['letter_repo'], ctx['colli_repo'])
        
        with pytest.raises(NotFoundException):
            use_case.execute(CreateCommentCommand(
                letter_id=uuid4(),
                sender_id=uuid4(),
                content="Ceci est un contenu suffisamment long."
            ))
    
    def test_create_comment_not_member(self):
        """Doit lever ForbiddenException si non-membre."""
        ctx = self._setup()
        use_case = CreateCommentUseCase(ctx['comment_repo'], ctx['letter_repo'], ctx['colli_repo'])
        
        with pytest.raises(ForbiddenException):
            use_case.execute(CreateCommentCommand(
                letter_id=to_uuid(ctx['letter'].id),
                sender_id=uuid4(),  # Non-membre
                content="Ceci est un contenu suffisamment long."
            ))


class TestGetCommentsForLetterUseCase(CommentTestBase):
    """Tests pour GetCommentsForLetterUseCase."""
    
    def test_get_comments_empty(self):
        """Doit retourner une liste vide."""
        ctx = self._setup()
        use_case = GetCommentsForLetterUseCase(ctx['comment_repo'], ctx['letter_repo'], ctx['colli_repo'])
        
        result = use_case.execute(to_uuid(ctx['letter'].id), ctx['member_id'], page=1, per_page=50)
        
        assert result.total == 0
        assert result.items == []
    
    def test_get_comments_with_data(self):
        """Doit lister les commentaires."""
        ctx = self._setup()
        create_uc = CreateCommentUseCase(ctx['comment_repo'], ctx['letter_repo'], ctx['colli_repo'])
        letter_uuid = to_uuid(ctx['letter'].id)
        
        for i in range(3):
            create_uc.execute(CreateCommentCommand(
                letter_id=letter_uuid,
                sender_id=ctx['member_id'],
                content=f"Commentaire {i}"
            ))
        
        get_uc = GetCommentsForLetterUseCase(ctx['comment_repo'], ctx['letter_repo'], ctx['colli_repo'])
        result = get_uc.execute(letter_uuid, ctx['member_id'], page=1, per_page=50)
        
        assert result.total == 3
        assert len(result.items) == 3
    
    def test_get_comments_pagination(self):
        """Doit paginer les commentaires."""
        ctx = self._setup()
        create_uc = CreateCommentUseCase(ctx['comment_repo'], ctx['letter_repo'], ctx['colli_repo'])
        letter_uuid = to_uuid(ctx['letter'].id)
        
        for i in range(5):
            create_uc.execute(CreateCommentCommand(
                letter_id=letter_uuid,
                sender_id=ctx['member_id'],
                content=f"Commentaire {i}"
            ))
        
        get_uc = GetCommentsForLetterUseCase(ctx['comment_repo'], ctx['letter_repo'], ctx['colli_repo'])
        result = get_uc.execute(letter_uuid, ctx['member_id'], page=1, per_page=2)
        
        assert result.total == 5
        assert len(result.items) == 2
        assert result.has_more is True
    
    def test_get_comments_not_member(self):
        """Doit lever ForbiddenException si non-membre."""
        ctx = self._setup()
        use_case = GetCommentsForLetterUseCase(ctx['comment_repo'], ctx['letter_repo'], ctx['colli_repo'])
        
        with pytest.raises(ForbiddenException):
            use_case.execute(to_uuid(ctx['letter'].id), uuid4(), page=1, per_page=50)


class TestDeleteCommentUseCase(CommentTestBase):
    """Tests pour DeleteCommentUseCase."""
    
    def test_delete_by_author(self):
        """L'auteur peut supprimer son commentaire."""
        ctx = self._setup()
        create_uc = CreateCommentUseCase(ctx['comment_repo'], ctx['letter_repo'], ctx['colli_repo'])
        comment = create_uc.execute(CreateCommentCommand(
            letter_id=to_uuid(ctx['letter'].id),
            sender_id=ctx['member_id'],
            content="Mon commentaire"
        ))
        
        delete_uc = DeleteCommentUseCase(ctx['comment_repo'], ctx['letter_repo'], ctx['colli_repo'])
        result = delete_uc.execute(to_uuid(comment.id), ctx['member_id'])
        
        assert result is True
    
    def test_delete_by_moderator(self):
        """Un modérateur peut supprimer un commentaire."""
        ctx = self._setup()
        create_uc = CreateCommentUseCase(ctx['comment_repo'], ctx['letter_repo'], ctx['colli_repo'])
        comment = create_uc.execute(CreateCommentCommand(
            letter_id=to_uuid(ctx['letter'].id),
            sender_id=ctx['member_id'],
            content="Commentaire à modérer"
        ))
        
        delete_uc = DeleteCommentUseCase(ctx['comment_repo'], ctx['letter_repo'], ctx['colli_repo'])
        result = delete_uc.execute(to_uuid(comment.id), ctx['creator_id'])  # Manager
        
        assert result is True
    
    def test_delete_nonexistent_comment(self):
        """Doit lever NotFoundException."""
        ctx = self._setup()
        use_case = DeleteCommentUseCase(ctx['comment_repo'], ctx['letter_repo'], ctx['colli_repo'])
        
        with pytest.raises(NotFoundException):
            use_case.execute(uuid4(), uuid4())
    
    def test_delete_by_random_user(self):
        """Un utilisateur random ne peut pas supprimer."""
        ctx = self._setup()
        create_uc = CreateCommentUseCase(ctx['comment_repo'], ctx['letter_repo'], ctx['colli_repo'])
        comment = create_uc.execute(CreateCommentCommand(
            letter_id=to_uuid(ctx['letter'].id),
            sender_id=ctx['member_id'],
            content="Commentaire"
        ))
        
        delete_uc = DeleteCommentUseCase(ctx['comment_repo'], ctx['letter_repo'], ctx['colli_repo'])
        
        with pytest.raises(ForbiddenException):
            delete_uc.execute(to_uuid(comment.id), uuid4())
