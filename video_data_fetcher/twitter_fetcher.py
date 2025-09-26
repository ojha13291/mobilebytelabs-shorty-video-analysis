"""
Twitter/X Video Fetcher Module

This module provides functionality to fetch video metadata from Twitter/X.
"""

import re
import json
from typing import Optional, Dict
from .base_fetcher import BaseVideoFetcher, VideoMetadata


class TwitterFetcher(BaseVideoFetcher):
    """Fetcher for Twitter/X video metadata."""
    
    def __init__(self, timeout: int = 30):
        super().__init__(timeout)
    
    def can_fetch(self, url: str) -> bool:
        """Check if this fetcher can handle the given URL."""
        twitter_patterns = [
            r'twitter\.com/[^/]+/status/',
            r'x\.com/[^/]+/status/',
            r'mobile\.twitter\.com/[^/]+/status/',
            r'm\.twitter\.com/[^/]+/status/'
        ]
        return any(re.search(pattern, url) for pattern in twitter_patterns)
    
    def fetch_metadata(self, url: str) -> VideoMetadata:
        """
        Fetch Twitter/X video metadata.
        
        Args:
            url (str): The Twitter/X video URL
            
        Returns:
            VideoMetadata: The fetched metadata
        """
        try:
            response = self.make_request(url)
            if not response:
                return VideoMetadata(platform="twitter", url=url)
            
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
            print(f"Error fetching Twitter/X metadata: {e}")
            return VideoMetadata(platform="twitter", url=url)
    
    def _extract_from_json_ld(self, soup, url: str) -> VideoMetadata:
        """Extract metadata from JSON-LD structured data."""
        json_ld = self.extract_json_ld(soup)
        if not json_ld:
            return VideoMetadata(platform="twitter", url=url)
        
        # Twitter/X typically uses Article or SocialMediaPosting schema
        if json_ld.get('@type') in ['Article', 'SocialMediaPosting', 'VideoObject']:
            return VideoMetadata(
                platform="twitter",
                title=json_ld.get('headline', json_ld.get('name', '')),
                description=json_ld.get('description', ''),
                thumbnail_url=json_ld.get('image', {}).get('url', '') if isinstance(json_ld.get('image'), dict) else json_ld.get('image', ''),
                published_at=json_ld.get('datePublished'),
                url=url
            )
        
        return VideoMetadata(platform="twitter", url=url)
    
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
        username_match = re.search(r'(?:twitter|x)\.com/([^/]+)', url)
        username = username_match.group(1) if username_match else ''
        
        return VideoMetadata(
            platform="twitter",
            title=title or f"Tweet by @{username}" if username else "Twitter Post",
            description=description,
            thumbnail_url=thumbnail_url,
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
        username_match = re.search(r'(?:twitter|x)\.com/([^/]+)', url)
        username = username_match.group(1) if username_match else ''
        
        # Try to find description (tweet content)
        description = ""
        
        # Look for common Twitter/X content selectors
        content_selectors = [
            '[data-testid="tweet-text"]',
            '.tweet-text',
            '.tweet-content',
            '.status-content',
            '[data-testid="tweet"]'
        ]
        
        for selector in content_selectors:
            element = soup.select_one(selector)
            if element:
                description = element.get_text(strip=True)
                break
        
        # Try to find image/video thumbnail
        thumbnail_url = ""
        image_selectors = [
            'meta[property="og:image"]',
            'meta[name="twitter:image"]',
            'img[src*="twimg.com"]',
            'img[src*="x.com"]',
            '.media img',
            '[data-testid="tweetPhoto"] img'
        ]
        
        for selector in image_selectors:
            element = soup.select_one(selector)
            if element:
                thumbnail_url = element.get('content', '') or element.get('src', '')
                break
        
        # Try to extract engagement metrics
        views = None
        engagement_elements = soup.find_all(text=re.compile(r'(\d+(?:\.\d+)?[KMB]?) views?', re.I))
        if engagement_elements:
            views_text = engagement_elements[0]
            views_match = re.search(r'(\d+(?:\.\d+)?[KMB]?)', views_text)
            if views_match:
                views = self.format_views(views_match.group(1))
        
        return VideoMetadata(
            platform="twitter",
            title=title or f"Tweet by @{username}" if username else "Twitter Post",
            description=description,
            thumbnail_url=thumbnail_url,
            views=views,
            url=url
        )