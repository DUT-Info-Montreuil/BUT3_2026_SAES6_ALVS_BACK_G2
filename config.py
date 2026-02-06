import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    
    db_path = os.getenv('DATABASE_URL', 'app.db')
    
    SQLALCHEMY_DATABASE_URI = f'sqlite:///{os.path.join(BASE_DIR, db_path)}'
    
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    
    # JWT Configuration
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'jwt-dev-secret-key-32-chars-min!!')
    JWT_TOKEN_LOCATION = ['headers']
    JWT_HEADER_NAME = 'Authorization'
    JWT_HEADER_TYPE = 'Bearer'
    
    UPLOAD_FOLDER = os.path.join(BASE_DIR, 'static/uploads')
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'mp3', 'wav', 'm4a', 'pdf'}
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024


class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False