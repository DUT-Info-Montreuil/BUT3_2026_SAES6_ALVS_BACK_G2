# -*- coding: utf-8 -*-
"""
ALVS IA pipeline test - Fichier traité par le système multi-agent IA

Tests des routes d'authentification
"""

import pytest
import json
from app.models.user import User
from app.extensions import db


class TestAuthRoutes:
    """Tests des routes d'authentification"""
    
    def test_register_success(self, client):
        """Test d'inscription réussie"""
        response = client.post('/api/auth/register', json={
            'email': 'newuser@example.com',
            'password': 'password123',
            'first_name': 'New',
            'last_name': 'User'
        })
        
        assert response.status_code == 201
        data = response.get_json()
        assert data['success'] is True
        assert 'access_token' in data
        assert 'user' in data
        assert data['user']['email'] == 'newuser@example.com'
    
    def test_register_missing_fields(self, client):
        """Test d'inscription avec champs manquants"""
        response = client.post('/api/auth/register', json={
            'email': 'newuser@example.com',
            'password': 'password123'
            # first_name et last_name manquants
        })
        
        assert response.status_code == 400
        data = response.get_json()
        assert data['success'] is False
        assert 'requis' in data['message']
    
    def test_register_duplicate_email(self, client, test_user):
        """Test d'inscription avec email existant"""
        response = client.post('/api/auth/register', json={
            'email': test_user['email'],  # Utiliser la syntaxe dictionnaire
            'password': 'password123',
            'first_name': 'New',
            'last_name': 'User'
        })
        
        assert response.status_code == 400
        data = response.get_json()
        assert data['success'] is False
        assert 'existe déjà' in data['message']
    
    def test_login_success(self, client, test_user):
        """Test de connexion réussie"""
        response = client.post('/api/auth/login', json={
            'email': test_user['email'],  # Utiliser la syntaxe dictionnaire
            'password': 'password123'
        })
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
        assert 'access_token' in data
        assert 'user' in data
        assert data['user']['email'] == test_user['email']
    
    def test_login_invalid_credentials(self, client, test_user):
        """Test de connexion avec mauvais identifiants"""
        response = client.post('/api/auth/login', json={
            'email': test_user['email'],  # Utiliser la syntaxe dictionnaire
            'password': 'wrongpassword'
        })
        
        assert response.status_code == 401
        data = response.get_json()
        assert data['success'] is False
        assert 'incorrect' in data['message']
    
    def test_login_missing_fields(self, client):
        """Test de connexion avec champs manquants"""
        response = client.post('/api/auth/login', json={
            'email': 'test@example.com'
            # password manquant
        })
        
        assert response.status_code == 400
        data = response.get_json()
        assert data['success'] is False
        assert 'requis' in data['message']
    
    def test_get_current_user(self, client, auth_headers):
        """Test de récupération de l'utilisateur connecté"""
        response = client.get('/api/auth/me', headers=auth_headers)
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
        assert 'user' in data
    
    def test_get_current_user_unauthorized(self, client):
        """Test de récupération sans authentification"""
        response = client.get('/api/auth/me')
        
        assert response.status_code == 401


