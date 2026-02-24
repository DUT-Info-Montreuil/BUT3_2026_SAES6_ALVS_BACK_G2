import pytest
from marshmallow import ValidationError
from uuid import uuid4

from src.infrastructure.web.schemas.colli_schema import (
    CreateColliSchema,
    UpdateColliSchema,
    RejectColliSchema,
    AddMemberSchema,
    ColliListQuerySchema
)


class TestCreateColliSchema:
    """Tests pour le schéma de création de COLLI."""
    
    def test_valid_data(self):
        """Test validation avec données valides."""
        # Arrange
        schema = CreateColliSchema()
        valid_data = {
            'name': 'Test COLLI',
            'theme': 'Test Theme',
            'description': 'Test Description'
        }
        
        # Act
        result = schema.load(valid_data)
        
        # Assert
        assert result['name'] == 'Test COLLI'
        assert result['theme'] == 'Test Theme'
        assert result['description'] == 'Test Description'
    
    def test_required_fields_only(self):
        """Test validation avec champs requis uniquement."""
        # Arrange
        schema = CreateColliSchema()
        minimal_data = {
            'name': 'Test COLLI',
            'theme': 'Test Theme'
        }
        
        # Act
        result = schema.load(minimal_data)
        
        # Assert
        assert result['name'] == 'Test COLLI'
        assert result['theme'] == 'Test Theme'
        assert 'description' not in result
    
    def test_missing_required_name(self):
        """Test validation avec nom manquant."""
        # Arrange
        schema = CreateColliSchema()
        invalid_data = {
            'theme': 'Test Theme'
        }
        
        # Act & Assert
        with pytest.raises(ValidationError) as exc_info:
            schema.load(invalid_data)
        
        assert 'name' in exc_info.value.messages
    
    def test_missing_required_theme(self):
        """Test validation avec thème manquant."""
        # Arrange
        schema = CreateColliSchema()
        invalid_data = {
            'name': 'Test COLLI'
        }
        
        # Act & Assert
        with pytest.raises(ValidationError) as exc_info:
            schema.load(invalid_data)
        
        assert 'theme' in exc_info.value.messages
    
    def test_empty_name(self):
        """Test validation avec nom vide."""
        # Arrange
        schema = CreateColliSchema()
        invalid_data = {
            'name': '',
            'theme': 'Test Theme'
        }
        
        # Act & Assert
        with pytest.raises(ValidationError) as exc_info:
            schema.load(invalid_data)
        
        assert 'name' in exc_info.value.messages
    
    def test_empty_theme(self):
        """Test validation avec thème vide."""
        # Arrange
        schema = CreateColliSchema()
        invalid_data = {
            'name': 'Test COLLI',
            'theme': ''
        }
        
        # Act & Assert
        with pytest.raises(ValidationError) as exc_info:
            schema.load(invalid_data)
        
        assert 'theme' in exc_info.value.messages
    
    def test_name_too_long(self):
        """Test validation avec nom trop long."""
        # Arrange
        schema = CreateColliSchema()
        invalid_data = {
            'name': 'x' * 256,  # Nom trop long
            'theme': 'Test Theme'
        }
        
        # Act & Assert
        with pytest.raises(ValidationError) as exc_info:
            schema.load(invalid_data)
        
        assert 'name' in exc_info.value.messages


