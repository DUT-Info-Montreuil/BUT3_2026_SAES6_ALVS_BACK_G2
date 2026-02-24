# src/infrastructure/persistence/sqlalchemy/mappers/comment_mapper.py
"""Mapper pour convertir entre Comment entity et CommentModel."""

from src.domain.collaboration.entities.comment import Comment
from src.infrastructure.persistence.sqlalchemy.models.comment_model import CommentModel


class CommentMapper:
    """
    Mapper bidirectionnel Comment Entity ↔ CommentModel ORM.
    """

    @staticmethod
    def to_entity(model: CommentModel) -> Comment:
        """
        Convertit un modèle ORM en entité du domaine.
        """
        return Comment(
            id=model.id,
            content=model.content,
            letter_id=model.letter_id,
            sender_id=model.sender_id,
            created_at=model.created_at,
            updated_at=model.updated_at
        )

    @staticmethod
    def to_model(entity: Comment) -> CommentModel:
        """
        Convertit une entité du domaine en modèle ORM.
        """
        return CommentModel(
            id=entity.id,
            content=entity.content,
            letter_id=entity.letter_id,
            sender_id=entity.sender_id,
            created_at=entity.created_at,
            updated_at=entity.updated_at
        )

    @staticmethod
    def update_model(model: CommentModel, entity: Comment) -> CommentModel:
        """
        Met à jour un modèle existant avec les données d'une entité.
        """
        model.content = entity.content
        model.updated_at = entity.updated_at
        return model
