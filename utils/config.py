"""
Configuration management for the application
"""

import os
import json
from typing import Dict, Any, Optional, Union
from pathlib import Path
from dataclasses import dataclass, field
from dotenv import load_dotenv


@dataclass
class DatabaseConfig:
    """Database configuration"""
    host: str = "localhost"
    port: int = 5432
    database: str = "video_sentiment"
    username: str = "postgres"
    password: str = ""
    ssl_mode: str = "disable"
    connection_timeout: int = 30
    
    @property
    def connection_string(self) -> str:
        """Get PostgreSQL connection string"""
        return f"postgresql://{self.username}:{self.password}@{self.host}:{self.port}/{self.database}?sslmode={self.ssl_mode}"


@dataclass
class APIConfig:
    """API configuration"""
    host: str = "0.0.0.0"
    port: int = 5000
    debug: bool = False
    cors_origins: list = field(default_factory=lambda: ["*"])
    rate_limit_per_minute: int = 60
    max_content_length: int = 16 * 1024 * 1024  # 16MB
    
    def __post_init__(self):
        """Post-initialization validation"""
        if not isinstance(self.cors_origins, list):
            self.cors_origins = [self.cors_origins]


@dataclass
class MistralConfig:
    """Mistral AI configuration"""
    api_key: str = ""
    model: str = "mistral-tiny"
    max_tokens: int = 2048
    temperature: float = 0.7
    top_p: float = 0.9
    timeout: int = 30
    
    def __post_init__(self):
        """Post-initialization validation"""
        if self.temperature < 0 or self.temperature > 2:
            self.temperature = 0.7
        
        if self.top_p < 0 or self.top_p > 1:
            self.top_p = 0.9


@dataclass
class InstagramConfig:
    """Instagram configuration"""
    username: str = ""
    password: str = ""
    headless: bool = True
    user_agent: str = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    page_load_timeout: int = 30
    implicit_wait: int = 10


@dataclass
class ScraperConfig:
    """Scraper configuration"""
    rate_limit_delay: float = 1.0
    max_retries: int = 3
    timeout: int = 30
    max_posts_per_user: int = 50
    max_users_per_hashtag: int = 100
    enable_caching: bool = True
    cache_ttl: int = 3600  # 1 hour


@dataclass
class AnalyzerConfig:
    """Analyzer configuration"""
    embedding_model: str = "all-MiniLM-L6-v2"
    sentiment_threshold: float = 0.1
    confidence_threshold: float = 0.7
    max_text_length: int = 10000
    batch_size: int = 32
    enable_gpu: bool = True


@dataclass
class Config:
    """Main configuration class"""
    database: DatabaseConfig = field(default_factory=DatabaseConfig)
    api: APIConfig = field(default_factory=APIConfig)
    mistral: MistralConfig = field(default_factory=MistralConfig)
    instagram: InstagramConfig = field(default_factory=InstagramConfig)
    scraper: ScraperConfig = field(default_factory=ScraperConfig)
    analyzer: AnalyzerConfig = field(default_factory=AnalyzerConfig)
    
    def __post_init__(self):
        """Post-initialization validation"""
        # Ensure all nested configs are properly initialized
        if isinstance(self.database, dict):
            self.database = DatabaseConfig(**self.database)
        if isinstance(self.api, dict):
            self.api = APIConfig(**self.api)
        if isinstance(self.mistral, dict):
            self.mistral = MistralConfig(**self.mistral)
        if isinstance(self.instagram, dict):
            self.instagram = InstagramConfig(**self.instagram)
        if isinstance(self.scraper, dict):
            self.scraper = ScraperConfig(**self.scraper)
        if isinstance(self.analyzer, dict):
            self.analyzer = AnalyzerConfig(**self.analyzer)


