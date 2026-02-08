# tests/unit/test_notification_service.py
"""Tests unitaires pour le service de notifications."""

import pytest
from uuid import uuid4
from datetime import datetime

from src.domain.notification.entities.notification import Notification, NotificationType
from src.infrastructure.persistence.in_memory.notification_repository import InMemoryNotificationRepository


class TestNotificationEntity:
    """Tests pour l'entite Notification."""
    
    def test_create_notification(self):
        """Test: creation d'une notification."""
        user_id = uuid4()
        notification = Notification(
            user_id=user_id,
            type=NotificationType.NEW_LETTER,
            title="Test Title",
            message="Test message"
        )
        
        assert notification.user_id == user_id
        assert notification.type == NotificationType.NEW_LETTER
        assert notification.title == "Test Title"
        assert notification.message == "Test message"
        assert notification.read is False
    
    def test_mark_as_read(self):
        """Test: marquer une notification comme lue."""
        notification = Notification(
            user_id=uuid4(),
            type=NotificationType.NEW_COMMENT,
            title="Test",
            message="Test"
        )
        
        assert notification.read is False
        notification.mark_as_read()
        assert notification.read is True
        assert notification.read_at is not None
    
    def test_to_dict(self):
        """Test: conversion en dictionnaire."""
        user_id = uuid4()
        notification = Notification(
            user_id=user_id,
            type=NotificationType.COLLI_APPROVED,
            title="COLLI Approved",
            message="Your COLLI was approved"
        )
        
        data = notification.to_dict()
        
        assert 'id' in data
        assert data['user_id'] == str(user_id)
        assert data['type'] == 'colli_approved'
        assert data['title'] == "COLLI Approved"
        assert data['read'] is False
    
    def test_notification_type_alias(self):
        """Test: alias notification_type fonctionne."""
        notification = Notification(
            user_id=uuid4(),
            type=NotificationType.NEW_LETTER,
            title="Test",
            message="Test"
        )
        
        assert notification.notification_type == NotificationType.NEW_LETTER


class TestNotificationRepository:
    """Tests pour le repository de notifications."""
    
    def test_save_and_find(self):
        """Test: sauvegarder et retrouver une notification."""
        repo = InMemoryNotificationRepository()
        user_id = uuid4()
        
        notification = Notification(
            user_id=user_id,
            type=NotificationType.NEW_LETTER,
            title="Test",
            message="Test"
        )
        
        repo.save(notification)
        found = repo.find_by_id(notification.id)
        
        assert found is not None
        assert found.id == notification.id
    
    def test_find_by_user(self):
        """Test: trouver les notifications d'un utilisateur."""
        repo = InMemoryNotificationRepository()
        user_id = uuid4()
        other_user_id = uuid4()
        
        # Creer des notifications pour differents utilisateurs
        for i in range(3):
            repo.save(Notification(
                user_id=user_id,
                type=NotificationType.NEW_LETTER,
                title=f"Notification {i}",
                message="Test"
            ))
        
        repo.save(Notification(
            user_id=other_user_id,
            type=NotificationType.NEW_COMMENT,
            title="Other user notification",
            message="Test"
        ))
        
        user_notifications = repo.find_by_user(user_id)
        
        assert len(user_notifications) == 3
        for n in user_notifications:
            assert n.user_id == user_id
    
    def test_count_unread(self):
        """Test: compter les notifications non lues."""
        repo = InMemoryNotificationRepository()
        user_id = uuid4()
        
        # Creer 3 notifications
        for i in range(3):
            repo.save(Notification(
                user_id=user_id,
                type=NotificationType.NEW_LETTER,
                title=f"Notification {i}",
                message="Test"
            ))
        
        assert repo.count_unread(user_id) == 3
        
        # Marquer une comme lue
        notifications = repo.find_by_user(user_id)
        repo.mark_as_read(notifications[0].id)
        
        assert repo.count_unread(user_id) == 2
    
    def test_mark_all_as_read(self):
        """Test: marquer toutes les notifications comme lues."""
        repo = InMemoryNotificationRepository()
        user_id = uuid4()
        
        for i in range(5):
            repo.save(Notification(
                user_id=user_id,
                type=NotificationType.NEW_LETTER,
                title=f"Notification {i}",
                message="Test"
            ))
        
        count = repo.mark_all_as_read(user_id)
        
        assert count == 5
        assert repo.count_unread(user_id) == 0
    
    def test_delete(self):
        """Test: supprimer une notification."""
        repo = InMemoryNotificationRepository()
        
        notification = Notification(
            user_id=uuid4(),
            type=NotificationType.NEW_LETTER,
            title="Test",
            message="Test"
        )
        
        repo.save(notification)
        assert repo.find_by_id(notification.id) is not None
        
        repo.delete(notification.id)
        assert repo.find_by_id(notification.id) is None
