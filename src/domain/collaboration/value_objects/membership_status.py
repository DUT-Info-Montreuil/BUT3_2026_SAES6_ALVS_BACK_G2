# src/domain/collaboration/value_objects/membership_status.py
"""Value Object pour le statut d'adhésion d'un membre à un COLLI."""

from enum import Enum


class MembershipStatus(Enum):
    """
    Statuts possibles d'une demande d'adhésion à un COLLI.

    Workflow: PENDING → ACCEPTED | REJECTED
    """
    PENDING = "pending"       # Demande en attente d'approbation
    ACCEPTED = "accepted"     # Membre accepté
    REJECTED = "rejected"     # Demande rejetée
