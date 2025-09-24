"""
Configuration management for Instagram Reels Microservice
Handles environment variables and configuration settings
"""
import os
from typing import Optional
from dataclasses import dataclass
import logging

@dataclass
class InstagramConfig:
    """Instagram configuration settings"""
    username: Optional[str] = None
    password: Optional[str] = None
    use_login: bool = False

@dataclass
class MistralConfig:
    """Mistral AI configuration settings"""
    api_key: Optional[str] = None
    api_url: str = "https://api.mistral.ai/v1/chat/completions"
    model: str = "mistral-tiny"
    temperature: float = 0.7
    max_tokens: int = 500

@dataclass
class ServiceConfig:
    """Main service configuration"""
    host: str = "0.0.0.0"
    port: int = 5001
    debug: bool = False
    max_reels_default: int = 10
    scraping_timeout: int = 30
    max_retries: int = 3
    
class ConfigManager:
    """Configuration manager for the microservice"""
    
    def __init__(self):
        self.instagram = InstagramConfig()
        self.mistral = MistralConfig()
        self.service = ServiceConfig()
        self._load_from_environment()
        self._setup_logging()
    
    def _load_from_environment(self):
        """Load configuration from environment variables"""
        # Instagram configuration
        self.instagram.username = os.getenv('INSTAGRAM_USERNAME')
        self.instagram.password = os.getenv('INSTAGRAM_PASSWORD')
        self.instagram.use_login = os.getenv('INSTAGRAM_USE_LOGIN', 'true').lower() == 'true'
        
        # Mistral configuration
        self.mistral.api_key = os.getenv('MISTRAL_API_KEY')
        self.mistral.api_url = os.getenv('MISTRAL_API_URL', self.mistral.api_url)
        self.mistral.model = os.getenv('MISTRAL_MODEL', self.mistral.model)
        self.mistral.temperature = float(os.getenv('MISTRAL_TEMPERATURE', str(self.mistral.temperature)))
        self.mistral.max_tokens = int(os.getenv('MISTRAL_MAX_TOKENS', str(self.mistral.max_tokens)))
        
        # Service configuration
        self.service.host = os.getenv('SERVICE_HOST', self.service.host)
        self.service.port = int(os.getenv('SERVICE_PORT', str(self.service.port)))
        self.service.debug = os.getenv('DEBUG', 'false').lower() == 'true'
        self.service.max_reels_default = int(os.getenv('MAX_REELS_DEFAULT', str(self.service.max_reels_default)))
        self.service.scraping_timeout = int(os.getenv('SCRAPING_TIMEOUT', str(self.service.scraping_timeout)))
        self.service.max_retries = int(os.getenv('MAX_RETRIES', str(self.service.max_retries)))
    
    def _setup_logging(self):
        """Setup logging configuration"""
        log_level = logging.DEBUG if self.service.debug else logging.INFO
        logging.basicConfig(
            level=log_level,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
    
    def validate_config(self) -> bool:
        """Validate the configuration"""
        errors = []
        
        if not self.mistral.api_key:
            errors.append("MISTRAL_API_KEY is required")
        
        if self.instagram.use_login and (not self.instagram.username or not self.instagram.password):
            errors.append("Instagram credentials required when INSTAGRAM_USE_LOGIN is true")
        
        if errors:
            raise ValueError(f"Configuration validation failed: {', '.join(errors)}")
        
        return True
    
    def to_dict(self) -> dict:
        """Convert configuration to dictionary (excluding sensitive data)"""
        return {
            'service': {
                'host': self.service.host,
                'port': self.service.port,
                'debug': self.service.debug,
                'max_reels_default': self.service.max_reels_default,
                'scraping_timeout': self.service.scraping_timeout,
                'max_retries': self.service.max_retries
            },
            'mistral': {
                'api_url': self.mistral.api_url,
                'model': self.mistral.model,
                'temperature': self.mistral.temperature,
                'max_tokens': self.mistral.max_tokens
            },
            'instagram': {
                'use_login': self.instagram.use_login,
                'username_configured': bool(self.instagram.username)
            }
        }

# Global configuration instance
config = ConfigManager()