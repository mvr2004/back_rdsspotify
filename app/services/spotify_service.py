import requests
import base64
import time
from typing import Dict, List, Optional
from app.core.config import settings

class SpotifyService:
    # Client credentials token cache.
    _token_cache = None
    _token_expiry = 0
    _TOKEN_DURATION = 3500
    _API_BASE_URL = "https://api.spotify.com/v1"

    @staticmethod
    def _spotify_get(path: str, access_token: str, params: Optional[Dict] = None) -> Dict:
        """Make an authenticated Spotify API request for a logged-in user."""
        response = requests.get(
            f"{SpotifyService._API_BASE_URL}{path}",
            headers={"Authorization": f"Bearer {access_token}"},
            params=params or {}
        )

        if response.status_code != 200:
            message = "Unknown error"
            try:
                message = response.json().get("error", {}).get("message", message)
            except Exception:
                pass
            raise Exception(f"Spotify API error: {response.status_code} - {message}")

        return response.json()

    @staticmethod
    def _format_track(track: Dict) -> Dict:
        artists = [artist["name"] for artist in track.get("artists", [])]
        album_images = track.get("album", {}).get("images", [])

        return {
            "id": track.get("id"),
            "name": track.get("name"),
            "artists": artists,
            "artist_names": ", ".join(artists),
            "album": track.get("album", {}).get("name"),
            "album_id": track.get("album", {}).get("id"),
            "duration_ms": track.get("duration_ms"),
            "popularity": track.get("popularity"),
            "track_number": track.get("track_number"),
            "image_url": album_images[0]["url"] if album_images else None,
            "preview_url": track.get("preview_url"),
            "external_url": track.get("external_urls", {}).get("spotify"),
            "uri": track.get("uri")
        }

    @staticmethod
    def _format_artist(artist: Dict) -> Dict:
        images = artist.get("images", [])

        return {
            "id": artist.get("id"),
            "name": artist.get("name"),
            "genres": artist.get("genres", []),
            "popularity": artist.get("popularity"),
            "followers": artist.get("followers", {}).get("total", 0),
            "image_url": images[0]["url"] if images else None,
            "external_url": artist.get("external_urls", {}).get("spotify"),
            "uri": artist.get("uri")
        }

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
        return [SpotifyService._format_track(track) for track in tracks]
    
    @staticmethod
    def clear_token_cache():
        """Clear cached token (for testing or credential changes)"""
        SpotifyService._token_cache = None
        SpotifyService._token_expiry = 0


    @staticmethod
    def search_artists(
        query: str, 
        limit: int = 20,
        offset: int = 0
    ) -> List[Dict]:
        """
        Search for artists with formatted results
        
        Returns:
            List of formatted artist objects
        """
        results = SpotifyService.search(
            query=query,
            search_type="artist",
            limit=limit,
            offset=offset
        )
        
        artists = results.get("artists", {}).get("items", [])
        return [SpotifyService._format_artist(artist) for artist in artists]

    @staticmethod
    def get_user_profile(access_token: str) -> Dict:
        """Get the logged-in user's Spotify profile."""
        profile = SpotifyService._spotify_get("/me", access_token)
        images = profile.get("images", [])

        return {
            "spotify_id": profile.get("id"),
            "display_name": profile.get("display_name") or profile.get("id"),
            "email": profile.get("email", ""),
            "country": profile.get("country", ""),
            "followers": profile.get("followers", {}).get("total", 0),
            "profile_image": images[0]["url"] if images else "",
            "external_url": profile.get("external_urls", {}).get("spotify"),
            "uri": profile.get("uri")
        }

    @staticmethod
    def get_user_top_tracks(access_token: str, time_range: str, limit: int) -> List[Dict]:
        """Get the logged-in user's top tracks."""
        results = SpotifyService._spotify_get(
            "/me/top/tracks",
            access_token,
            {"time_range": time_range, "limit": min(limit, 50)}
        )
        return [SpotifyService._format_track(track) for track in results.get("items", [])]

    @staticmethod
    def get_user_top_artists(access_token: str, time_range: str, limit: int) -> List[Dict]:
        """Get the logged-in user's top artists."""
        results = SpotifyService._spotify_get(
            "/me/top/artists",
            access_token,
            {"time_range": time_range, "limit": min(limit, 50)}
        )
        return [SpotifyService._format_artist(artist) for artist in results.get("items", [])]

    @staticmethod
    def get_recently_played(access_token: str, limit: int) -> List[Dict]:
        """Get the logged-in user's recently played tracks."""
        results = SpotifyService._spotify_get(
            "/me/player/recently-played",
            access_token,
            {"limit": min(limit, 50)}
        )

        recently_played = []
        for item in results.get("items", []):
            recently_played.append({
                "played_at": item.get("played_at"),
                "track": SpotifyService._format_track(item.get("track", {}))
            })

        return recently_played
