# src/infrastructure/persistence/sqlalchemy/mappers/letter_mapper.py
"""Mapper pour convertir entre Letter entity et LetterModel."""

from src.domain.collaboration.entities.letter import Letter
from src.domain.collaboration.value_objects.letter_type import LetterType
from src.infrastructure.persistence.sqlalchemy.models.letter_model import LetterModel


class LetterMapper:
    """
    Mapper bidirectionnel Letter Entity ↔ LetterModel ORM.
    """

    @staticmethod
    def to_entity(model: LetterModel) -> Letter:
        """
        Convertit un modèle ORM en entité du domaine.
        """
        return Letter(
            id=model.id,
            letter_type=LetterType(model.letter_type),
            content=model.content,
            file_url=model.file_url,
            file_name=model.file_name,
            title=model.title,
            colli_id=model.colli_id,
            sender_id=model.sender_id,
            created_at=model.created_at,
            updated_at=model.updated_at
        )

    @staticmethod
    def to_model(entity: Letter) -> LetterModel:
        """
        Convertit une entité du domaine en modèle ORM.
        """
        return LetterModel(
            id=entity.id,
            letter_type=entity.letter_type.value,
            content=entity.content,
            file_url=entity.file_url,
            file_name=entity.file_name,
            title=entity.title,
            colli_id=entity.colli_id,
            sender_id=entity.sender_id,
            created_at=entity.created_at,
            updated_at=entity.updated_at
        )

    @staticmethod
    def update_model(model: LetterModel, entity: Letter) -> LetterModel:
        """
        Met à jour un modèle existant avec les données d'une entité.
        """
        model.content = entity.content
        model.file_url = entity.file_url
        model.file_name = entity.file_name
        model.title = entity.title
        model.updated_at = entity.updated_at
        return model
