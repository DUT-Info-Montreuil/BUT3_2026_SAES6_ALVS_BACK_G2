# tests/integration/test_notification_routes.py
"""Tests d'integration pour les routes de notifications."""

import pytest
from uuid import uuid4


class TestNotificationRoutes:
    """Tests pour les endpoints de notifications."""
    
    def test_list_notifications_unauthorized(self, client):
        """Test: liste des notifications sans auth retourne 401."""
        response = client.get('/api/v1/notifications')
        assert response.status_code == 401
    
    def test_list_notifications_empty(self, client, auth_headers):
        """Test: liste des notifications vide."""
        response = client.get('/api/v1/notifications', headers=auth_headers)
        assert response.status_code == 200
        data = response.get_json()
        assert 'items' in data
        assert 'unread_count' in data
    
    def test_get_unread_count(self, client, auth_headers):
        """Test: recuperer le nombre de notifications non lues."""
        response = client.get('/api/v1/notifications/count', headers=auth_headers)
        assert response.status_code == 200
        data = response.get_json()
        assert 'unread_count' in data
        assert isinstance(data['unread_count'], int)
    
    def test_mark_notification_as_read_not_found(self, client, auth_headers):
        """Test: marquer une notification inexistante retourne 404."""
        fake_id = str(uuid4())
        response = client.patch(
            f'/api/v1/notifications/{fake_id}/read',
            headers=auth_headers
        )
        assert response.status_code == 404
    
    def test_mark_all_as_read(self, client, auth_headers):
        """Test: marquer toutes les notifications comme lues."""
        response = client.post('/api/v1/notifications/read-all', headers=auth_headers)
        assert response.status_code == 200
        data = response.get_json()
        assert 'marked_count' in data
    
    def test_delete_notification_not_found(self, client, auth_headers):
        """Test: supprimer une notification inexistante retourne 404."""
        fake_id = str(uuid4())
        response = client.delete(
            f'/api/v1/notifications/{fake_id}',
            headers=auth_headers
        )
        assert response.status_code == 404


class TestNotificationFiltering:
    """Tests pour le filtrage des notifications."""
    
    def test_list_unread_only(self, client, auth_headers):
        """Test: filtrer les notifications non lues uniquement."""
        response = client.get(
            '/api/v1/notifications?unread_only=true',
            headers=auth_headers
        )
        assert response.status_code == 200
    
    def test_list_with_limit(self, client, auth_headers):
        """Test: limiter le nombre de notifications retournees."""
        response = client.get(
            '/api/v1/notifications?limit=5',
            headers=auth_headers
        )
        assert response.status_code == 200
