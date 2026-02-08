# tests/unit/domain/collaboration/test_value_objects.py
"""Tests unitaires pour les Value Objects du domaine Collaboration."""

import pytest

from src.domain.collaboration.value_objects.colli_status import ColliStatus
from src.domain.collaboration.value_objects.member_role import MemberRole
from src.domain.collaboration.value_objects.file_attachment import FileAttachment, FileType


class TestColliStatus:
    """Tests pour ColliStatus."""
    
    def test_pending_can_transition_to_active(self):
        """PENDING peut transitionner vers ACTIVE."""
        assert ColliStatus.PENDING.can_transition_to(ColliStatus.ACTIVE)
    
    def test_pending_can_transition_to_rejected(self):
        """PENDING peut transitionner vers REJECTED."""
        assert ColliStatus.PENDING.can_transition_to(ColliStatus.REJECTED)
    
    def test_active_can_transition_to_completed(self):
        """ACTIVE peut transitionner vers COMPLETED."""
        assert ColliStatus.ACTIVE.can_transition_to(ColliStatus.COMPLETED)
    
    def test_active_cannot_transition_to_pending(self):
        """ACTIVE ne peut pas revenir à PENDING."""
        assert not ColliStatus.ACTIVE.can_transition_to(ColliStatus.PENDING)
    
    def test_rejected_cannot_transition(self):
        """REJECTED est un état final."""
        assert not ColliStatus.REJECTED.can_transition_to(ColliStatus.ACTIVE)
        assert not ColliStatus.REJECTED.can_transition_to(ColliStatus.PENDING)


class TestMemberRole:
    """Tests pour MemberRole."""
    
    def test_manager_has_all_permissions(self):
        """MANAGER a toutes les permissions."""
        assert MemberRole.MANAGER.can_moderate()
        assert MemberRole.MANAGER.can_manage_members()
        assert MemberRole.MANAGER.has_permission(MemberRole.MEMBER)
    
    def test_moderator_can_moderate(self):
        """MODERATOR peut modérer."""
        assert MemberRole.MODERATOR.can_moderate()
        assert not MemberRole.MODERATOR.can_manage_members()
    
    def test_member_cannot_moderate(self):
        """MEMBER ne peut pas modérer."""
        assert not MemberRole.MEMBER.can_moderate()
        assert not MemberRole.MEMBER.can_manage_members()
    
    def test_role_hierarchy(self):
        """La hiérarchie des rôles fonctionne."""
        assert MemberRole.MANAGER.has_permission(MemberRole.MODERATOR)
        assert MemberRole.MODERATOR.has_permission(MemberRole.PATRON)
        assert not MemberRole.MEMBER.has_permission(MemberRole.MODERATOR)


class TestFileAttachment:
    """Tests pour FileAttachment."""
    
    def test_create_valid_image(self):
        """Une image valide peut être créée."""
        attachment = FileAttachment.create(
            url="/uploads/photo.jpg",
            original_name="photo.jpg",
            size_bytes=1024 * 100,  # 100 KB
            mime_type="image/jpeg"
        )
        
        assert attachment.file_type == FileType.IMAGE
        assert attachment.original_name == "photo.jpg"
    
    def test_create_invalid_extension_raises_error(self):
        """Une extension non autorisée lève une erreur."""
        with pytest.raises(ValueError, match="Extension.*non autorisée"):
            FileAttachment.create(
                url="/uploads/script.exe",
                original_name="script.exe",
                size_bytes=1024,
                mime_type="application/x-executable"
            )
    
    def test_create_oversized_file_raises_error(self):
        """Un fichier trop volumineux lève une erreur."""
        with pytest.raises(ValueError, match="trop volumineux"):
            FileAttachment.create(
                url="/uploads/huge.jpg",
                original_name="huge.jpg",
                size_bytes=20 * 1024 * 1024,  # 20 MB > 16 MB max
                mime_type="image/jpeg"
            )
    
    def test_size_mb_property(self):
        """La conversion en MB fonctionne."""
        attachment = FileAttachment.create(
            url="/uploads/file.pdf",
            original_name="file.pdf",
            size_bytes=5 * 1024 * 1024,  # 5 MB
            mime_type="application/pdf"
        )
        
        assert attachment.size_mb == 5.0
