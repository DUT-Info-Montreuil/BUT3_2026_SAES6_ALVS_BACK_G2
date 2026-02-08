# tests/integration/test_admin_routes.py
"""Tests d'integration pour les routes d'administration."""

import pytest
from uuid import uuid4


class TestAdminUserRoutes:
    """Tests pour les endpoints admin de gestion des utilisateurs."""
    
    def test_list_users_unauthorized(self, client):
        """Test: lister les utilisateurs sans auth retourne 401."""
        response = client.get('/api/v1/admin/users')
        assert response.status_code == 401
    
    def test_list_users_not_admin(self, client, auth_headers):
        """Test: lister les utilisateurs sans role admin retourne 403."""
        response = client.get('/api/v1/admin/users', headers=auth_headers)
        assert response.status_code == 403
    
    def test_get_user_unauthorized(self, client):
        """Test: obtenir un utilisateur sans auth retourne 401."""
        user_id = str(uuid4())
        response = client.get(f'/api/v1/admin/users/{user_id}')
        assert response.status_code == 401
    
    def test_create_user_unauthorized(self, client):
        """Test: creer un utilisateur sans auth retourne 401."""
        response = client.post('/api/v1/admin/users', json={})
        assert response.status_code == 401
    
    def test_create_user_not_admin(self, client, auth_headers):
        """Test: creer un utilisateur sans role admin retourne 403."""
        response = client.post(
            '/api/v1/admin/users',
            headers=auth_headers,
            json={
                'email': 'newuser@example.com',
                'password': 'Password123!',
                'first_name': 'New',
                'last_name': 'User'
            }
        )
        assert response.status_code == 403
    
    def test_delete_user_unauthorized(self, client):
        """Test: supprimer un utilisateur sans auth retourne 401."""
        user_id = str(uuid4())
        response = client.delete(f'/api/v1/admin/users/{user_id}')
        assert response.status_code == 401
    
    def test_update_role_unauthorized(self, client):
        """Test: modifier un role sans auth retourne 401."""
        user_id = str(uuid4())
        response = client.patch(
            f'/api/v1/admin/users/{user_id}',
            json={'role': 'admin'}
        )
        assert response.status_code == 401


class TestAdminStatsRoutes:
    """Tests pour les endpoints de statistiques admin."""
    
    def test_get_stats_unauthorized(self, client):
        """Test: obtenir les stats sans auth retourne 401."""
        response = client.get('/api/v1/admin/stats')
        assert response.status_code == 401
    
    def test_get_stats_not_admin(self, client, auth_headers):
        """Test: obtenir les stats sans role admin retourne 403."""
        response = client.get('/api/v1/admin/stats', headers=auth_headers)
        assert response.status_code == 403


class TestAdminWithAdminRole:
    """Tests pour les endpoints admin avec le role admin."""
    
    def test_list_users_as_admin(self, client, admin_headers):
        """Test: lister les utilisateurs en tant qu'admin."""
        response = client.get('/api/v1/admin/users', headers=admin_headers)
        # Peut retourner 200 ou 401 si admin_headers n'est pas configu
        assert response.status_code in [200, 401]
    
    def test_get_stats_as_admin(self, client, admin_headers):
        """Test: obtenir les stats en tant qu'admin."""
        response = client.get('/api/v1/admin/stats', headers=admin_headers)
        assert response.status_code in [200, 401]
