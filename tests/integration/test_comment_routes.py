# tests/integration/test_comment_routes.py
"""Tests d'intégration pour les routes Comment."""

import pytest
from uuid import uuid4
from flask_jwt_extended import create_access_token


class TestCommentRoutes:
    """Tests d'intégration pour les routes Comment."""
    
    @pytest.fixture
    def setup_letter(self, client, app):
        """Crée un COLLI actif avec une lettre."""
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
        create_colli = client.post(
            '/api/v1/collis',
            json={'name': 'Test COLLI', 'theme': 'Test'},
            headers={'Authorization': f'Bearer {teacher_token}'}
        )
        assert create_colli.status_code == 201, f"Create Colli failed: {create_colli.get_json()}"
        colli_id = create_colli.get_json()['id']
        
        approve_res = client.patch(
            f'/api/v1/collis/{colli_id}/approve',
            headers={'Authorization': f'Bearer {admin_token}'}
        )
        assert approve_res.status_code == 200, f"Approve failed: {approve_res.get_json()}"
        
        # Member rejoint
        join_res = client.post(
            f'/api/v1/collis/{colli_id}/join',
            headers={'Authorization': f'Bearer {member_token}'}
        )
        assert join_res.status_code == 200, f"Join failed: {join_res.get_json()}"
        
        # Créer lettre
        create_letter = client.post(
            f'/api/v1/collis/{colli_id}/letters',
            json={'letter_type': 'text', 'content': 'Ma lettre longue pour le test'},
            headers={'Authorization': f'Bearer {member_token}'}
        )
        assert create_letter.status_code == 201, f"Create Letter failed: {create_letter.get_json()}"
        letter_id = create_letter.get_json()['id']
        
        return {
            'colli_id': colli_id,
            'letter_id': letter_id,
            'teacher_id': teacher_id,
            'teacher_token': teacher_token,
            'member_id': member_id,
            'member_token': member_token
        }
    
    def test_create_comment(self, client, setup_letter):
        """POST /api/v1/letters/<id>/comments - Créer un commentaire."""
        response = client.post(
            f'/api/v1/letters/{setup_letter["letter_id"]}/comments',
            json={'content': 'Super lettre !'},
            headers={'Authorization': f'Bearer {setup_letter["member_token"]}'}
        )
        
        assert response.status_code == 201
        data = response.get_json()
        assert data['content'] == 'Super lettre !'
    
    def test_create_comment_unauthorized(self, client, setup_letter):
        """POST sans token refusé."""
        response = client.post(
            f'/api/v1/letters/{setup_letter["letter_id"]}/comments',
            json={'content': 'Test'}
        )
        
        assert response.status_code == 401
    
    def test_create_comment_non_member(self, client, app, setup_letter):
        """Non-membre ne peut pas commenter."""
        with app.app_context():
            stranger_token = create_access_token(
                identity=str(uuid4()),
                additional_claims={'role': 'student'}
            )
        
        response = client.post(
            f'/api/v1/letters/{setup_letter["letter_id"]}/comments',
            json={'content': 'Je ne suis pas membre'},
            headers={'Authorization': f'Bearer {stranger_token}'}
        )
        
        assert response.status_code == 403
    
    def test_create_comment_empty_content(self, client, setup_letter):
        """Contenu vide refusé."""
        response = client.post(
            f'/api/v1/letters/{setup_letter["letter_id"]}/comments',
            json={'content': ''},
            headers={'Authorization': f'Bearer {setup_letter["member_token"]}'}
        )
        
        assert response.status_code == 400
    
    def test_list_comments(self, client, setup_letter):
        """GET /api/v1/letters/<id>/comments - Lister les commentaires."""
        # Créer des commentaires
        for i in range(3):
            client.post(
                f'/api/v1/letters/{setup_letter["letter_id"]}/comments',
                json={'content': f'Commentaire {i}'},
                headers={'Authorization': f'Bearer {setup_letter["member_token"]}'}
            )
        
        # Lister
        response = client.get(
            f'/api/v1/letters/{setup_letter["letter_id"]}/comments',
            headers={'Authorization': f'Bearer {setup_letter["member_token"]}'}
        )
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'items' in data
        assert data['total'] == 3
    
    def test_list_comments_pagination(self, client, setup_letter):
        """Pagination des commentaires."""
        # Créer 5 commentaires
        for i in range(5):
            client.post(
                f'/api/v1/letters/{setup_letter["letter_id"]}/comments',
                json={'content': f'Commentaire {i}'},
                headers={'Authorization': f'Bearer {setup_letter["member_token"]}'}
            )
        
        # Page 1
        response = client.get(
            f'/api/v1/letters/{setup_letter["letter_id"]}/comments?per_page=2',
            headers={'Authorization': f'Bearer {setup_letter["member_token"]}'}
        )
        
        data = response.get_json()
        assert len(data['items']) == 2
        assert data['has_more'] is True
    
    def test_delete_comment_by_author(self, client, setup_letter):
        """DELETE /api/v1/letters/<id>/comments/<id> - Supprimer son commentaire."""
        # Créer
        create_res = client.post(
            f'/api/v1/letters/{setup_letter["letter_id"]}/comments',
            json={'content': 'À supprimer'},
            headers={'Authorization': f'Bearer {setup_letter["member_token"]}'}
        )
        comment_id = create_res.get_json()['id']
        
        # Delete
        response = client.delete(
            f'/api/v1/letters/{setup_letter["letter_id"]}/comments/{comment_id}',
            headers={'Authorization': f'Bearer {setup_letter["member_token"]}'}
        )
        
        assert response.status_code == 204
    
    def test_delete_comment_by_moderator(self, client, setup_letter):
        """Modérateur peut supprimer n'importe quel commentaire."""
        # Créer par member
        create_res = client.post(
            f'/api/v1/letters/{setup_letter["letter_id"]}/comments',
            json={'content': 'Commentaire à modérer'},
            headers={'Authorization': f'Bearer {setup_letter["member_token"]}'}
        )
        comment_id = create_res.get_json()['id']
        
        # Delete par teacher (modérateur)
        response = client.delete(
            f'/api/v1/letters/{setup_letter["letter_id"]}/comments/{comment_id}',
            headers={'Authorization': f'Bearer {setup_letter["teacher_token"]}'}
        )
        
        assert response.status_code == 204
    
    def test_delete_comment_forbidden(self, client, app, setup_letter):
        """Non-auteur et non-modérateur ne peut pas supprimer."""
        # Créer par member
        create_res = client.post(
            f'/api/v1/letters/{setup_letter["letter_id"]}/comments',
            json={'content': 'Mon commentaire'},
            headers={'Authorization': f'Bearer {setup_letter["member_token"]}'}
        )
        comment_id = create_res.get_json()['id']
        
        # Autre utilisateur essaie de supprimer
        with app.app_context():
            other_token = create_access_token(
                identity=str(uuid4()),
                additional_claims={'role': 'student'}
            )
        
        response = client.delete(
            f'/api/v1/letters/{setup_letter["letter_id"]}/comments/{comment_id}',
            headers={'Authorization': f'Bearer {other_token}'}
        )
        
        assert response.status_code == 403
