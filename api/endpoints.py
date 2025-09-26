"""
API endpoints for the social media analyzer
"""

from flask import Blueprint, request, jsonify
import time
import json
from datetime import datetime
from typing import Dict, List, Any

from api.dependencies import get_embedder, get_mistral_config, get_instagram_credentials
from api.schemas import HealthResponse, PlatformInfo
from resolver.platform_resolver import PlatformResolver, detect_platform, get_platform_info
from analyzer.video_analyzer import analyze_reels
from scrapers.instagram_scraper import InstagramScraper

api_bp = Blueprint('api', __name__)

# Initialize platform resolver
platform_resolver = PlatformResolver()


@api_bp.route('/health', methods=['GET'])
def health_check():
    """
    Health check endpoint to verify API status
    
    Returns:
        JSON response with health status
    """
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'version': '1.0.0',
        'services': {
            'api': 'running',
            'embedding': 'available' if get_embedder() else 'unavailable',
            'mistral': 'configured' if get_mistral_config()['api_key'] else 'not_configured'
        }
    })


@api_bp.route('/platforms', methods=['GET'])
def get_supported_platforms():
    """
    Get list of supported social media platforms
    
    Returns:
        JSON response with supported platforms
    """
    platforms = platform_resolver.get_supported_platforms()
    return jsonify({
        'platforms': platforms,
        'count': len(platforms)
    })


@api_bp.route('/detect-platform', methods=['POST'])
def detect_platform_endpoint():
    """
    Detect social media platform from URL
    
    Returns:
        JSON response with platform detection results
    """
    try:
        data = request.get_json()
        if not data or 'url' not in data:
            return jsonify({'error': 'URL is required'}), 400
        
        url = data['url']
        platform_info = get_platform_info(url)
        
        return jsonify(platform_info)
    
    except Exception as e:
        return jsonify({
            'error': f'Error detecting platform: {str(e)}',
            'platform': 'unknown',
            'confidence': 0.0
        }), 500


@api_bp.route('/detect-platform/batch', methods=['POST'])
def detect_platform_batch_endpoint():
    """
    Detect platforms from multiple URLs
    
    Returns:
        JSON response with batch platform detection results
    """
    try:
        data = request.get_json()
        if not data or 'urls' not in data:
            return jsonify({'error': 'URLs array is required'}), 400
        
        urls = data['urls']
        if not isinstance(urls, list) or len(urls) == 0:
            return jsonify({'error': 'URLs must be a non-empty array'}), 400
        
        results = []
        for url in urls:
            try:
                platform_info = get_platform_info(url)
                results.append({
                    'url': url,
                    'platform': platform_info['platform'],
                    'confidence': platform_info['confidence'],
                    'details': platform_info.get('details', {})
                })
            except Exception as e:
                results.append({
                    'url': url,
                    'platform': 'unknown',
                    'confidence': 0.0,
                    'error': str(e)
                })
        
        return jsonify({
            'results': results,
            'total': len(results),
            'successful': len([r for r in results if r['platform'] != 'unknown'])
        })
    
    except Exception as e:
        return jsonify({
            'error': f'Error in batch platform detection: {str(e)}'
        }), 500


@api_bp.route('/analyze', methods=['POST'])
def analyze_reels():
    """
    Analyze social media reels/posts
    
    Returns:
        JSON response with analysis results
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Request body is required'}), 400
        
        # Extract parameters
        target = data.get('target', '')
        platform = data.get('platform', 'auto').lower()
        max_reels = data.get('max_reels', 10)
        analysis_type = data.get('analysis_type', 'comprehensive')
        
        if not target:
            return jsonify({'error': 'Target (username, hashtag, or URL) is required'}), 400
        
        # Auto-detect platform if needed
        if platform == 'auto':
            platform = detect_platform(target)
        
        # Validate platform
        supported_platforms = platform_resolver.get_supported_platforms()
        if platform not in supported_platforms:
            return jsonify({
                'error': f'Unsupported platform: {platform}. Supported: {supported_platforms}'
            }), 400
        
        # Scrape data based on platform
        scraper = None
        if platform == 'instagram':
            scraper = InstagramScraper()
            reels_data = scraper.scrape_reels(target, max_reels)
        else:
            return jsonify({
                'error': f'Analysis for {platform} is not yet implemented'
            }), 501
        
        if not reels_data:
            return jsonify({
                'error': 'No data could be scraped. Check if the target exists and is public.',
                'target': target,
                'platform': platform
            }), 404
        
        # Analyze the scraped data
        analyzer = VideoAnalyzer()
        analysis_results = analyzer.analyze_reels_batch(reels_data, analysis_type)
        
        return jsonify({
            'target': target,
            'platform': platform,
            'max_reels': max_reels,
            'analysis_type': analysis_type,
            'total_reels': len(reels_data),
            'reels_data': reels_data,
            'analysis_results': analysis_results,
            'timestamp': datetime.now().isoformat()
        })
    
    except Exception as e:
        return jsonify({
            'error': f'Error analyzing reels: {str(e)}',
            'target': data.get('target', 'unknown') if data else 'unknown',
            'platform': data.get('platform', 'unknown') if data else 'unknown'
        }), 500