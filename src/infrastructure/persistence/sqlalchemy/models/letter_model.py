# src/infrastructure/persistence/sqlalchemy/models/letter_model.py
"""Modèle SQLAlchemy pour les Letters."""

from sqlalchemy import Column, String, Text, DateTime, ForeignKey, Uuid
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid

from src.infrastructure.persistence.sqlalchemy.database import Base


class LetterModel(Base):
    """
    Modèle ORM pour la table letters.
    """
    __tablename__ = 'letters'
    
    id = Column(Uuid, primary_key=True, default=uuid.uuid4)
    letter_type = Column(String(20), nullable=False, default='text')
    title = Column(String(255), nullable=True)
    content = Column(Text, nullable=True)
    file_url = Column(String(255), nullable=True)
    file_name = Column(String(255), nullable=True)
    colli_id = Column(Uuid, ForeignKey('collis.id'), nullable=False, index=True)
    sender_id = Column(Uuid, ForeignKey('users.id'), nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relations
    sender = relationship("UserModel", backref="letters")
    colli = relationship("ColliModel", backref="letters")
    comments = relationship("CommentModel", back_populates="letter", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<LetterModel(id={self.id}, type={self.letter_type})>"
