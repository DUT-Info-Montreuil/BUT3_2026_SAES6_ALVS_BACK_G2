# tests/integration/test_colli_routes.py
"""Tests d'intégration pour les routes Colli."""

import pytest
from uuid import uuid4
from flask_jwt_extended import create_access_token


class TestColliRoutes:
    """Tests d'intégration pour les routes Colli."""
    
    def test_create_colli_success(self, client, app):
        """POST /api/v1/collis - Doit créer un COLLI."""
        with app.app_context():
            token = create_access_token(
                identity=str(uuid4()),
                additional_claims={'role': 'teacher'}
            )
        
        response = client.post(
            '/api/v1/collis',
            json={
                'name': 'Test COLLI',
                'theme': 'Littérature',
                'description': 'Description du COLLI'
            },
            headers={'Authorization': f'Bearer {token}'}
        )
        
        assert response.status_code == 201
        data = response.get_json()
        assert data['name'] == 'Test COLLI'
        assert data['theme'] == 'Littérature'
        assert data['status'] == 'pending'
    
    def test_create_colli_unauthorized(self, client):
        """POST /api/v1/collis - Doit refuser sans token."""
        response = client.post(
            '/api/v1/collis',
            json={'name': 'Test', 'theme': 'Test'}
        )
        
        assert response.status_code == 401
    
    def test_create_colli_forbidden_student(self, client, app):
        """POST /api/v1/collis - Doit refuser pour un étudiant."""
        with app.app_context():
            token = create_access_token(
                identity=str(uuid4()),
                additional_claims={'role': 'student'}
            )
        
        response = client.post(
            '/api/v1/collis',
            json={'name': 'Test', 'theme': 'Test'},
            headers={'Authorization': f'Bearer {token}'}
        )
        
        assert response.status_code == 403
    
    def test_create_colli_validation_error(self, client, app):
        """POST /api/v1/collis - Doit valider les données."""
        with app.app_context():
            token = create_access_token(
                identity=str(uuid4()),
                additional_claims={'role': 'teacher'}
            )
        
        response = client.post(
            '/api/v1/collis',
            json={'name': ''},  # Nom vide
            headers={'Authorization': f'Bearer {token}'}
        )
        
        assert response.status_code == 400
    
    def test_list_collis(self, client, auth_headers):
        """GET /api/v1/collis - Doit lister les COLLIs."""
        response = client.get(
            '/api/v1/collis',
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'items' in data
        assert 'total' in data
    
    def test_get_colli_not_found(self, client, auth_headers):
        """GET /api/v1/collis/<id> - Doit retourner 404."""
        response = client.get(
            f'/api/v1/collis/{uuid4()}',
            headers=auth_headers
        )
        
        assert response.status_code == 404


class TestColliApprovalRoutes:
    """Tests pour l'approbation des COLLIs."""
    
    def test_approve_colli_admin_only(self, client, app):
        """PATCH /api/v1/collis/<id>/approve - Réservé aux admins."""
        with app.app_context():
            teacher_token = create_access_token(
                identity=str(uuid4()),
                additional_claims={'role': 'teacher'}
            )
        
        response = client.patch(
            f'/api/v1/collis/{uuid4()}/approve',
            headers={'Authorization': f'Bearer {teacher_token}'}
        )
        
        assert response.status_code == 403
    
    def test_approve_colli_success(self, client, app):
        """PATCH /api/v1/collis/<id>/approve - Admin peut approuver."""
        # Créer un COLLI d'abord
        teacher_id = uuid4()
        with app.app_context():
            teacher_token = create_access_token(
                identity=str(teacher_id),
                additional_claims={'role': 'teacher'}
            )
            admin_token = create_access_token(
                identity=str(uuid4()),
                additional_claims={'role': 'admin'}
            )
        
        # Créer le COLLI
        create_response = client.post(
            '/api/v1/collis',
            json={'name': 'Test COLLI', 'theme': 'Test'},
            headers={'Authorization': f'Bearer {teacher_token}'}
        )
        
        assert create_response.status_code == 201
        colli_id = create_response.get_json()['id']
        
        # Approuver
        approve_response = client.patch(
            f'/api/v1/collis/{colli_id}/approve',
            headers={'Authorization': f'Bearer {admin_token}'}
        )
        
        assert approve_response.status_code == 200
        assert approve_response.get_json()['status'] == 'active'


class TestColliMembershipRoutes:
    """Tests pour les routes de membership."""
    
    def test_join_colli_success(self, client, app):
        """POST /api/v1/collis/<id>/join - Rejoindre un COLLI actif."""
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
        
        # Créer et approuver le COLLI
        create_res = client.post(
            '/api/v1/collis',
            json={'name': 'Test', 'theme': 'Test'},
            headers={'Authorization': f'Bearer {teacher_token}'}
        )
        colli_id = create_res.get_json()['id']
        
        client.patch(
            f'/api/v1/collis/{colli_id}/approve',
            headers={'Authorization': f'Bearer {admin_token}'}
        )
        
        # Rejoindre
        join_res = client.post(
            f'/api/v1/collis/{colli_id}/join',
            headers={'Authorization': f'Bearer {member_token}'}
        )
        
        assert join_res.status_code == 200
    
    def test_list_members(self, client, app):
        """GET /api/v1/collis/<id>/members - Lister les membres."""
        teacher_id = uuid4()
        
        with app.app_context():
            teacher_token = create_access_token(
                identity=str(teacher_id),
                additional_claims={'role': 'teacher'}
            )
            admin_token = create_access_token(
                identity=str(uuid4()),
                additional_claims={'role': 'admin'}
            )
        
        # Créer et approuver
        create_res = client.post(
            '/api/v1/collis',
            json={'name': 'Test', 'theme': 'Test'},
            headers={'Authorization': f'Bearer {teacher_token}'}
        )
        colli_id = create_res.get_json()['id']
        
        client.patch(
            f'/api/v1/collis/{colli_id}/approve',
            headers={'Authorization': f'Bearer {admin_token}'}
        )
        
        # Lister les membres
        members_res = client.get(
            f'/api/v1/collis/{colli_id}/members',
            headers={'Authorization': f'Bearer {teacher_token}'}
        )
        
        assert members_res.status_code == 200
        data = members_res.get_json()
        assert 'members' in data
        assert data['total'] >= 1  # Au moins le créateur
