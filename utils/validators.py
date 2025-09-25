"""
Validation utilities for the application
"""

import re
from typing import Dict, List, Any, Optional, Union
from urllib.parse import urlparse
import validators


class ValidationError(Exception):
    """Custom validation error"""
    pass


class URLValidator:
    """URL validation utilities"""
    
    @staticmethod
    def is_valid_url(url: str) -> bool:
        """
        Check if URL is valid
        
        Args:
            url: URL to validate
            
        Returns:
            True if valid, False otherwise
        """
        if not url or not isinstance(url, str):
            return False
        
        try:
            result = urlparse(url)
            return all([result.scheme, result.netloc])
        except Exception:
            return False
    
    @staticmethod
    def normalize_url(url: str) -> str:
        """
        Normalize URL format
        
        Args:
            url: URL to normalize
            
        Returns:
            Normalized URL
        """
        if not url:
            return ""
        
        # Add protocol if missing
        if not url.startswith(('http://', 'https://')):
            url = f"https://{url}"
        
        # Remove trailing slash
        return url.rstrip('/')
    
    @staticmethod
    def extract_domain(url: str) -> Optional[str]:
        """
        Extract domain from URL
        
        Args:
            url: URL to extract domain from
            
        Returns:
            Domain or None if invalid
        """
        if not URLValidator.is_valid_url(url):
            return None
        
        try:
            parsed = urlparse(url)
            return parsed.netloc.lower()
        except Exception:
            return None


class SocialMediaValidator:
    """Social media specific validation"""
    
    @staticmethod
    def is_valid_instagram_username(username: str) -> bool:
        """
        Validate Instagram username
        
        Args:
            username: Username to validate
            
        Returns:
            True if valid, False otherwise
        """
        if not username or not isinstance(username, str):
            return False
        
        # Instagram username rules:
        # - 1-30 characters
        # - Only letters, numbers, periods, underscores
        # - Cannot start or end with period
        # - Cannot have consecutive periods
        pattern = r'^[a-zA-Z0-9_]([a-zA-Z0-9_.]{0,28}[a-zA-Z0-9_])?$'
        return bool(re.match(pattern, username))
    
    @staticmethod
    def is_valid_tiktok_username(username: str) -> bool:
        """
        Validate TikTok username
        
        Args:
            username: Username to validate
            
        Returns:
            True if valid, False otherwise
        """
        if not username or not isinstance(username, str):
            return False
        
        # TikTok username rules:
        # - 2-24 characters
        # - Only letters, numbers, periods, underscores
        # - Cannot start with period
        pattern = r'^[a-zA-Z0-9_][a-zA-Z0-9_.]{1,23}$'
        return bool(re.match(pattern, username))
    
    @staticmethod
    def is_valid_twitter_username(username: str) -> bool:
        """
        Validate Twitter/X username
        
        Args:
            username: Username to validate
            
        Returns:
            True if valid, False otherwise
        """
        if not username or not isinstance(username, str):
            return False
        
        # Twitter username rules:
        # - 1-15 characters
        # - Only letters, numbers, underscores
        # - Cannot be all numbers
        pattern = r'^[a-zA-Z0-9_]{1,15}$'
        if not re.match(pattern, username):
            return False
        
        # Check if all numbers
        return not username.isdigit()
    
    @staticmethod
    def is_valid_youtube_channel_url(url: str) -> bool:
        """
        Validate YouTube channel URL
        
        Args:
            url: YouTube channel URL to validate
            
        Returns:
            True if valid, False otherwise
        """
        if not URLValidator.is_valid_url(url):
            return False
        
        youtube_patterns = [
            r'https?://(www\.)?youtube\.com/channel/[a-zA-Z0-9_-]+',
            r'https?://(www\.)?youtube\.com/c/[a-zA-Z0-9_-]+',
            r'https?://(www\.)?youtube\.com/user/[a-zA-Z0-9_-]+',
            r'https?://(www\.)?youtube\.com/@[a-zA-Z0-9_-]+'
        ]
        
        return any(re.match(pattern, url) for pattern in youtube_patterns)


