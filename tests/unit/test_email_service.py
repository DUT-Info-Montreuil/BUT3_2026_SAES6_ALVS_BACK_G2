# tests/unit/test_email_service.py
"""Tests unitaires pour le service email."""

import pytest
from unittest.mock import patch, MagicMock

from src.infrastructure.services.email_service import EmailService, EmailConfig


class TestEmailConfig:
    """Tests pour la configuration email."""
    
    def test_default_config(self):
        """Test: configuration par defaut."""
        config = EmailConfig()
        
        assert config.host == "smtp.gmail.com"
        assert config.port == 587
        assert config.use_tls is True
    
    def test_custom_config(self):
        """Test: configuration personnalisee."""
        config = EmailConfig(
            host="smtp.example.com",
            port=465,
            username="user@example.com",
            password="secret",
            from_email="no-reply@example.com"
        )
        
        assert config.host == "smtp.example.com"
        assert config.port == 465
        assert config.username == "user@example.com"


class TestEmailService:
    """Tests pour le service email."""
    
    def test_service_disabled_without_credentials(self):
        """Test: service desactive sans credentials."""
        config = EmailConfig()  # Sans username/password
        service = EmailService(config)
        
        assert service.is_enabled() is False
    
    def test_service_enabled_with_credentials(self):
        """Test: service active avec credentials."""
        config = EmailConfig(
            username="user@example.com",
            password="password"
        )
        service = EmailService(config)
        
        assert service.is_enabled() is True
    
    def test_send_email_disabled_returns_false(self):
        """Test: envoi email desactive retourne False."""
        config = EmailConfig()
        service = EmailService(config)
        
        result = service.send_email(
            to_email="test@example.com",
            subject="Test",
            body_html="<p>Test</p>"
        )
        
        assert result is False
    
    @patch('smtplib.SMTP')
    def test_send_email_success(self, mock_smtp):
        """Test: envoi email reussi."""
        # Configurer le mock
        mock_server = MagicMock()
        mock_smtp.return_value.__enter__.return_value = mock_server
        
        config = EmailConfig(
            username="user@example.com",
            password="password",
            from_email="no-reply@example.com"
        )
        service = EmailService(config)
        
        result = service.send_email(
            to_email="test@example.com",
            subject="Test Subject",
            body_html="<p>Test Body</p>"
        )
        
        assert result is True
        mock_server.starttls.assert_called_once()
        mock_server.login.assert_called_once()
        mock_server.sendmail.assert_called_once()
    
    def test_send_password_reset_disabled(self):
        """Test: envoi password reset desactive."""
        config = EmailConfig()
        service = EmailService(config)
        
        result = service.send_password_reset(
            to_email="test@example.com",
            reset_token="abc123",
            reset_url="http://example.com/reset?token=abc123"
        )
        
        assert result is False


class TestPasswordResetEmail:
    """Tests pour l'email de reset de mot de passe."""
    
    @patch('smtplib.SMTP')
    def test_password_reset_email_content(self, mock_smtp):
        """Test: contenu de l'email de reset."""
        mock_server = MagicMock()
        mock_smtp.return_value.__enter__.return_value = mock_server
        
        config = EmailConfig(
            username="user@example.com",
            password="password",
            from_email="no-reply@example.com"
        )
        service = EmailService(config)
        
        service.send_password_reset(
            to_email="test@example.com",
            reset_token="abc123",
            reset_url="http://example.com/reset"
        )
        
        # Verifier que sendmail a ete appele
        mock_server.sendmail.assert_called_once()
        
        # Verifier le contenu
        call_args = mock_server.sendmail.call_args
        email_content = call_args[0][2]  # 3eme argument = message
        
        assert "abc123" in email_content
        assert "http://example.com/reset" in email_content
