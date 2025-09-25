"""
Logger utility for the application
"""

import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional


class CustomLogger:
    """
    Custom logger with file and console output
    """
    
    def __init__(self, name: str = "video_sentiment_analyzer", log_level: str = "INFO"):
        """
        Initialize custom logger
        
        Args:
            name: Logger name
            log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        """
        self.name = name
        self.log_level = getattr(logging, log_level.upper(), logging.INFO)
        self.logger = None
        self.file_handler = None
        self.console_handler = None
        self._setup_logger()
    
    def _setup_logger(self):
        """Setup logger with handlers"""
        # Create logger
        self.logger = logging.getLogger(self.name)
        self.logger.setLevel(self.log_level)
        
        # Prevent duplicate handlers
        if self.logger.handlers:
            return
        
        # Create formatters
        file_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s'
        )
        console_formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s'
        )
        
        # File handler
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)
        
        log_file = log_dir / f"{self.name}_{datetime.now().strftime('%Y%m%d')}.log"
        self.file_handler = logging.FileHandler(log_file)
        self.file_handler.setLevel(self.log_level)
        self.file_handler.setFormatter(file_formatter)
        
        # Console handler
        self.console_handler = logging.StreamHandler(sys.stdout)
        self.console_handler.setLevel(self.log_level)
        self.console_handler.setFormatter(console_formatter)
        
        # Add handlers to logger
        self.logger.addHandler(self.file_handler)
        self.logger.addHandler(self.console_handler)
    
    def debug(self, message: str, *args, **kwargs):
        """Log debug message"""
        if self.logger:
            self.logger.debug(message, *args, **kwargs)
    
    def info(self, message: str, *args, **kwargs):
        """Log info message"""
        if self.logger:
            self.logger.info(message, *args, **kwargs)
    
    def warning(self, message: str, *args, **kwargs):
        """Log warning message"""
        if self.logger:
            self.logger.warning(message, *args, **kwargs)
    
    def error(self, message: str, *args, **kwargs):
        """Log error message"""
        if self.logger:
            self.logger.error(message, *args, **kwargs)
    
    def critical(self, message: str, *args, **kwargs):
        """Log critical message"""
        if self.logger:
            self.logger.critical(message, *args, **kwargs)
    
    def exception(self, message: str, *args, **kwargs):
        """Log exception with traceback"""
        if self.logger:
            self.logger.exception(message, *args, **kwargs)
    
    def log_api_request(self, endpoint: str, method: str, status_code: int, response_time: Optional[float] = None):
        """
        Log API request details
        
        Args:
            endpoint: API endpoint
            method: HTTP method
            status_code: Response status code
            response_time: Response time in seconds
        """
        message = f"API {method} {endpoint} - Status: {status_code}"
        if response_time:
            message += f" - Response time: {response_time:.3f}s"
        
        if status_code >= 500:
            self.error(message)
        elif status_code >= 400:
            self.warning(message)
        else:
            self.info(message)
    
    def log_scraping_attempt(self, platform: str, target: str, success: bool, error: Optional[str] = None):
        """
        Log scraping attempt
        
        Args:
            platform: Platform being scraped
            target: Target being scraped
            success: Whether scraping was successful
            error: Error message if failed
        """
        message = f"Scraping {platform} - Target: {target} - Success: {success}"
        if error:
            message += f" - Error: {error}"
        
        if success:
            self.info(message)
        else:
            self.error(message)
    
    def log_analysis_result(self, analysis_type: str, input_size: int, processing_time: float, success: bool):
        """
        Log analysis result
        
        Args:
            analysis_type: Type of analysis performed
            input_size: Size of input data
            processing_time: Processing time in seconds
            success: Whether analysis was successful
        """
        message = f"Analysis {analysis_type} - Input size: {input_size} - Processing time: {processing_time:.3f}s - Success: {success}"
        
        if success:
            self.info(message)
        else:
            self.error(message)
    
    def close(self):
        """Close logger and cleanup"""
        if self.logger:
            self.logger.removeHandler(self.file_handler)
            self.logger.removeHandler(self.console_handler)
            self.file_handler.close()
            self.console_handler.close()


# Global logger instance
logger = CustomLogger()


def get_logger(name: Optional[str] = None) -> CustomLogger:
    """
    Get logger instance
    
    Args:
        name: Logger name (optional)
        
    Returns:
        CustomLogger instance
    """
    if name:
        return CustomLogger(name)
    return logger