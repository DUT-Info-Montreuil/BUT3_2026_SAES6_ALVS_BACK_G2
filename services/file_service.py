import os
import uuid
from werkzeug.utils import secure_filename
from flask import current_app

class FileService:
    def __init__(self):
        pass
    
    
    def _get_upload_folder(self):
        return current_app.config['UPLOAD_FOLDER']
    
    
    def _allowed_file(self, filename):
        allowed_extensions = current_app.config['ALLOWED_EXTENSIONS']
        return '.' in filename and \
            filename.rsplit('.', 1)[1].lower() in allowed_extensions
            
            
    def _ensure_folder_exists(self, subfolder):
        path = os.path.join(self._get_upload_folder(), subfolder)
        if not os.path.exists(path):
            os.makedirs(path, exist_ok=True)
        return path
    
    
    def _get_type_from_extension(self, filename):
        ext = filename.rsplit('.', 1)[1].lower()
        if ext in {'png', 'jpg', 'jpeg', 'gif'}:
            return 'image'
        elif ext in {'mp3', 'wav', 'm4a'}:
            return 'audio'
        elif ext == 'pdf':
            return 'pdf'
        return 'file'
    
    def upload_file(self, file, subfolder='letters'):
        if not file or file.filename == '':
            return None
        
        if not self._allowed_file(file.filename):
            raise ValueError('File type not allowed')
        
        
        letter_type = self._get_type_from_extension(file.filename)
        target_dir = self._ensure_folder_exists(subfolder)
        
        original_name = secure_filename(file.filename)
        unique_name = f'{uuid.uuid4().hex}_{original_name}'
        
        file_path = os.path.join(target_dir, unique_name)
        file.save(file_path)
        
        return os.path.join(subfolder, unique_name), letter_type
    
    
    def delete_file(self, file_url):
        if not file_url:
            return False
        
        full_path = os.path.join(self._get_upload_folder(), file_url)
        if not os.path.exists(full_path):
            return False
        
        os.remove(full_path)
        return True