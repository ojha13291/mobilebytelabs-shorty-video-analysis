#!/usr/bin/env python3
"""
Integrated Streamlit Launcher for Video Sentiment Analysis System
Connects all project components: API, LLM Processor, Scrapers, Resolver, and Analyzer
"""

import os
import sys
import subprocess
import argparse
import time
import json
import requests
from pathlib import Path
from typing import Dict, Any, Optional
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class IntegratedSystemLauncher:
    """Integrated launcher for the complete video sentiment analysis system"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.api_process = None
        self.streamlit_process = None
        self.required_components = {
            'api': self.check_api_integrity,
            'scrapers': self.check_scrapers_integrity,
            'llm_processor': self.check_llm_integrity,
            'analyzer': self.check_analyzer_integrity,
            'resolver': self.check_resolver_integrity
        }
    
    def check_api_integrity(self) -> bool:
        """Check if API components are properly configured"""
        api_files = ['api/app.py', 'api/endpoints.py', 'api/models.py', 'api/schemas.py', 'api/dependencies.py']
        for file in api_files:
            if not (self.project_root / file).exists():
                logger.error(f"Missing API file: {file}")
                return False
        
        # Check if API can be imported
        try:
            sys.path.insert(0, str(self.project_root))
            from api.app import app
            from api.endpoints import api_bp
            from api.llm_processor import LLMProcessor
            logger.info("✅ API components imported successfully")
            return True
        except Exception as e:
            logger.error(f"❌ API import error: {e}")
            return False
    
    def check_scrapers_integrity(self) -> bool:
        """Check if scrapers are properly configured"""
        scraper_files = [
            'scrapers/__init__.py',
            'scrapers/base_scraper.py',
            'scrapers/selenium_scraper.py',
            'scrapers/youtube_selenium_scraper.py',
            'scrapers/instagram_selenium_scraper.py'
        ]
        for file in scraper_files:
            if not (self.project_root / file).exists():
                logger.error(f"Missing scraper file: {file}")
                return False
        
        try:
            from scrapers.youtube_selenium_scraper import YouTubeSeleniumScraper
            from scrapers.instagram_selenium_scraper import InstagramSeleniumScraper
            logger.info("✅ Scrapers imported successfully")
            return True
        except Exception as e:
            logger.error(f"❌ Scraper import error: {e}")
            return False
    
    def check_llm_integrity(self) -> bool:
        """Check if LLM processor is properly configured"""
        try:
            from api.llm_processor import LLMProcessor
            # Check if environment variables are set
            providers = ['mistral', 'openrouter', 'ollama']
            provider_configured = False
            
            for provider in providers:
                if provider == 'mistral' and os.getenv('MISTRAL_API_KEY'):
                    provider_configured = True
                    break
                elif provider == 'openrouter' and os.getenv('OPENROUTER_API_KEY'):
                    provider_configured = True
                    break
                elif provider == 'ollama' and os.getenv('OLLAMA_API_URL'):
                    provider_configured = True
                    break
            
            if not provider_configured:
                logger.warning("⚠️  No LLM provider API keys configured")
                logger.info("Available providers: mistral, openrouter, ollama")
                logger.info("Please configure your .env file with appropriate API keys")
            
            logger.info("✅ LLM processor imported successfully")
            return True
        except Exception as e:
            logger.error(f"❌ LLM processor error: {e}")
            return False
    
    def check_analyzer_integrity(self) -> bool:
        """Check if analyzer is properly configured"""
        try:
            from analyzer.video_analyzer import VideoAnalyzer
            logger.info("✅ Video analyzer imported successfully")
            return True
        except Exception as e:
            logger.error(f"❌ Video analyzer error: {e}")
            return False
    
    def check_resolver_integrity(self) -> bool:
        """Check if platform resolver is properly configured"""
        try:
            from resolver.platform_resolver import PlatformResolver
            logger.info("✅ Platform resolver imported successfully")
            return True
        except Exception as e:
            logger.error(f"❌ Platform resolver error: {e}")
            return False
    
    def check_environment_config(self) -> Dict[str, Any]:
        """Check environment configuration"""
        config_status = {}
        
        # Check .env file
        env_file = self.project_root / '.env'
        env_example = self.project_root / '.env.example'
        
        if not env_file.exists():
            if env_example.exists():
                logger.warning("⚠️  .env file not found, but .env.example exists")
                logger.info("Please copy .env.example to .env and configure your API keys")
                config_status['env_file'] = False
            else:
                logger.error("❌ No .env file found")
                config_status['env_file'] = False
        else:
            config_status['env_file'] = True
        
        # Check critical environment variables
        critical_vars = [
            'SERVICE_PORT', 'DATABASE_URL', 'LLM_PROVIDER',
            'MISTRAL_API_KEY', 'OPENROUTER_API_KEY', 'OLLAMA_API_URL'
        ]
        
        for var in critical_vars:
            value = os.getenv(var)
            if value:
                config_status[var] = True
                logger.info(f"✅ {var}: {'*' * 8 if 'KEY' in var else value}")
            else:
                config_status[var] = False
                logger.warning(f"⚠️  {var} not configured")
        
        return config_status
    
    def check_api_server_status(self, host: str = "localhost", port: int = 5001) -> bool:
        """Check if API server is running and accessible"""
        try:
            response = requests.get(f"http://{host}:{port}/api/health", timeout=5)
            if response.status_code == 200:
                data = response.json()
                logger.info(f"✅ API server is running - Status: {data.get('status', 'unknown')}")
                return True
            else:
                logger.warning(f"⚠️  API server returned status {response.status_code}")
                return False
        except requests.exceptions.ConnectionError:
            logger.info("❌ API server is not running")
            return False
        except Exception as e:
            logger.error(f"❌ Error checking API server: {e}")
            return False
    
    def start_api_server(self, host: str = "0.0.0.0", port: int = 5001, debug: bool = False) -> bool:
        """Start the API server"""
        logger.info(f"🚀 Starting API server on {host}:{port}")
        
        try:
            # Set environment variables
            env = os.environ.copy()
            env['SERVICE_HOST'] = host
            env['SERVICE_PORT'] = str(port)
            env['DEBUG'] = str(debug).lower()
            
            # Start API server
            cmd = [sys.executable, "api/app.py"]
            
            self.api_process = subprocess.Popen(
                cmd,
                env=env,
                cwd=str(self.project_root),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            
            # Wait a moment for server to start
            time.sleep(3)
            
            # Check if API is running
            if self.check_api_server_status(host, port):
                logger.info("✅ API server started successfully")
                return True
            else:
                logger.error("❌ Failed to start API server")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error starting API server: {e}")
            return False
    
    def start_integrated_streamlit(self, host: str = "localhost", port: int = 8501, debug: bool = False) -> bool:
        """Start the integrated Streamlit application"""
        logger.info(f"🚀 Starting integrated Streamlit app on {host}:{port}")
        
        try:
            # Set environment variables
            env = os.environ.copy()
            env['STREAMLIT_SERVER_HEADLESS'] = 'true'
            env['STREAMLIT_SERVER_PORT'] = str(port)
            env['STREAMLIT_SERVER_ADDRESS'] = host
            
            if debug:
                env['STREAMLIT_GLOBAL_LOG_LEVEL'] = 'debug'
            
            # Use the integrated streamlit app
            cmd = [
                sys.executable, "-m", "streamlit",
                "run", "integrated_streamlit_app.py",
                "--server.port", str(port),
                "--server.address", host,
                "--theme.base", "light",
                "--theme.primaryColor", "#667eea",
                "--theme.backgroundColor", "#ffffff",
                "--theme.secondaryBackgroundColor", "#f8f9fa",
                "--theme.textColor", "#262730"
            ]
            
            self.streamlit_process = subprocess.Popen(
                cmd,
                env=env,
                cwd=str(self.project_root),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            
            # Wait a moment for app to start
            time.sleep(5)
            
            logger.info("✅ Integrated Streamlit app started successfully")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error starting Streamlit app: {e}")
            return False
    
    def setup_instagram_login(self) -> bool:
        """Setup Instagram login configuration"""
        logger.info("🔐 Setting up Instagram login configuration")
        
        instagram_username = os.getenv('INSTAGRAM_USERNAME')
        instagram_password = os.getenv('INSTAGRAM_PASSWORD')
        instagram_use_login = os.getenv('INSTAGRAM_USE_LOGIN', 'false').lower() == 'true'
        
        if instagram_use_login and instagram_username and instagram_password:
            logger.info(f"✅ Instagram login configured for user: {instagram_username}")
            logger.info("ℹ️  Instagram login will be available in the UI")
            return True
        else:
            logger.warning("⚠️  Instagram login not fully configured")
            logger.info("Set INSTAGRAM_USERNAME, INSTAGRAM_PASSWORD, and INSTAGRAM_USE_LOGIN=true in .env")
            return False
    
    def run_complete_system(self, api_host: str = "0.0.0.0", api_port: int = 5001, 
                          streamlit_host: str = "localhost", streamlit_port: int = 8501,
                          start_api: bool = True, debug: bool = False) -> bool:
        """Run the complete integrated system"""
        
        logger.info("🚀 Starting Complete Video Sentiment Analysis System")
        logger.info("=" * 60)
        
        # Check system integrity
        logger.info("🔍 Checking system integrity...")
        all_integrity_passed = True
        for component_name, check_func in self.required_components.items():
            logger.info(f"Checking {component_name}...")
            if not check_func():
                all_integrity_passed = False
        
        if not all_integrity_passed:
            logger.error("❌ System integrity check failed")
            return False
        
        # Check environment configuration
        logger.info("\n🔍 Checking environment configuration...")
        env_status = self.check_environment_config()
        
        # Setup Instagram login
        self.setup_instagram_login()
        
        # Start API server if requested
        if start_api:
            logger.info("\n🔍 Checking API server status...")
            if not self.check_api_server_status(api_host, api_port):
                logger.info("🚀 Starting API server...")
                if not self.start_api_server(api_host, api_port, debug):
                    logger.error("❌ Failed to start API server")
                    return False
            else:
                logger.info("✅ API server already running")
        
        # Start Streamlit app
        logger.info("\n🚀 Starting integrated Streamlit application...")
        if not self.start_integrated_streamlit(streamlit_host, streamlit_port, debug):
            logger.error("❌ Failed to start Streamlit app")
            return False
        
        # System summary
        logger.info("\n" + "=" * 60)
        logger.info("✅ System started successfully!")
        logger.info(f"🌐 API Server: http://{api_host}:{api_port}")
        logger.info(f"🌐 Streamlit App: http://{streamlit_host}:{streamlit_port}")
        logger.info("\n📋 Available endpoints:")
        logger.info(f"   • API Health: http://{api_host}:{api_port}/api/health")
        logger.info(f"   • API Docs: http://{api_host}:{api_port}/api/docs")
        logger.info(f"   • Streamlit App: http://{streamlit_host}:{streamlit_port}")
        
        if env_status.get('INSTAGRAM_USE_LOGIN'):
            logger.info("\n🔐 Instagram login is configured and available")
        
        logger.info("\n📝 Press Ctrl+C to stop the system")
        logger.info("=" * 60)
        
        return True
    
    def cleanup(self):
        """Cleanup running processes"""
        logger.info("\n🧹 Cleaning up...")
        
        if self.api_process:
            logger.info("Stopping API server...")
            self.api_process.terminate()
            self.api_process.wait(timeout=5)
        
        if self.streamlit_process:
            logger.info("Stopping Streamlit app...")
            self.streamlit_process.terminate()
            self.streamlit_process.wait(timeout=5)
        
        logger.info("✅ Cleanup completed")

def main():
    """Main function"""
    parser = argparse.ArgumentParser(
        description="Integrated Video Sentiment Analysis System Launcher",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python run_streamlit.py                    # Start complete system
  python run_streamlit.py --no-api          # Start only Streamlit app
  python run_streamlit.py --debug           # Start with debug mode
  python run_streamlit.py --api-port 6000   # Use custom API port
n        """
    )
    
    parser.add_argument("--api-host", default="0.0.0.0", help="API server host (default: 0.0.0.0)")
    parser.add_argument("--api-port", type=int, default=5001, help="API server port (default: 5001)")
    parser.add_argument("--streamlit-host", default="localhost", help="Streamlit app host (default: localhost)")
    parser.add_argument("--streamlit-port", type=int, default=8501, help="Streamlit app port (default: 8501)")
    parser.add_argument("--no-api", action="store_true", help="Don't start API server (assume it's already running)")
    parser.add_argument("--debug", action="store_true", help="Enable debug mode")
    parser.add_argument("--check-only", action="store_true", help="Only check system integrity without starting")
    
    args = parser.parse_args()
    
    # Create launcher
    launcher = IntegratedSystemLauncher()
    
    try:
        if args.check_only:
            logger.info("🔍 Running system integrity check only...")
            all_integrity_passed = True
            for component_name, check_func in launcher.required_components.items():
                logger.info(f"Checking {component_name}...")
                if not check_func():
                    all_integrity_passed = False
            
            env_status = launcher.check_environment_config()
            launcher.setup_instagram_login()
            
            if all_integrity_passed:
                logger.info("✅ All system integrity checks passed")
            else:
                logger.error("❌ Some system integrity checks failed")
                sys.exit(1)
        else:
            # Run complete system
            success = launcher.run_complete_system(
                api_host=args.api_host,
                api_port=args.api_port,
                streamlit_host=args.streamlit_host,
                streamlit_port=args.streamlit_port,
                start_api=not args.no_api,
                debug=args.debug
            )
            
            if success:
                # Keep the main thread alive
                try:
                    while True:
                        time.sleep(1)
                except KeyboardInterrupt:
                    logger.info("\n👋 Shutting down system...")
                    launcher.cleanup()
            else:
                sys.exit(1)
    
    except Exception as e:
        logger.error(f"❌ Unexpected error: {e}")
        launcher.cleanup()
        sys.exit(1)

if __name__ == "__main__":
    main()