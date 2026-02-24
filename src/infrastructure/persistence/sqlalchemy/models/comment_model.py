# src/infrastructure/persistence/sqlalchemy/models/comment_model.py
"""Modèle SQLAlchemy pour les Comments."""

from sqlalchemy import Column, Text, DateTime, ForeignKey, Uuid
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid

from src.infrastructure.persistence.sqlalchemy.database import Base


class CommentModel(Base):
    """
    Modèle ORM pour la table comments.
    """
    __tablename__ = 'comments'
    
    id = Column(Uuid, primary_key=True, default=uuid.uuid4)
    content = Column(Text, nullable=False)
    letter_id = Column(Uuid, ForeignKey('letters.id'), nullable=False, index=True)
    sender_id = Column(Uuid, ForeignKey('users.id'), nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relations
    sender = relationship("UserModel", backref="comments")
    letter = relationship("LetterModel", back_populates="comments")
    
    def __repr__(self):
        return f"<CommentModel(id={self.id}, letter_id={self.letter_id})>"
