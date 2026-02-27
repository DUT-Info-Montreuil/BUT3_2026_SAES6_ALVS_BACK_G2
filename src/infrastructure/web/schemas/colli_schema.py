# src/infrastructure/web/schemas/colli_schema.py
"""Schémas de validation pour les Collis."""

from marshmallow import Schema, fields, validate, post_load


class CreateColliSchema(Schema):
    """Schéma de validation pour la création d'un COLLI."""
    name = fields.String(
        required=True,
        validate=validate.Length(min=3, max=100, error="Le nom doit contenir entre 3 et 100 caractères"),
        error_messages={"required": "Le nom du COLLI est obligatoire"}
    )
    theme = fields.String(
        required=True,
        validate=validate.Length(min=2, max=100, error="Le thème doit contenir entre 2 et 100 caractères"),
        error_messages={"required": "Le thème du COLLI est obligatoire"}
    )
    description = fields.String(
        required=False,
        validate=validate.Length(max=2000, error="La description ne peut pas dépasser 2000 caractères"),
        allow_none=True
    )


class UpdateColliSchema(Schema):
    """Schéma de validation pour la mise à jour d'un COLLI."""
    name = fields.String(
        required=False,
        validate=validate.Length(min=3, max=100)
    )
    theme = fields.String(
        required=False,
        validate=validate.Length(min=2, max=100)
    )
    description = fields.String(
        required=False,
        validate=validate.Length(max=2000),
        allow_none=True
    )


class RejectColliSchema(Schema):
    """Schéma pour le rejet d'un COLLI."""
    reason = fields.String(
        required=False,
        validate=validate.Length(max=500),
        allow_none=True
    )


class AddMemberSchema(Schema):
    """Schéma pour ajouter un membre à un COLLI."""
    user_id = fields.UUID(
        required=True,
        error_messages={"required": "L'ID de l'utilisateur est obligatoire"}
    )
    role = fields.String(
        required=False,
        validate=validate.OneOf(
            ["member", "moderator", "patron"],
            error="Rôle invalide. Valeurs acceptées: member, moderator, patron"
        ),
        load_default="member"
    )


class ColliListQuerySchema(Schema):
    """Schéma pour les paramètres de liste des COLLIs."""
    page = fields.Integer(
        required=False,
        load_default=1,
        validate=validate.Range(min=1, error="Le numéro de page doit être >= 1")
    )
    per_page = fields.Integer(
        required=False,
        load_default=20,
        validate=validate.Range(min=1, max=100, error="per_page doit être entre 1 et 100")
    )
    status = fields.String(
        required=False,
        validate=validate.OneOf(
            ["pending", "active", "rejected", "completed"],
            error="Statut invalide"
        )
    )
