# tests/unit/shared/test_domain_exception.py
"""Tests pour les exceptions du domaine métier."""

import pytest
from src.shared.domain_exception import DomainException, ConfigurationError


class TestDomainException:
    """Tests pour DomainException."""
    
    def test_domain_exception_creation(self):
        """Test la création d'une DomainException."""
        message = "Erreur du domaine"
        exception = DomainException(message)
        
        assert str(exception) == message
        assert isinstance(exception, Exception)
    
    def test_domain_exception_inheritance(self):
        """Test que DomainException hérite bien d'Exception."""
        exception = DomainException("test")
        
        assert isinstance(exception, Exception)
        assert issubclass(DomainException, Exception)
    
    def test_domain_exception_without_message(self):
        """Test la création d'une DomainException sans message."""
        exception = DomainException()
        
        assert str(exception) == ""


class TestConfigurationError:
    """Tests pour ConfigurationError."""
    
    def test_configuration_error_creation(self):
        """Test la création d'une ConfigurationError."""
        message = "Erreur de configuration"
        exception = ConfigurationError(message)
        
        assert str(exception) == message
        assert isinstance(exception, DomainException)
        assert isinstance(exception, Exception)
    
    def test_configuration_error_inheritance(self):
        """Test que ConfigurationError hérite de DomainException."""
        exception = ConfigurationError("test")
        
        assert isinstance(exception, DomainException)
        assert isinstance(exception, Exception)
        assert issubclass(ConfigurationError, DomainException)
    
    def test_configuration_error_without_message(self):
        """Test la création d'une ConfigurationError sans message."""
        exception = ConfigurationError()
        
        assert str(exception) == ""
    
    def test_configuration_error_can_be_raised(self):
        """Test qu'on peut lever une ConfigurationError."""
        with pytest.raises(ConfigurationError) as exc_info:
            raise ConfigurationError("Test error")
        
        assert str(exc_info.value) == "Test error"