from models.colli_member_model import ColliMember
from repositories.colli_member_repository import ColliMemberRepository
from dtos.colli_member_dto import ColliMemberDTO


class ColliMemberService:
    def __init__(self):
        self.colli_member_repository = ColliMemberRepository()
        
        
    def add_member_to_colli(self, data):
        new_member = ColliMember(
            user_id=data.get('user_id'),
            colli_id=data.get('colli_id'),
            role=data.get('role', 'member')
        )
        
        saved_member = self.colli_member_repository.save(new_member)
        return ColliMemberDTO(saved_member).to_json()
    
    
    def get_members_by_colli_id(self, colli_id):
        members = self.colli_member_repository.get_members_by_colli_id(colli_id)
        return ColliMemberDTO.from_list(members)
    
    
    def get_by_user_and_colli(self, user_id, colli_id):
        member = self.colli_member_repository.get_by_user_and_colli(user_id, colli_id)
        if not member:
            return None
        return ColliMemberDTO(member).to_json()
    
    
    def remove_member_from_colli(self, colli_member_id):
        member = self.colli_member_repository.get_colli_member_by_id(colli_member_id)
        if not member:
            return False
        
        self.colli_member_repository.delete(member)
        return True
    
    
    def update_member_role(self, colli_member_id, new_role):
        member = self.colli_member_repository.get_colli_member_by_id(colli_member_id)
        if not member:
            return None
        
        member.role = new_role
        updated_member = self.colli_member_repository.save(member)
        return ColliMemberDTO(updated_member).to_json()