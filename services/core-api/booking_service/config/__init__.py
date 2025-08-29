import os
from pathlib import Path

class Config:
    GOOGLE_APPLICATION_CREDENTIALS = os.getenv('GOOGLE_APPLICATION_CREDENTIALS', '')
    
    @classmethod
    def validate_credentials(cls):
        if not cls.GOOGLE_APPLICATION_CREDENTIALS:
            raise ValueError('GOOGLE_APPLICATION_CREDENTIALS environment variable not set')
        if not Path(cls.GOOGLE_APPLICATION_CREDENTIALS).exists():
            raise FileNotFoundError(f'Credentials file not found at {cls.GOOGLE_APPLICATION_CREDENTIALS}')
