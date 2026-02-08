# tests/unit/application/test_create_colli_use_case.py
"""Tests unitaires pour le Use Case CreateColli."""

import pytest
from uuid import uuid4

from src.application.use_cases.colli.create_colli import (
    CreateColliUseCase,
    CreateColliCommand
)
from src.infrastructure.persistence.in_memory.colli_repository import InMemoryColliRepository


class TestCreateColliUseCase:
    """Tests pour le use case de création de COLLI."""
    
    @pytest.fixture
    def repository(self):
        """Repository In-Memory pour les tests."""
        return InMemoryColliRepository()
    
    @pytest.fixture
    def use_case(self, repository):
        """Use case avec dépendances injectées."""
        return CreateColliUseCase(colli_repository=repository)
    
    def test_create_colli_successfully(self, use_case, repository):
        """Créer un COLLI avec des données valides."""
        creator_id = uuid4()
        command = CreateColliCommand(
            name="Mon COLLI",
            theme="Poésie française",
            creator_id=creator_id,
            description="Un test"
        )
        
        result = use_case.execute(command)
        
        assert result.name == "Mon COLLI"
        assert result.theme == "Poésie française"
        assert result.status == "pending"
        assert result.creator_id == str(creator_id)
        
        # Vérifier que le COLLI est persisté
        assert repository.count() == 1
    
    def test_create_colli_without_description(self, use_case):
        """Créer un COLLI sans description."""
        command = CreateColliCommand(
            name="COLLI sans desc",
            theme="Roman",
            creator_id=uuid4()
        )
        
        result = use_case.execute(command)
        
        assert result.description is None
    
    def test_create_colli_with_invalid_name_raises_error(self, use_case):
        """Un nom trop court lève une erreur."""
        command = CreateColliCommand(
            name="AB",  # Trop court
            theme="Roman",
            creator_id=uuid4()
        )
        
        with pytest.raises(ValueError, match="au moins 3 caractères"):
            use_case.execute(command)
