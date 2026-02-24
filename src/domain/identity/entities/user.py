# src/domain/identity/entities/user.py
"""
Aggregate Root User - Utilisateur du système ALVS.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4

from src.domain.identity.value_objects.email import Email
from src.domain.identity.value_objects.user_role import UserRole
from src.domain.identity.value_objects.hashed_password import HashedPassword
from src.domain.shared.domain_exception import DomainException


class InvalidCredentialsException(DomainException):
    """Exception levée quand les identifiants sont invalides."""
    pass


@dataclass
class User:
    """
    Aggregate Root pour les utilisateurs.
    
    Invariants:
    - L'email doit être unique (vérifié au niveau du repository)
    - Le mot de passe doit respecter les règles de complexité
    - Le rôle détermine les permissions globales
    """
    id: UUID
    email: Email
    password: HashedPassword
    first_name: str
    last_name: str
    role: UserRole = UserRole.MEMBER
    is_active: bool = True
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    last_login_at: Optional[datetime] = None
    
    @classmethod
    def create(
        cls,
        email: str,
        password: str,
        first_name: str,
        last_name: str,
        role: UserRole = UserRole.MEMBER
    ) -> "User":
        """
        Factory method pour créer un nouvel utilisateur.
        
        Args:
            email: Adresse email.
            password: Mot de passe en clair (sera hashé).
            first_name: Prénom.
            last_name: Nom de famille.
            role: Rôle global (défaut: MEMBER).
            
        Returns:
            User: Nouvel utilisateur.
        """
        validated_email = Email.create(email)
        hashed_password = HashedPassword.create(password)
        
        if not first_name or len(first_name.strip()) < 1:
            raise ValueError("Le prénom est obligatoire")
        if not last_name or len(last_name.strip()) < 1:
            raise ValueError("Le nom est obligatoire")
        
        return cls(
            id=uuid4(),
            email=validated_email,
            password=hashed_password,
            first_name=first_name.strip(),
            last_name=last_name.strip(),
            role=role
        )
    
    def verify_password(self, plain_password: str) -> bool:
        """
        Vérifie si le mot de passe correspond.
        
        Args:
            plain_password: Mot de passe en clair.
            
        Returns:
            bool: True si correct.
        """
        return self.password.verify(plain_password)
    
    def authenticate(self, plain_password: str) -> None:
        """
        Authentifie l'utilisateur et met à jour last_login_at.
        
        Args:
            plain_password: Mot de passe en clair.
            
        Raises:
            InvalidCredentialsException: Si le mot de passe est incorrect.
        """
        if not self.is_active:
            raise InvalidCredentialsException("Compte désactivé")
        
        if not self.verify_password(plain_password):
            raise InvalidCredentialsException("Identifiants invalides")
        
        self.last_login_at = datetime.utcnow()
        self._touch()
    
    def change_password(self, current: str, new_password: str) -> None:
        """
        Change le mot de passe de l'utilisateur.
        
        Args:
            current: Mot de passe actuel.
            new_password: Nouveau mot de passe.
            
        Raises:
            InvalidCredentialsException: Si le mot de passe actuel est incorrect.
        """
        if not self.verify_password(current):
            raise InvalidCredentialsException("Mot de passe actuel incorrect")
        
        self.password = HashedPassword.create(new_password)
        self._touch()
    
    def promote_to(self, new_role: UserRole) -> None:
        """Promeut l'utilisateur à un nouveau rôle."""
        self.role = new_role
        self._touch()
    
    def deactivate(self) -> None:
        """Désactive le compte utilisateur."""
        self.is_active = False
        self._touch()
    
    def reactivate(self) -> None:
        """Réactive le compte utilisateur."""
        self.is_active = True
        self._touch()
    
    @property
    def full_name(self) -> str:
        """Retourne le nom complet."""
        return f"{self.first_name} {self.last_name}"
    
    @property
    def can_create_colli(self) -> bool:
        """Vérifie si l'utilisateur peut créer un COLLI."""
        return self.role.can_create_colli()
    
    @property
    def is_admin(self) -> bool:
        """Vérifie si l'utilisateur est admin."""
        return self.role.is_admin()
    
    def _touch(self) -> None:
        """Met à jour updated_at."""
        self.updated_at = datetime.utcnow()
    
    def __eq__(self, other: object) -> bool:
        if not isinstance(other, User):
            return False
        return self.id == other.id
    
    def __hash__(self) -> int:
        return hash(self.id)
