# -*- coding: utf-8 -*-
"""
ALVS IA pipeline test - Fichier traité par le système multi-agent IA

Tests pour les routes d'authentification
"""

import pytest
import json


class TestAuthRoutes:
    """Tests pour les routes d'authentification"""
    
    def test_register_success(self, client, sample_user_data):
        """Test d'inscription réussie"""
        response = client.post('/api/auth/register', 
                             data=json.dumps(sample_user_data),
                             content_type='application/json')
        
        assert response.status_code == 201
        data = response.get_json()
        assert 'message' in data
        assert 'user' in data
        assert data['user']['email'] == sample_user_data['email']
    
    def test_register_missing_fields(self, client):
        """Test d'inscription avec des champs manquants"""
        incomplete_data = {
            'email': 'test@example.com'
            # Champs manquants: password, first_name, last_name
        }
        
        response = client.post('/api/auth/register',
                             data=json.dumps(incomplete_data),
                             content_type='application/json')
        
        assert response.status_code == 400
        data = response.get_json()
        assert 'message' in data
    
    def test_register_duplicate_email(self, client, sample_user_data):
        """Test d'inscription avec un email déjà utilisé"""
        # Première inscription
        client.post('/api/auth/register',
                   data=json.dumps(sample_user_data),
                   content_type='application/json')
        
        # Tentative de deuxième inscription avec le même email
        response = client.post('/api/auth/register',
                             data=json.dumps(sample_user_data),
                             content_type='application/json')
        
        assert response.status_code == 400
        data = response.get_json()
        assert 'message' in data
        assert 'existe déjà' in data['message']
    
    def test_login_success(self, client, sample_user_data):
        """Test de connexion réussie"""
        # Inscription préalable
        client.post('/api/auth/register',
                   data=json.dumps(sample_user_data),
                   content_type='application/json')
        
        # Connexion
        login_data = {
            'email': sample_user_data['email'],
            'password': sample_user_data['password']
        }
        
        response = client.post('/api/auth/login',
                             data=json.dumps(login_data),
                             content_type='application/json')
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'access_token' in data
        assert 'refresh_token' in data
        assert 'user' in data
    
    def test_login_invalid_credentials(self, client, sample_user_data):
        """Test de connexion avec des identifiants invalides"""
        # Inscription préalable
        client.post('/api/auth/register',
                   data=json.dumps(sample_user_data),
                   content_type='application/json')
        
        # Tentative de connexion avec un mauvais mot de passe
        login_data = {
            'email': sample_user_data['email'],
            'password': 'wrongpassword'
        }
        
        response = client.post('/api/auth/login',
                             data=json.dumps(login_data),
                             content_type='application/json')
        
        assert response.status_code == 401
        data = response.get_json()
        assert 'message' in data
    
    def test_login_missing_fields(self, client):
        """Test de connexion avec des champs manquants"""
        login_data = {
            'email': 'test@example.com'
            # Champ manquant: password
        }
        
        response = client.post('/api/auth/login',
                             data=json.dumps(login_data),
                             content_type='application/json')
        
        assert response.status_code == 400
        data = response.get_json()
        assert 'message' in data
    
    def test_get_current_user(self, client, auth_headers):
        """Test de récupération de l'utilisateur connecté"""
        response = client.get('/api/auth/me', headers=auth_headers)
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'user' in data
        assert data['user']['email'] == 'test@example.com'
    
    def test_get_current_user_without_token(self, client):
        """Test de récupération de l'utilisateur sans token"""
        response = client.get('/api/auth/me')
        
        assert response.status_code == 401
    
    def test_change_password_success(self, client, auth_headers, test_user):
        """Test de changement de mot de passe réussi"""
        password_data = {
            'old_password': test_user['password'],
            'new_password': 'newpassword123'
        }
        
        response = client.post('/api/users/change-password',
                             json=password_data,
                             headers=auth_headers)
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'message' in data
    
    def test_change_password_wrong_old_password(self, client, auth_headers):
        """Test de changement de mot de passe avec mauvais ancien mot de passe"""
        password_data = {
            'old_password': 'wrongoldpassword',
            'new_password': 'newpassword123'
        }
        
        response = client.post('/api/users/change-password',
                             json=password_data,
                             headers=auth_headers)
        
        assert response.status_code == 400
        data = response.get_json()
        assert 'message' in data
    
    def test_refresh_token(self, client, sample_user_data):
        """Test de rafraîchissement du token"""
        # Inscription et connexion
        client.post('/api/auth/register',
                   data=json.dumps(sample_user_data),
                   content_type='application/json')
        
        login_response = client.post('/api/auth/login',
                                   data=json.dumps({
                                       'email': sample_user_data['email'],
                                       'password': sample_user_data['password']
                                   }),
                                   content_type='application/json')
        
        refresh_token = login_response.get_json()['refresh_token']
        
        # Rafraîchissement du token
        headers = {
            'Authorization': f'Bearer {refresh_token}',
            'Content-Type': 'application/json'
        }
        
        response = client.post('/api/auth/refresh', headers=headers)
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'access_token' in data
