"""
Main Video Data Fetcher Module

This module provides the main interface for fetching video metadata from various platforms.
"""

from typing import Optional, Dict, Any, List
try:
    from ..resolver.platform_resolver import PlatformResolver
except ImportError:
    # Handle case when running as standalone module
    import sys
    import os
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from resolver.platform_resolver import PlatformResolver
from .base_fetcher import VideoMetadata
from .youtube_fetcher import YouTubeFetcher
from .instagram_fetcher import InstagramFetcher
from .tiktok_fetcher import TikTokFetcher
from .twitter_fetcher import TwitterFetcher


class VideoDataFetcher:
    """
    Main class for fetching video metadata from various social media platforms.
    
    This class integrates with the platform resolver to automatically detect
    the platform and use the appropriate fetcher.
    """
    
    def __init__(self, timeout: int = 30):
        self.platform_resolver = PlatformResolver()
        self.timeout = timeout
        
        # Initialize platform-specific fetchers
        self.fetchers = {
            'youtube': YouTubeFetcher(timeout),
            'instagram': InstagramFetcher(timeout),
            'tiktok': TikTokFetcher(timeout),
            'twitter': TwitterFetcher(timeout),
        }
    
    def fetch_metadata(self, url: str) -> Dict[str, Any]:
        """
        Fetch video metadata from the given URL.
        
        Args:
            url (str): The video URL
            
        Returns:
            Dict[str, Any]: The video metadata or error information
            
        Examples:
            >>> fetcher = VideoDataFetcher()
            >>> metadata = fetcher.fetch_metadata('https://www.youtube.com/watch?v=dQw4w9WgXcQ')
            >>> print(metadata['title'])
            'Rick Astley - Never Gonna Give You Up (Official Video)'
        """
        try:
            # Detect platform
            platform_info = self.platform_resolver.get_platform_info(url)
            platform = platform_info['platform']
            
            if platform == 'unknown':
                return {
                    'error': 'Unable to detect platform from URL',
                    'url': url,
                    'success': False
                }
            
            # Get appropriate fetcher
            fetcher = self.fetchers.get(platform)
            if not fetcher:
                return {
                    'error': f'No fetcher available for platform: {platform}',
                    'platform': platform,
                    'url': url,
                    'success': False
                }
            
            # Check if fetcher can handle this specific URL
            if not fetcher.can_fetch(url):
                return {
                    'error': f'Fetcher cannot handle this specific URL type for {platform}',
                    'platform': platform,
                    'url': url,
                    'success': False
                }
            
            # Fetch metadata
            metadata = fetcher.fetch_metadata(url)
            
            # Convert to dictionary and add success flag
            result = metadata.to_dict()
            result['success'] = metadata.is_valid()
            result['platform'] = platform
            
            if not metadata.is_valid():
                result['warning'] = 'Some metadata fields may be missing or incomplete'
            
            return result
            
        except Exception as e:
            return {
                'error': f'Failed to fetch metadata: {str(e)}',
                'url': url,
                'success': False
            }
    
    def fetch_batch_metadata(self, urls: List[str]) -> List[Dict[str, Any]]:
        """
        Fetch metadata for multiple URLs.
        
        Args:
            urls (List[str]): List of video URLs
            
        Returns:
            List[Dict[str, Any]]: List of metadata results
        """
        results = []
        for url in urls:
            try:
                result = self.fetch_metadata(url)
                results.append(result)
            except Exception as e:
                results.append({
                    'error': f'Failed to fetch metadata: {str(e)}',
                    'url': url,
                    'success': False
                })
        
        return results
    
    def get_supported_platforms(self) -> List[str]:
        """
        Get list of supported platforms.
        
        Returns:
            List[str]: List of platform names
        """
        return list(self.fetchers.keys())
    
    def add_fetcher(self, platform: str, fetcher) -> None:
        """
        Add a new platform fetcher.
        
        Args:
            platform (str): Platform name
            fetcher: The fetcher instance
        """
        self.fetchers[platform] = fetcher
    
    def remove_fetcher(self, platform: str) -> None:
        """
        Remove a platform fetcher.
        
        Args:
            platform (str): Platform name to remove
        """
        if platform in self.fetchers:
            del self.fetchers[platform]


# Convenience functions
def fetch_video_metadata(url: str, timeout: int = 30) -> Dict[str, Any]:
    """
    Convenience function to fetch video metadata.
    
    Args:
        url (str): The video URL
        timeout (int): Request timeout in seconds
        
    Returns:
        Dict[str, Any]: The video metadata
    """
    fetcher = VideoDataFetcher(timeout)
    return fetcher.fetch_metadata(url)


def fetch_batch_video_metadata(urls: List[str], timeout: int = 30) -> List[Dict[str, Any]]:
    """
    Convenience function to fetch metadata for multiple videos.
    
    Args:
        urls (List[str]): List of video URLs
        timeout (int): Request timeout in seconds
        
    Returns:
        List[Dict[str, Any]]: List of metadata results
    """
    fetcher = VideoDataFetcher(timeout)
    return fetcher.fetch_batch_metadata(urls)