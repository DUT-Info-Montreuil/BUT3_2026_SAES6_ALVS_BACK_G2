from models.letter_model import Letter
from repositories.letter_repository import LetterRepository
from dtos.letter_dto import LetterDTO
from shared.socketio import socketio


class LetterService:
    
    def __init__(self):
        self.letter_repository = LetterRepository()
        
        
    def create_letter(self, data):
        new_letter = Letter(
            letter_type=data.get('letter_type'),
            content=data.get('content'),
            file_url=data.get('file_url'),
            sender_id=data.get('sender_id'),
            colli_id=data.get('colli_id')
        )
        
        saved_letter = self.letter_repository.save(new_letter)
        letter_dict = LetterDTO(saved_letter).to_json()
        
        socketio.emit('new_letter', letter_dict, room=data.get('colli_id'))
        
        return letter_dict
    
    
    def get_letter_by_id(self, letter_id):
        letter = self.letter_repository.get_letter_by_id(letter_id)
        if not letter:
            return None
        return LetterDTO(letter).to_json()
    
    
    def get_letters_by_colli_id(self, colli_id):
        letters = self.letter_repository.get_letters_by_colli_id(colli_id)
        return LetterDTO.from_list(letters)
    
    
    def delete_letter_by_id(self, letter_id):
        letter = self.letter_repository.get_letter_by_id(letter_id)
        if not letter:
            return False
        
        self.letter_repository.delete(letter)
        return True