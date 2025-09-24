"""
Main API service for Instagram Reels Microservice
Provides REST API endpoints for reel analysis
"""
import logging
import time
from datetime import datetime
from typing import Dict, Any, Optional
from flask import Flask, request, jsonify
from flask_cors import CORS

from ..models import ScrapingRequest, ScrapingResponse, HealthStatus, ServiceMetrics
from ..config import config
from .scraper import InstagramScraper
from .analyzer import AIAnalyzer

logger = logging.getLogger(__name__)

class InstagramReelsService:
    """Main service class for Instagram Reels Microservice"""
    
    def __init__(self):
        self.app = Flask(__name__)
        CORS(self.app)
        
        self.scraper = InstagramScraper()
        self.analyzer = AIAnalyzer()
        
        self.metrics = ServiceMetrics()
        self.start_time = datetime.now()
        
        self._setup_routes()
    
    def _setup_routes(self):
        """Setup Flask routes"""
        
        @self.app.route('/health', methods=['GET'])
        def health_check():
            """Health check endpoint"""
            return self._handle_health_check()
        
        @self.app.route('/api/analyze', methods=['POST'])
        def analyze_reels():
            """Main analysis endpoint"""
            return self._handle_analyze_reels()
        
        @self.app.route('/api/metrics', methods=['GET'])
        def get_metrics():
            """Service metrics endpoint"""
            return self._handle_metrics()
        
        @self.app.route('/api/config', methods=['GET'])
        def get_config():
            """Configuration endpoint"""
            return self._handle_config()
        
        @self.app.errorhandler(404)
        def not_found(error):
            return jsonify({'error': 'Endpoint not found'}), 404
        
        @self.app.errorhandler(500)
        def internal_error(error):
            logger.error(f"Internal server error: {error}")
            return jsonify({'error': 'Internal server error'}), 500
    
    def _handle_health_check(self) -> tuple:
        """Handle health check request"""
        try:
            uptime = (datetime.now() - self.start_time).total_seconds()
            
            # Check service health
            services_status = {
                'api': 'healthy',
                'scraper': 'healthy' if self.scraper else 'unhealthy',
                'analyzer': 'healthy' if self.analyzer.embedder else 'unhealthy'
            }
            
            health_status = HealthStatus(
                status='healthy',
                version='1.0.0',
                timestamp=datetime.now(),
                services=services_status,
                uptime=uptime
            )
            
            return jsonify(health_status.__dict__), 200
            
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            error_status = HealthStatus(
                status='unhealthy',
                version='1.0.0',
                timestamp=datetime.now(),
                services={'api': 'unhealthy'}
            )
            return jsonify(error_status.__dict__), 500
    
    def _handle_analyze_reels(self) -> tuple:
        """Handle reel analysis request"""
        start_time = time.time()
        self.metrics.total_requests += 1
        self.metrics.last_request_time = datetime.now()
        
        try:
            # Parse request data
            data = request.get_json()
            if not data:
                return jsonify({'error': 'No JSON data provided'}), 400
            
            # Validate required fields
            target = data.get('target')
            if not target:
                return jsonify({'error': 'target field is required'}), 400
            
            # Create scraping request
            scraping_request = ScrapingRequest(
                target=target,
                max_reels=data.get('max_reels', config.service.max_reels_default),
                use_login=data.get('use_login', config.instagram.use_login),
                scraping_method=data.get('scraping_method', 'instaloader'),
                include_comments=data.get('include_comments', True),
                include_analysis=data.get('include_analysis', True)
            )
            
            logger.info(f"Processing analysis request for target: {target}")
            
            # Scrape reels
            reels = self.scraper.scrape_reels(scraping_request)
            
            if not reels:
                return jsonify({
                    'status': 'success',
                    'count': 0,
                    'results': [],
                    'message': 'No reels found for the given target'
                }), 200
            
            # Perform AI analysis if requested
            if scraping_request.include_analysis:
                reels = self.analyzer.analyze_batch(reels)
            
            # Convert to response format
            processing_time = time.time() - start_time
            
            response = ScrapingResponse(
                status='success',
                count=len(reels),
                results=reels,
                processing_time=processing_time
            )
            
            # Update metrics
            self.metrics.successful_requests += 1
            if self.metrics.average_processing_time == 0:
                self.metrics.average_processing_time = processing_time
            else:
                self.metrics.average_processing_time = (
                    (self.metrics.average_processing_time + processing_time) / 2
                )
            
            # Convert to JSON-serializable format
            response_dict = self._serialize_response(response)
            
            logger.info(f"Successfully processed {len(reels)} reels in {processing_time:.2f}s")
            return jsonify(response_dict), 200
            
        except ValueError as e:
            logger.error(f"Validation error: {e}")
            self.metrics.failed_requests += 1
            return jsonify({'error': str(e)}), 400
            
        except Exception as e:
            logger.error(f"Analysis failed: {e}")
            self.metrics.failed_requests += 1
            return jsonify({'error': 'Internal server error'}), 500
    
    def _handle_metrics(self) -> tuple:
        """Handle metrics request"""
        try:
            uptime = (datetime.now() - self.start_time).total_seconds()
            
            metrics_dict = {
                'total_requests': self.metrics.total_requests,
                'successful_requests': self.metrics.successful_requests,
                'failed_requests': self.metrics.failed_requests,
                'average_processing_time': round(self.metrics.average_processing_time, 2),
                'last_request_time': self.metrics.last_request_time.isoformat() if self.metrics.last_request_time else None,
                'uptime_seconds': round(uptime, 2),
                'success_rate': round(
                    (self.metrics.successful_requests / max(self.metrics.total_requests, 1)) * 100, 2
                )
            }
            
            return jsonify(metrics_dict), 200
            
        except Exception as e:
            logger.error(f"Metrics request failed: {e}")
            return jsonify({'error': 'Failed to retrieve metrics'}), 500
    
    def _handle_config(self) -> tuple:
        """Handle configuration request"""
        try:
            config_dict = config.to_dict()
            return jsonify(config_dict), 200
            
        except Exception as e:
            logger.error(f"Config request failed: {e}")
            return jsonify({'error': 'Failed to retrieve configuration'}), 500
    
    def _serialize_response(self, response: ScrapingResponse) -> Dict[str, Any]:
        """Convert response to JSON-serializable format"""
        def serialize_reel(reel: ReelData) -> Dict[str, Any]:
            return {
                'reel_id': reel.reel_id,
                'reel_url': reel.reel_url,
                'video_url': reel.video_url,
                'caption': reel.caption,
                'creator': {
                    'username': reel.creator.username,
                    'profile_url': reel.creator.profile_url,
                    'full_name': reel.creator.full_name,
                    'followers_count': reel.creator.followers_count,
                    'following_count': reel.creator.following_count
                },
                'likes': reel.likes,
                'views': reel.views,
                'comments_count': reel.comments_count,
                'posted_at': reel.posted_at.isoformat() if reel.posted_at else None,
                'hashtags': reel.hashtags,
                'mentions': reel.mentions,
                'top_comments': [
                    {
                        'user': comment.user,
                        'comment': comment.comment,
                        'timestamp': comment.timestamp.isoformat() if comment.timestamp else None,
                        'likes': comment.likes
                    }
                    for comment in reel.top_comments
                ],
                'analysis': {
                    'summary': reel.analysis.summary if reel.analysis else None,
                    'category': reel.analysis.category if reel.analysis else None,
                    'sentiment': reel.analysis.sentiment if reel.analysis else None,
                    'top_comment_summary': reel.analysis.top_comment_summary if reel.analysis else None,
                    'keywords': reel.analysis.keywords if reel.analysis else None
                } if reel.analysis else None,
                'embeddings': reel.embeddings
            }
        
        return {
            'status': response.status,
            'count': response.count,
            'results': [serialize_reel(reel) for reel in response.results],
            'errors': response.errors,
            'processing_time': response.processing_time
        }
    
    def run(self):
        """Run the Flask application"""
        try:
            config.validate_config()
            logger.info("Starting Instagram Reels Microservice")
            logger.info(f"Service running on {config.service.host}:{config.service.port}")
            
            self.app.run(
                host=config.service.host,
                port=config.service.port,
                debug=config.service.debug
            )
            
        except ValueError as e:
            logger.error(f"Configuration error: {e}")
            raise
        except Exception as e:
            logger.error(f"Failed to start service: {e}")
            raise

# Create global service instance
service = InstagramReelsService()

def create_app():
    """Factory function for creating the Flask app"""
    return service.app

def run_service():
    """Run the service"""
    service.run()

if __name__ == '__main__':
    run_service()