# ALVS IA pipeline test - Fichier traité par le système multi-agent IA
# Ce commentaire valide le bon fonctionnement du pipeline de développement automatisé

import pytest
import json
from app.controllers.user_controller import UserController


class TestUserController:
    """Tests pour le contrôleur utilisateur"""
    
    def test_user_controller_init(self, app):
        """Test l'initialisation du contrôleur utilisateur"""
        with app.app_context():
            controller = UserController()
            assert controller is not None
            assert controller.user_service is not None
    
    def test_get_users_empty(self, client, admin_auth_headers):
        """Test l'endpoint GET /api/users (liste vide avec admin)"""
        response = client.get('/api/users/', headers=admin_auth_headers)
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert 'users' in data
        assert isinstance(data['users'], list)
    
    def test_create_user_via_register(self, client):
        """Test création d'utilisateur via l'endpoint register"""
        user_data = {
            'email': 'newuser@example.com',
            'password': 'password123',
            'first_name': 'New',
            'last_name': 'User'
        }
        
        response = client.post('/api/auth/register', 
                             data=json.dumps(user_data),
                             content_type='application/json')
        
        assert response.status_code == 201
        
        data = json.loads(response.data)
        assert 'user' in data
        assert data['user']['email'] == 'newuser@example.com'
        assert data['user']['first_name'] == 'New'
    
    def test_create_user_missing_data(self, client):
        """Test création d'utilisateur avec données manquantes"""
        user_data = {
            'email': 'test@example.com'
            # password, first_name, last_name manquants
        }
        
        response = client.post('/api/auth/register', 
                             data=json.dumps(user_data),
                             content_type='application/json')
        
        assert response.status_code == 400
        
        data = json.loads(response.data)
        assert 'message' in data
    
    def test_get_user_not_found(self, client, auth_headers):
        """Test l'endpoint GET /api/users/<id> (utilisateur inexistant ou accès refusé)"""
        response = client.get('/api/users/99999', headers=auth_headers)
        # L'API peut retourner 403 (accès refusé) ou 404 (non trouvé)
        assert response.status_code in [403, 404]
        
        data = json.loads(response.data)
        assert 'message' in data or 'error' in data
    
    def test_get_user_success(self, client, test_user, auth_headers):
        """Test l'endpoint GET /api/users/<id> (utilisateur existant)"""
        user_id = test_user['id']
        
        # Récupérer l'utilisateur
        response = client.get(f'/api/users/{user_id}', headers=auth_headers)
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert 'user' in data
        assert data['user']['email'] == test_user['email']
