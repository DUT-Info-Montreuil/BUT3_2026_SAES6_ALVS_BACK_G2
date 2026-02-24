# src/application/use_cases/colli/create_colli.py
"""Use Case: Créer un COLLI."""

from dataclasses import dataclass
from uuid import UUID

from src.domain.collaboration.entities.colli import Colli
from src.domain.collaboration.repositories.colli_repository import IColliRepository
from src.application.dtos.colli_dto import CreateColliDTO, ColliResponseDTO


@dataclass
class CreateColliCommand:
    """Commande pour créer un COLLI."""
    name: str
    theme: str
    creator_id: UUID
    description: str = None


class CreateColliUseCase:
    """
    Use Case: Créer un nouveau COLLI.
    
    Règles métier:
    - Tout utilisateur authentifié peut créer un COLLI
    - Le COLLI est créé en statut PENDING (nécessite approbation admin)
    - Le créateur sera automatiquement ajouté comme MANAGER à l'approbation
    """
    
    def __init__(self, colli_repository: IColliRepository):
        self._colli_repo = colli_repository
    
    def execute(self, command: CreateColliCommand) -> ColliResponseDTO:
        """
        Exécute la création du COLLI.
        
        Args:
            command: Commande contenant les données du COLLI.
            
        Returns:
            ColliResponseDTO: Le COLLI créé.
        """
        # Créer l'entité via la factory method
        colli = Colli.create(
            name=command.name,
            theme=command.theme,
            creator_id=command.creator_id,
            description=command.description
        )
        
        # Persister
        saved_colli = self._colli_repo.save(colli)
        
        # Retourner le DTO
        return ColliResponseDTO.from_entity(saved_colli)
