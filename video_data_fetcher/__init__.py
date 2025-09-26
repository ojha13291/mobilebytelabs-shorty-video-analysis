"""
Video Data Fetcher Module

This module provides functionality to fetch video metadata from various social media platforms
including YouTube, Instagram, TikTok, Twitter/X, and more.
"""

from typing import Dict

from .fetcher import VideoDataFetcher
from .base_fetcher import BaseVideoFetcher
from .youtube_fetcher import YouTubeFetcher
from .instagram_fetcher import InstagramFetcher
from .tiktok_fetcher import TikTokFetcher
from .twitter_fetcher import TwitterFetcher

# Convenience function for easy usage
def fetch_video_metadata(url: str) -> Dict:
    """
    Fetch video metadata from a URL.
    
    Args:
        url: The video URL to fetch metadata from
        
    Returns:
        dict: Video metadata or error information
    """
    fetcher = VideoDataFetcher()
    return fetcher.fetch_metadata(url)

__all__ = [
    'VideoDataFetcher',
    'BaseVideoFetcher',
    'YouTubeFetcher',
    'InstagramFetcher',
    'TikTokFetcher',
    'TwitterFetcher',
    'fetch_video_metadata'
]