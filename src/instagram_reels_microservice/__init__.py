"""
Instagram Reels Microservice - A modular microservice for Instagram reel analysis

This package provides a complete microservice solution for scraping and analyzing
Instagram reels using AI-powered content analysis.
"""

__version__ = "1.0.0"
__author__ = "Instagram Reels Microservice Team"
__description__ = "Modular microservice for Instagram reel analysis with AI"

from .models import (
    ReelData, ReelAnalysis, CreatorInfo, Comment,
    ScrapingRequest, ScrapingResponse, HealthStatus
)
from .config import config, ConfigManager
from .services.scraper import InstagramScraper
from .services.analyzer import AIAnalyzer
from .services.api_service import InstagramReelsService, create_app, run_service

__all__ = [
    # Models
    'ReelData', 'ReelAnalysis', 'CreatorInfo', 'Comment',
    'ScrapingRequest', 'ScrapingResponse', 'HealthStatus',
    
    # Configuration
    'config', 'ConfigManager',
    
    # Services
    'InstagramScraper', 'AIAnalyzer', 'InstagramReelsService',
    
    # Application factory
    'create_app', 'run_service'
]