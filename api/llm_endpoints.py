"""
API endpoints for LLM video processing
"""

import logging
from flask import Blueprint, request, jsonify
from flask_cors import cross_origin
from typing import Dict, Any, Optional

from llm_processor.processor import LLMProcessor
from llm_processor.database import DatabaseManager

logger = logging.getLogger(__name__)

# Create blueprint for LLM endpoints
llm_bp = Blueprint('llm', __name__)

# Initialize processor and database manager
processor = LLMProcessor()
db_manager = DatabaseManager()


@llm_bp.route('/health', methods=['GET'])
@cross_origin()
def health_check():
    """
    Health check endpoint for LLM processor
    
    Returns:
        JSON response with health status
    """
    try:
        # Check database connection
        db_status = db_manager.check_connection()
        
        # Check LLM client availability
        llm_status = processor.llm_client.is_available()
        
        health_data = {
            'status': 'healthy' if db_status and llm_status else 'degraded',
            'database': 'connected' if db_status else 'disconnected',
            'llm_service': 'available' if llm_status else 'unavailable',
            'service': 'llm_processor'
        }
        
        status_code = 200 if db_status and llm_status else 503
        return jsonify(health_data), status_code
        
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return jsonify({
            'status': 'error',
            'error': str(e),
            'service': 'llm_processor'
        }), 500


@llm_bp.route('/process', methods=['POST'])
@cross_origin()
def process_video():
    """
    Process a video through LLM analysis
    
    Request Body:
        {
            "video_id": "string",      // Required: Unique video identifier
            "video_url": "string",     // Required: Video URL
            "platform": "string",       // Optional: Platform (auto-detected if not provided)
            "force_reprocess": boolean  // Optional: Force reprocessing (default: false)
        }
    
    Returns:
        {
            "success": boolean,
            "message": "string",
            "data": {                   // Analysis results
                "video_id": "string",
                "summary": "string",
                "topics": ["string"],
                "sentiment": "positive|neutral|negative",
                "confidence_score": number,
                "processed_at": "ISO timestamp"
            },
            "cached": boolean          // True if result was retrieved from cache
        }
    """
    try:
        # Validate request data
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'error': 'No JSON data provided'
            }), 400
        
        # Required fields
        video_id = data.get('video_id')
        video_url = data.get('video_url')
        
        if not video_id or not video_url:
            return jsonify({
                'success': False,
                'error': 'Both video_id and video_url are required'
            }), 400
        
        # Optional fields
        platform = data.get('platform', 'auto')
        force_reprocess = data.get('force_reprocess', False)
        
        logger.info(f"Processing video: {video_id} from URL: {video_url}")
        
        # Process video
        result = processor.process_video(
            video_id=video_id,
            video_url=video_url,
            platform=platform,
            force_reprocess=force_reprocess
        )
        
        # Determine HTTP status code
        if result['success']:
            status_code = 200
        else:
            # Check if it's a client error (4xx) or server error (5xx)
            if 'No transcript available' in result['message']:
                status_code = 422  # Unprocessable Entity
            else:
                status_code = 500
        
        return jsonify(result), status_code
        
    except Exception as e:
        logger.error(f"Error processing video: {e}")
        return jsonify({
            'success': False,
            'error': f'Internal server error: {str(e)}'
        }), 500


@llm_bp.route('/analysis/<video_id>', methods=['GET'])
@cross_origin()
def get_analysis(video_id: str):
    """
    Get LLM analysis results for a specific video
    
    Args:
        video_id: Unique video identifier
    
    Returns:
        {
            "success": boolean,
            "data": {                   // Analysis results or null
                "video_id": "string",
                "summary": "string",
                "topics": ["string"],
                "sentiment": "positive|neutral|negative",
                "confidence_score": number,
                "processed_at": "ISO timestamp",
                "error_message": "string"   // Present if analysis failed
            }
        }
    """
    try:
        logger.info(f"Retrieving analysis for video: {video_id}")
        
        # Get analysis from database
        analysis = processor.get_analysis(video_id)
        
        if analysis:
            return jsonify({
                'success': True,
                'data': analysis
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': 'Analysis not found for this video_id',
                'data': None
            }), 404
            
    except Exception as e:
        logger.error(f"Error retrieving analysis for video {video_id}: {e}")
        return jsonify({
            'success': False,
            'error': f'Internal server error: {str(e)}'
        }), 500


