# src/infrastructure/persistence/sqlalchemy/mappers/user_mapper.py
"""Mapper pour convertir entre User entity et UserModel."""

from src.domain.identity.entities.user import User
from src.domain.identity.value_objects.email import Email
from src.domain.identity.value_objects.hashed_password import HashedPassword
from src.domain.identity.value_objects.user_role import UserRole
from src.infrastructure.persistence.sqlalchemy.models.user_model import UserModel


class UserMapper:
    """
    Mapper bidirectionnel User Entity ↔ UserModel ORM.

    Responsabilités:
    - Isolation du domaine de l'infrastructure
    - Conversion sans perte de données
    """

    @staticmethod
    def to_entity(model: UserModel) -> User:
        """
        Convertit un modèle ORM en entité du domaine.

        Args:
            model: Le modèle UserModel.

        Returns:
            User: L'entité du domaine.
        """
        return User(
            id=model.id,
            email=Email(value=model.email),
            password=HashedPassword.from_hash(model.password_hash),
            first_name=model.first_name,
            last_name=model.last_name,
            role=UserRole(model.role),
            is_active=model.is_active,
            created_at=model.created_at,
            updated_at=model.updated_at,
            last_login_at=model.last_login_at
        )

    @staticmethod
    def to_model(entity: User) -> UserModel:
        """
        Convertit une entité du domaine en modèle ORM.

        Args:
            entity: L'entité User.

        Returns:
            UserModel: Le modèle ORM.
        """
        return UserModel(
            id=entity.id,
            email=str(entity.email),
            password_hash=entity.password.value,
            first_name=entity.first_name,
            last_name=entity.last_name,
            role=entity.role.value,
            is_active=entity.is_active,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
            last_login_at=entity.last_login_at
        )

    @staticmethod
    def update_model(model: UserModel, entity: User) -> UserModel:
        """
        Met à jour un modèle existant avec les données d'une entité.

        Args:
            model: Le modèle ORM existant.
            entity: L'entité source.

        Returns:
            UserModel: Le modèle mis à jour.
        """
        model.email = str(entity.email)
        model.password_hash = entity.password.value
        model.first_name = entity.first_name
        model.last_name = entity.last_name
        model.role = entity.role.value
        model.is_active = entity.is_active
        model.updated_at = entity.updated_at
        model.last_login_at = entity.last_login_at
        return model
