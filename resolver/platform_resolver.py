"""
Platform Resolver Module

This module provides functionality to detect social media platforms from URLs.
It supports YouTube, Instagram, TikTok, Twitter/X, and can be easily extended
for additional platforms.
"""

import re
from urllib.parse import urlparse
from typing import Dict, List, Optional


class PlatformResolver:
    """
    A class to detect social media platforms from URLs.
    
    This class provides methods to identify which social media platform
    a given URL belongs to, with support for multiple URL formats and
    easy extensibility for new platforms.
    """
    
    def __init__(self):
        """Initialize the PlatformResolver with platform patterns."""
        self.platform_patterns = self._initialize_patterns()
    
    def _initialize_patterns(self) -> Dict[str, List[str]]:
        """
        Initialize URL patterns for different social media platforms.
        
        Returns:
            Dict[str, List[str]]: Dictionary mapping platform names to URL patterns
        """
        patterns = {
            'youtube': [
                # Standard YouTube URLs
                r'youtube\.com/watch\?v=',
                r'youtube\.com/embed/',
                r'youtube\.com/v/',
                r'youtube\.com/shorts/',
                r'youtube\.com/channel/',
                r'youtube\.com/c/',
                r'youtube\.com/user/',
                r'youtube\.com/playlist\?list=',
                # YouTube mobile URLs
                r'm\.youtube\.com/watch\?v=',
                r'm\.youtube\.com/shorts/',
                # YouTube Studio
                r'studio\.youtube\.com/',
                # YouTube Music
                r'music\.youtube\.com/',
                # YouTube TV
                r'tv\.youtube\.com/',
                # Short URLs
                r'youtu\.be/',
                r'yt\.be/',
                # YouTube Kids
                r'youtubekids\.com/',
            ],
            'instagram': [
                # Standard Instagram URLs
                r'instagram\.com/p/',
                r'instagram\.com/reel/',
                r'instagram\.com/tv/',
                r'instagram\.com/stories/',
                r'instagram\.com/highlights/',
                # Profile URLs
                r'instagram\.com/[^/]+/?$',
                r'instagram\.com/[^/]+/feed/',
                r'instagram\.com/[^/]+/tagged/',
                r'instagram\.com/[^/]+/reels/',
                # IGTV
                r'instagram\.com/igtv/',
                # Mobile URLs
                r'm\.instagram\.com/p/',
                r'm\.instagram\.com/reel/',
                r'm\.instagram\.com/[^/]+/?$',
                # Business URLs
                r'business\.instagram\.com/',
                # Lite URLs
                r'instagr\.am/p/',
                r'instagr\.am/reel/',
                r'instagr\.am/[^/]+/?$',
            ],
            'tiktok': [
                # Standard TikTok URLs
                r'tiktok\.com/@',
                r'tiktok\.com/video/',
                r'tiktok\.com/discover/',
                r'tiktok\.com/tag/',
                r'tiktok\.com/music/',
                r'tiktok\.com/trending/',
                # Mobile URLs
                r'm\.tiktok\.com/v/',
                r'm\.tiktok\.com/h5/share/usr/',
                r'm\.tiktok\.com/h5/share/video/',
                # Short URLs
                r'vm\.tiktok\.com/',
                r'tiktok\.com/t/',
                # Creator URLs
                r'www\.tiktok\.com/@',
                # Business URLs
                r'business\.tiktok\.com/',
                # TikTok for Developers
                r'developers\.tiktok\.com/',
            ],
            'twitter': [
                # Standard Twitter URLs (both twitter.com and x.com)
                r'twitter\.com/[^/]+/status/',
                r'twitter\.com/[^/]+/statuses/',
                r'twitter\.com/[^/]+/media',
                r'twitter\.com/[^/]+/likes',
                r'twitter\.com/[^/]+/with_replies',
                r'twitter\.com/search\?q=',
                r'twitter\.com/hashtag/',
                r'twitter\.com/i/',
                r'twitter\.com/messages',
                r'twitter\.com/notifications',
                # Profile URLs
                r'twitter\.com/[^/]+/?$',
                # Mobile URLs
                r'mobile\.twitter\.com/',
                r'm\.twitter\.com/',
                # X.com (Twitter rebrand)
                r'x\.com/[^/]+/status/',
                r'x\.com/[^/]+/statuses/',
                r'x\.com/[^/]+/media',
                r'x\.com/[^/]+/likes',
                r'x\.com/[^/]+/with_replies',
                r'x\.com/search\?q=',
                r'x\.com/hashtag/',
                r'x\.com/i/',
                r'x\.com/messages',
                r'x\.com/notifications',
                r'x\.com/[^/]+/?$',
                # Short URLs
                r't\.co/',
                r'tw\.tl/',
                r'twt\.to/',
                # Twitter Spaces
                r'twitter\.com/i/spaces/',
                r'x\.com/i/spaces/',
            ],
            'facebook': [
                # Standard Facebook URLs
                r'facebook\.com/[^/]+/posts/',
                r'facebook\.com/[^/]+/videos/',
                r'facebook\.com/[^/]+/photos/',
                r'facebook\.com/[^/]+/live_videos/',
                r'facebook\.com/watch/',
                r'facebook\.com/groups/',
                r'facebook\.com/events/',
                r'facebook\.com/pages/',
                r'facebook\.com/marketplace/',
                # Profile URLs
                r'facebook\.com/[^/]+/?$',
                r'facebook\.com/profile\.php\?id=',
                # Mobile URLs
                r'm\.facebook\.com/',
                r'mobile\.facebook\.com/',
                # Business URLs
                r'business\.facebook\.com/',
                # Facebook Business Suite
                r'business\.suite\.facebook\.com/',
                # Facebook Gaming
                r'fb\.gg/',
                r'gaming\.facebook\.com/',
                # Facebook Messenger
                r'messenger\.com/',
                r'm\.me/',
                # Facebook Lite
                r'lite\.facebook\.com/',
            ],
            'linkedin': [
                # Standard LinkedIn URLs
                r'linkedin\.com/in/',
                r'linkedin\.com/company/',
                r'linkedin\.com/jobs/',
                r'linkedin\.com/feed/',
                r'linkedin\.com/posts/',
                r'linkedin\.com/pulse/',
                r'linkedin\.com/learning/',
                r'linkedin\.com/groups/',
                r'linkedin\.com/events/',
                # Mobile URLs
                r'm\.linkedin\.com/',
                # Business URLs
                r'business\.linkedin\.com/',
                # Learning URLs
                r'learning\.linkedin\.com/',
            ],
            'snapchat': [
                # Standard Snapchat URLs
                r'snapchat\.com/add/',
                r'snapchat\.com/discover/',
                r'snapchat\.com/stories/',
                r'snapchat\.com/create/',
                # Mobile URLs
                r'm\.snapchat\.com/',
                # Short URLs
                r'sc\.to/',
                r'snap\.me/',
                # Business URLs
                r'business\.snapchat\.com/',
                r'forbusiness\.snapchat\.com/',
            ],
            'pinterest': [
                # Standard Pinterest URLs
                r'pinterest\.com/pin/',
                r'pinterest\.com/[^/]+/',
                r'pinterest\.com/search/',
                r'pinterest\.com/categories/',
                r'pinterest\.com/explore/',
                # Mobile URLs
                r'm\.pinterest\.com/',
                # Business URLs
                r'business\.pinterest\.com/',
                # Short URLs
                r'pin\.it/',
            ],
            'reddit': [
                # Standard Reddit URLs
                r'reddit\.com/r/',
                r'reddit\.com/u/',
                r'reddit\.com/user/',
                r'reddit\.com/comments/',
                r'reddit\.com/submit',
                r'reddit\.com/search\?q=',
                # Mobile URLs
                r'm\.reddit\.com/',
                r'i\.reddit\.com/',
                # Old Reddit
                r'old\.reddit\.com/',
                # Short URLs
                r'redd\.it/',
                r'rdt\.me/',
            ],
            'twitch': [
                # Standard Twitch URLs
                r'twitch\.tv/',
                r'twitch\.tv/videos/',
                r'twitch\.tv/clips/',
                r'twitch\.tv/collections/',
                r'twitch\.tv/events/',
                r'twitch\.tv/directory/',
                # Mobile URLs
                r'm\.twitch\.tv/',
                # Business URLs
                r'creator\.twitch\.tv/',
                r'dev\.twitch\.tv/',
            ],
            'discord': [
                # Standard Discord URLs
                r'discord\.com/channels/',
                r'discord\.com/invite/',
                r'discord\.com/servers/',
                r'discord\.com/activity',
                # App URLs
                r'discordapp\.com/channels/',
                r'discordapp\.com/invite/',
                # Short URLs
                r'discord\.gg/',
                r'dsc\.gg/',
                r'disboard\.org/',
            ],
            'telegram': [
                # Standard Telegram URLs
                r't\.me/',
                r'telegram\.me/',
                r'telegram\.org/',
                # Web URLs
                r'web\.telegram\.org/',
                # Desktop URLs
                r'desktop\.telegram\.org/',
                # Mac URLs
                r'macapp\.telegram\.org/',
            ],
            'whatsapp': [
                # Standard WhatsApp URLs
                r'whatsapp\.com/',
                r'web\.whatsapp\.com/',
                r'api\.whatsapp\.com/',
                r'me\.whatsapp\.com/',
                # Business URLs
                r'business\.whatsapp\.com/',
                # Short URLs
                r'wa\.me/',
                r'whatsapp\.com/dl/',
            ],
            'vimeo': [
                # Standard Vimeo URLs
                r'vimeo\.com/',
                r'vimeo\.com/ondemand/',
                r'vimeo\.com/showcase/',
                r'vimeo\.com/channels/',
                r'vimeo\.com/groups/',
                # Creator URLs
                r'vimeo\.com/creator/',
                # Business URLs
                r'business\.vimeo\.com/',
                r'vimeo\.com/enterprise/',
            ],
            'dailymotion': [
                # Standard Dailymotion URLs
                r'dailymotion\.com/video/',
                r'dailymotion\.com/playlist/',
                r'dailymotion\.com/user/',
                r'dailymotion\.com/channel/',
                # Mobile URLs
                r'm\.dailymotion\.com/',
                # Short URLs
                r'dai\.ly/',
            ],
        }
        return patterns
    
    def detect_platform(self, url: str) -> str:
        """
        Detect the social media platform from a given URL.
        
        Args:
            url (str): The URL to analyze
            
        Returns:
            str: The platform name ('unknown' if not recognized)
            
        Examples:
            >>> resolver = PlatformResolver()
            >>> resolver.detect_platform('https://www.youtube.com/watch?v=dQw4w9WgXcQ')
            'youtube'
            >>> resolver.detect_platform('https://www.instagram.com/reel/ABC123DEF/')
            'instagram'
            >>> resolver.detect_platform('invalid-url')
            'unknown'
        """
        if not url or not isinstance(url, str):
            return 'unknown'
        
        try:
            # Handle protocol-relative URLs (//example.com)
            if url.startswith('//'):
                url = 'https:' + url
            
            # Basic URL validation
            if not url.startswith(('http://', 'https://')):
                url = 'https://' + url
            
            # Parse URL to get domain
            parsed_url = urlparse(url)
            domain = parsed_url.netloc.lower()
            
            # Check if URL is valid
            if not domain:
                return 'unknown'
            
            # Remove 'www.' prefix for cleaner matching
            domain = domain.replace('www.', '')
            
            # Check each platform's patterns
            for platform, patterns in self.platform_patterns.items():
                for pattern in patterns:
                    # Create full pattern with domain
                    full_pattern = pattern.replace('\\.', '.')
                    if re.search(pattern, url, re.IGNORECASE):
                        return platform
            
            # Additional check for domain-based detection
            domain_platforms = {
                'youtube.com': 'youtube',
                'youtu.be': 'youtube',
                'instagram.com': 'instagram',
                'instagr.am': 'instagram',
                'tiktok.com': 'tiktok',
                'twitter.com': 'twitter',
                'x.com': 'twitter',
                'facebook.com': 'facebook',
                'fb.com': 'facebook',
                'linkedin.com': 'linkedin',
                'snapchat.com': 'snapchat',
                'pinterest.com': 'pinterest',
                'reddit.com': 'reddit',
                'twitch.tv': 'twitch',
                'discord.com': 'discord',
                'discordapp.com': 'discord',
                'telegram.org': 'telegram',
                't.me': 'telegram',
                'whatsapp.com': 'whatsapp',
                'wa.me': 'whatsapp',
                'vimeo.com': 'vimeo',
                'dailymotion.com': 'dailymotion',
            }
            
            # Check if domain matches any known platform
            for known_domain, platform in domain_platforms.items():
                if known_domain in domain:
                    return platform
            
            return 'unknown'
            
        except Exception as e:
            # Handle malformed URLs gracefully
            return 'unknown'
    
    def get_platform_info(self, url: str) -> Dict[str, str]:
        """
        Get detailed information about the detected platform.
        
        Args:
            url (str): The URL to analyze
            
        Returns:
            Dict[str, str]: Dictionary containing platform information
            
        Examples:
            >>> resolver = PlatformResolver()
            >>> info = resolver.get_platform_info('https://www.youtube.com/watch?v=dQw4w9WgXcQ')
            >>> print(info)
            {'platform': 'youtube', 'confidence': 'high', 'url_type': 'video'}
        """
        platform = self.detect_platform(url)
        
        if platform == 'unknown':
            return {
                'platform': 'unknown',
                'confidence': 'low',
                'url_type': 'unknown',
                'description': 'Platform not recognized'
            }
        
        # Determine URL type based on patterns
        url_type = self._determine_url_type(platform, url)
        confidence = self._determine_confidence(platform, url)
        
        platform_descriptions = {
            'youtube': 'Video sharing platform',
            'instagram': 'Photo and video sharing platform',
            'tiktok': 'Short-form video platform',
            'twitter': 'Microblogging and social networking',
            'facebook': 'Social networking platform',
            'linkedin': 'Professional networking platform',
            'snapchat': 'Multimedia messaging app',
            'pinterest': 'Visual discovery and bookmarking',
            'reddit': 'Social news and discussion platform',
            'twitch': 'Live streaming platform',
            'discord': 'Voice, video, and text communication',
            'telegram': 'Cloud-based instant messaging',
            'whatsapp': 'Instant messaging and voice over IP',
            'vimeo': 'Video hosting and sharing platform',
            'dailymotion': 'Video sharing platform',
        }
        
        return {
            'platform': platform,
            'confidence': confidence,
            'url_type': url_type,
            'description': platform_descriptions.get(platform, 'Social media platform')
        }
    
    def _determine_url_type(self, platform: str, url: str) -> str:
        """Determine the type of content the URL points to."""
        url_lower = url.lower()
        
        # YouTube
        if platform == 'youtube':
            if '/watch?v=' in url_lower or '/embed/' in url_lower or '/v/' in url_lower:
                return 'video'
            elif '/shorts/' in url_lower:
                return 'shorts'
            elif '/channel/' in url_lower or '/c/' in url_lower or '/user/' in url_lower:
                return 'channel'
            elif '/playlist' in url_lower:
                return 'playlist'
            else:
                return 'page'
        
        # Instagram
        elif platform == 'instagram':
            if '/p/' in url_lower:
                return 'post'
            elif '/reel/' in url_lower:
                return 'reel'
            elif '/stories/' in url_lower:
                return 'story'
            elif '/tv/' in url_lower:
                return 'igtv'
            elif '/highlights/' in url_lower:
                return 'highlight'
            else:
                return 'profile'
        
        # TikTok
        elif platform == 'tiktok':
            if '/video/' in url_lower:
                return 'video'
            elif '/@' in url_lower:
                return 'profile'
            elif '/tag/' in url_lower:
                return 'hashtag'
            else:
                return 'page'
        
        # Twitter/X
        elif platform == 'twitter':
            if '/status/' in url_lower or '/statuses/' in url_lower:
                return 'tweet'
            elif '/media' in url_lower:
                return 'media'
            elif '/hashtag/' in url_lower:
                return 'hashtag'
            else:
                return 'profile'
        
        # Default for other platforms
        else:
            return 'content'
    
    def _determine_confidence(self, platform: str, url: str) -> str:
        """Determine the confidence level of the platform detection."""
        try:
            parsed_url = urlparse(url)
            domain = parsed_url.netloc.lower().replace('www.', '')
            
            # High confidence if domain exactly matches known platform
            domain_platforms = {
                'youtube.com': 'youtube',
                'youtu.be': 'youtube',
                'instagram.com': 'instagram',
                'instagr.am': 'instagram',
                'tiktok.com': 'tiktok',
                'twitter.com': 'twitter',
                'x.com': 'twitter',
                'facebook.com': 'facebook',
                'linkedin.com': 'linkedin',
                'snapchat.com': 'snapchat',
                'pinterest.com': 'pinterest',
                'reddit.com': 'reddit',
                'twitch.tv': 'twitch',
                'discord.com': 'discord',
                'telegram.org': 'telegram',
                'whatsapp.com': 'whatsapp',
                'vimeo.com': 'vimeo',
                'dailymotion.com': 'dailymotion',
            }
            
            if domain in domain_platforms and domain_platforms[domain] == platform:
                return 'high'
            else:
                return 'medium'
                
        except Exception:
            return 'low'
    
    def add_platform(self, platform_name: str, patterns: List[str]) -> None:
        """
        Add a new platform with its URL patterns.
        
        Args:
            platform_name (str): Name of the platform
            patterns (List[str]): List of regex patterns for the platform
        """
        self.platform_patterns[platform_name.lower()] = patterns
    
    def remove_platform(self, platform_name: str) -> None:
        """
        Remove a platform from detection.
        
        Args:
            platform_name (str): Name of the platform to remove
        """
        if platform_name.lower() in self.platform_patterns:
            del self.platform_patterns[platform_name.lower()]
    
    def list_platforms(self) -> List[str]:
        """
        Get a list of all supported platforms.
        
        Returns:
            List[str]: List of platform names
        """
        return list(self.platform_patterns.keys())
    
    def get_supported_platforms(self) -> List[str]:
        """
        Get a list of all supported platforms (alias for list_platforms).
        
        Returns:
            List[str]: List of supported platform names
        """
        return self.list_platforms()


