"""
Instagram Video Fetcher Module

This module provides functionality to fetch video metadata from Instagram.
"""

import re
import json
from typing import Optional, Dict
from .base_fetcher import BaseVideoFetcher, VideoMetadata


class InstagramFetcher(BaseVideoFetcher):
    """Fetcher for Instagram video metadata."""
    
    def __init__(self, timeout: int = 30):
        super().__init__(timeout)
    
    def can_fetch(self, url: str) -> bool:
        """Check if this fetcher can handle the given URL."""
        instagram_patterns = [
            r'instagram\.com/p/',
            r'instagram\.com/reel/',
            r'instagram\.com/tv/',
            r'm\.instagram\.com/p/',
            r'm\.instagram\.com/reel/',
            r'instagr\.am/p/',
            r'instagr\.am/reel/'
        ]
        return any(re.search(pattern, url) for pattern in instagram_patterns)
    
    def fetch_metadata(self, url: str) -> VideoMetadata:
        """
        Fetch Instagram video metadata.
        
        Args:
            url (str): The Instagram video URL
            
        Returns:
            VideoMetadata: The fetched metadata
        """
        try:
            response = self.make_request(url)
            if not response:
                return VideoMetadata(platform="instagram", url=url)
            
            soup = self.parse_html(response.text)
            
            # Try multiple extraction methods
            metadata = self._extract_from_json_ld(soup, url)
            if metadata.is_valid():
                return metadata
            
            metadata = self._extract_from_meta_tags(soup, url)
            if metadata.is_valid():
                return metadata
            
            # Final fallback
            result = self._extract_from_page_content(soup, url)
            return result
            
        except Exception as e:
            print(f"Error fetching Instagram metadata: {e}")
            return VideoMetadata(platform="instagram", url=url)
    
    def _extract_from_json_ld(self, soup, url: str) -> VideoMetadata:
        """Extract metadata from JSON-LD structured data."""
        json_ld = self.extract_json_ld(soup)
        if not json_ld:
            return VideoMetadata(platform="instagram", url=url)
        
        # Instagram typically uses VideoObject schema
        if json_ld.get('@type') == 'VideoObject':
            return VideoMetadata(
                platform="instagram",
                title=json_ld.get('name', ''),
                description=json_ld.get('description', ''),
                thumbnail_url=json_ld.get('thumbnailUrl', ''),
                duration=self.format_duration(json_ld.get('duration')),
                views=self.format_views(str(json_ld.get('interactionCount', ''))),
                published_at=json_ld.get('uploadDate'),
                url=url
            )
        
        return VideoMetadata(platform="instagram", url=url)
    
    def _extract_from_meta_tags(self, soup, url: str) -> VideoMetadata:
        """Extract metadata from HTML meta tags."""
        def get_meta_content(property_name):
            # Try different property names
            for prop in [property_name, f'og:{property_name}', f'twitter:{property_name}']:
                meta = soup.find('meta', {'property': prop}) or soup.find('meta', {'name': prop})
                if meta:
                    return meta.get('content', '')
            return ''
        
        # First try to get og:title directly
        og_title = soup.find('meta', {'property': 'og:title'})
        if og_title:
            title = og_title.get('content', '')
        else:
            # Fallback to other title sources
            title = get_meta_content('title')
            
            if not title:
                title_tag = soup.find('title')
                if title_tag:
                    title = title_tag.text
        
        description = get_meta_content('description')
        thumbnail_url = get_meta_content('image')
        
        # Extract username from URL if possible
        username_match = re.search(r'instagram\.com/([^/]+)', url)
        username = username_match.group(1) if username_match else ''
        
        # Try to extract view count from meta tags
        views = None
        view_meta = get_meta_content('video:views') or get_meta_content('interactionCount')
        if view_meta:
            views = self.format_views(view_meta)
        
        return VideoMetadata(
            platform="instagram",
            title=title or f"Instagram Post by @{username}" if username else "Instagram Post",
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
        username_match = re.search(r'instagram\.com/([^/]+)', url)
        username = username_match.group(1) if username_match else ''
        
        # Try to find description
        description = ""
        
        # Look for common Instagram content selectors
        content_selectors = [
            '[data-testid="post-caption"]',
            '.Caption',
            '.caption',
            '.post-caption',
            '[data-testid="caption"]'
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
            'img[src*="cdninstagram.com"]',
            'img[src*="instagram.com"]'
        ]
        
        for selector in image_selectors:
            element = soup.select_one(selector)
            if element:
                thumbnail_url = element.get('content', '') or element.get('src', '')
                break
        
        return VideoMetadata(
            platform="instagram",
            title=title or f"Instagram Post by @{username}" if username else "Instagram Post",
            description=description,
            thumbnail_url=thumbnail_url,
            url=url
        )