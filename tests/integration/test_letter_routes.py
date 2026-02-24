# tests/integration/test_letter_routes.py
"""Tests d'intégration pour les routes Letter."""

import pytest
from uuid import uuid4
from flask_jwt_extended import create_access_token


class TestLetterRoutes:
    """Tests d'intégration pour les routes Letter."""
    
    @pytest.fixture
    def setup_colli(self, client, app):
        """Crée un COLLI actif pour les tests."""
        teacher_id = uuid4()
        admin_id = uuid4()
        member_id = uuid4()
        
        with app.app_context():
            teacher_token = create_access_token(
                identity=str(teacher_id),
                additional_claims={'role': 'teacher'}
            )
            admin_token = create_access_token(
                identity=str(admin_id),
                additional_claims={'role': 'admin'}
            )
            member_token = create_access_token(
                identity=str(member_id),
                additional_claims={'role': 'student'}
            )
        
        # Créer et approuver COLLI
        create_res = client.post(
            '/api/v1/collis',
            json={'name': 'Test COLLI', 'theme': 'Test'},
            headers={'Authorization': f'Bearer {teacher_token}'}
        )
        assert create_res.status_code == 201, f"Create failed: {create_res.get_json()}"
        colli_id = create_res.get_json()['id']

        approve_res = client.patch(
            f'/api/v1/collis/{colli_id}/approve',
            headers={'Authorization': f'Bearer {admin_token}'}
        )
        assert approve_res.status_code == 200, f"Approve failed: {approve_res.get_json()}"

        # Member rejoint (demande PENDING)
        join_res = client.post(
            f'/api/v1/collis/{colli_id}/join',
            headers={'Authorization': f'Bearer {member_token}'}
        )
        assert join_res.status_code == 200, f"Join failed: {join_res.get_json()}"

        # Teacher (manager) accepte le member
        accept_res = client.patch(
            f'/api/v1/collis/{colli_id}/members/{member_id}/accept',
            headers={'Authorization': f'Bearer {teacher_token}'}
        )
        assert accept_res.status_code == 200, f"Accept failed: {accept_res.get_json()}"

        return {
            'colli_id': colli_id,
            'teacher_id': teacher_id,
            'teacher_token': teacher_token,
            'member_id': member_id,
            'member_token': member_token
        }
    
    def test_create_text_letter(self, client, setup_colli):
        """POST /api/v1/collis/<id>/letters - Créer lettre texte."""
        response = client.post(
            f'/api/v1/collis/{setup_colli["colli_id"]}/letters',
            json={
                'letter_type': 'text',
                'content': 'Ceci est le contenu de ma lettre.'
            },
            headers={'Authorization': f'Bearer {setup_colli["member_token"]}'}
        )
        
        assert response.status_code == 201
        data = response.get_json()
        assert data['letter_type'] == 'text'
        assert data['content'] == 'Ceci est le contenu de ma lettre.'
    
    def test_create_file_letter(self, client, setup_colli):
        """POST /api/v1/collis/<id>/letters - Créer lettre fichier."""
        response = client.post(
            f'/api/v1/collis/{setup_colli["colli_id"]}/letters',
            json={
                'letter_type': 'file',
                'file_url': 'https://example.com/doc.pdf',
                'file_name': 'document.pdf',
                'description': 'Mon document'
            },
            headers={'Authorization': f'Bearer {setup_colli["member_token"]}'}
        )
        
        assert response.status_code == 201
        data = response.get_json()
        assert data['letter_type'] == 'file'
        assert data['file_url'] == 'https://example.com/doc.pdf'
    
    def test_create_letter_unauthorized(self, client, setup_colli):
        """POST sans token refusé."""
        response = client.post(
            f'/api/v1/collis/{setup_colli["colli_id"]}/letters',
            json={'letter_type': 'text', 'content': 'Test'}
        )
        
        assert response.status_code == 401
    
    def test_create_letter_non_member(self, client, app, setup_colli):
        """Non-membre ne peut pas créer de lettre."""
        with app.app_context():
            stranger_token = create_access_token(
                identity=str(uuid4()),
                additional_claims={'role': 'student'}
            )
        
        response = client.post(
            f'/api/v1/collis/{setup_colli["colli_id"]}/letters',
            json={'letter_type': 'text', 'content': 'Test'},
            headers={'Authorization': f'Bearer {stranger_token}'}
        )
        
        assert response.status_code == 403
    
    def test_list_letters(self, client, setup_colli):
        """GET /api/v1/collis/<id>/letters - Lister les lettres."""
        # Créer une lettre
        client.post(
            f'/api/v1/collis/{setup_colli["colli_id"]}/letters',
            json={'letter_type': 'text', 'content': 'Test lettre'},
            headers={'Authorization': f'Bearer {setup_colli["member_token"]}'}
        )
        
        # Lister
        response = client.get(
            f'/api/v1/collis/{setup_colli["colli_id"]}/letters',
            headers={'Authorization': f'Bearer {setup_colli["member_token"]}'}
        )
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'items' in data
        assert data['total'] >= 1
    
    def test_get_letter_by_id(self, client, setup_colli):
        """GET /api/v1/collis/<id>/letters/<id> - Récupérer une lettre."""
        # Créer
        create_res = client.post(
            f'/api/v1/collis/{setup_colli["colli_id"]}/letters',
            json={'letter_type': 'text', 'content': 'Contenu valide pour test'},
            headers={'Authorization': f'Bearer {setup_colli["member_token"]}'}
        )
        letter_id = create_res.get_json()['id']
        
        # Get
        response = client.get(
            f'/api/v1/collis/{setup_colli["colli_id"]}/letters/{letter_id}',
            headers={'Authorization': f'Bearer {setup_colli["member_token"]}'}
        )
        
        assert response.status_code == 200
        assert response.get_json()['id'] == letter_id
    
    def test_delete_letter_by_author(self, client, setup_colli):
        """DELETE /api/v1/collis/<id>/letters/<id> - Supprimer sa lettre."""
        # Créer
        create_res = client.post(
            f'/api/v1/collis/{setup_colli["colli_id"]}/letters',
            json={'letter_type': 'text', 'content': 'À supprimer'},
            headers={'Authorization': f'Bearer {setup_colli["member_token"]}'}
        )
        letter_id = create_res.get_json()['id']
        
        # Delete
        response = client.delete(
            f'/api/v1/collis/{setup_colli["colli_id"]}/letters/{letter_id}',
            headers={'Authorization': f'Bearer {setup_colli["member_token"]}'}
        )
        
        assert response.status_code == 204
    
    def test_delete_letter_by_manager(self, client, setup_colli):
        """Manager peut supprimer n'importe quelle lettre."""
        # Créer par member
        create_res = client.post(
            f'/api/v1/collis/{setup_colli["colli_id"]}/letters',
            json={'letter_type': 'text', 'content': 'Lettre member'},
            headers={'Authorization': f'Bearer {setup_colli["member_token"]}'}
        )
        letter_id = create_res.get_json()['id']
        
        # Delete par teacher (manager)
        response = client.delete(
            f'/api/v1/collis/{setup_colli["colli_id"]}/letters/{letter_id}',
            headers={'Authorization': f'Bearer {setup_colli["teacher_token"]}'}
        )
        
        assert response.status_code == 204