# Global instance for convenience
_resolver = PlatformResolver()


def detect_platform(url: str) -> str:
    """
    Convenience function to detect platform from URL.
    
    Args:
        url (str): The URL to analyze
        
    Returns:
        str: The detected platform name or 'unknown'
        
    Examples:
        >>> detect_platform('https://www.youtube.com/watch?v=dQw4w9WgXcQ')
        'youtube'
        >>> detect_platform('https://www.instagram.com/reel/ABC123DEF/')
        'instagram'
        >>> detect_platform('invalid-url')
        'unknown'
    """
    return _resolver.detect_platform(url)


def get_platform_info(url: str) -> Dict[str, str]:
    """
    Convenience function to get detailed platform information.
    
    Args:
        url (str): The URL to analyze
        
    Returns:
        Dict[str, str]: Dictionary containing platform information
        
    Examples:
        >>> info = get_platform_info('https://www.youtube.com/watch?v=dQw4w9WgXcQ')
        >>> print(info['platform'], info['url_type'])
        youtube video
    """
    return _resolver.get_platform_info(url)


# Example usage and testing
if __name__ == "__main__":
    # Test URLs
    test_urls = [
        "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
        "https://www.instagram.com/reel/ABC123DEF/",
        "https://www.tiktok.com/@username/video/1234567890",
        "https://twitter.com/username/status/1234567890123456789",
        "https://x.com/username/status/1234567890123456789",
        "https://www.facebook.com/username/posts/1234567890123456",
        "https://invalid-url-example.com",
        "not-a-url",
        "",
    ]
    
    print("Platform Detection Test Results:")
    print("=" * 50)
    
    for url in test_urls:
        try:
            platform = detect_platform(url)
            info = get_platform_info(url)
            print(f"URL: {url}")
            print(f"Platform: {platform}")
            print(f"Type: {info['url_type']}")
            print(f"Confidence: {info['confidence']}")
            print(f"Description: {info['description']}")
            print("-" * 30)
        except Exception as e:
            print(f"Error processing URL '{url}': {e}")
            print("-" * 30)