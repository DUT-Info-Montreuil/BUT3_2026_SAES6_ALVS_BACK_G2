class LetterDTO:
    def __init__ (self, letter):
        self.id = letter.id
        self.letter_type = letter.letter_type
        self.content = letter.content
        self.file_url = letter.file_url
        self.sender_id = letter.sender_id
        self.colli_id = letter.colli_id
        self.created_at = letter.created_at.isoformat()
        self.updated_at = letter.updated_at.isoformat()
        
    
    def to_json(self):
        return {
            'id': self.id,
            'letter_type': self.letter_type,
            'content': self.content,
            'file_url': self.file_url,
            'sender_id': self.sender_id,
            'colli_id': self.colli_id,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }
    
    
    @staticmethod
    def from_list(letters):
        return [LetterDTO(letter).to_json() for letter in letters]