@llm_bp.route('/analyses', methods=['GET'])
@cross_origin()
def list_analyses():
    """
    List LLM analyses with optional filtering
    
    Query Parameters:
        sentiment: Filter by sentiment (positive|neutral|negative)
        topic: Filter by topic (partial match)
        limit: Maximum number of results (default: 50, max: 200)
        offset: Number of results to skip (default: 0)
        
    Returns:
        {
            "success": boolean,
            "data": [
                {
                    "video_id": "string",
                    "summary": "string",
                    "topics": ["string"],
                    "sentiment": "string",
                    "confidence_score": number,
                    "processed_at": "ISO timestamp"
                }
            ],
            "pagination": {
                "total": number,
                "limit": number,
                "offset": number
            }
        }
    """
    try:
        # Parse query parameters
        sentiment = request.args.get('sentiment')
        topic = request.args.get('topic')
        limit = min(int(request.args.get('limit', 50)), 200)  # Max 200
        offset = int(request.args.get('offset', 0))
        
        logger.info(f"Listing analyses: sentiment={sentiment}, topic={topic}, limit={limit}, offset={offset}")
        
        # Query database
        analyses = db_manager.get_analyses_by_filter(
            sentiment=sentiment,
            topic=topic,
            limit=limit,
            offset=offset
        )
        
        # Convert to dict format
        analyses_data = [analysis.to_dict() for analysis in analyses]
        
        # Get total count for pagination
        total_count = db_manager.get_analyses_count(sentiment=sentiment, topic=topic)
        
        return jsonify({
            'success': True,
            'data': analyses_data,
            'pagination': {
                'total': total_count,
                'limit': limit,
                'offset': offset
            }
        }), 200
        
    except ValueError as e:
        return jsonify({
            'success': False,
            'error': f'Invalid parameter: {str(e)}'
        }), 400
    except Exception as e:
        logger.error(f"Error listing analyses: {e}")
        return jsonify({
            'success': False,
            'error': f'Internal server error: {str(e)}'
        }), 500


@llm_bp.route('/stats', methods=['GET'])
@cross_origin()
def get_stats():
    """
    Get LLM processing statistics
    
    Returns:
        {
            "success": boolean,
            "data": {
                "total_analyses": number,
                "successful_analyses": number,
                "failed_analyses": number,
                "average_confidence_score": number,
                "sentiment_distribution": {
                    "positive": number,
                    "neutral": number,
                    "negative": number
                },
                "top_topics": [
                    {"topic": "string", "count": number}
                ],
                "recent_analyses": number  // Last 24 hours
            }
        }
    """
    try:
        logger.info("Retrieving processing statistics")
        
        # Get statistics from processor
        stats = processor.get_processing_stats()
        
        return jsonify({
            'success': True,
            'data': stats
        }), 200
        
    except Exception as e:
        logger.error(f"Error retrieving statistics: {e}")
        return jsonify({
            'success': False,
            'error': f'Internal server error: {str(e)}'
        }), 500


@llm_bp.route('/reprocess/<video_id>', methods=['POST'])
@cross_origin()
def reprocess_video(video_id: str):
    """
    Force reprocessing of a video
    
    Args:
        video_id: Unique video identifier
    
    Request Body:
        {
            "video_url": "string",     // Required: Video URL
            "platform": "string"       // Optional: Platform (auto-detected if not provided)
        }
    
    Returns:
        {
            "success": boolean,
            "message": "string",
            "data": {                   // New analysis results
                "video_id": "string",
                "summary": "string",
                "topics": ["string"],
                "sentiment": "positive|neutral|negative",
                "confidence_score": number,
                "processed_at": "ISO timestamp"
            }
        }
    """
    try:
        # Validate request data
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'error': 'No JSON data provided'
            }), 400
        
        video_url = data.get('video_url')
        if not video_url:
            return jsonify({
                'success': False,
                'error': 'video_url is required'
            }), 400
        
        platform = data.get('platform', 'auto')
        
        logger.info(f"Force reprocessing video: {video_id}")
        
        # Force reprocess
        result = processor.reprocess_video(video_id, video_url, platform)
        
        # Determine HTTP status code
        status_code = 200 if result['success'] else 500
        
        return jsonify(result), status_code
        
    except Exception as e:
        logger.error(f"Error reprocessing video {video_id}: {e}")
        return jsonify({
            'success': False,
            'error': f'Internal server error: {str(e)}'
        }), 500


@llm_bp.route('/providers', methods=['GET'])
@cross_origin()
def get_providers():
    """
    Get available LLM providers and their status
    
    Returns:
        {
            "success": boolean,
            "data": [
                {
                    "name": "string",
                    "provider": "mistral|openrouter|ollama",
                    "available": boolean,
                    "model": "string",
                    "description": "string"
                }
            ]
        }
    """
    try:
        from llm_processor.llm_client import LLMProvider
        
        providers = []
        
        # Check each provider
        for provider in LLMProvider:
            client = processor.llm_client.get_client_for_provider(provider)
            available = client.check_availability() if client else False
            
            provider_info = {
                'name': provider.value.title(),
                'provider': provider.value,
                'available': available,
                'model': processor.llm_client.get_model_for_provider(provider),
                'description': get_provider_description(provider)
            }
            providers.append(provider_info)
        
        return jsonify({
            'success': True,
            'data': providers
        }), 200
        
    except Exception as e:
        logger.error(f"Error retrieving provider information: {e}")
        return jsonify({
            'success': False,
            'error': f'Internal server error: {str(e)}'
        }), 500


def get_provider_description(provider):
    """Get human-readable description for LLM provider"""
    descriptions = {
        'mistral': 'Mistral AI models via API',
        'openrouter': 'Multiple AI models via OpenRouter',
        'ollama': 'Local AI models via Ollama'
    }
    return descriptions.get(provider.value, 'AI language model provider')


@llm_bp.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({
        'success': False,
        'error': 'Endpoint not found'
    }), 404


@llm_bp.errorhandler(405)
def method_not_allowed(error):
    """Handle 405 errors"""
    return jsonify({
        'success': False,
        'error': 'Method not allowed'
    }), 405


@llm_bp.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    logger.error(f"Internal server error: {error}")
    return jsonify({
        'success': False,
        'error': 'Internal server error'
    }), 500