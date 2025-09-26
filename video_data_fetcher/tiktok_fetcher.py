"""
TikTok Video Fetcher Module

This module provides functionality to fetch video metadata from TikTok.
"""

import re
import json
from typing import Optional, Dict
from .base_fetcher import BaseVideoFetcher, VideoMetadata


class TikTokFetcher(BaseVideoFetcher):
    """Fetcher for TikTok video metadata."""
    
    def __init__(self, timeout: int = 30):
        super().__init__(timeout)
    
    def can_fetch(self, url: str) -> bool:
        """Check if this fetcher can handle the given URL."""
        tiktok_patterns = [
            r'tiktok\.com/@',
            r'tiktok\.com/video/',
            r'm\.tiktok\.com/v/',
            r'vm\.tiktok\.com/',
            r'tiktok\.com/t/'
        ]
        return any(re.search(pattern, url) for pattern in tiktok_patterns)
    
    def fetch_metadata(self, url: str) -> VideoMetadata:
        """
        Fetch TikTok video metadata.
        
        Args:
            url (str): The TikTok video URL
            
        Returns:
            VideoMetadata: The fetched metadata
        """
        try:
            response = self.make_request(url)
            if not response:
                return VideoMetadata(platform="tiktok", url=url)
            
            soup = self.parse_html(response.text)
            
            # Try multiple extraction methods
            metadata = self._extract_from_json_ld(soup, url)
            if metadata.is_valid():
                return metadata
            
            metadata = self._extract_from_meta_tags(soup, url)
            if metadata.is_valid():
                return metadata
            
            # Final fallback
            return self._extract_from_page_content(soup, url)
            
        except Exception as e:
            print(f"Error fetching TikTok metadata: {e}")
            return VideoMetadata(platform="tiktok", url=url)
    
    def _extract_from_json_ld(self, soup, url: str) -> VideoMetadata:
        """Extract metadata from JSON-LD structured data."""
        json_ld = self.extract_json_ld(soup)
        if not json_ld:
            return VideoMetadata(platform="tiktok", url=url)
        
        # TikTok typically uses VideoObject schema
        if json_ld.get('@type') == 'VideoObject':
            return VideoMetadata(
                platform="tiktok",
                title=json_ld.get('name', ''),
                description=json_ld.get('description', ''),
                thumbnail_url=json_ld.get('thumbnailUrl', ''),
                duration=self.format_duration(json_ld.get('duration')),
                views=self.format_views(str(json_ld.get('interactionCount', ''))),
                published_at=json_ld.get('uploadDate'),
                url=url
            )
        
        return VideoMetadata(platform="tiktok", url=url)
    
    def _extract_from_meta_tags(self, soup, url: str) -> VideoMetadata:
        """Extract metadata from HTML meta tags."""
        def get_meta_content(property_name):
            # Try different property names
            for prop in [property_name, f'og:{property_name}', f'twitter:{property_name}']:
                meta = soup.find('meta', {'property': prop}) or soup.find('meta', {'name': prop})
                if meta:
                    return meta.get('content', '')
            return ''
        
        title = get_meta_content('title') or soup.find('title')
        if hasattr(title, 'text'):
            title = title.text
        
        description = get_meta_content('description')
        thumbnail_url = get_meta_content('image')
        
        # Extract username from URL if possible
        username_match = re.search(r'tiktok\.com/@([^/]+)', url)
        username = username_match.group(1) if username_match else ''
        
        # Try to extract view count from meta tags
        views = None
        view_meta = get_meta_content('video:views') or get_meta_content('interactionCount')
        if view_meta:
            views = self.format_views(view_meta)
        
        return VideoMetadata(
            platform="tiktok",
            title=title or f"TikTok by @{username}" if username else "TikTok Video",
            description=description,
            thumbnail_url=thumbnail_url,
            views=views,
            url=url
        )
    
    def _extract_from_page_content(self, soup, url: str) -> VideoMetadata:
        """Extract metadata from page content as fallback."""
        # Try to find title from various elements
        title = ""
        
        # Look for h1, h2 tags
        h1 = soup.find('h1')
        if h1:
            title = h1.get_text(strip=True)
        else:
            h2 = soup.find('h2')
            if h2:
                title = h2.get_text(strip=True)
        
        # Extract username from URL
        username_match = re.search(r'tiktok\.com/@([^/]+)', url)
        username = username_match.group(1) if username_match else ''
        
        # Try to find description
        description = ""
        
        # Look for common TikTok content selectors
        content_selectors = [
            '[data-e2e="video-desc"]',
            '.video-description',
            '.caption',
            '.description',
            '[data-testid="video-description"]'
        ]
        
        for selector in content_selectors:
            element = soup.select_one(selector)
            if element:
                description = element.get_text(strip=True)
                break
        
        # Try to find image
        thumbnail_url = ""
        image_selectors = [
            'meta[property="og:image"]',
            'meta[name="twitter:image"]',
            'img[src*="tiktok.com"]',
            '.video-poster img',
            '[data-e2e="video-poster"] img'
        ]
        
        for selector in image_selectors:
            element = soup.select_one(selector)
            if element:
                thumbnail_url = element.get('content', '') or element.get('src', '')
                break
        
        # Try to extract view count from text
        views = None
        view_elements = soup.find_all(text=re.compile(r'(\d+(?:\.\d+)?[KMB]?) views?', re.I))
        if view_elements:
            views_text = view_elements[0]
            views_match = re.search(r'(\d+(?:\.\d+)?[KMB]?)', views_text)
            if views_match:
                views = self.format_views(views_match.group(1))
        
        return VideoMetadata(
            platform="tiktok",
            title=title or f"TikTok by @{username}" if username else "TikTok Video",
            description=description,
            thumbnail_url=thumbnail_url,
            views=views,
            url=url
        )