# -*- coding: utf-8 -*-
"""
ALVS IA pipeline test - Fichier traité par le système multi-agent IA

Tests des routes de sondages
"""

import pytest
import json
from app.models.poll import Poll, Option, Vote
from app.extensions import db


class TestPollRoutes:
    """Tests des routes de sondages"""
    
    def test_get_all_polls(self, client, test_poll):
        """Test de récupération de tous les sondages"""
        response = client.get('/api/polls/')
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
        assert 'polls' in data
        assert len(data['polls']) >= 1
    
    def test_create_poll_success(self, client, auth_headers):
        """Test de création de sondage réussie"""
        response = client.post('/api/polls/', 
                             headers=auth_headers,
                             json={
                                 'title': 'New Poll',
                                 'description': 'A new poll',
                                 'options': ['Option A', 'Option B', 'Option C']
                             })
        
        assert response.status_code == 201
        data = response.get_json()
        assert data['success'] is True
        assert data['poll']['title'] == 'New Poll'
        assert len(data['poll']['options']) == 3
    
    def test_create_poll_unauthorized(self, client):
        """Test de création de sondage sans authentification"""
        response = client.post('/api/polls/', 
                             json={
                                 'title': 'New Poll',
                                 'options': ['Option A', 'Option B']
                             })
        
        assert response.status_code == 401
    
    def test_create_poll_missing_fields(self, client, auth_headers):
        """Test de création de sondage avec champs manquants"""
        response = client.post('/api/polls/', 
                             headers=auth_headers,
                             json={'title': 'New Poll'})
        
        assert response.status_code == 400
        data = response.get_json()
        assert data['success'] is False
        assert 'requis' in data['message']
    
    def test_create_poll_insufficient_options(self, client, auth_headers):
        """Test de création de sondage avec trop peu d'options"""
        response = client.post('/api/polls/', 
                             headers=auth_headers,
                             json={
                                 'title': 'New Poll',
                                 'options': ['Only One Option']
                             })
        
        assert response.status_code == 400
        data = response.get_json()
        assert data['success'] is False
        assert '2 options' in data['message']
    
    def test_get_poll_by_id(self, client, test_poll):
        """Test de récupération d'un sondage par ID"""
        response = client.get(f'/api/polls/{test_poll["id"]}')
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
        assert data['poll']['id'] == test_poll['id']
        assert data['poll']['title'] == test_poll['title']
    
    def test_get_nonexistent_poll(self, client):
        """Test de récupération d'un sondage inexistant"""
        response = client.get('/api/polls/99999')
        
        assert response.status_code == 404
        data = response.get_json()
        assert data['success'] is False
        assert 'non trouvé' in data['message']
    
    def test_vote_on_poll_success(self, client, auth_headers, test_poll):
        """Test de vote réussi"""
        option = test_poll['options'][0]  # Utiliser la syntaxe dictionnaire
        
        response = client.post(f'/api/polls/{test_poll["id"]}/vote', 
                             headers=auth_headers,
                             json={'option_id': option['id']})
        
        assert response.status_code == 201
        data = response.get_json()
        assert data['success'] is True
        assert 'enregistré' in data['message']
    
    def test_vote_on_poll_unauthorized(self, client, test_poll):
        """Test de vote sans authentification"""
        option = test_poll['options'][0]  # Utiliser la syntaxe dictionnaire
        
        response = client.post(f'/api/polls/{test_poll["id"]}/vote', 
                             json={'option_id': option['id']})
        
        assert response.status_code == 401
    
    def test_vote_on_poll_missing_option(self, client, auth_headers, test_poll):
        """Test de vote sans spécifier d'option"""
        response = client.post(f'/api/polls/{test_poll["id"]}/vote', 
                             headers=auth_headers,
                             json={})
        
        assert response.status_code == 400
        data = response.get_json()
        assert data['success'] is False
        assert 'requis' in data['message']
    
    def test_vote_twice_on_same_poll(self, client, auth_headers, test_poll):
        """Test de vote multiple sur le même sondage"""
        option = test_poll['options'][0]  # Utiliser la syntaxe dictionnaire
        
        # Premier vote
        client.post(f'/api/polls/{test_poll["id"]}/vote', 
                   headers=auth_headers,
                   json={'option_id': option['id']})
        
        # Deuxième vote (doit échouer)
        response = client.post(f'/api/polls/{test_poll["id"]}/vote', 
                             headers=auth_headers,
                             json={'option_id': option['id']})
        
        assert response.status_code == 400
        data = response.get_json()
        assert data['success'] is False
        assert 'déjà voté' in data['message']
    
    def test_get_poll_results(self, client, test_poll):
        """Test de récupération des résultats d'un sondage"""
        response = client.get(f'/api/polls/{test_poll["id"]}/results')
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
        assert 'results' in data
        assert 'total_votes' in data['results']
        assert 'options_results' in data['results']
    
    def test_has_user_voted(self, client, auth_headers, test_poll):
        """Test de vérification si l'utilisateur a voté"""
        # Avant le vote
        response = client.get(f'/api/polls/{test_poll["id"]}/has-voted', headers=auth_headers)
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
        assert data['has_voted'] is False
        
        # Après le vote
        option = test_poll['options'][0]  # Utiliser la syntaxe dictionnaire
        client.post(f'/api/polls/{test_poll["id"]}/vote', 
                   headers=auth_headers,
                   json={'option_id': option['id']})
        
        response = client.get(f'/api/polls/{test_poll["id"]}/has-voted', headers=auth_headers)
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
        assert data['has_voted'] is True
    
    def test_has_user_voted_unauthorized(self, client, test_poll):
        """Test de vérification de vote sans authentification"""
        response = client.get(f'/api/polls/{test_poll["id"]}/has-voted')
        
        assert response.status_code == 401
    
    def test_delete_poll_as_creator(self, client, auth_headers, test_poll):
        """Test de suppression de sondage par le créateur"""
        response = client.delete(f'/api/polls/{test_poll["id"]}', headers=auth_headers)
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
        assert 'supprimé' in data['message']
    
    def test_delete_poll_unauthorized(self, client, test_poll):
        """Test de suppression de sondage sans authentification"""
        response = client.delete(f'/api/polls/{test_poll["id"]}')
        
        assert response.status_code == 401
    
    def test_delete_nonexistent_poll(self, client, auth_headers):
        """Test de suppression d'un sondage inexistant"""
        response = client.delete('/api/polls/99999', headers=auth_headers)
        
        assert response.status_code == 404
        data = response.get_json()
        assert data['success'] is False
        assert 'non trouvé' in data['message']