class TestUserRoutes:
    """Tests des routes utilisateurs"""
    
    def test_get_all_users_as_admin(self, client, admin_auth_headers):
        """Test de récupération de tous les utilisateurs (admin)"""
        response = client.get('/api/users/', headers=admin_auth_headers)
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
        assert 'users' in data
    
    def test_get_all_users_as_non_admin(self, client, auth_headers):
        """Test de récupération de tous les utilisateurs (non-admin)"""
        response = client.get('/api/users/', headers=auth_headers)
        
        assert response.status_code == 403
        data = response.get_json()
        assert data['success'] is False
        assert 'administrateur' in data['message']
    
    def test_get_user_profile(self, client, auth_headers, test_user):
        """Test de récupération du profil utilisateur"""
        response = client.get(f'/api/users/{test_user["id"]}', headers=auth_headers)
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
        assert data['user']['id'] == test_user['id']
    
    def test_get_user_profile_unauthorized(self, client, auth_headers, admin_user):
        """Test de récupération du profil d'un autre utilisateur"""
        response = client.get(f'/api/users/{admin_user["id"]}', headers=auth_headers)
        
        assert response.status_code == 403
        data = response.get_json()
        assert data['success'] is False
        assert 'non autorisé' in data['message']
    
    def test_update_user_profile(self, client, auth_headers, test_user):
        """Test de mise à jour du profil utilisateur"""
        response = client.put(f'/api/users/{test_user["id"]}', 
                            headers=auth_headers,
                            json={
                                'first_name': 'Updated',
                                'last_name': 'Name'
                            })
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
        assert data['user']['first_name'] == 'Updated'
        assert data['user']['last_name'] == 'Name'
    
    def test_update_user_role_as_non_admin(self, client, auth_headers, test_user):
        """Test de modification du rôle par un non-admin"""
        response = client.put(f'/api/users/{test_user["id"]}', 
                            headers=auth_headers,
                            json={'role': 'admin'})
        
        assert response.status_code == 403
        data = response.get_json()
        assert data['success'] is False
        assert 'administrateurs' in data['message']
    
    def test_delete_user_as_admin(self, client, admin_auth_headers, test_user):
        """Test de suppression d'utilisateur (admin)"""
        response = client.delete(f'/api/users/{test_user["id"]}', headers=admin_auth_headers)
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
    
    def test_delete_user_as_non_admin(self, client, auth_headers, admin_user):
        """Test de suppression d'utilisateur (non-admin)"""
        response = client.delete(f'/api/users/{admin_user["id"]}', headers=auth_headers)
        
        assert response.status_code == 403
        data = response.get_json()
        assert data['success'] is False
        assert 'administrateur' in data['message']
    
    def test_delete_user_success(self, client, admin_auth_headers, test_user):
        """Test de suppression d'utilisateur réussie"""
        response = client.delete(f'/api/users/{test_user["id"]}', headers=admin_auth_headers)
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
        assert 'supprimé' in data['message']
    
    def test_delete_nonexistent_user(self, client, admin_auth_headers):
        """Test de suppression d'utilisateur inexistant"""
        response = client.delete('/api/users/99999', headers=admin_auth_headers)
        
        assert response.status_code == 404
        data = response.get_json()
        assert data['success'] is False
        assert 'non trouvé' in data['message']
    
    def test_authenticate_user_success(self, client, test_user):
        """Test d'authentification réussie"""
        response = client.post('/api/auth/login', json={
            'email': test_user['email'],  # Utiliser la syntaxe dictionnaire
            'password': 'password123'
        })
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
        assert 'access_token' in data
    
    def test_authenticate_user_invalid_credentials(self, client, test_user):
        """Test d'authentification avec identifiants invalides"""
        response = client.post('/api/auth/login', json={
            'email': test_user['email'],  # Utiliser la syntaxe dictionnaire
            'password': 'wrongpassword'
        })
        
        assert response.status_code == 401
        data = response.get_json()
        assert data['success'] is False
        assert 'incorrect' in data['message']
    
    def test_update_nonexistent_user(self, client, admin_auth_headers):
        """Test de mise à jour d'utilisateur inexistant"""
        response = client.put('/api/users/99999', 
                            headers=admin_auth_headers,
                            json={'first_name': 'Updated'})
        
        assert response.status_code == 400
        data = response.get_json()
        assert data['success'] is False
        assert 'non trouvé' in data['message']
    
    def test_get_nonexistent_user(self, client, admin_auth_headers):
        """Test de récupération d'utilisateur inexistant"""
        response = client.get('/api/users/99999', headers=admin_auth_headers)
        
        assert response.status_code == 404
        data = response.get_json()
        assert data['success'] is False
        assert 'non trouvé' in data['message']
    
    def test_update_user_with_invalid_data(self, client, auth_headers, test_user):
        """Test de mise à jour avec données invalides"""
        response = client.put(f'/api/users/{test_user["id"]}', 
                            headers=auth_headers,
                            json={})
        
        assert response.status_code == 400
        data = response.get_json()
        assert data['success'] is False
        assert 'requises' in data['message']
