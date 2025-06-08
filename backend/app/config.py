import os

class Config:
    """Configuration settings for the application."""
    
    # Database configuration
    DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./test.db")
    
    # API keys and secrets
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
    
    # OCR settings
    OCR_ENGINE = os.getenv("OCR_ENGINE", "tesseract")
    
    # Upload settings
    MAX_UPLOAD_SIZE = int(os.getenv("MAX_UPLOAD_SIZE", 10 * 1024 * 1024))  # 10 MB
    
    # Other configurations
    DEBUG = os.getenv("DEBUG", "False") == "True"  # Default to False
    ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg', 'txt'}
    
    @staticmethod
    def is_allowed_file(filename):
        """Check if the uploaded file has an allowed extension."""
        return '.' in filename and filename.rsplit('.', 1)[1].lower() in Config.ALLOWED_EXTENSIONS