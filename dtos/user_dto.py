class UserDTO:
    def __init__(self, user):
        self.id = user.id
        self.username = user.username
        self.email = user.email
        self.created_at = user.created_at.isoformat()
        
        
    def to_json(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'created_at': self.created_at
        }
        
        
    @staticmethod
    def from_list(users):
        return [UserDTO(u).to_json() for u in users]