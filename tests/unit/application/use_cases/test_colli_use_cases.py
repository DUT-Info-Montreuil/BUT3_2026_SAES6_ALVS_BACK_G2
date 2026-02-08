# tests/unit/application/use_cases/test_colli_use_cases.py
"""Tests unitaires pour les Use Cases Colli."""

import pytest
from uuid import uuid4, UUID

from src.application.use_cases.colli.create_colli import CreateColliUseCase, CreateColliCommand
from src.application.use_cases.colli.approve_colli import ApproveColliUseCase, ApproveColliCommand
from src.application.use_cases.colli.get_colli import GetColliByIdUseCase, ListCollisUseCase
from src.application.use_cases.colli.delete_colli import DeleteColliUseCase
from src.application.use_cases.colli.membership import JoinColliUseCase, LeaveColliUseCase
from src.application.use_cases.colli.list_members import ListMembersUseCase
from src.application.exceptions import NotFoundException, ForbiddenException
from src.infrastructure.persistence.in_memory.colli_repository import InMemoryColliRepository


class ColliTestEventPublisher:
    def publish(self, event): pass
    def publish_all(self, events): pass


def to_uuid(id_str):
    """Convertit un ID string en UUID si nécessaire."""
    if isinstance(id_str, UUID):
        return id_str
    return UUID(id_str) if id_str else None


class TestCreateColliUseCase:
    """Tests pour CreateColliUseCase."""
    
    def test_create_colli_success(self):
        """Doit créer un COLLI avec succès."""
        repo = InMemoryColliRepository()
        use_case = CreateColliUseCase(repo)
        
        result = use_case.execute(CreateColliCommand(
            name="Test COLLI",
            theme="Littérature",
            description="Description test",
            creator_id=uuid4()
        ))
        
        assert result is not None
        assert result.name == "Test COLLI"
        assert result.theme == "Littérature"
        assert result.status == "pending"
    
    def test_create_colli_without_description(self):
        """Doit créer un COLLI sans description."""
        repo = InMemoryColliRepository()
        use_case = CreateColliUseCase(repo)
        
        result = use_case.execute(CreateColliCommand(
            name="Test COLLI",
            theme="Science",
            description=None,
            creator_id=uuid4()
        ))
        
        assert result is not None
        assert result.description is None


class TestApproveColliUseCase:
    """Tests pour ApproveColliUseCase."""
    
    def test_approve_colli_success(self):
        """Doit approuver un COLLI."""
        repo = InMemoryColliRepository()
        create_uc = CreateColliUseCase(repo)
        approve_uc = ApproveColliUseCase(repo, ColliTestEventPublisher())
        
        creator_id = uuid4()
        colli = create_uc.execute(CreateColliCommand(
            name="Test", theme="Test", description=None, creator_id=creator_id
        ))
        
        result = approve_uc.execute(ApproveColliCommand(
            colli_id=to_uuid(colli.id),
            approver_id=uuid4()
        ))
        
        assert result.status == "active"
    
    def test_approve_nonexistent_colli(self):
        """Doit lever NotFoundException si COLLI inexistant."""
        repo = InMemoryColliRepository()
        approve_uc = ApproveColliUseCase(repo, ColliTestEventPublisher())
        
        with pytest.raises(NotFoundException):
            approve_uc.execute(ApproveColliCommand(
                colli_id=uuid4(),
                approver_id=uuid4()
            ))


class TestGetColliByIdUseCase:
    """Tests pour GetColliByIdUseCase."""
    
    def test_get_colli_success(self):
        """Doit récupérer un COLLI existant."""
        repo = InMemoryColliRepository()
        create_uc = CreateColliUseCase(repo)
        get_uc = GetColliByIdUseCase(repo)
        
        colli = create_uc.execute(CreateColliCommand(
            name="Test", theme="Test", description=None, creator_id=uuid4()
        ))
        
        result = get_uc.execute(to_uuid(colli.id), uuid4())
        
        assert result.id == colli.id
        assert result.name == "Test"
    
    def test_get_nonexistent_colli(self):
        """Doit lever NotFoundException si COLLI inexistant."""
        repo = InMemoryColliRepository()
        get_uc = GetColliByIdUseCase(repo)
        
        with pytest.raises(NotFoundException):
            get_uc.execute(uuid4(), uuid4())


class TestListCollisUseCase:
    """Tests pour ListCollisUseCase."""
    
    def test_list_empty(self):
        """Doit retourner une liste vide."""
        repo = InMemoryColliRepository()
        use_case = ListCollisUseCase(repo)
        
        result = use_case.execute(page=1, per_page=20)
        
        assert result['total'] == 0
        assert result['items'] == []
    
    def test_list_with_collis(self):
        """Doit lister les COLLIs."""
        repo = InMemoryColliRepository()
        create_uc = CreateColliUseCase(repo)
        use_case = ListCollisUseCase(repo)
        
        for i in range(3):
            create_uc.execute(CreateColliCommand(
                name=f"COLLI {i}", theme="Test", description=None, creator_id=uuid4()
            ))
        
        result = use_case.execute(page=1, per_page=20)
        
        assert result['total'] == 3
        assert len(result['items']) == 3
    
    def test_list_pagination(self):
        """Doit paginer les résultats."""
        repo = InMemoryColliRepository()
        create_uc = CreateColliUseCase(repo)
        use_case = ListCollisUseCase(repo)
        
        for i in range(5):
            create_uc.execute(CreateColliCommand(
                name=f"COLLI {i}", theme="Test", description=None, creator_id=uuid4()
            ))
        
        result = use_case.execute(page=1, per_page=2)
        
        assert result['total'] == 5
        assert len(result['items']) == 2
        assert result['has_more'] is True


