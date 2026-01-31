# src/infrastructure/web/schemas/auth_schema.py
"""Schémas de validation pour l'authentification."""

from marshmallow import Schema, fields, validate, validates, ValidationError


class LoginSchema(Schema):
    """Schéma de validation pour la connexion."""
    email = fields.Email(required=True, error_messages={
        "required": "L'email est obligatoire",
        "invalid": "Format d'email invalide"
    })
    password = fields.String(required=True, validate=validate.Length(min=1), error_messages={
        "required": "Le mot de passe est obligatoire"
    })


class RegisterSchema(Schema):
    """Schéma de validation pour l'inscription."""
    email = fields.Email(required=True, error_messages={
        "required": "L'email est obligatoire",
        "invalid": "Format d'email invalide"
    })
    password = fields.String(
        required=True,
        validate=validate.Length(min=8, error="Le mot de passe doit contenir au moins 8 caractères"),
        error_messages={"required": "Le mot de passe est obligatoire"}
    )
    password_confirm = fields.String(required=True)
    first_name = fields.String(required=True, validate=validate.Length(min=1, max=100))
    last_name = fields.String(required=True, validate=validate.Length(min=1, max=100))
    
    @validates('password_confirm')
    def validate_password_confirm(self, value):
        """Vérifie que password_confirm est présent."""
        if not value:
            raise ValidationError("La confirmation du mot de passe est obligatoire")


class RefreshTokenSchema(Schema):
    """Schéma pour le rafraîchissement de token."""
    refresh_token = fields.String(required=True)


class ChangePasswordSchema(Schema):
    """Schéma pour le changement de mot de passe."""
    current_password = fields.String(required=True)
    new_password = fields.String(
        required=True,
        validate=validate.Length(min=8, error="Le nouveau mot de passe doit contenir au moins 8 caractères")
    )
    new_password_confirm = fields.String(required=True)
