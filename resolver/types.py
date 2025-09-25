"""
Data classes and enums for platform detection
"""

from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Optional, Any


class PlatformType(Enum):
    """Supported platform types"""
    YOUTUBE = "youtube"
    INSTAGRAM = "instagram"
    TIKTOK = "tiktok"
    TWITTER = "twitter"
    FACEBOOK = "facebook"
    LINKEDIN = "linkedin"
    SNAPCHAT = "snapchat"
    PINTEREST = "pinterest"
    REDDIT = "reddit"
    TWITCH = "twitch"
    DISCORD = "discord"
    SPOTIFY = "spotify"
    APPLE_MUSIC = "apple_music"
    SOUNDCLOUD = "soundcloud"
    VIMEO = "vimeo"
    DAILYMOTION = "dailymotion"
    MEDIUM = "medium"
    QUORA = "quora"
    STACK_OVERFLOW = "stack_overflow"
    GITHUB = "github"
    GITLAB = "gitlab"
    BEHANCE = "behance"
    DRIBBBLE = "dribbble"
    UNSPLASH = "unsplash"
    IMGUR = "imgur"
    GIPHY = "giphy"
    TELEGRAM = "telegram"
    WHATSAPP = "whatsapp"
    SIGNAL = "signal"
    MASTODON = "mastodon"
    CLUBHOUSE = "clubhouse"
    UNKNOWN = "unknown"


class ConfidenceLevel(Enum):
    """Confidence levels for platform detection"""
    VERY_HIGH = 0.95
    HIGH = 0.8
    MEDIUM = 0.5
    LOW = 0.3
    VERY_LOW = 0.1


@dataclass
class PlatformInfo:
    """Information about a detected platform"""
    platform: str
    confidence: float
    url: str
    platform_type: PlatformType
    confidence_level: ConfidenceLevel
    details: Optional[Dict[str, Any]] = None
    
    def __post_init__(self):
        """Post-initialization to set derived fields"""
        if self.confidence >= 0.95:
            self.confidence_level = ConfidenceLevel.VERY_HIGH
        elif self.confidence >= 0.8:
            self.confidence_level = ConfidenceLevel.HIGH
        elif self.confidence >= 0.5:
            self.confidence_level = ConfidenceLevel.MEDIUM
        elif self.confidence >= 0.3:
            self.confidence_level = ConfidenceLevel.LOW
        else:
            self.confidence_level = ConfidenceLevel.VERY_LOW
        
        try:
            self.platform_type = PlatformType(self.platform)
        except ValueError:
            self.platform_type = PlatformType.UNKNOWN


@dataclass
class PlatformDetectionResult:
    """Result of platform detection"""
    url: str
    platform: str
    confidence: float
    is_supported: bool
    platform_info: Optional[PlatformInfo] = None
    alternative_platforms: Optional[List[str]] = None
    error: Optional[str] = None


@dataclass
class BatchDetectionResult:
    """Result of batch platform detection"""
    results: List[PlatformDetectionResult]
    total_urls: int
    successful_detections: int
    failed_detections: int
    processing_time: float
    timestamp: str