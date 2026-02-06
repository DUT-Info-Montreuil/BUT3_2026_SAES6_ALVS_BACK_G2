# -*- coding: utf-8 -*-
"""
Tests pour les routes d'authentification
"""

import pytest
import json
from app.services.user_service import UserService


class TestAuthRoutes:
    """Tests pour les routes d'authentification"""
    
    def test_register_success(self, client, app):
        """Test d'inscription réussie"""
        with app.app_context():
            response = client.post('/api/auth/register', 
                                 data=json.dumps({
                                     'email': 'test@example.com',
                                     'password': 'password123',
                                     'first_name': 'John',
                                     'last_name': 'Doe'
                                 }),
                                 content_type='application/json')
            
            assert response.status_code == 201
            data = json.loads(response.data)
            assert 'message' in data
            assert 'user' in data
            assert data['user']['email'] == 'test@example.com'
    
    def test_register_missing_fields(self, client, app):
        """Test d'inscription avec champs manquants"""
        with app.app_context():
            response = client.post('/api/auth/register', 
                                 data=json.dumps({
                                     'email': 'test@example.com',
                                     'password': 'password123'
                                     # first_name et last_name manquants
                                 }),
                                 content_type='application/json')
            
            assert response.status_code == 400
            data = json.loads(response.data)
            assert 'message' in data
    
    def test_register_duplicate_email(self, client, app):
        """Test d'inscription avec email existant"""
        with app.app_context():
            # Créer un utilisateur d'abord
            UserService.create_user(
                email='test@example.com',
                password='password123',
                first_name='John',
                last_name='Doe'
            )
            
            # Tenter de créer un autre utilisateur avec le même email
            response = client.post('/api/auth/register', 
                                 data=json.dumps({
                                     'email': 'test@example.com',
                                     'password': 'password456',
                                     'first_name': 'Jane',
                                     'last_name': 'Smith'
                                 }),
                                 content_type='application/json')
            
            assert response.status_code == 400
            data = json.loads(response.data)
            assert 'message' in data
    
    def test_login_success(self, client, app):
        """Test de connexion réussie"""
        with app.app_context():
            # Créer un utilisateur d'abord
            UserService.create_user(
                email='test@example.com',
                password='password123',
                first_name='John',
                last_name='Doe'
            )
            
            # Tenter la connexion
            response = client.post('/api/auth/login', 
                                 data=json.dumps({
                                     'email': 'test@example.com',
                                     'password': 'password123'
                                 }),
                                 content_type='application/json')
            
            assert response.status_code == 200
            data = json.loads(response.data)
            assert 'access_token' in data
            assert 'user' in data
            assert data['user']['email'] == 'test@example.com'
    
    def test_login_invalid_credentials(self, client, app):
        """Test de connexion avec identifiants invalides"""
        with app.app_context():
            # Créer un utilisateur d'abord
            UserService.create_user(
                email='test@example.com',
                password='password123',
                first_name='John',
                last_name='Doe'
            )
            
            # Tenter la connexion avec un mauvais mot de passe
            response = client.post('/api/auth/login', 
                                 data=json.dumps({
                                     'email': 'test@example.com',
                                     'password': 'wrongpassword'
                                 }),
                                 content_type='application/json')
            
            assert response.status_code == 401
            data = json.loads(response.data)
            assert 'message' in data
    
    def test_get_current_user_success(self, client, app):
        """Test de récupération de l'utilisateur connecté"""
        with app.app_context():
            # Créer un utilisateur et se connecter
            UserService.create_user(
                email='test@example.com',
                password='password123',
                first_name='John',
                last_name='Doe'
            )
            
            # Se connecter pour obtenir le token
            login_response = client.post('/api/auth/login', 
                                       data=json.dumps({
                                           'email': 'test@example.com',
                                           'password': 'password123'
                                       }),
                                       content_type='application/json')
            
            login_data = json.loads(login_response.data)
            access_token = login_data['access_token']
            
            # Utiliser le token pour récupérer les infos utilisateur
            response = client.get('/api/auth/me',
                                headers={'Authorization': f'Bearer {access_token}'})
            
            assert response.status_code == 200
            data = json.loads(response.data)
            assert 'user' in data
            assert data['user']['email'] == 'test@example.com'
    
    def test_get_current_user_no_token(self, client, app):
        """Test de récupération de l'utilisateur connecté sans token"""
        with app.app_context():
            response = client.get('/api/auth/me')
            
            assert response.status_code == 401
