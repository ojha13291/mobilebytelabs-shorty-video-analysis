"""
Instagram scraper implementation
"""

import time
import random
from typing import Dict, List, Any, Optional
from datetime import datetime
from scrapers.base_scraper import BaseScraper


class InstagramScraper(BaseScraper):
    """
    Instagram scraper for reels and user profiles
    """
    
    def __init__(self, rate_limit_delay: float = 2.0):
        """
        Initialize Instagram scraper
        
        Args:
            rate_limit_delay: Delay between requests to avoid rate limiting
        """
        super().__init__("instagram", rate_limit_delay)
        
    def scrape_reels(self, target: str, max_reels: int = 10) -> List[Dict[str, Any]]:
        """
        Scrape Instagram reels/posts
        
        Args:
            target: Target to scrape (username, hashtag, or URL)
            max_reels: Maximum number of reels to scrape
            
        Returns:
            List of scraped reel data
        """
        if not self.validate_target(target):
            return []
        
        # Apply rate limiting
        self.rate_limit()
        
        # Mock implementation for demonstration
        # In a real implementation, this would use Instagram's API or web scraping
        reels_data = []
        
        for i in range(min(max_reels, 5)):  # Limit to 5 for demo
            reel_data = {
                'id': f'instagram_reel_{i+1}',
                'platform': 'instagram',
                'url': f'https://www.instagram.com/reel/ABC123DEF{i}/',
                'username': target if not target.startswith('#') else 'sample_user',
                'caption': f'Sample Instagram reel caption {i+1} #trending #viral #instagram',
                'likes': random.randint(1000, 50000),
                'comments': random.randint(50, 2000),
                'shares': random.randint(10, 500),
                'timestamp': datetime.now().isoformat(),
                'hashtags': ['trending', 'viral', 'instagram', 'reels'],
                'mentions': [],
                'video_url': f'https://example.com/video_{i+1}.mp4',
                'thumbnail_url': f'https://example.com/thumbnail_{i+1}.jpg',
                'duration': random.randint(15, 60),
                'is_video': True
            }
            reels_data.append(reel_data)
            
            # Small delay between mock data generation
            time.sleep(0.1)
        
        return reels_data
    
    def scrape_user_profile(self, username: str) -> Optional[Dict[str, Any]]:
        """
        Scrape Instagram user profile
        
        Args:
            username: Instagram username to scrape
            
        Returns:
            User profile data or None if not found
        """
        if not self.validate_target(username):
            return None
        
        # Apply rate limiting
        self.rate_limit()
        
        # Mock implementation for demonstration
        return {
            'username': username,
            'full_name': f'{username.title()} User',
            'biography': f'Instagram user {username} - Sample biography',
            'followers': random.randint(1000, 100000),
            'following': random.randint(100, 5000),
            'posts': random.randint(50, 1000),
            'is_private': False,
            'is_verified': random.choice([True, False]),
            'profile_pic_url': f'https://example.com/profile_{username}.jpg',
            'external_url': f'https://example.com/{username}',
            'timestamp': datetime.now().isoformat()
        }
    
    def validate_target(self, target: str) -> bool:
        """
        Validate Instagram target format
        
        Args:
            target: Target to validate
            
        Returns:
            True if valid, False otherwise
        """
        if not super().validate_target(target):
            return False
        
        target = target.strip()
        
        # Allow usernames, hashtags, and URLs
        if target.startswith('#'):
            # Hashtag validation
            hashtag = target[1:]
            return len(hashtag) > 0 and hashtag.replace('_', '').isalnum()
        elif target.startswith('@'):
            # Username validation
            username = target[1:]
            return len(username) > 0 and username.replace('_', '').replace('.', '').isalnum()
        elif target.startswith('http'):
            # URL validation
            return 'instagram.com' in target.lower()
        else:
            # Plain username validation
            return len(target) > 0 and target.replace('_', '').replace('.', '').isalnum()
        
        return True