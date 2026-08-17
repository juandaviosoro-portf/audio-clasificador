import os
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = os.path.abspath(os.path.dirname(__file__))


class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'clave-desarrollo-no-usar-en-produccion')
    SQLALCHEMY_DATABASE_URI = f"sqlite:///{os.path.join(BASE_DIR, 'database', 'app.db')}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')
    DATABASE_FOLDER = os.path.join(BASE_DIR, 'database')
    MAX_CONTENT_LENGTH = 50 * 1024 * 1024  # 50 MB max

    ALLOWED_EXTENSIONS = {'mp3', 'wav', 'ogg', 'm4a', 'webm'}

    GEMINI_API_KEY = os.getenv('GEMINI_API_KEY', '')
    GEMINI_MODEL = os.getenv('GEMINI_MODEL', 'gemini-3.6-flash')

    WHISPER_MODEL = os.getenv('WHISPER_MODEL', 'base')

    CATEGORIAS = [
        'VENTAS',
        'SOPORTE',
        'FACTURACIÓN',
        'GARANTÍA',
        'INFORMACIÓN',
        'RECLAMO',
        'OTRO'
    ]

    PRIORIDADES = ['ALTA', 'MEDIA', 'BAJA']
