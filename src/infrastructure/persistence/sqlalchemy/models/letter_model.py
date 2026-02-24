# src/infrastructure/persistence/sqlalchemy/models/letter_model.py
"""Modèle SQLAlchemy pour les Letters."""

import uuid

from sqlalchemy import Column, DateTime, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from src.infrastructure.persistence.sqlalchemy.database import Base


class LetterModel(Base):
    """
    Modèle ORM pour la table letters.
    """
    __tablename__ = 'letters'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    letter_type = Column(String(20), nullable=False, default='text')
    content = Column(Text, nullable=True)
    file_url = Column(String(255), nullable=True)
    file_name = Column(String(255), nullable=True)
    colli_id = Column(UUID(as_uuid=True), ForeignKey('collis.id'), nullable=False, index=True)
    sender_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relations
    sender = relationship("UserModel", backref="letters")
    colli = relationship("ColliModel", backref="letters")
    comments = relationship("CommentModel", back_populates="letter", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<LetterModel(id={self.id}, type={self.letter_type})>"
