import logging
from models.letter_model import Letter
from repositories.letter_repository import LetterRepository
from dtos.letter_dto import LetterDTO
from shared.socketio import socketio
from services.file_service import FileService

logger = logging.getLogger(__name__)


class LetterService:
    
    def __init__(self):
        self.letter_repository = LetterRepository()
        self.file_service = FileService()
        
        
    def create_letter(self, data, file_info=None):
        file_url, letter_type = file_info if file_info else (None, 'text')
        new_letter = Letter(
            letter_type=letter_type,
            content=data.get('content'),
            file_url=file_url,
            sender_id=data.get('sender_id'),
            colli_id=data.get('colli_id')
        )
        
        saved_letter = self.letter_repository.save(new_letter)
        letter_dto = LetterDTO(saved_letter).to_json()
        
        socketio.emit('new_letter', letter_dto, room=data.get('colli_id'))
        
        return letter_dto
    
    
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
        
        if letter.file_url:
            try:
                self.file_service.delete_file(letter.file_url)
            except Exception as e:
                logger.warning(f'Could not delete physical file {letter.file_url}: {e}')
        
        self.letter_repository.delete(letter)
        return True