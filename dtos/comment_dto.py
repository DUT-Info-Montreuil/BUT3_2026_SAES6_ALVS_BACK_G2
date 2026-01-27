class CommentDTO:
    def __init__(self, comment):
        self.id = comment.id
        self.content = comment.content
        self.letter_id = comment.letter_id
        self.sender_id = comment.sender_id
        self.created_at = comment.created_at.isoformat()
        self.updated_at = comment.updated_at.isoformat()
        
        
    def to_json(self):
        return {
            'id': self.id,
            'content': self.content,
            'letter_id': self.letter_id,
            'sender_id': self.sender_id,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }
        
        
    @staticmethod
    def from_list(comments):
        return [CommentDTO(comment).to_json() for comment in comments]