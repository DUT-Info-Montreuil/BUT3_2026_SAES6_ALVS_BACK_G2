class ColliDTO:
    def __init__(self, colli):
        self.id = colli.id
        self.name = colli.name
        self.theme = colli.theme
        self.description = colli.description
        self.created_at = colli.created_at.strftime("%d/%m/%Y %H:%M")
        
        
    def to_json(self):
        return {
            'id': self.id,
            'name': self.name,
            'theme': self.theme,
            'description': self.description,
            'created_at': self.created_at
        }
        
        
    @staticmethod
    def from_list(collis):
        return [ColliDTO(c).to_json() for c in collis]