class DataValidator:
    """General data validation utilities"""
    
    @staticmethod
    def validate_email(email: str) -> bool:
        """
        Validate email address
        
        Args:
            email: Email to validate
            
        Returns:
            True if valid, False otherwise
        """
        if not email or not isinstance(email, str):
            return False
        
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))
    
    @staticmethod
    def validate_phone_number(phone: str) -> bool:
        """
        Validate phone number
        
        Args:
            phone: Phone number to validate
            
        Returns:
            True if valid, False otherwise
        """
        if not phone or not isinstance(phone, str):
            return False
        
        # Remove common formatting characters
        cleaned = re.sub(r'[\s\-\(\)\+\.]', '', phone)
        
        # Check if it's a valid phone number (7-15 digits)
        return cleaned.isdigit() and 7 <= len(cleaned) <= 15
    
    @staticmethod
    def validate_hashtag(hashtag: str) -> bool:
        """
        Validate hashtag format
        
        Args:
            hashtag: Hashtag to validate
            
        Returns:
            True if valid, False otherwise
        """
        if not hashtag or not isinstance(hashtag, str):
            return False
        
        pattern = r'^#[a-zA-Z0-9_]{1,100}$'
        return bool(re.match(pattern, hashtag))
    
    @staticmethod
    def validate_text_length(text: str, min_length: int = 0, max_length: Optional[int] = None) -> bool:
        """
        Validate text length
        
        Args:
            text: Text to validate
            min_length: Minimum length required
            max_length: Maximum length allowed
            
        Returns:
            True if valid, False otherwise
        """
        if not isinstance(text, str):
            return False
        
        text_length = len(text.strip())
        
        if text_length < min_length:
            return False
        
        if max_length is not None and text_length > max_length:
            return False
        
        return True
    
    @staticmethod
    def validate_numeric_range(value: Union[int, float], min_value: Optional[Union[int, float]] = None, max_value: Optional[Union[int, float]] = None) -> bool:
        """
        Validate numeric range
        
        Args:
            value: Numeric value to validate
            min_value: Minimum allowed value
            max_value: Maximum allowed value
            
        Returns:
            True if valid, False otherwise
        """
        if not isinstance(value, (int, float)):
            return False
        
        if min_value is not None and value < min_value:
            return False
        
        if max_value is not None and value > max_value:
            return False
        
        return True


class ValidationResult:
    """Validation result container"""
    
    def __init__(self, is_valid: bool = True, errors: Optional[List[str]] = None):
        self.is_valid = is_valid
        self.errors = errors or []
    
    def add_error(self, error: str):
        """Add error message"""
        self.is_valid = False
        self.errors.append(error)
    
    def merge(self, other: 'ValidationResult'):
        """Merge another validation result"""
        if not other.is_valid:
            self.is_valid = False
            self.errors.extend(other.errors)
    
    def __bool__(self):
        return self.is_valid
    
    def __str__(self):
        if self.is_valid:
            return "Valid"
        return f"Invalid: {', '.join(self.errors)}"


def validate_batch_urls(urls: List[str]) -> Dict[str, ValidationResult]:
    """
    Validate a batch of URLs
    
    Args:
        urls: List of URLs to validate
        
    Returns:
        Dictionary mapping URLs to validation results
    """
    results = {}
    
    for url in urls:
        result = ValidationResult()
        
        if not URLValidator.is_valid_url(url):
            result.add_error(f"Invalid URL format: {url}")
        else:
            normalized = URLValidator.normalize_url(url)
            if normalized != url:
                result.add_error(f"URL should be normalized to: {normalized}")
        
        results[url] = result
    
    return results


def validate_social_media_username(platform: str, username: str) -> ValidationResult:
    """
    Validate social media username for specific platform
    
    Args:
        platform: Platform name (instagram, tiktok, twitter, etc.)
        username: Username to validate
        
    Returns:
        Validation result
    """
    result = ValidationResult()
    
    if not username or not isinstance(username, str):
        result.add_error("Username cannot be empty")
        return result
    
    validators = {
        'instagram': SocialMediaValidator.is_valid_instagram_username,
        'tiktok': SocialMediaValidator.is_valid_tiktok_username,
        'twitter': SocialMediaValidator.is_valid_twitter_username,
        'x': SocialMediaValidator.is_valid_twitter_username,
    }
    
    validator = validators.get(platform.lower())
    if validator:
        if not validator(username):
            result.add_error(f"Invalid {platform} username format: {username}")
    else:
        result.add_error(f"Unknown platform: {platform}")
    
    return result