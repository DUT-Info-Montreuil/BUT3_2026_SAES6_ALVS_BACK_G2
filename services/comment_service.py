from models.comment_model import Comment
from repositories.comment_repository import CommentRepository
from dtos.comment_dto import CommentDTO
from shared.socketio import socketio


class CommentService:
    def __init__(self):
        self.comment_repository = CommentRepository()
        
        
    def add_comment(self, data):
        new_comment = Comment(
            content=data.get('content'),
            letter_id=data.get('letter_id'),
            sender_id=data.get('sender_id')
        )
        
        saved_comment = self.comment_repository.save(new_comment)
        comment_dto = CommentDTO(saved_comment).to_json()
        
        socketio.emit('new_comment', comment_dto, room=f'letter_{data.get('letter_id')}')
        
        return comment_dto
    
    
    def get_comment_by_id(self, comment_id):
        comment = self.comment_repository.get_comment_by_id(comment_id)
        if not comment:
            return None
        return CommentDTO(comment).to_json()
    
    
    def get_comments_by_letter_id(self, letter_id):
        comments = self.comment_repository.get_comments_by_letter_id(letter_id)
        return CommentDTO.from_list(comments)
    
    
    def delete_comment_by_id(self, comment_id):
        comment = self.comment_repository.get_comment_by_id(comment_id)
        if not comment:
            return False
        self.comment_repository.delete(comment)
        return True