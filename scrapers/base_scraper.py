"""
Base scraper class for social media platforms
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional
import time
import random
from datetime import datetime


class BaseScraper(ABC):
    """
    Abstract base class for social media scrapers
    """
    
    def __init__(self, platform_name: str, rate_limit_delay: float = 1.0):
        """
        Initialize the base scraper
        
        Args:
            platform_name: Name of the platform
            rate_limit_delay: Delay between requests to avoid rate limiting
        """
        self.platform_name = platform_name
        self.rate_limit_delay = rate_limit_delay
        self.request_count = 0
        self.last_request_time = None
    
    @abstractmethod
    def scrape_reels(self, target: str, max_reels: int = 10) -> List[Dict[str, Any]]:
        """
        Scrape reels/posts from the platform
        
        Args:
            target: Target to scrape (username, hashtag, etc.)
            max_reels: Maximum number of reels to scrape
            
        Returns:
            List of scraped reel data
        """
        pass
    
    @abstractmethod
    def scrape_user_profile(self, username: str) -> Optional[Dict[str, Any]]:
        """
        Scrape user profile information
        
        Args:
            username: Username to scrape
            
        Returns:
            User profile data or None if not found
        """
        pass
    
    def rate_limit(self):
        """Apply rate limiting between requests"""
        if self.last_request_time:
            elapsed = time.time() - self.last_request_time
            if elapsed < self.rate_limit_delay:
                sleep_time = self.rate_limit_delay - elapsed + random.uniform(0.1, 0.5)
                time.sleep(sleep_time)
        
        self.last_request_time = time.time()
        self.request_count += 1
    
    def normalize_url(self, url: str) -> str:
        """
        Normalize URL format
        
        Args:
            url: URL to normalize
            
        Returns:
            Normalized URL
        """
        if not url.startswith('http'):
            url = f"https://{url}"
        
        return url.rstrip('/')
    
    def parse_count(self, count_text: str) -> int:
        """
        Parse count text (e.g., "1.2K", "5M") to integer
        
        Args:
            count_text: Text representation of count
            
        Returns:
            Integer count value
        """
        if not count_text:
            return 0
        
        count_text = count_text.strip().lower()
        
        # Handle numeric-only strings
        if count_text.replace(',', '').replace('.', '').isdigit():
            return int(float(count_text.replace(',', '')))
        
        # Handle K, M, B suffixes
        multipliers = {
            'k': 1000,
            'm': 1000000,
            'b': 1000000000
        }
        
        for suffix, multiplier in multipliers.items():
            if count_text.endswith(suffix):
                number_part = count_text[:-1].replace(',', '')
                try:
                    return int(float(number_part) * multiplier)
                except ValueError:
                    return 0
        
        # Try to extract number from text
        import re
        numbers = re.findall(r'\d+(?:\.\d+)?', count_text)
        if numbers:
            try:
                return int(float(numbers[0]))
            except ValueError:
                return 0
        
        return 0
    
    def extract_hashtags(self, text: str) -> List[str]:
        """
        Extract hashtags from text
        
        Args:
            text: Text to extract hashtags from
            
        Returns:
            List of hashtags
        """
        import re
        hashtags = re.findall(r'#\w+', text)
        return [tag.lower() for tag in hashtags]
    
    def extract_mentions(self, text: str) -> List[str]:
        """
        Extract mentions from text
        
        Args:
            text: Text to extract mentions from
            
        Returns:
            List of mentions
        """
        import re
        mentions = re.findall(r'@\w+', text)
        return [mention.lower() for mention in mentions]
    
    def clean_text(self, text: str) -> str:
        """
        Clean text by removing extra whitespace and special characters
        
        Args:
            text: Text to clean
            
        Returns:
            Cleaned text
        """
        if not text:
            return ""
        
        # Remove extra whitespace
        text = ' '.join(text.split())
        
        # Remove special characters that might cause issues
        text = text.replace('\u200b', '')  # Zero-width space
        text = text.replace('\u200c', '')  # Zero-width non-joiner
        text = text.replace('\u200d', '')  # Zero-width joiner
        
        return text.strip()
    
    def validate_target(self, target: str) -> bool:
        """
        Validate the target format
        
        Args:
            target: Target to validate
            
        Returns:
            True if valid, False otherwise
        """
        if not target or not target.strip():
            return False
        
        # Basic validation - can be overridden in subclasses
        target = target.strip()
        
        # Check for invalid characters
        invalid_chars = ['<', '>', '"', "'", '&', '%', '$', '#', '@', '!', '*']
        if any(char in target for char in invalid_chars):
            return False
        
        return True
    
    def format_timestamp(self, timestamp: Any) -> Optional[str]:
        """
        Format timestamp to ISO format
        
        Args:
            timestamp: Timestamp to format
            
        Returns:
            Formatted timestamp string
        """
        if not timestamp:
            return None
        
        try:
            if isinstance(timestamp, str):
                # Try to parse string timestamp
                from dateutil import parser
                dt = parser.parse(timestamp)
                return dt.isoformat()
            elif isinstance(timestamp, (int, float)):
                # Assume Unix timestamp
                dt = datetime.fromtimestamp(timestamp)
                return dt.isoformat()
            elif isinstance(timestamp, datetime):
                return timestamp.isoformat()
            else:
                return str(timestamp)
        except Exception:
            return str(timestamp)
    
    def get_scraper_info(self) -> Dict[str, Any]:
        """
        Get scraper information
        
        Returns:
            Dictionary with scraper information
        """
        return {
            'platform': self.platform_name,
            'rate_limit_delay': self.rate_limit_delay,
            'request_count': self.request_count,
            'last_request_time': self.last_request_time,
            'status': 'active' if self.request_count > 0 else 'inactive'
        }