import requests
import base64
import time
from app.core.config import settings

class SpotifyService:
    # Cache for token
    _token_cache = None
    _token_expiry = 0
    _TOKEN_DURATION = 3500  

    @staticmethod
    def get_client_token():
        """Get Spotify API access token with cache"""
        
        # Check if we have a valid cached token
        current_time = time.time()
        if (SpotifyService._token_cache and 
            SpotifyService._token_expiry > current_time):
            return SpotifyService._token_cache
        
        # Validate credentials
        if not settings.SPOTIFY_CLIENT_ID or not settings.SPOTIFY_CLIENT_SECRET:
            raise ValueError("Spotify credentials not configured")
        
        # Prepare authentication
        auth_str = f"{settings.SPOTIFY_CLIENT_ID}:{settings.SPOTIFY_CLIENT_SECRET}"
        auth_b64 = base64.b64encode(auth_str.encode()).decode()
        
        # Request token from Spotify
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
            error_msg = f"Spotify API error: {response.status_code}"
            try:
                error_data = response.json()
                error_msg = f"{error_msg} - {error_data.get('error_description', 'Unknown error')}"
            except:
                pass
            raise Exception(error_msg)
        
        # Parse response
        data = response.json()
        token = data.get("access_token")
        
        if not token:
            raise Exception("No access token in response")
        
        # Cache the token
        SpotifyService._token_cache = token
        SpotifyService._token_expiry = current_time + SpotifyService._TOKEN_DURATION
        
        return token
    
    @staticmethod
    def clear_token_cache():
        """Clear cached token (for testing or credential changes)"""
        SpotifyService._token_cache = None
        SpotifyService._token_expiry = 0