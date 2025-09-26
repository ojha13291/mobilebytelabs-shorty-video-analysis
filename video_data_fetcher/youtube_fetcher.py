"""
YouTube Video Fetcher Module

This module provides functionality to fetch video metadata from YouTube.
"""

import re
import json
from typing import Optional, Dict, Any
from urllib.parse import parse_qs, urlparse
from .base_fetcher import BaseVideoFetcher, VideoMetadata


class YouTubeFetcher(BaseVideoFetcher):
    """Fetcher for YouTube video metadata."""
    
    def __init__(self, timeout: int = 30):
        super().__init__(timeout)
        self.api_key = None  # Optional: Add YouTube Data API v3 key for better results
    
    def can_fetch(self, url: str) -> bool:
        """Check if this fetcher can handle the given URL."""
        youtube_patterns = [
            r'youtube\.com/watch\?v=',
            r'youtube\.com/shorts/',
            r'youtu\.be/',
            r'm\.youtube\.com/watch\?v='
        ]
        return any(re.search(pattern, url) for pattern in youtube_patterns)
    
    def fetch_metadata(self, url: str) -> VideoMetadata:
        """
        Fetch YouTube video metadata.
        
        Args:
            url (str): The YouTube video URL
            
        Returns:
            VideoMetadata: The fetched metadata
        """
        try:
            # First try to use YouTube Data API if available
            if self.api_key:
                return self._fetch_with_api(url)
            else:
                # Fallback to web scraping
                return self._fetch_with_scraping(url)
        except Exception as e:
            print(f"Error fetching YouTube metadata: {e}")
            return VideoMetadata(platform="youtube", url=url)
    
    def _extract_video_id(self, url: str) -> Optional[str]:
        """Extract video ID from YouTube URL."""
        patterns = [
            r'youtube\.com/watch\?v=([a-zA-Z0-9_-]{11})',
            r'youtube\.com/shorts/([a-zA-Z0-9_-]{11})',
            r'youtu\.be/([a-zA-Z0-9_-]{11})',
            r'm\.youtube\.com/watch\?v=([a-zA-Z0-9_-]{11})'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        
        return None
    
    def _fetch_with_api(self, url: str) -> VideoMetadata:
        """Fetch metadata using YouTube Data API v3."""
        video_id = self._extract_video_id(url)
        if not video_id:
            return VideoMetadata(platform="youtube", url=url)
        
        api_url = f"https://www.googleapis.com/youtube/v3/videos"
        params = {
            'part': 'snippet,statistics,contentDetails',
            'id': video_id,
            'key': self.api_key
        }
        
        response = self.make_request(api_url, params=params)
        if not response:
            return VideoMetadata(platform="youtube", url=url)
        
        data = response.json()
        if not data.get('items'):
            return VideoMetadata(platform="youtube", url=url)
        
        video_data = data['items'][0]
        snippet = video_data.get('snippet', {})
        statistics = video_data.get('statistics', {})
        content_details = video_data.get('contentDetails', {})
        
        return VideoMetadata(
            platform="youtube",
            title=snippet.get('title', ''),
            description=snippet.get('description', ''),
            thumbnail_url=self._get_best_thumbnail(snippet.get('thumbnails', {})),
            duration=self.format_duration(content_details.get('duration', '')),
            views=self.format_views(statistics.get('viewCount')),
            published_at=snippet.get('publishedAt'),
            url=url
        )
    
    def _fetch_with_scraping(self, url: str) -> VideoMetadata:
        """Fetch metadata by scraping the YouTube page."""
        response = self.make_request(url)
        if not response:
            return VideoMetadata(platform="youtube", url=url)
        
        soup = self.parse_html(response.text)
        
        # Try to extract data from various sources
        metadata = self._extract_from_json_ld(soup, url)
        if metadata.is_valid():
            return metadata
        
        # Fallback to meta tags
        return self._extract_from_meta_tags(soup, url)
    
    def _extract_from_json_ld(self, soup, url: str) -> VideoMetadata:
        """Extract metadata from JSON-LD structured data."""
        json_ld = self.extract_json_ld(soup)
        if not json_ld:
            return VideoMetadata(platform="youtube", url=url)
        
        # YouTube typically uses VideoObject schema
        if json_ld.get('@type') == 'VideoObject':
            return VideoMetadata(
                platform="youtube",
                title=json_ld.get('name', ''),
                description=json_ld.get('description', ''),
                thumbnail_url=json_ld.get('thumbnailUrl', ''),
                duration=self.format_duration(json_ld.get('duration')),
                views=self.format_views(str(json_ld.get('interactionCount', ''))),
                published_at=json_ld.get('uploadDate'),
                url=url
            )
        
        return VideoMetadata(platform="youtube", url=url)
    
    def _extract_from_meta_tags(self, soup, url: str) -> VideoMetadata:
        """Extract metadata from HTML meta tags."""
        def get_meta_content(property_name):
            # Try different property names
            for prop in [property_name, f'og:{property_name}', f'twitter:{property_name}']:
                meta = soup.find('meta', {'property': prop}) or soup.find('meta', {'name': prop})
                if meta:
                    return meta.get('content', '')
            return ''
        
        title = get_meta_content('title')
        if not title:
            title_tag = soup.find('title')
            if title_tag:
                title = title_tag.text
        
        description = get_meta_content('description')
        thumbnail_url = get_meta_content('image')
        
        # Try to extract view count from page
        views = None
        view_elements = soup.find_all(string=re.compile(r'(\d+(?:\.\d+)?[KMB]?) views?', re.I))
        if view_elements:
            views_text = view_elements[0]
            views_match = re.search(r'(\d+(?:\.\d+)?[KMB]?)', views_text)
            if views_match:
                views = self.format_views(views_match.group(1))
        
        return VideoMetadata(
            platform="youtube",
            title=title or '',
            description=description,
            thumbnail_url=thumbnail_url,
            views=views,
            url=url
        )
    
    def _get_best_thumbnail(self, thumbnails: Dict) -> str:
        """Get the best quality thumbnail URL."""
        quality_order = ['maxres', 'standard', 'high', 'medium', 'default']
        
        for quality in quality_order:
            if quality in thumbnails:
                return thumbnails[quality].get('url', '')
        
        return ''