"""
URL patterns and regex constants for platform detection
"""

import re
from typing import Dict, List


# URL patterns for different social media platforms
PLATFORM_PATTERNS = {
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
        r'snap\.chat/',
        # Business URLs
        r'business\.snapchat\.com/',
        # Creator URLs
        r'creator\.snapchat\.com/',
    ],
    'pinterest': [
        # Standard Pinterest URLs
        r'pinterest\.com/pin/',
        r'pinterest\.com/[^/]+/',
        r'pinterest\.com/search/pins/',
        r'pinterest\.com/search/boards/',
        # Mobile URLs
        r'm\.pinterest\.com/',
        # Business URLs
        r'business\.pinterest\.com/',
        # Creator URLs
        r'creator\.pinterest\.com/',
    ],
    'reddit': [
        # Standard Reddit URLs
        r'reddit\.com/r/',
        r'reddit\.com/u/',
        r'reddit\.com/user/',
        r'reddit\.com/comments/',
        # Old Reddit
        r'old\.reddit\.com/',
        # Mobile URLs
        r'm\.reddit\.com/',
        # Short URLs
        r'redd\.it/',
    ],
    'twitch': [
        # Standard Twitch URLs
        r'twitch\.tv/',
        r'twitch\.tv/[^/]+/videos/',
        r'twitch\.tv/[^/]+/clips/',
        # Mobile URLs
        r'm\.twitch\.tv/',
        # Creator dashboard
        r'dashboard\.twitch\.tv/',
        # Business URLs
        r'business\.twitch\.tv/',
    ],
    'discord': [
        # Discord invite URLs
        r'discord\.gg/',
        r'discordapp\.com/invite/',
        r'discord\.com/invite/',
        # Discord server URLs
        r'discord\.com/channels/',
        # Short URLs
        r'discord\.me/',
    ],
    'spotify': [
        # Spotify track URLs
        r'spotify\.com/track/',
        r'spotify\.com/album/',
        r'spotify\.com/playlist/',
        r'spotify\.com/artist/',
        r'spotify\.com/episode/',
        r'spotify\.com/show/',
        # Short URLs
        r'spoti\.fi/',
        # Open URLs
        r'open\.spotify\.com/',
    ],
    'apple_music': [
        # Apple Music URLs
        r'music\.apple\.com/',
        r'itunes\.apple\.com/',
    ],
    'soundcloud': [
        # SoundCloud URLs
        r'soundcloud\.com/',
        r'soundcloud\.com/[^/]+/sets/',
        r'soundcloud\.com/[^/]+/tracks/',
        r'soundcloud\.com/[^/]+/likes/',
        # Mobile URLs
        r'm\.soundcloud\.com/',
        # Short URLs
        r'scn\.co/',
        r'snd\.sc/',
    ],
    'vimeo': [
        # Vimeo URLs
        r'vimeo\.com/',
        r'vimeo\.com/ondemand/',
        r'vimeo\.com/channels/',
        r'vimeo\.com/groups/',
        r'vimeo\.com/album/',
        # Vimeo Pro
        r'vimeopro\.com/',
        # Short URLs
        r'vimeo\.me/',
    ],
    'dailymotion': [
        # Dailymotion URLs
        r'dailymotion\.com/video/',
        r'dailymotion\.com/playlist/',
        r'dailymotion\.com/channel/',
        r'dailymotion\.com/user/',
        # Short URLs
        r'dai\.ly/',
    ],
    'medium': [
        # Medium URLs
        r'medium\.com/',
        r'medium\.com/@[^/]+/',
        r'medium\.com/tag/',
        r'medium\.com/search\?q=',
        # Publication URLs
        r'[^\.]+\.medium\.com/',
        # Short URLs
        r'me\.di\.um/',
    ],
    'quora': [
        # Quora URLs
        r'quora\.com/',
        r'quora\.com/profile/',
        r'quora\.com/topic/',
        r'quora\.com/What-is-',
        r'quora\.com/How-do-I-',
        r'quora\.com/Why-is-',
        # Short URLs
        r'qr\.ae/',
    ],
    'stack_overflow': [
        # Stack Overflow URLs
        r'stackoverflow\.com/questions/',
        r'stackoverflow\.com/users/',
        r'stackoverflow\.com/tags/',
        # Other Stack Exchange sites
        r'stackexchange\.com/',
        r'[^\.]+\.stackexchange\.com/',
        r'serverfault\.com/',
        r'superuser\.com/',
        r'askubuntu\.com/',
    ],
    'github': [
        # GitHub URLs
        r'github\.com/',
        r'github\.com/[^/]+/',
        r'github\.com/[^/]+/[^/]+',
        r'github\.com/search\?q=',
        r'github\.com/topics/',
        r'github\.com/trending/',
        # GitHub Gists
        r'gist\.github\.com/',
        # Short URLs
        r'git\.io/',
    ],
    'gitlab': [
        # GitLab URLs
        r'gitlab\.com/',
        r'gitlab\.com/[^/]+/',
        r'gitlab\.com/[^/]+/[^/]+',
        # Self-hosted GitLab instances
        r'[^\.]+\.gitlab\.io/',
        r'[^\.]+\.gitlab\.com/',
    ],
    'behance': [
        # Behance URLs
        r'behance\.net/',
        r'behance\.net/gallery/',
        r'behance\.net/search\?q=',
        # Portfolio URLs
        r'[^\.]+\.myportfolio\.com/',
    ],
    'dribbble': [
        # Dribbble URLs
        r'dribbble\.com/',
        r'dribbble\.com/shots/',
        r'dribbble\.com/search\?q=',
        # Short URLs
        r'drbl\.in/',
    ],
    'unsplash': [
        # Unsplash URLs
        r'unsplash\.com/',
        r'unsplash\.com/photos/',
        r'unsplash\.com/search\?q=',
        r'unsplash\.com/collections/',
        # Short URLs
        r'unsplash\.me/',
        r'unp\.sh/',
    ],
    'imgur': [
        # Imgur URLs
        r'imgur\.com/',
        r'imgur\.com/gallery/',
        r'imgur\.com/a/',
        r'imgur\.com/search\?q=',
        # Short URLs
        r'imgur\.me/',
        r'i\.imgur\.com/',
        r'm\.imgur\.com/',
    ],
    'giphy': [
        # Giphy URLs
        r'giphy\.com/',
        r'giphy\.com/gifs/',
        r'giphy\.com/search\?q=',
        # Short URLs
        r'gph\.is/',
        r'media\.giphy\.com/',
    ],
    'telegram': [
        # Telegram URLs
        r't\.me/',
        r'telegram\.me/',
        r'telegram\.org/',
        # Channel URLs
        r't\.me/[^/]+',
        r'telegram\.me/[^/]+',
    ],
    'whatsapp': [
        # WhatsApp Business URLs
        r'wa\.me/',
        r'whatsapp\.com/',
        r'web\.whatsapp\.com/',
        # Business API
        r'business\.whatsapp\.com/',
    ],
    'signal': [
        # Signal URLs
        r'signal\.me/',
        r'signal\.org/',
    ],
    'mastodon': [
        # Mastodon URLs (general pattern for instances)
        r'/@[^/]+/',
        r'/tags/',
        r'/search\?q=',
        # Common instances
        r'mastodon\.social/',
        r'mstdn\.social/',
        r'fosstodon\.org/',
        r'techhub\.social/',
    ],
    'clubhouse': [
        # Clubhouse URLs
        r'clubhouse\.com/',
        r'clubhouse\.com/room/',
        r'clubhouse\.com/user/',
        r'clubhouse\.com/club/',
        # Short URLs
        r'ch\.link/',
        r'joinclubhouse\.com/',
    ],
}


