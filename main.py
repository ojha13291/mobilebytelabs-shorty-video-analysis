"""
Main entry point for the video sentiment analysis application
"""

import argparse
import sys
from pathlib import Path

# Add the current directory to Python path for imports
sys.path.insert(0, str(Path(__file__).parent))

from api.app import create_app
from utils.logger import get_logger
from utils.config import get_config, load_config


def create_sample_config():
    """Create a sample configuration file"""
    from utils.config import ConfigManager
    
    config_manager = ConfigManager()
    config_manager.save_config("config.json")
    print("Sample configuration file created: config.json")
    print("Please update the configuration with your API keys and settings.")


def run_api_server(host=None, port=None, debug=None):
    """
    Run the API server
    
    Args:
        host: Host to bind to
        port: Port to bind to
        debug: Enable debug mode
    """
    logger = get_logger("main")
    
    try:
        # Load configuration
        config = get_config()
        
        # Override config with command line arguments
        if host:
            config.api.host = host
        if port:
            config.api.port = port
        if debug is not None:
            config.api.debug = debug
        
        # Validate configuration
        validation_result = load_config().validate_config()
        if not validation_result['is_valid']:
            logger.error("Configuration validation failed:")
            for error in validation_result['errors']:
                logger.error(f"  - {error}")
            return False
        
        # Create and run the app
        app = create_app()
        
        logger.info(f"Starting API server on {config.api.host}:{config.api.port}")
        logger.info(f"Debug mode: {config.api.debug}")
        
        app.run(
            host=config.api.host,
            port=config.api.port,
            debug=config.api.debug,
            threaded=True
        )
        
        return True
        
    except Exception as e:
        logger.error(f"Failed to start API server: {e}")
        return False


def run_analysis(url, platform=None):
    """
    Run analysis on a single URL
    
    Args:
        url: URL to analyze
        platform: Platform to analyze (optional)
    """
    logger = get_logger("main")
    
    try:
        from resolver.platform_resolver import PlatformResolver
        from analyzer.video_analyzer import VideoAnalyzer
        from api.dependencies import get_embedder, get_mistral_config
        
        # Initialize components
        resolver = PlatformResolver()
        analyzer = VideoAnalyzer()
        
        # Detect platform
        platform_name = resolver.detect_platform(url)
        logger.info(f"Detected platform: {platform_name}")
        
        # Create reel data dictionary
        reel_data = {
            'url': url,
            'platform': platform_name,
            'description': 'Sample description for analysis',
            'hashtags': ['#sample', '#test'],
            'likes': 100,
            'comments': 10,
            'shares': 5,
            'views': 1000
        }
        
        # Analyze content
        result = analyzer.analyze_single_reel(reel_data)
        
        # Print results
        print("\n=== Analysis Results ===")
        print(f"URL: {url}")
        print(f"Platform: {platform_name}")
        print(f"Engagement Score: {result.get('engagement_score', 'N/A')}")
        print(f"Sentiment: {result.get('sentiment', 'N/A')}")
        print(f"Content Quality: {result.get('content_quality', 'N/A')}")
        print(f"Recommendations: {result.get('recommendations', 'N/A')}")
        
        return result
        
    except Exception as e:
        logger.error(f"Analysis failed: {e}")
        return None


def main():
    """Main function"""
    parser = argparse.ArgumentParser(
        description="Video Sentiment Analysis Application",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run API server
  python main.py api
  
  # Run API server with custom host and port
  python main.py api --host 127.0.0.1 --port 8080
  
  # Create sample configuration
  python main.py config
  
  # Analyze a single URL
  python main.py analyze https://www.instagram.com/p/ABC123DEF/
  
  # Analyze with specific platform
  python main.py analyze https://example.com/video --platform instagram
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # API server command
    api_parser = subparsers.add_parser('api', help='Run API server')
    api_parser.add_argument('--host', type=str, help='Host to bind to')
    api_parser.add_argument('--port', type=int, help='Port to bind to')
    api_parser.add_argument('--debug', action='store_true', help='Enable debug mode')
    
    # Config command
    config_parser = subparsers.add_parser('config', help='Create sample configuration')
    
    # Analyze command
    analyze_parser = subparsers.add_parser('analyze', help='Analyze a single URL')
    analyze_parser.add_argument('url', type=str, help='URL to analyze')
    analyze_parser.add_argument('--platform', type=str, help='Platform to analyze')
    
    # Parse arguments
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    # Execute command
    if args.command == 'api':
        success = run_api_server(args.host, args.port, args.debug)
        sys.exit(0 if success else 1)
    
    elif args.command == 'config':
        create_sample_config()
    
    elif args.command == 'analyze':
        result = run_analysis(args.url, args.platform)
        sys.exit(0 if result else 1)
    
    else:
        parser.print_help()


if __name__ == '__main__':
    main()