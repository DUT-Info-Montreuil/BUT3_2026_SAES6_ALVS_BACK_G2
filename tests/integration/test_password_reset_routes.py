# tests/integration/test_password_reset_routes.py
"""Tests d'integration pour les routes de reset de mot de passe."""

import pytest


class TestForgotPasswordRoutes:
    """Tests pour l'endpoint forgot-password."""
    
    def test_forgot_password_missing_email(self, client):
        """Test: forgot password sans email retourne 400."""
        response = client.post(
            '/api/v1/auth/forgot-password',
            json={}
        )
        assert response.status_code == 400
    
    def test_forgot_password_invalid_email(self, client):
        """Test: forgot password avec email inexistant retourne 200 (securite)."""
        response = client.post(
            '/api/v1/auth/forgot-password',
            json={'email': 'nonexistent@example.com'}
        )
        # Retourne toujours 200 pour ne pas reveler si l'email existe
        assert response.status_code == 200
        data = response.get_json()
        assert 'message' in data
    
    def test_forgot_password_valid_email(self, client, registered_user):
        """Test: forgot password avec email valide."""
        response = client.post(
            '/api/v1/auth/forgot-password',
            json={'email': registered_user['email']}
        )
        assert response.status_code == 200
        data = response.get_json()
        assert 'message' in data


class TestResetPasswordRoutes:
    """Tests pour l'endpoint reset-password."""
    
    def test_reset_password_missing_fields(self, client):
        """Test: reset password sans champs retourne 400."""
        response = client.post(
            '/api/v1/auth/reset-password',
            json={}
        )
        assert response.status_code == 400
    
    def test_reset_password_invalid_token(self, client):
        """Test: reset password avec token invalide retourne 400."""
        response = client.post(
            '/api/v1/auth/reset-password',
            json={
                'token': 'invalid-token',
                'new_password': 'NewPassword123!',
                'confirm_password': 'NewPassword123!'
            }
        )
        assert response.status_code == 400
    
    def test_reset_password_mismatched_passwords(self, client):
        """Test: reset password avec mots de passe differents retourne 400."""
        response = client.post(
            '/api/v1/auth/reset-password',
            json={
                'token': 'some-token',
                'new_password': 'NewPassword123!',
                'confirm_password': 'DifferentPassword!'
            }
        )
        assert response.status_code == 400
    
    def test_reset_password_short_password(self, client):
        """Test: reset password avec mot de passe court retourne 400."""
        response = client.post(
            '/api/v1/auth/reset-password',
            json={
                'token': 'some-token',
                'new_password': 'short',
                'confirm_password': 'short'
            }
        )
        assert response.status_code == 400


class TestFullPasswordResetFlow:
    """Tests pour le flow complet de reset de mot de passe."""
    
    def test_forgot_then_reset(self, client, registered_user):
        """Test: flow complet forgot -> reset."""
        # 1. Demander un reset
        forgot_response = client.post(
            '/api/v1/auth/forgot-password',
            json={'email': registered_user['email']}
        )
        assert forgot_response.status_code == 200
        
        # En mode dev, le token est retourne
        data = forgot_response.get_json()
        token = data.get('token')
        
        if token:
            # 2. Utiliser le token pour reset
            reset_response = client.post(
                '/api/v1/auth/reset-password',
                json={
                    'token': token,
                    'new_password': 'NewSecurePassword123!',
                    'confirm_password': 'NewSecurePassword123!'
                }
            )
            assert reset_response.status_code == 200
