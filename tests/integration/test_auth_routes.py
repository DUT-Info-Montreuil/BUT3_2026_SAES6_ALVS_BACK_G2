# tests/integration/test_auth_routes.py
"""Tests d'intégration pour les routes Auth."""

import pytest
from uuid import uuid4
from flask_jwt_extended import create_access_token


class TestAuthRoutes:
    """Tests d'intégration pour les routes d'authentification."""
    
    def test_register_success(self, client):
        """POST /api/v1/auth/register - Inscription réussie."""
        response = client.post(
            '/api/v1/auth/register',
            json={
                'email': f'test_{uuid4().hex[:8]}@example.com',
                'password': 'password123',
                'password_confirm': 'password123',
                'first_name': 'John',
                'last_name': 'Doe'
            }
        )
        
        assert response.status_code == 201
        data = response.get_json()
        assert 'email' in data
        assert 'first_name' in data
    
    def test_register_duplicate_email(self, client):
        """POST /api/v1/auth/register - Email dupliqué refusé."""
        email = f'test_{uuid4().hex[:8]}@example.com'
        
        # Premier enregistrement
        client.post(
            '/api/v1/auth/register',
            json={
                'email': email,
                'password': 'password123',
                'password_confirm': 'password123',
                'first_name': 'John',
                'last_name': 'Doe'
            }
        )
        
        # Deuxième avec même email
        response = client.post(
            '/api/v1/auth/register',
            json={
                'email': email,
                'password': 'password123',
                'password_confirm': 'password123',
                'first_name': 'Jane',
                'last_name': 'Doe'
            }
        )
        
        assert response.status_code == 409
    
    def test_register_password_mismatch(self, client):
        """POST /api/v1/auth/register - Mots de passe différents."""
        response = client.post(
            '/api/v1/auth/register',
            json={
                'email': f'test_{uuid4().hex[:8]}@example.com',
                'password': 'password123',
                'password_confirm': 'different_password',
                'first_name': 'John',
                'last_name': 'Doe'
            }
        )
        
        assert response.status_code == 400
    
    def test_register_invalid_email(self, client):
        """POST /api/v1/auth/register - Email invalide."""
        response = client.post(
            '/api/v1/auth/register',
            json={
                'email': 'invalid-email',
                'password': 'password123',
                'password_confirm': 'password123',
                'first_name': 'John',
                'last_name': 'Doe'
            }
        )
        
        assert response.status_code == 400
    
    def test_register_short_password(self, client):
        """POST /api/v1/auth/register - Mot de passe trop court."""
        response = client.post(
            '/api/v1/auth/register',
            json={
                'email': f'test_{uuid4().hex[:8]}@example.com',
                'password': 'short',
                'password_confirm': 'short',
                'first_name': 'John',
                'last_name': 'Doe'
            }
        )
        
        assert response.status_code == 400
    
    def test_login_success(self, client):
        """POST /api/v1/auth/login - Connexion réussie."""
        email = f'test_{uuid4().hex[:8]}@example.com'
        
        # Enregistrer
        client.post(
            '/api/v1/auth/register',
            json={
                'email': email,
                'password': 'password123',
                'password_confirm': 'password123',
                'first_name': 'John',
                'last_name': 'Doe'
            }
        )
        
        # Connexion
        response = client.post(
            '/api/v1/auth/login',
            json={
                'email': email,
                'password': 'password123'
            }
        )
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'access_token' in data
        assert data['token_type'] == 'Bearer'
        # refresh_token est maintenant dans un cookie HttpOnly
    
    def test_login_wrong_password(self, client):
        """POST /api/v1/auth/login - Mauvais mot de passe."""
        email = f'test_{uuid4().hex[:8]}@example.com'
        
        # Enregistrer
        client.post(
            '/api/v1/auth/register',
            json={
                'email': email,
                'password': 'password123',
                'password_confirm': 'password123',
                'first_name': 'John',
                'last_name': 'Doe'
            }
        )
        
        # Connexion avec mauvais mot de passe
        response = client.post(
            '/api/v1/auth/login',
            json={
                'email': email,
                'password': 'wrongpassword'
            }
        )
        
        assert response.status_code == 401
    
    def test_login_unknown_email(self, client):
        """POST /api/v1/auth/login - Email inconnu."""
        response = client.post(
            '/api/v1/auth/login',
            json={
                'email': 'unknown@example.com',
                'password': 'password123'
            }
        )
        
        assert response.status_code == 401
    
    def test_get_me_success(self, client, app):
        """GET /api/v1/auth/me - Récupérer profil."""
        email = f'test_{uuid4().hex[:8]}@example.com'
        
        # Enregistrer
        register_res = client.post(
            '/api/v1/auth/register',
            json={
                'email': email,
                'password': 'password123',
                'password_confirm': 'password123',
                'first_name': 'John',
                'last_name': 'Doe'
            }
        )
        
        # Connexion
        login_res = client.post(
            '/api/v1/auth/login',
            json={'email': email, 'password': 'password123'}
        )
        token = login_res.get_json()['access_token']
        
        # Get me
        response = client.get(
            '/api/v1/auth/me',
            headers={'Authorization': f'Bearer {token}'}
        )
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['email'] == email
        assert data['first_name'] == 'John'
    
    def test_get_me_unauthorized(self, client):
        """GET /api/v1/auth/me - Sans token refusé."""
        response = client.get('/api/v1/auth/me')
        
        assert response.status_code == 401


class TestHealthRoutes:
    """Tests pour les routes de santé."""
    
    def test_health_check(self, client):
        """GET /health - Vérifie la santé."""
        response = client.get('/health')
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['status'] == 'healthy'
    
    def test_ready_check(self, client):
        """GET /ready - Vérifie la disponibilité."""
        response = client.get('/ready')
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'ready' in data
        assert 'checks' in data
    
    def test_version_info(self, client):
        """GET /version - Info de version."""
        response = client.get('/version')
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'service' in data
        assert 'version' in data