# Confidence thresholds
CONFIDENCE_THRESHOLDS = {
    'high': 0.8,
    'medium': 0.5,
    'low': 0.3
}


# Platform display names
PLATFORM_DISPLAY_NAMES = {
    'youtube': 'YouTube',
    'instagram': 'Instagram',
    'tiktok': 'TikTok',
    'twitter': 'Twitter/X',
    'facebook': 'Facebook',
    'linkedin': 'LinkedIn',
    'snapchat': 'Snapchat',
    'pinterest': 'Pinterest',
    'reddit': 'Reddit',
    'twitch': 'Twitch',
    'discord': 'Discord',
    'spotify': 'Spotify',
    'apple_music': 'Apple Music',
    'soundcloud': 'SoundCloud',
    'vimeo': 'Vimeo',
    'dailymotion': 'Dailymotion',
    'medium': 'Medium',
    'quora': 'Quora',
    'stack_overflow': 'Stack Overflow',
    'github': 'GitHub',
    'gitlab': 'GitLab',
    'behance': 'Behance',
    'dribbble': 'Dribbble',
    'unsplash': 'Unsplash',
    'imgur': 'Imgur',
    'giphy': 'Giphy',
    'telegram': 'Telegram',
    'whatsapp': 'WhatsApp',
    'signal': 'Signal',
    'mastodon': 'Mastodon',
    'clubhouse': 'Clubhouse',
}


def get_platform_patterns() -> Dict[str, List[str]]:
    """Get all platform URL patterns"""
    return PLATFORM_PATTERNS.copy()


def get_platform_display_name(platform: str) -> str:
    """Get display name for a platform"""
    return PLATFORM_DISPLAY_NAMES.get(platform, platform.title())


def get_confidence_thresholds() -> Dict[str, float]:
    """Get confidence thresholds"""
    return CONFIDENCE_THRESHOLDS.copy()