class ConfigManager:
    """Configuration manager"""
    
    def __init__(self, config_file: Optional[str] = None, env_file: Optional[str] = None):
        """
        Initialize configuration manager
        
        Args:
            config_file: Path to configuration file
            env_file: Path to environment file
        """
        self.config_file = config_file or "config.json"
        self.env_file = env_file or ".env"
        self.config = Config()
        self._load_config()
    
    def _load_config(self):
        """Load configuration from files and environment"""
        # Load environment variables
        load_dotenv(self.env_file)
        
        # Load from JSON config file if exists
        if Path(self.config_file).exists():
            self._load_from_file()
        
        # Override with environment variables
        self._load_from_env()
    
    def _load_from_file(self):
        """Load configuration from JSON file"""
        try:
            with open(self.config_file, 'r') as f:
                config_data = json.load(f)
                
            # Update config with file data
            if 'database' in config_data:
                self.config.database = DatabaseConfig(**config_data['database'])
            if 'api' in config_data:
                self.config.api = APIConfig(**config_data['api'])
            if 'mistral' in config_data:
                self.config.mistral = MistralConfig(**config_data['mistral'])
            if 'instagram' in config_data:
                self.config.instagram = InstagramConfig(**config_data['instagram'])
            if 'scraper' in config_data:
                self.config.scraper = ScraperConfig(**config_data['scraper'])
            if 'analyzer' in config_data:
                self.config.analyzer = AnalyzerConfig(**config_data['analyzer'])
                
        except Exception as e:
            print(f"Warning: Could not load config from {self.config_file}: {e}")
    
    def _load_from_env(self):
        """Load configuration from environment variables"""
        # Database config
        self.config.database.host = os.getenv('DB_HOST', self.config.database.host)
        self.config.database.port = int(os.getenv('DB_PORT', self.config.database.port))
        self.config.database.database = os.getenv('DB_NAME', self.config.database.database)
        self.config.database.username = os.getenv('DB_USER', self.config.database.username)
        self.config.database.password = os.getenv('DB_PASSWORD', self.config.database.password)
        
        # API config
        self.config.api.host = os.getenv('API_HOST', self.config.api.host)
        self.config.api.port = int(os.getenv('API_PORT', self.config.api.port))
        self.config.api.debug = os.getenv('API_DEBUG', str(self.config.api.debug)).lower() == 'true'
        
        # Mistral config
        self.config.mistral.api_key = os.getenv('MISTRAL_API_KEY', self.config.mistral.api_key)
        self.config.mistral.model = os.getenv('MISTRAL_MODEL', self.config.mistral.model)
        self.config.mistral.max_tokens = int(os.getenv('MISTRAL_MAX_TOKENS', self.config.mistral.max_tokens))
        
        # Instagram config
        self.config.instagram.username = os.getenv('INSTAGRAM_USERNAME', self.config.instagram.username)
        self.config.instagram.password = os.getenv('INSTAGRAM_PASSWORD', self.config.instagram.password)
        
        # Scraper config
        self.config.scraper.rate_limit_delay = float(os.getenv('SCRAPER_RATE_LIMIT_DELAY', self.config.scraper.rate_limit_delay))
        self.config.scraper.max_retries = int(os.getenv('SCRAPER_MAX_RETRIES', self.config.scraper.max_retries))
        
        # Analyzer config
        self.config.analyzer.embedding_model = os.getenv('EMBEDDING_MODEL', self.config.analyzer.embedding_model)
        self.config.analyzer.batch_size = int(os.getenv('ANALYZER_BATCH_SIZE', self.config.analyzer.batch_size))
        self.config.analyzer.enable_gpu = os.getenv('ENABLE_GPU', str(self.config.analyzer.enable_gpu)).lower() == 'true'
    
    def save_config(self, config_file: Optional[str] = None):
        """
        Save current configuration to file
        
        Args:
            config_file: Path to save configuration file
        """
        if config_file:
            self.config_file = config_file
        
        try:
            config_data = {
                'database': self.config.database.__dict__,
                'api': self.config.api.__dict__,
                'mistral': self.config.mistral.__dict__,
                'instagram': self.config.instagram.__dict__,
                'scraper': self.config.scraper.__dict__,
                'analyzer': self.config.analyzer.__dict__
            }
            
            with open(self.config_file, 'w') as f:
                json.dump(config_data, f, indent=2, default=str)
                
            print(f"Configuration saved to {self.config_file}")
            
        except Exception as e:
            print(f"Error saving configuration: {e}")
    
    def get_config(self) -> Config:
        """
        Get current configuration
        
        Returns:
            Current configuration
        """
        return self.config
    
    def update_config(self, **kwargs):
        """
        Update configuration
        
        Args:
            **kwargs: Configuration updates
        """
        for key, value in kwargs.items():
            if hasattr(self.config, key):
                setattr(self.config, key, value)
            else:
                print(f"Warning: Unknown configuration key: {key}")
    
    def validate_config(self) -> Dict[str, Any]:
        """
        Validate current configuration
        
        Returns:
            Dictionary with validation results
        """
        errors = []
        warnings = []
        
        # Validate required fields
        if not self.config.mistral.api_key:
            errors.append("Mistral API key is required")
        
        if not self.config.instagram.username or not self.config.instagram.password:
            warnings.append("Instagram credentials not configured")
        
        # Validate numeric ranges
        if self.config.api.port < 1 or self.config.api.port > 65535:
            errors.append(f"Invalid API port: {self.config.api.port}")
        
        if self.config.mistral.temperature < 0 or self.config.mistral.temperature > 2:
            errors.append(f"Invalid Mistral temperature: {self.config.mistral.temperature}")
        
        if self.config.mistral.top_p < 0 or self.config.mistral.top_p > 1:
            errors.append(f"Invalid Mistral top_p: {self.config.mistral.top_p}")
        
        return {
            'is_valid': len(errors) == 0,
            'errors': errors,
            'warnings': warnings
        }


# Global configuration manager instance
config_manager = ConfigManager()


def get_config() -> Config:
    """
    Get global configuration
    
    Returns:
        Global configuration
    """
    return config_manager.get_config()


def load_config(config_file: Optional[str] = None, env_file: Optional[str] = None) -> ConfigManager:
    """
    Load configuration
    
    Args:
        config_file: Path to configuration file
        env_file: Path to environment file
        
    Returns:
        Configuration manager
    """
    global config_manager
    config_manager = ConfigManager(config_file, env_file)
    return config_manager