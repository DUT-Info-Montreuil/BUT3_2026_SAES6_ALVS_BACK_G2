from models.colli_model import Colli
from repositories.colli_repository import ColliRepository
from dtos.colli_dto import ColliDTO
from services.colli_member_service import ColliMemberService


class ColliService:
    
    def __init__(self):
        self.colli_repository = ColliRepository()
        self.colli_member_service = ColliMemberService()
    
    
    def get_all_collis(self):
        collis = self.colli_repository.get_all_collis()
        return ColliDTO.from_list(collis)
    
    
    def create_colli(self, data):
        new_colli = Colli(
            name=data.get('name'),
            theme=data.get('theme'),
            description=data.get('description'),
            creator_id=data.get('creator_id'),
            status=data.get('status')
        )
        
        saved_colli = self.colli_repository.save(new_colli)
        
        return ColliDTO(saved_colli).to_json()
    
    
    def get_colli_by_id(self, colli_id):
        colli = self.colli_repository.get_colli_by_id(colli_id)
        if not colli:
            return None
        return ColliDTO(colli).to_json()
    
    
    def update_colli_by_id(self, colli_id, data):
        colli = self.colli_repository.get_colli_by_id(colli_id)
        if not colli:
            return None

        if 'name' in data: colli.name = data.get('name')
        if 'theme' in data: colli.theme = data.get('theme')
        if 'description' in data: colli.description = data.get('description')
        if 'creator_id' in data: colli.creator_id = data.get('creator_id')
        if 'status' in data: colli.status = data.get('status')
        
        return ColliDTO(self.colli_repository.save(colli)).to_json()
    
    
    def delete_colli_by_id(self, colli_id):
        colli = self.colli_repository.get_colli_by_id(colli_id)
        if not colli:
            return False
        
        self.colli_repository.delete(colli)
        return True 
    
    
    def approve_colli(self, colli_id):
        colli = self.colli_repository.get_colli_by_id(colli_id)
        if not colli:
            return None
        
        colli.status = 'active'
        self.colli_repository.save(colli)
        
        colli_manager_data = {
            'user_id': colli.creator_id,
            'colli_id': colli.id,
            'role': 'manager'
        }
        self.colli_member_service.add_member_to_colli(colli_manager_data)
        
        return ColliDTO(colli).to_json()
    
    
    def reject_colli(self, colli_id):
        colli = self.colli_repository.get_colli_by_id(colli_id)
        if not colli:
            return None
        
        colli.status = 'rejected'
        self.colli_repository.save(colli)
        
        return ColliDTO(colli).to_json()
    