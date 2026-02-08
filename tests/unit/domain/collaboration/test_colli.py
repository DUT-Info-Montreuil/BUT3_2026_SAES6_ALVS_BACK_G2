# tests/unit/domain/collaboration/test_colli.py
"""Tests unitaires pour l'entité Colli."""

import pytest
from uuid import uuid4

from src.domain.collaboration.entities.colli import (
    Colli,
    ColliAlreadyActiveException,
    UserAlreadyMemberException,
    UserNotMemberException,
    InactiveColliException
)
from src.domain.collaboration.value_objects.colli_status import ColliStatus
from src.domain.collaboration.value_objects.member_role import MemberRole
from src.domain.collaboration.events import ColliApproved, ColliRejected, MemberAdded


class TestColliCreation:
    """Tests pour la création de COLLI."""
    
    def test_create_colli_with_valid_data(self):
        """Un COLLI peut être créé avec des données valides."""
        creator_id = uuid4()
        
        colli = Colli.create(
            name="Test COLLI",
            theme="Littérature",
            creator_id=creator_id,
            description="Description"
        )
        
        assert colli.name == "Test COLLI"
        assert colli.theme == "Littérature"
        assert colli.creator_id == creator_id
        assert colli.status == ColliStatus.PENDING
        assert colli.member_count == 0
    
    def test_create_colli_strips_whitespace(self):
        """Les espaces sont supprimés autour du nom."""
        colli = Colli.create(
            name="  Nom avec espaces  ",
            theme="Thème",
            creator_id=uuid4()
        )
        
        assert colli.name == "Nom avec espaces"
    
    def test_create_colli_with_short_name_raises_error(self):
        """Un nom trop court lève une erreur."""
        with pytest.raises(ValueError, match="au moins 3 caractères"):
            Colli.create(
                name="AB",
                theme="Thème",
                creator_id=uuid4()
            )
    
    def test_create_colli_without_theme_raises_error(self):
        """Un thème vide lève une erreur."""
        with pytest.raises(ValueError, match="thème.*obligatoire"):
            Colli.create(
                name="Nom valide",
                theme="",
                creator_id=uuid4()
            )


class TestColliApproval:
    """Tests pour le workflow d'approbation."""
    
    def test_approve_pending_colli(self):
        """Un COLLI en attente peut être approuvé."""
        colli = Colli.create(name="Test", theme="Thème", creator_id=uuid4())
        admin_id = uuid4()
        
        colli.approve(approved_by=admin_id)
        
        assert colli.status == ColliStatus.ACTIVE
        assert colli.member_count == 1  # Créateur ajouté comme manager
    
    def test_approve_adds_creator_as_manager(self):
        """L'approbation ajoute automatiquement le créateur comme manager."""
        creator_id = uuid4()
        colli = Colli.create(name="Test", theme="Thème", creator_id=creator_id)
        
        colli.approve()
        
        membership = colli.get_member(creator_id)
        assert membership is not None
        assert membership.role == MemberRole.MANAGER
    
    def test_approve_emits_domain_event(self):
        """L'approbation émet un événement ColliApproved."""
        colli = Colli.create(name="Test", theme="Thème", creator_id=uuid4())
        admin_id = uuid4()
        
        colli.approve(approved_by=admin_id)
        events = colli.collect_events()
        
        assert len(events) >= 1
        approved_events = [e for e in events if isinstance(e, ColliApproved)]
        assert len(approved_events) == 1
        assert approved_events[0].colli_id == colli.id
    
    def test_approve_active_colli_raises_error(self):
        """Un COLLI déjà actif ne peut pas être ré-approuvé."""
        colli = Colli.create(name="Test", theme="Thème", creator_id=uuid4())
        colli.approve()
        
        with pytest.raises(ColliAlreadyActiveException):
            colli.approve()
    
    def test_reject_pending_colli(self):
        """Un COLLI en attente peut être rejeté."""
        colli = Colli.create(name="Test", theme="Thème", creator_id=uuid4())
        
        colli.reject(reason="Thème non conforme")
        
        assert colli.status == ColliStatus.REJECTED
    
    def test_reject_emits_domain_event(self):
        """Le rejet émet un événement ColliRejected."""
        colli = Colli.create(name="Test", theme="Thème", creator_id=uuid4())
        
        colli.reject(reason="Raison")
        events = colli.collect_events()
        
        assert any(isinstance(e, ColliRejected) for e in events)


class TestColliMembership:
    """Tests pour la gestion des membres."""
    
    def test_add_member_to_active_colli(self):
        """Un membre peut être ajouté à un COLLI actif."""
        colli = Colli.create(name="Test", theme="Thème", creator_id=uuid4())
        colli.approve()
        user_id = uuid4()
        
        membership = colli.add_member(user_id, MemberRole.MEMBER)
        
        assert colli.is_member(user_id)
        assert membership.role == MemberRole.MEMBER
    
    def test_add_member_to_inactive_colli_raises_error(self):
        """On ne peut pas ajouter un membre à un COLLI inactif."""
        colli = Colli.create(name="Test", theme="Thème", creator_id=uuid4())
        # Colli est en PENDING, pas ACTIVE
        
        with pytest.raises(InactiveColliException):
            colli.add_member(uuid4())
    
    def test_add_existing_member_raises_error(self):
        """Ajouter un membre existant lève une erreur."""
        creator_id = uuid4()
        colli = Colli.create(name="Test", theme="Thème", creator_id=creator_id)
        colli.approve()
        
        with pytest.raises(UserAlreadyMemberException):
            colli.add_member(creator_id)  # Déjà manager
    
    def test_remove_member(self):
        """Un membre peut être retiré."""
        creator_id = uuid4()
        colli = Colli.create(name="Test", theme="Thème", creator_id=creator_id)
        colli.approve()
        user_id = uuid4()
        colli.add_member(user_id)
        
        colli.remove_member(user_id)
        
        assert not colli.is_member(user_id)
    
    def test_remove_non_member_raises_error(self):
        """Retirer un non-membre lève une erreur."""
        colli = Colli.create(name="Test", theme="Thème", creator_id=uuid4())
        colli.approve()
        
        with pytest.raises(UserNotMemberException):
            colli.remove_member(uuid4())
    
    def test_promote_member(self):
        """Un membre peut être promu."""
        colli = Colli.create(name="Test", theme="Thème", creator_id=uuid4())
        colli.approve()
        user_id = uuid4()
        colli.add_member(user_id, MemberRole.MEMBER)
        
        colli.promote_member(user_id, MemberRole.MODERATOR)
        
        membership = colli.get_member(user_id)
        assert membership.role == MemberRole.MODERATOR


class TestColliQueries:
    """Tests pour les méthodes de requête."""
    
    def test_is_active(self):
        """is_active retourne True seulement pour un COLLI actif."""
        colli = Colli.create(name="Test", theme="Thème", creator_id=uuid4())
        
        assert not colli.is_active
        
        colli.approve()
        assert colli.is_active
    
    def test_can_user_write_for_member(self):
        """Un membre peut écrire dans un COLLI actif."""
        creator_id = uuid4()
        colli = Colli.create(name="Test", theme="Thème", creator_id=creator_id)
        colli.approve()
        
        assert colli.can_user_write(creator_id)
    
    def test_can_user_write_for_non_member(self):
        """Un non-membre ne peut pas écrire."""
        colli = Colli.create(name="Test", theme="Thème", creator_id=uuid4())
        colli.approve()
        
        assert not colli.can_user_write(uuid4())
