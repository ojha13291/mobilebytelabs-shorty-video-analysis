"""
API schemas and data models
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum


class Platform(Enum):
    """Supported social media platforms"""
    YOUTUBE = "youtube"
    INSTAGRAM = "instagram"
    TIKTOK = "tiktok"
    TWITTER = "twitter"
    FACEBOOK = "facebook"
    LINKEDIN = "linkedin"
    SNAPCHAT = "snapchat"
    UNKNOWN = "unknown"


@dataclass
class PlatformInfo:
    """Information about a detected platform"""
    platform: str
    confidence: float
    url: str
    details: Optional[Dict[str, Any]] = None


@dataclass
class ReelData:
    """Data structure for social media reel/post"""
    url: str
    platform: str
    title: Optional[str] = None
    description: Optional[str] = None
    likes: Optional[int] = None
    comments: Optional[int] = None
    shares: Optional[int] = None
    views: Optional[int] = None
    author: Optional[str] = None
    timestamp: Optional[str] = None
    hashtags: Optional[List[str]] = None
    mentions: Optional[List[str]] = None
    media_url: Optional[str] = None
    thumbnail_url: Optional[str] = None


@dataclass
class AnalysisResult:
    """Result of sentiment and content analysis"""
    sentiment: str
    confidence: float
    summary: str
    key_themes: List[str]
    emotional_tone: str
    engagement_prediction: str
    recommendations: List[str]
    raw_analysis: Optional[Dict[str, Any]] = None


@dataclass
class HealthResponse:
    """Health check response"""
    status: str
    timestamp: str
    version: str
    services: Dict[str, str]