class TestColliListQuerySchema:
    """Tests pour le schéma de requête de liste des COLLIs."""
    
    def test_valid_pagination_params(self):
        """Test validation avec paramètres de pagination valides."""
        # Arrange
        schema = ColliListQuerySchema()
        valid_data = {
            'page': '2',
            'per_page': '10'
        }
        
        # Act
        result = schema.load(valid_data)
        
        # Assert
        assert result['page'] == 2
        assert result['per_page'] == 10
    
    def test_default_values(self):
        """Test valeurs par défaut."""
        # Arrange
        schema = ColliListQuerySchema()
        empty_data = {}
        
        # Act
        result = schema.load(empty_data)
        
        # Assert
        assert result.get('page', 1) == 1
        assert result.get('per_page', 20) == 20
    
    def test_invalid_page_number(self):
        """Test validation avec numéro de page invalide."""
        # Arrange
        schema = ColliListQuerySchema()
        invalid_data = {
            'page': '0'  # Page doit être >= 1
        }
        
        # Act & Assert
        with pytest.raises(ValidationError) as exc_info:
            schema.load(invalid_data)
        
        assert 'page' in exc_info.value.messages
    
    def test_invalid_per_page_number(self):
        """Test validation avec per_page invalide."""
        # Arrange
        schema = ColliListQuerySchema()
        invalid_data = {
            'per_page': '0'  # per_page doit être >= 1
        }
        
        # Act & Assert
        with pytest.raises(ValidationError) as exc_info:
            schema.load(invalid_data)
        
        assert 'per_page' in exc_info.value.messages
    
    def test_per_page_too_high(self):
        """Test validation avec per_page trop élevé."""
        # Arrange
        schema = ColliListQuerySchema()
        invalid_data = {
            'per_page': '101'  # Maximum 100
        }
        
        # Act & Assert
        with pytest.raises(ValidationError) as exc_info:
            schema.load(invalid_data)
        
        assert 'per_page' in exc_info.value.messages
    
    def test_non_numeric_values(self):
        """Test validation avec valeurs non numériques."""
        # Arrange
        schema = ColliListQuerySchema()
        invalid_data = {
            'page': 'invalid',
            'per_page': 'invalid'
        }
        
        # Act & Assert
        with pytest.raises(ValidationError) as exc_info:
            schema.load(invalid_data)
        
        assert 'page' in exc_info.value.messages
        assert 'per_page' in exc_info.value.messages


class TestUpdateColliSchema:
    """Tests pour le schéma de mise à jour de COLLI."""
    
    def test_partial_update(self):
        """Test mise à jour partielle."""
        # Arrange
        schema = UpdateColliSchema()
        partial_data = {
            'name': 'Updated Name'
        }
        
        # Act
        result = schema.load(partial_data)
        
        # Assert
        assert result['name'] == 'Updated Name'
        assert 'theme' not in result
        assert 'description' not in result
    
    def test_full_update(self):
        """Test mise à jour complète."""
        # Arrange
        schema = UpdateColliSchema()
        full_data = {
            'name': 'Updated Name',
            'theme': 'Updated Theme',
            'description': 'Updated Description'
        }
        
        # Act
        result = schema.load(full_data)
        
        # Assert
        assert result['name'] == 'Updated Name'
        assert result['theme'] == 'Updated Theme'
        assert result['description'] == 'Updated Description'
    
    def test_empty_update(self):
        """Test mise à jour vide (devrait être valide)."""
        # Arrange
        schema = UpdateColliSchema()
        empty_data = {}
        
        # Act
        result = schema.load(empty_data)
        
        # Assert
        assert result == {}


class TestAddMemberSchema:
    """Tests pour le schéma d'ajout de membre."""
    
    def test_valid_user_id(self):
        """Test avec ID utilisateur valide."""
        # Arrange
        schema = AddMemberSchema()
        user_id = uuid4()
        valid_data = {
            'user_id': str(user_id)
        }
        
        # Act
        result = schema.load(valid_data)
        
        # Assert
        assert str(result['user_id']) == str(user_id)
    
    def test_missing_user_id(self):
        """Test avec ID utilisateur manquant."""
        # Arrange
        schema = AddMemberSchema()
        invalid_data = {}
        
        # Act & Assert
        with pytest.raises(ValidationError) as exc_info:
            schema.load(invalid_data)
        
        assert 'user_id' in exc_info.value.messages
    
    def test_invalid_uuid_format(self):
        """Test avec format UUID invalide."""
        # Arrange
        schema = AddMemberSchema()
        invalid_data = {
            'user_id': 'invalid-uuid'
        }
        
        # Act & Assert
        with pytest.raises(ValidationError) as exc_info:
            schema.load(invalid_data)
        
        assert 'user_id' in exc_info.value.messages