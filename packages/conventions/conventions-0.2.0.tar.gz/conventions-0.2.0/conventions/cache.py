"""
Simple caching mechanism for conference data.
"""
import os
import json
import time
from typing import Dict, Any, Optional
from conventions.config import CACHE_DIR, CACHE_MAX_AGE_HOURS


class ConferenceCache:
    """Simple cache for conference data to avoid redundant fetching."""
    
    def __init__(self, cache_dir: Optional[str] = None):
        """
        Initialize the cache with the given directory.
        
        Args:
            cache_dir: Directory to store cache files. Defaults to value from config
        """
        self.cache_dir = cache_dir or CACHE_DIR
        self._ensure_cache_dir()
    
    def _ensure_cache_dir(self):
        """Ensure the cache directory exists."""
        os.makedirs(self.cache_dir, exist_ok=True)
    
    def _get_cache_path(self, conference_id: str) -> str:
        """Get the path to the cache file for the given conference."""
        return os.path.join(self.cache_dir, f"{conference_id}.json")
    
    def get(self, conference_id: str, max_age_hours: Optional[float] = None) -> Optional[Dict[str, Any]]:
        """
        Get conference data from cache if available and not too old.
        
        Args:
            conference_id: The identifier of the conference
            max_age_hours: Maximum age of the cache in hours (defaults to config value)
            
        Returns:
            The cached conference data or None if not available or too old
        """
        if max_age_hours is None:
            max_age_hours = CACHE_MAX_AGE_HOURS
            
        cache_path = self._get_cache_path(conference_id)
        
        if not os.path.exists(cache_path):
            return None
        
        # Check if cache is too old
        cache_age = time.time() - os.path.getmtime(cache_path)
        if cache_age > max_age_hours * 3600:
            return None
        
        try:
            with open(cache_path, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            # Cache is corrupt or unreadable
            return None
    
    def set(self, conference_id: str, data: Dict[str, Any]) -> None:
        """
        Save conference data to cache.
        
        Args:
            conference_id: The identifier of the conference
            data: The conference data to cache
        """
        cache_path = self._get_cache_path(conference_id)
        
        try:
            with open(cache_path, 'w') as f:
                json.dump(data, f, indent=2)
        except IOError:
            # Failed to write cache, just continue without caching
            pass
    
    def clear(self, conference_id: Optional[str] = None) -> None:
        """
        Clear the cache for a specific conference or all conferences.
        
        Args:
            conference_id: The identifier of the conference to clear, or None for all
        """
        if conference_id:
            cache_path = self._get_cache_path(conference_id)
            if os.path.exists(cache_path):
                os.remove(cache_path)
        else:
            # Clear all cache files
            for filename in os.listdir(self.cache_dir):
                if filename.endswith('.json'):
                    os.remove(os.path.join(self.cache_dir, filename))


# Singleton instance
cache = ConferenceCache() 