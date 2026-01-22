class ColliMemberDTO:
    def __init__(self, colli_member):
        self.id = colli_member.id
        self.user_id = colli_member.user_id
        self.colli_id = colli_member.colli_id
        self.role = colli_member.role
        self.joined_at = colli_member.joined_at.isoformat()
        self.updated_at = colli_member.updated_at.isoformat()
        
        
    def to_json(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'colli_id': self.colli_id,
            'role': self.role,
            'joined_at': self.joined_at,
            'updated_at': self.updated_at
        }
        
        
    @staticmethod
    def from_list(colli_members):
        return [ColliMemberDTO(cm).to_json() for cm in colli_members]