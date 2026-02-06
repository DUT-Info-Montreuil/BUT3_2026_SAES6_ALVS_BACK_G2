# -*- coding: utf-8 -*-
"""
ALVS IA pipeline test - Fichier traité par le système multi-agent IA

Tests spécifiques aux routes utilisateurs
"""

import pytest
import json
from app.models.user import User
from app.extensions import db


class TestUserRoutes:
    """Tests des routes utilisateurs"""
    
    def test_get_user_profile(self, client, auth_headers, test_user):
        """Test de récupération du profil utilisateur"""
        response = client.get(f'/api/users/{test_user["id"]}', headers=auth_headers)
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
        assert data['user']['id'] == test_user['id']
        assert data['user']['email'] == test_user['email']
    
    def test_get_user_profile_unauthorized(self, client):
        """Test de récupération du profil sans authentification"""
        response = client.get('/api/users/1')
        
        assert response.status_code == 401
    
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
    
    def test_get_users_as_non_admin(self, client, auth_headers):
        """Test de récupération de tous les utilisateurs (non-admin)"""
        response = client.get('/api/users/', headers=auth_headers)
        
        assert response.status_code == 403
        data = response.get_json()
        assert data['success'] is False
        assert 'administrateur' in data['message']
    
    def test_delete_user_as_non_admin(self, client, auth_headers, admin_user):
        """Test de suppression d'utilisateur (non-admin)"""
        response = client.delete(f'/api/users/{admin_user["id"]}', headers=auth_headers)
        
        assert response.status_code == 403
        data = response.get_json()
        assert data['success'] is False
        assert 'administrateur' in data['message']
    
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
        """Test de mise à jour avec données invalides (corps vide)"""
        response = client.put(f'/api/users/{test_user["id"]}',
                            headers=auth_headers,
                            json={})
        
        # La route devrait gérer le corps vide gracieusement
        # Soit 400 (données requises) ou 200 (aucune modification)
        assert response.status_code in [200, 400]
        data = response.get_json()
        assert 'success' in data
    
    def test_change_password_success(self, client, auth_headers):
        """Test de changement de mot de passe réussi"""
        response = client.post('/api/users/change-password', 
                             headers=auth_headers,
                             json={
                                 'old_password': 'password123',
                                 'new_password': 'newpassword123'
                             })
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
        assert 'changé' in data['message']
    
    def test_change_password_wrong_old_password(self, client, auth_headers):
        """Test de changement de mot de passe avec mauvais ancien mot de passe"""
        response = client.post('/api/users/change-password', 
                             headers=auth_headers,
                             json={
                                 'old_password': 'wrongpassword',
                                 'new_password': 'newpassword123'
                             })
        
        assert response.status_code == 400
        data = response.get_json()
        assert data['success'] is False
        assert 'incorrect' in data['message']
    
    def test_change_password_missing_fields(self, client, auth_headers):
        """Test de changement de mot de passe avec champs manquants"""
        response = client.post('/api/users/change-password', 
                             headers=auth_headers,
                             json={'old_password': 'password123'})
        
        assert response.status_code == 400
        data = response.get_json()
        assert data['success'] is False
        assert 'requis' in data['message']
