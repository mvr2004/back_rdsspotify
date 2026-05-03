import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Settings:
    # Spotify Credentials
    SPOTIFY_CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
    SPOTIFY_CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")
    SPOTIFY_REDIRECT_URI = os.getenv("SPOTIFY_REDIRECT_URI")
    
    # App Configuration
    DEBUG = os.getenv("DEBUG", "False").lower() == "true"
    PORT = int(os.getenv("PORT", 8000))
    FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:3000")
    CORS_ORIGINS = [
        origin.strip()
        for origin in os.getenv("CORS_ORIGINS", FRONTEND_URL).split(",")
        if origin.strip()
    ]
    
    # JWT Secret Key
    SECRET_KEY = os.getenv("SECRET_KEY")

    def __init__(self):
        if not self.SECRET_KEY:
            if self.DEBUG:
                self.SECRET_KEY = "dev-only-secret-key-change-before-production"
            else:
                raise RuntimeError("SECRET_KEY must be configured when DEBUG is false")

# Create settings instance
settings = Settings()
