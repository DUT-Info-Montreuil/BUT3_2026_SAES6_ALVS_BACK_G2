# src/domain/identity/value_objects/email.py
"""Value Object pour les adresses email validées."""

import re
from dataclasses import dataclass


@dataclass(frozen=True)
class Email:
    """
    Value Object représentant une adresse email validée.

    Immuable, avec validation lors de la création.
    """
    value: str

    EMAIL_REGEX = re.compile(
        r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    )

    def __post_init__(self):
        if not self.value:
            raise ValueError("L'email ne peut pas être vide")
        if not self.EMAIL_REGEX.match(self.value):
            raise ValueError(f"Format d'email invalide: {self.value}")

    @classmethod
    def create(cls, value: str) -> "Email":
        """Factory method avec normalisation."""
        return cls(value=value.lower().strip())

    @property
    def domain(self) -> str:
        """Retourne le domaine de l'email."""
        return self.value.split("@")[1]

    def __str__(self) -> str:
        return self.value
