# src/application/dtos/user_dto.py
"""Data Transfer Objects pour les utilisateurs."""

from dataclasses import asdict, dataclass

from src.domain.identity.entities.user import User


@dataclass
class RegisterUserDTO:
    """DTO pour l'inscription d'un utilisateur."""
    email: str
    password: str
    first_name: str
    last_name: str


@dataclass
class LoginDTO:
    """DTO pour la connexion."""
    email: str
    password: str


@dataclass
class UserResponseDTO:
    """DTO pour les réponses contenant un utilisateur."""
    id: str
    email: str
    first_name: str
    last_name: str
    role: str
    is_active: bool
    created_at: str

    @classmethod
    def from_entity(cls, user: User) -> "UserResponseDTO":
        """Construit le DTO depuis une entité."""
        return cls(
            id=str(user.id),
            email=str(user.email),
            first_name=user.first_name,
            last_name=user.last_name,
            role=user.role.value,
            is_active=user.is_active,
            created_at=user.created_at.isoformat()
        )

    def to_dict(self) -> dict:
        """Convertit en dictionnaire."""
        return asdict(self)


@dataclass
class AuthTokensDTO:
    """DTO pour les tokens d'authentification."""
    access_token: str
    refresh_token: str
    token_type: str = "Bearer"
    expires_in: int = 3600

    def to_dict(self) -> dict:
        """Convertit en dictionnaire."""
        return asdict(self)


@dataclass
class LoginResponseDTO:
    """DTO pour la réponse de connexion."""
    user: UserResponseDTO
    tokens: AuthTokensDTO

    def to_dict(self) -> dict:
        """Convertit en dictionnaire."""
        return {
            "user": self.user.to_dict(),
            "tokens": self.tokens.to_dict()
        }
