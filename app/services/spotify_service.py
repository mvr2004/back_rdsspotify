import requests
import base64
import time
from typing import Dict, List, Optional
from app.core.config import settings

class SpotifyService:
    # Cache para o token
    _token_cache = None
    _token_expiry = 0
    _TOKEN_DURATION = 3500  # Segundos (1 hora menos margem)

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
    def search(
        query: str, 
        search_type: str = "track",
        limit: int = 20,
        offset: int = 0,
        market: Optional[str] = None
    ) -> Dict:
        """
        Search for items on Spotify
        
        Args:
            query: Search query
            search_type: Type of search (track, artist, album, playlist)
            limit: Number of results (1-50)
            offset: Pagination offset
            market: Market code (e.g., "PT", "US")
        
        Returns:
            Dictionary with search results
        """
        token = SpotifyService.get_client_token()
        
        # Prepare parameters
        params = {
            "q": query,
            "type": search_type,
            "limit": min(limit, 50),  # Spotify max is 50
            "offset": offset
        }
        
        if market:
            params["market"] = market
        
        # Make request to Spotify API
        response = requests.get(
            "https://api.spotify.com/v1/search",
            headers={"Authorization": f"Bearer {token}"},
            params=params
        )
        
        # Check for errors
        if response.status_code != 200:
            error_msg = f"Spotify search error: {response.status_code}"
            try:
                error_data = response.json()
                error_msg = f"{error_msg} - {error_data.get('error', {}).get('message', 'Unknown error')}"
            except:
                pass
            raise Exception(error_msg)
        
        return response.json()
    
    @staticmethod
    def search_tracks(
        query: str, 
        limit: int = 20,
        offset: int = 0
    ) -> List[Dict]:
        """
        Search for tracks with formatted results
        
        Returns:
            List of formatted track objects
        """
        results = SpotifyService.search(
            query=query,
            search_type="track",
            limit=limit,
            offset=offset
        )
        
        tracks = results.get("tracks", {}).get("items", [])
        formatted_tracks = []
        
        for track in tracks:
            # Get artists names
            artists = [artist["name"] for artist in track.get("artists", [])]
            
            # Get album image (try different sizes)
            album_images = track.get("album", {}).get("images", [])
            image_url = album_images[0]["url"] if album_images else None
            
            # Get preview URL (30 second preview)
            preview_url = track.get("preview_url")
            
            formatted_track = {
                "id": track.get("id"),
                "name": track.get("name"),
                "artists": artists,
                "artist_names": ", ".join(artists),
                "album": track.get("album", {}).get("name"),
                "album_id": track.get("album", {}).get("id"),
                "duration_ms": track.get("duration_ms"),
                "popularity": track.get("popularity"),
                "track_number": track.get("track_number"),
                "image_url": image_url,
                "preview_url": preview_url,
                "external_url": track.get("external_urls", {}).get("spotify"),
                "uri": track.get("uri")
            }
            formatted_tracks.append(formatted_track)
        
        return formatted_tracks
    
    @staticmethod
    def clear_token_cache():
        """Clear cached token (for testing or credential changes)"""
        SpotifyService._token_cache = None
        SpotifyService._token_expiry = 0
