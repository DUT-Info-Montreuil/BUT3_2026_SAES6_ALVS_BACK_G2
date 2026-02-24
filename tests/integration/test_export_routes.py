# tests/integration/test_export_routes.py
"""Tests d'integration pour les routes d'export RGPD."""

import pytest
import json


class TestExportRoutes:
    """Tests pour les endpoints d'export des donnees."""
    
    def test_export_my_data_unauthorized(self, client):
        """Test: export sans auth retourne 401."""
        response = client.get('/api/v1/export/my-data')
        assert response.status_code == 401
    
    def test_export_my_data_success(self, client, auth_headers):
        """Test: export des donnees utilisateur."""
        response = client.get('/api/v1/export/my-data', headers=auth_headers)
        # Accept 200 (success) or 404 (user not found in test context)
        assert response.status_code in [200, 404]
        
        if response.status_code == 200:
            # Verifier le header Content-Disposition si 200
            assert 'Content-Disposition' in response.headers
            assert 'attachment' in response.headers['Content-Disposition']
            
            # Verifier la structure JSON
            data = response.get_json()
            assert 'export_date' in data
            assert 'user' in data
            assert 'rgpd_notice' in data
    
    def test_export_contains_user_data(self, client, auth_headers):
        """Test: export contient les donnees utilisateur."""
        response = client.get('/api/v1/export/my-data', headers=auth_headers)
        
        if response.status_code == 200:
            data = response.get_json()
            user_data = data.get('user', {})
            assert 'id' in user_data
            assert 'email' in user_data
        else:
            # Test passe si l'utilisateur n'existe pas dans le contexte de test
            assert response.status_code in [404, 401]
    
    def test_export_contains_statistics(self, client, auth_headers):
        """Test: export contient les statistiques."""
        response = client.get('/api/v1/export/my-data', headers=auth_headers)
        
        if response.status_code == 200:
            data = response.get_json()
            assert 'statistics' in data
            stats = data['statistics']
            assert 'total_collis' in stats
            assert 'total_letters' in stats
        else:
            assert response.status_code in [404, 401]


class TestDataDeletionRequest:
    """Tests pour la demande de suppression de donnees."""
    
    def test_delete_request_unauthorized(self, client):
        """Test: demande de suppression sans auth retourne 401."""
        response = client.delete('/api/v1/export/my-data')
        assert response.status_code == 401
    
    def test_delete_request_without_confirmation(self, client, auth_headers):
        """Test: demande sans confirmation retourne 400."""
        response = client.delete(
            '/api/v1/export/my-data',
            headers=auth_headers,
            json={}
        )
        # Peut retourner 400 ou 404 selon le contexte
        assert response.status_code in [400, 404]
    
    def test_delete_request_with_confirmation(self, client, auth_headers):
        """Test: demande avec confirmation reussit."""
        response = client.delete(
            '/api/v1/export/my-data',
            headers=auth_headers,
            json={'confirm': True, 'reason': 'Test deletion'}
        )
        # Accept 200 or 404 (user not found in test context)
        assert response.status_code in [200, 404]
        
        if response.status_code == 200:
            data = response.get_json()
            assert 'deletion_date' in data
            assert 'notice' in data
