import requests
import base64
from app.core.config import settings

class SpotifyService:
    @staticmethod
    def get_client_token():
        
        # Check if credentials exist
        if not settings.SPOTIFY_CLIENT_ID or not settings.SPOTIFY_CLIENT_SECRET:
            raise ValueError("Spotify credentials not configured")
        
        # Prepare basic auth (same as your JavaScript code)
        auth_str = f"{settings.SPOTIFY_CLIENT_ID}:{settings.SPOTIFY_CLIENT_SECRET}"
        auth_b64 = base64.b64encode(auth_str.encode()).decode()
        
        # Make request to Spotify
        response = requests.post(
            "https://accounts.spotify.com/api/token",
            headers={
                "Authorization": f"Basic {auth_b64}",
                "Content-Type": "application/x-www-form-urlencoded"
            },
            data={"grant_type": "client_credentials"}
        )
        
        # Check for errors
        if response.status_code != 200:
            raise Exception(f"Spotify API error: {response.text}")
        
        # Return the token
        data = response.json()
        return data.get("access_token")