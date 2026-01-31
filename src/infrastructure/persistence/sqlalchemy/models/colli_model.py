# src/infrastructure/persistence/sqlalchemy/models/colli_model.py
"""Modèle SQLAlchemy pour les COLLIs et Memberships."""

from sqlalchemy import Column, String, Text, DateTime, ForeignKey, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid

from src.infrastructure.persistence.sqlalchemy.database import Base


class ColliModel(Base):
    """
    Modèle ORM pour la table collis.
    """
    __tablename__ = 'collis'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(100), nullable=False)
    theme = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    creator_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False)
    status = Column(String(20), nullable=False, default='pending', index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relations
    creator = relationship("UserModel", backref="created_collis")
    members = relationship("MembershipModel", back_populates="colli", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<ColliModel(id={self.id}, name={self.name})>"


class MembershipModel(Base):
    """
    Modèle ORM pour la table memberships (appartenance à un COLLI).
    """
    __tablename__ = 'memberships'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False)
    colli_id = Column(UUID(as_uuid=True), ForeignKey('collis.id'), nullable=False)
    role = Column(String(20), nullable=False, default='member')
    joined_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relations
    user = relationship("UserModel", backref="memberships")
    colli = relationship("ColliModel", back_populates="members")
    
    def __repr__(self):
        return f"<MembershipModel(user_id={self.user_id}, colli_id={self.colli_id})>"
