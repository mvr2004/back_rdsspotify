import secrets
from typing import Dict, Optional
import requests
from urllib.parse import urlencode
from app.core.config import settings

class AuthService:
    # Store state for CSRF protection
    _state_store = {}
    
    @staticmethod
    def verify_credentials():
        """Verify Spotify credentials are working"""
        print(f"Client ID: {settings.SPOTIFY_CLIENT_ID[:10]}...")
        print(f"Client Secret: {settings.SPOTIFY_CLIENT_SECRET[:10]}...")
        print(f"Redirect URI: {settings.SPOTIFY_REDIRECT_URI}")

    @staticmethod
    def get_authorization_url() -> str:
        """Generate Spotify OAuth authorization URL"""
        
        # Generate random state for CSRF protection
        state = secrets.token_urlsafe(16)
        AuthService._state_store[state] = True
        
        # Scopes define what access we're requesting
        scopes = [
            "user-read-private",
            "user-read-email",
            "user-top-read",
            "user-read-recently-played",
            "playlist-modify-public",
            "playlist-modify-private"
        ]
        
        params = {
            "client_id": settings.SPOTIFY_CLIENT_ID,
            "response_type": "code",
            "redirect_uri": settings.SPOTIFY_REDIRECT_URI,
            "scope": " ".join(scopes),
            "state": state,
            "show_dialog": "true"  # Force login dialog every time
        }
        
        return f"https://accounts.spotify.com/authorize?{urlencode(params)}"

    @staticmethod
    def exchange_code_for_token(code: str) -> Dict:
        """Exchange authorization code for access token"""
        
        import base64
        
        # Create Basic Auth header correctly
        client_id = settings.SPOTIFY_CLIENT_ID
        client_secret = settings.SPOTIFY_CLIENT_SECRET
        
        if not client_id or not client_secret:
            raise Exception("Spotify credentials not configured")
        
        # Encode to base64 correctly
        auth_str = f"{client_id}:{client_secret}"
        auth_bytes = auth_str.encode('utf-8')
        auth_b64 = base64.b64encode(auth_bytes).decode('utf-8')
        
        response = requests.post(
            "https://accounts.spotify.com/api/token",
            headers={
                "Authorization": f"Basic {auth_b64}",
                "Content-Type": "application/x-www-form-urlencoded"
            },
            data={
                "grant_type": "authorization_code",
                "code": code,
                "redirect_uri": settings.SPOTIFY_REDIRECT_URI
            }
        )
        
        print(f"Token exchange status: {response.status_code}")
        print(f"Token exchange response: {response.text}")
        
        if response.status_code != 200:
            error_msg = f"Token exchange failed: {response.text}"
            print(error_msg)
            raise Exception(error_msg)
        
        return response.json()
   

    @staticmethod
    def refresh_access_token(refresh_token: str) -> Dict:
        """Refresh expired access token"""
        
        auth_str = f"{settings.Spotify_CLIENT_ID}:{settings.SPOTIFY_CLIENT_SECRET}"
        auth_b64 = requests.utils.quote(auth_str, safe='')
        
        response = requests.post(
            "https://accounts.spotify.com/api/token",
            headers={
                "Authorization": f"Basic {auth_b64}",
                "Content-Type": "application/x-www-form-urlencoded"
            },
            data={
                "grant_type": "refresh_token",
                "refresh_token": refresh_token
            }
        )
        
        if response.status_code != 200:
            raise Exception(f"Token refresh failed: {response.text}")
        
        return response.json()

    @staticmethod
    def validate_state(state: str) -> bool:
        """Validate OAuth state to prevent CSRF attacks"""
        return state in AuthService._state_store

    @staticmethod
    def get_user_profile(access_token: str) -> Dict:
        """Get current user's profile from Spotify"""
        
        response = requests.get(
            "https://api.spotify.com/v1/me",
            headers={"Authorization": f"Bearer {access_token}"}
        )
        
        if response.status_code != 200:
            raise Exception(f"Failed to get user profile: {response.text}")
        
        return response.json()
