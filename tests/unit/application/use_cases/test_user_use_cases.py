# tests/unit/application/use_cases/test_user_use_cases.py
"""Tests unitaires pour les Use Cases User."""

import pytest
from uuid import uuid4, UUID

from src.application.use_cases.user.register_user import RegisterUserUseCase, RegisterUserCommand
from src.application.use_cases.user.authenticate_user import AuthenticateUserUseCase, AuthenticateUserCommand
from src.application.use_cases.user.get_current_user import GetCurrentUserUseCase
from src.application.exceptions import ValidationException, UnauthorizedException, NotFoundException, ConflictException
from src.infrastructure.persistence.in_memory.user_repository import InMemoryUserRepository


class MockJWTService:
    """Mock du service JWT pour les tests."""
    
    def create_access_token(self, user_id, role):
        return f"access_token_{user_id}"
    
    def create_refresh_token(self, user_id):
        return f"refresh_token_{user_id}"
        
    def create_tokens(self, user_id, role):
        return self.create_access_token(user_id, role), self.create_refresh_token(user_id)


def to_uuid(id_str):
    """Convertit un ID string en UUID si nécessaire."""
    if isinstance(id_str, UUID):
        return id_str
    return UUID(id_str) if id_str else None


class TestRegisterUserUseCase:
    """Tests pour RegisterUserUseCase."""
    
    def test_register_success(self):
        """Doit enregistrer un utilisateur."""
        repo = InMemoryUserRepository()
        use_case = RegisterUserUseCase(repo)
        
        command = RegisterUserCommand(
            email="test@example.com",
            password="password123",
            first_name="John",
            last_name="Doe"
        )
        
        result = use_case.execute(command)
        
        assert result is not None
        assert result.email == "test@example.com"
        assert result.first_name == "John"
        assert result.last_name == "Doe"
    
    def test_register_duplicate_email(self):
        """Doit lever ValidationException si email existe."""
        repo = InMemoryUserRepository()
        use_case = RegisterUserUseCase(repo)
        
        command = RegisterUserCommand(
            email="test@example.com",
            password="password123",
            first_name="John",
            last_name="Doe"
        )
        
        
        use_case.execute(command)
        
        with pytest.raises(ConflictException):
            use_case.execute(command)
    
    def test_register_invalid_email(self):
        """Doit lever si email invalide."""
        repo = InMemoryUserRepository()
        use_case = RegisterUserUseCase(repo)
        
        command = RegisterUserCommand(
            email="invalid-email",
            password="password123",
            first_name="John",
            last_name="Doe"
        )
        
        with pytest.raises((ValidationException, ValueError)):
            use_case.execute(command)


class TestAuthenticateUserUseCase:
    """Tests pour AuthenticateUserUseCase."""
    
    def test_authenticate_success(self):
        """Doit authentifier un utilisateur valide."""
        repo = InMemoryUserRepository()
        jwt_service = MockJWTService()
        
        # Register user first
        register_uc = RegisterUserUseCase(repo)
        register_uc.execute(RegisterUserCommand(
            email="user@example.com",
            password="password123",
            first_name="Test",
            last_name="User"
        ))
        
        use_case = AuthenticateUserUseCase(repo, jwt_service)
        
        command = AuthenticateUserCommand(
            email="user@example.com",
            password="password123"
        )
        
        result = use_case.execute(command)
        
        assert result is not None
        assert result.tokens.access_token is not None
        assert result.tokens.refresh_token is not None
    
    def test_authenticate_wrong_password(self):
        """Doit lever UnauthorizedException pour mauvais mot de passe."""
        repo = InMemoryUserRepository()
        jwt_service = MockJWTService()
        
        # Register user
        register_uc = RegisterUserUseCase(repo)
        register_uc.execute(RegisterUserCommand(
            email="user@example.com",
            password="password123",
            first_name="Test",
            last_name="User"
        ))
        
        use_case = AuthenticateUserUseCase(repo, jwt_service)
        
        command = AuthenticateUserCommand(
            email="user@example.com",
            password="wrongpassword"
        )
        
        with pytest.raises(UnauthorizedException):
            use_case.execute(command)
    
    def test_authenticate_unknown_email(self):
        """Doit lever UnauthorizedException pour email inconnu."""
        repo = InMemoryUserRepository()
        jwt_service = MockJWTService()
        use_case = AuthenticateUserUseCase(repo, jwt_service)
        
        command = AuthenticateUserCommand(
            email="unknown@example.com",
            password="password123"
        )
        
        with pytest.raises(UnauthorizedException):
            use_case.execute(command)


class TestGetCurrentUserUseCase:
    """Tests pour GetCurrentUserUseCase."""
    
    def test_get_current_user_success(self):
        """Doit retourner l'utilisateur courant."""
        repo = InMemoryUserRepository()
        
        # Register user
        register_uc = RegisterUserUseCase(repo)
        user_dto = register_uc.execute(RegisterUserCommand(
            email="user@example.com",
            password="password123",
            first_name="Test",
            last_name="User"
        ))
        
        use_case = GetCurrentUserUseCase(repo)
        result = use_case.execute(to_uuid(user_dto.id))
        
        assert result is not None
        assert result.email == "user@example.com"
    
    def test_get_nonexistent_user(self):
        """Doit lever NotFoundException."""
        repo = InMemoryUserRepository()
        use_case = GetCurrentUserUseCase(repo)
        
        with pytest.raises(NotFoundException):
            use_case.execute(uuid4())
