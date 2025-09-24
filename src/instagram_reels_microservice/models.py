"""
Data models for Instagram Reels Microservice
Defines the data structures used throughout the service
"""
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from datetime import datetime

@dataclass
class CreatorInfo:
    """Information about the reel creator"""
    username: str
    profile_url: str
    full_name: Optional[str] = None
    followers_count: Optional[int] = None
    following_count: Optional[int] = None

@dataclass
class Comment:
    """Instagram comment data"""
    user: str
    comment: str
    timestamp: Optional[datetime] = None
    likes: Optional[int] = None

@dataclass
class ReelAnalysis:
    """AI analysis results for a reel"""
    summary: str
    category: List[str]
    sentiment: str
    top_comment_summary: str
    keywords: List[str] = field(default_factory=list)

@dataclass
class ReelData:
    """Complete Instagram reel data"""
    reel_id: str
    reel_url: str
    video_url: Optional[str]
    caption: Optional[str]
    creator: CreatorInfo
    likes: int
    views: int
    comments_count: int
    posted_at: Optional[datetime] = None
    hashtags: List[str] = field(default_factory=list)
    mentions: List[str] = field(default_factory=list)
    top_comments: List[Comment] = field(default_factory=list)
    analysis: Optional[ReelAnalysis] = None
    embeddings: Optional[List[float]] = None
    raw_data: Optional[Dict[str, Any]] = None

@dataclass
class ScrapingRequest:
    """Request parameters for scraping reels"""
    target: str  # URL, profile, or hashtag
    max_reels: int = 10
    use_login: bool = True
    scraping_method: str = "instaloader"  # "instaloader" or "selenium"
    include_comments: bool = True
    include_analysis: bool = True

@dataclass
class ScrapingResponse:
    """Response from scraping operation"""
    status: str
    count: int
    results: List[ReelData]
    errors: List[str] = field(default_factory=list)
    processing_time: Optional[float] = None

@dataclass
class HealthStatus:
    """Health check status"""
    status: str
    version: str
    timestamp: datetime
    services: Dict[str, str] = field(default_factory=dict)
    uptime: Optional[float] = None

@dataclass
class ServiceMetrics:
    """Service performance metrics"""
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    average_processing_time: float = 0.0
    last_request_time: Optional[datetime] = None