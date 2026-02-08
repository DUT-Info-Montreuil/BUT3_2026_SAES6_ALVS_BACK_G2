# src/infrastructure/persistence/sqlalchemy/models/user_model.py
"""Modèle SQLAlchemy pour les utilisateurs."""

from sqlalchemy import Column, String, Boolean, DateTime, Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import uuid

from src.infrastructure.persistence.sqlalchemy.database import Base


class UserModel(Base):
    """
    Modèle ORM pour la table users.
    
    Ce modèle est distinct de l'entité User du domaine.
    La conversion se fait via le UserMapper.
    """
    __tablename__ = 'users'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    role = Column(String(50), nullable=False, default='member')
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    last_login_at = Column(DateTime(timezone=True), nullable=True)
    
    def __repr__(self):
        return f"<UserModel(id={self.id}, email={self.email})>"
