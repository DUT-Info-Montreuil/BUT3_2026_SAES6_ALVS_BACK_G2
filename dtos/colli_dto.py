class ColliDTO:
    def __init__(self, colli):
        self.id = colli.id
        self.name = colli.name
        self.theme = colli.theme
        self.description = colli.description
        self.creator_id = colli.creator_id
        self.status = colli.status
        self.created_at = colli.created_at.isoformat()
        self.updated_at = colli.updated_at.isoformat()
     
        
    def to_json(self):
        return {
            'id': self.id,
            'name': self.name,
            'theme': self.theme,
            'description': self.description,
            'creator_id': self.creator_id,
            'status': self.status,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }
        
        
    @staticmethod
    def from_list(collis):
        return [ColliDTO(c).to_json() for c in collis]