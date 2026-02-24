# src/infrastructure/persistence/sqlalchemy/mappers/colli_mapper.py
"""Mapper pour convertir entre Colli entity et ColliModel."""

from typing import List

from src.domain.collaboration.entities.colli import Colli
from src.domain.collaboration.entities.membership import Membership
from src.domain.collaboration.value_objects.colli_status import ColliStatus
from src.domain.collaboration.value_objects.member_role import MemberRole
from src.infrastructure.persistence.sqlalchemy.models.colli_model import ColliModel, MembershipModel


class MembershipMapper:
    """Mapper pour Membership Entity ↔ MembershipModel."""

    @staticmethod
    def to_entity(model: MembershipModel) -> Membership:
        """Convertit un modèle en entité."""
        return Membership(
            id=model.id,
            user_id=model.user_id,
            colli_id=model.colli_id,
            role=MemberRole(model.role),
            joined_at=model.joined_at
        )

    @staticmethod
    def to_model(entity: Membership) -> MembershipModel:
        """Convertit une entité en modèle."""
        return MembershipModel(
            id=entity.id,
            user_id=entity.user_id,
            colli_id=entity.colli_id,
            role=entity.role.value,
            joined_at=entity.joined_at
        )


class ColliMapper:
    """
    Mapper bidirectionnel Colli Entity ↔ ColliModel ORM.

    Gère également la conversion des Memberships imbriqués.
    """

    @staticmethod
    def to_entity(model: ColliModel, include_members: bool = True) -> Colli:
        """
        Convertit un modèle ORM en entité du domaine.

        Args:
            model: Le modèle ColliModel.
            include_members: Si True, inclut les membres.

        Returns:
            Colli: L'entité du domaine avec ses membres.
        """
        colli = Colli(
            id=model.id,
            name=model.name,
            theme=model.theme,
            description=model.description,
            creator_id=model.creator_id,
            status=ColliStatus(model.status),
            created_at=model.created_at,
            updated_at=model.updated_at
        )

        # Charger les membres si demandé
        if include_members and model.members:
            colli._members = [
                MembershipMapper.to_entity(m) for m in model.members
            ]

        return colli

    @staticmethod
    def to_model(entity: Colli) -> ColliModel:
        """
        Convertit une entité du domaine en modèle ORM.

        Args:
            entity: L'entité Colli.

        Returns:
            ColliModel: Le modèle ORM.
        """
        model = ColliModel(
            id=entity.id,
            name=entity.name,
            theme=entity.theme,
            description=entity.description,
            creator_id=entity.creator_id,
            status=entity.status.value,
            created_at=entity.created_at,
            updated_at=entity.updated_at
        )

        # Convertir les membres
        model.members = [
            MembershipMapper.to_model(m) for m in entity.members
        ]

        return model

    @staticmethod
    def update_model(model: ColliModel, entity: Colli) -> ColliModel:
        """
        Met à jour un modèle existant.

        Args:
            model: Le modèle ORM existant.
            entity: L'entité source.

        Returns:
            ColliModel: Le modèle mis à jour.
        """
        model.name = entity.name
        model.theme = entity.theme
        model.description = entity.description
        model.status = entity.status.value
        model.updated_at = entity.updated_at

        # Synchroniser les membres
        existing_member_ids = {m.id for m in model.members}
        entity_member_ids = {m.id for m in entity.members}

        # Supprimer les membres retirés
        model.members = [
            m for m in model.members if m.id in entity_member_ids
        ]

        # Ajouter les nouveaux membres
        for member in entity.members:
            if member.id not in existing_member_ids:
                model.members.append(MembershipMapper.to_model(member))

        return model

    @staticmethod
    def to_entity_list(models: List[ColliModel]) -> List[Colli]:
        """Convertit une liste de modèles en entités."""
        return [ColliMapper.to_entity(m) for m in models]