class TestDeleteColliUseCase:
    """Tests pour DeleteColliUseCase."""
    
    def test_delete_by_creator(self):
        """Le créateur peut supprimer son COLLI."""
        repo = InMemoryColliRepository()
        create_uc = CreateColliUseCase(repo)
        delete_uc = DeleteColliUseCase(repo)
        
        creator_id = uuid4()
        colli = create_uc.execute(CreateColliCommand(
            name="Test", theme="Test", description=None, creator_id=creator_id
        ))
        
        result = delete_uc.execute(to_uuid(colli.id), creator_id)
        
        assert result is True
    
    def test_delete_by_non_creator(self):
        """Un non-créateur ne peut pas supprimer."""
        repo = InMemoryColliRepository()
        create_uc = CreateColliUseCase(repo)
        delete_uc = DeleteColliUseCase(repo)
        
        creator_id = uuid4()
        other_user_id = uuid4()
        colli = create_uc.execute(CreateColliCommand(
            name="Test", theme="Test", description=None, creator_id=creator_id
        ))
        
        with pytest.raises(ForbiddenException):
            delete_uc.execute(to_uuid(colli.id), other_user_id)


class TestJoinColliUseCase:
    """Tests pour JoinColliUseCase."""
    
    def _create_active_colli(self, repo):
        """Helper pour créer un COLLI actif."""
        creator_id = uuid4()
        create_uc = CreateColliUseCase(repo)
        approve_uc = ApproveColliUseCase(repo, ColliTestEventPublisher())
        
        colli = create_uc.execute(CreateColliCommand(
            name="Test", theme="Test", description=None, creator_id=creator_id
        ))
        approve_uc.execute(ApproveColliCommand(colli_id=to_uuid(colli.id), approver_id=uuid4()))
        return colli, creator_id
    
    def test_join_success(self):
        """Un utilisateur peut rejoindre un COLLI actif."""
        repo = InMemoryColliRepository()
        colli, _ = self._create_active_colli(repo)
        join_uc = JoinColliUseCase(repo)
        
        result = join_uc.execute(to_uuid(colli.id), uuid4())
        
        assert result is not None
    
    def test_join_inactive_colli(self):
        """Ne peut pas rejoindre un COLLI inactif."""
        repo = InMemoryColliRepository()
        create_uc = CreateColliUseCase(repo)
        join_uc = JoinColliUseCase(repo)
        
        colli = create_uc.execute(CreateColliCommand(
            name="Test", theme="Test", description=None, creator_id=uuid4()
        ))
        
        with pytest.raises(ForbiddenException):
            join_uc.execute(to_uuid(colli.id), uuid4())


class TestLeaveColliUseCase:
    """Tests pour LeaveColliUseCase."""
    
    def test_leave_as_member(self):
        """Un membre peut quitter."""
        repo = InMemoryColliRepository()
        create_uc = CreateColliUseCase(repo)
        approve_uc = ApproveColliUseCase(repo, ColliTestEventPublisher())
        join_uc = JoinColliUseCase(repo)
        leave_uc = LeaveColliUseCase(repo)
        
        creator_id = uuid4()
        member_id = uuid4()
        
        colli = create_uc.execute(CreateColliCommand(
            name="Test", theme="Test", description=None, creator_id=creator_id
        ))
        colli_uuid = to_uuid(colli.id)
        approve_uc.execute(ApproveColliCommand(colli_id=colli_uuid, approver_id=uuid4()))
        join_uc.execute(colli_uuid, member_id)
        
        result = leave_uc.execute(colli_uuid, member_id)
        
        assert result is True
    
    def test_creator_cannot_leave(self):
        """Le créateur ne peut pas quitter."""
        repo = InMemoryColliRepository()
        create_uc = CreateColliUseCase(repo)
        approve_uc = ApproveColliUseCase(repo, ColliTestEventPublisher())
        leave_uc = LeaveColliUseCase(repo)
        
        creator_id = uuid4()
        colli = create_uc.execute(CreateColliCommand(
            name="Test", theme="Test", description=None, creator_id=creator_id
        ))
        colli_uuid = to_uuid(colli.id)
        
        approve_uc.execute(ApproveColliCommand(colli_id=colli_uuid, approver_id=uuid4()))
        
        with pytest.raises(ForbiddenException):
            leave_uc.execute(colli_uuid, creator_id)


class TestListMembersUseCase:
    """Tests pour ListMembersUseCase."""
    
    def test_list_members(self):
        """Doit lister les membres."""
        repo = InMemoryColliRepository()
        create_uc = CreateColliUseCase(repo)
        approve_uc = ApproveColliUseCase(repo, ColliTestEventPublisher())
        join_uc = JoinColliUseCase(repo)
        list_uc = ListMembersUseCase(repo)
        
        creator_id = uuid4()
        colli = create_uc.execute(CreateColliCommand(
            name="Test", theme="Test", description=None, creator_id=creator_id
        ))
        colli_uuid = to_uuid(colli.id)
        approve_uc.execute(ApproveColliCommand(colli_id=colli_uuid, approver_id=uuid4()))
        join_uc.execute(colli_uuid, uuid4())
        join_uc.execute(colli_uuid, uuid4())
        
        result = list_uc.execute(colli_uuid, creator_id)
        
        assert result['total'] == 3  # creator + 2 members

