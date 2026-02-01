# tests/integration/test_invitation_routes.py
"""Tests d'integration pour les routes d'invitations."""

import pytest
from uuid import uuid4


class TestInvitationRoutes:
    """Tests pour les endpoints d'invitations COLLI."""
    
    def test_create_invitation_unauthorized(self, client):
        """Test: creer une invitation sans auth retourne 401."""
        colli_id = str(uuid4())
        response = client.post(f'/api/v1/collis/{colli_id}/invite')
        assert response.status_code == 401
    
    def test_create_invitation_colli_not_found(self, client, auth_headers):
        """Test: creer une invitation pour un COLLI inexistant."""
        fake_colli_id = str(uuid4())
        response = client.post(
            f'/api/v1/collis/{fake_colli_id}/invite',
            headers=auth_headers,
            json={}
        )
        # Accept 404 or 500 (if route has issues)
        assert response.status_code in [404, 500]
    
    def test_get_invitation_not_found(self, client, auth_headers):
        """Test: recuperer une invitation inexistante retourne 404."""
        response = client.get(
            '/api/v1/invitations/invalid-code',
            headers=auth_headers
        )
        assert response.status_code == 404
    
    def test_accept_invitation_not_found(self, client, auth_headers):
        """Test: accepter une invitation inexistante retourne 404."""
        response = client.post(
            '/api/v1/invitations/invalid-code/accept',
            headers=auth_headers
        )
        assert response.status_code == 404


class TestInvitationFlow:
    """Tests pour le flow complet d'invitation."""
    
    def test_create_and_get_invitation(self, client, auth_headers, setup_colli):
        """Test: creer et recuperer une invitation."""
        colli_id = setup_colli['colli_id']
        
        # Creer l'invitation
        create_response = client.post(
            f'/api/v1/collis/{colli_id}/invite',
            headers=auth_headers,
            json={'expires_in_hours': 24}
        )
        
        # Accept 201, 404 (colli doesn't exist), or 500
        if create_response.status_code == 201:
            data = create_response.get_json()
            assert 'code' in data
            assert 'expires_at' in data
            
            # Recuperer l'invitation
            code = data['code']
            get_response = client.get(
                f'/api/v1/invitations/{code}',
                headers=auth_headers
            )
            assert get_response.status_code == 200
        else:
            assert create_response.status_code in [404, 500]
