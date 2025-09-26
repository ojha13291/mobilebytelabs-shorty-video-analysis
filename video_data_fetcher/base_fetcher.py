"""
Base Video Fetcher Module

This module provides the base class for all platform-specific video fetchers.
"""

from abc import ABC, abstractmethod
from typing import Dict, Optional, Any
from datetime import datetime
import requests
from bs4 import BeautifulSoup


class VideoMetadata:
    """Data model for video metadata."""
    
    def __init__(self, platform: str, title: str = "", description: str = "", 
                 thumbnail_url: str = "", duration: Optional[int] = None,
                 views: Optional[int] = None, published_at: Optional[str] = None,
                 url: str = ""):
        self.platform = platform
        self.title = title
        self.description = description
        self.thumbnail_url = thumbnail_url
        self.duration = duration  # in seconds
        self.views = views
        self.published_at = published_at  # ISO timestamp
        self.url = url
        self.fetched_at = datetime.now().isoformat()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert metadata to dictionary."""
        return {
            "platform": self.platform,
            "title": self.title,
            "description": self.description,
            "thumbnail_url": self.thumbnail_url,
            "duration": self.duration,
            "views": self.views,
            "published_at": self.published_at,
            "url": self.url,
            "fetched_at": self.fetched_at
        }
    
    def is_valid(self) -> bool:
        """Check if metadata has minimum required fields."""
        return bool(self.title and self.platform)


class BaseVideoFetcher(ABC):
    """Base class for all video fetchers."""
    
    def __init__(self, timeout: int = 30):
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
    
    @abstractmethod
    def fetch_metadata(self, url: str) -> VideoMetadata:
        """
        Fetch video metadata from the given URL.
        
        Args:
            url (str): The video URL
            
        Returns:
            VideoMetadata: The fetched metadata
        """
        pass
    
    @abstractmethod
    def can_fetch(self, url: str) -> bool:
        """
        Check if this fetcher can handle the given URL.
        
        Args:
            url (str): The URL to check
            
        Returns:
            bool: True if this fetcher can handle the URL
        """
        pass
    
    def make_request(self, url: str, **kwargs) -> Optional[requests.Response]:
        """
        Make an HTTP request with error handling.
        
        Args:
            url (str): The URL to request
            **kwargs: Additional arguments for the request
            
        Returns:
            Optional[requests.Response]: The response or None if failed
        """
        try:
            response = self.session.get(url, timeout=self.timeout, **kwargs)
            response.raise_for_status()
            return response
        except requests.RequestException as e:
            print(f"Request failed for {url}: {e}")
            return None
    
    def parse_html(self, html: str) -> BeautifulSoup:
        """
        Parse HTML content using BeautifulSoup.
        
        Args:
            html (str): The HTML content
            
        Returns:
            BeautifulSoup: The parsed HTML
        """
        return BeautifulSoup(html, 'html.parser')
    
    def extract_json_ld(self, soup: BeautifulSoup) -> Optional[Dict]:
        """
        Extract JSON-LD structured data from HTML.
        
        Args:
            soup (BeautifulSoup): The parsed HTML
            
        Returns:
            Optional[Dict]: The JSON-LD data or None
        """
        json_ld_scripts = soup.find_all('script', type='application/ld+json')
        if json_ld_scripts:
            import json
            try:
                return json.loads(json_ld_scripts[0].string)
            except (json.JSONDecodeError, AttributeError):
                pass
        return None
    
    def format_duration(self, duration_str: str) -> Optional[int]:
        """
        Convert duration string to seconds.
        
        Args:
            duration_str (str): Duration string (e.g., "PT4M13S", "4:13")
            
        Returns:
            Optional[int]: Duration in seconds or None
        """
        if not duration_str:
            return None
        
        # Handle ISO 8601 duration format (PT4M13S)
        if duration_str.startswith('PT'):
            import re
            match = re.match(r'PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?', duration_str)
            if match:
                hours = int(match.group(1) or 0)
                minutes = int(match.group(2) or 0)
                seconds = int(match.group(3) or 0)
                return hours * 3600 + minutes * 60 + seconds
        
        # Handle MM:SS format
        if ':' in duration_str:
            parts = duration_str.split(':')
            if len(parts) == 2:
                minutes, seconds = map(int, parts)
                return minutes * 60 + seconds
            elif len(parts) == 3:
                hours, minutes, seconds = map(int, parts)
                return hours * 3600 + minutes * 60 + seconds
        
        # Handle numeric seconds
        try:
            return int(duration_str)
        except ValueError:
            pass
        
        return None
    
    def format_views(self, views_str: str) -> Optional[int]:
        """
        Convert view count string to integer.
        
        Args:
            views_str (str): View count string (e.g., "1.2M", "1,234")
            
        Returns:
            Optional[int]: View count as integer or None
        """
        if not views_str:
            return None
        
        # Remove common suffixes and convert
        views_str = views_str.lower().strip()
        
        # Handle K, M, B suffixes
        if views_str.endswith('k'):
            return int(float(views_str[:-1]) * 1000)
        elif views_str.endswith('m'):
            return int(float(views_str[:-1]) * 1000000)
        elif views_str.endswith('b'):
            return int(float(views_str[:-1]) * 1000000000)
        
        # Remove commas and convert
        try:
            return int(views_str.replace(',', ''))
        except ValueError:
            pass
        
        return None