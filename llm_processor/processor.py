"""
Main LLM Processor for video content analysis
"""

import os
import time
import logging
from datetime import datetime
from typing import Dict, Any, Optional, List
import json
import re

from .database import DatabaseManager
from .llm_client import LLMClient, LLMProvider
from .transcript_extractor import TranscriptExtractor

logger = logging.getLogger(__name__)


class LLMProcessor:
    """Main processor for video content analysis using LLMs"""
    
    def __init__(self, 
                 database_manager: Optional[DatabaseManager] = None,
                 llm_client: Optional[LLMClient] = None,
                 transcript_extractor: Optional[TranscriptExtractor] = None):
        """
        Initialize LLM processor
        
        Args:
            database_manager: Database manager instance
            llm_client: LLM client instance
            transcript_extractor: Transcript extractor instance
        """
        self.db_manager = database_manager or DatabaseManager()
        self.llm_client = llm_client or LLMClient()
        self.transcript_extractor = transcript_extractor or TranscriptExtractor()
        
        # Analysis prompts
        self.summary_prompt = """
        Please provide a concise summary of the following video content. 
        Focus on the main topics, key points, and overall message.
        Keep the summary under 200 words and make it informative.
        
        Content: {content}
        """
        
        self.topics_prompt = """
        Analyze the following video content and identify the main topics discussed.
        Return a JSON array of topic strings, limited to the 5 most relevant topics.
        Make topics specific and descriptive.
        
        Content: {content}
        
        Response format: ["topic1", "topic2", "topic3", "topic4", "topic5"]
        """
        
        self.sentiment_prompt = """
        Analyze the sentiment of the following video content.
        Classify it as one of: positive, neutral, or negative.
        Also provide a confidence score from 0-100.
        
        Content: {content}
        
        Response format: {{
            "sentiment": "positive|neutral|negative",
            "confidence": 85
        }}
        """
    
    def process_video(self, video_id: str, video_url: str, 
                     platform: str = 'auto', force_reprocess: bool = False) -> Dict[str, Any]:
        """
        Process a video through LLM analysis
        
        Args:
            video_id: Unique video identifier
            video_url: Video URL
            platform: Platform name (auto-detected if not provided)
            force_reprocess: Force reprocessing even if analysis exists
            
        Returns:
            Dictionary containing analysis results
        """
        start_time = time.time()
        logger.info(f"Starting LLM processing for video_id: {video_id}")
        
        try:
            # Check if analysis already exists (idempotency)
            if not force_reprocess and self.db_manager.analysis_exists(video_id):
                logger.info(f"Analysis already exists for video_id: {video_id}. Returning cached result.")
                existing_analysis = self.db_manager.get_analysis_by_video_id(video_id)
                return {
                    'success': True,
                    'message': 'Analysis retrieved from cache',
                    'data': existing_analysis.to_dict() if existing_analysis else None,
                    'cached': True
                }
            
            # Step 1: Extract transcript
            logger.info(f"Extracting transcript for video_id: {video_id}")
            transcript = self.transcript_extractor.extract_transcript(video_url, platform)
            
            if not transcript:
                logger.warning(f"No transcript available for video_id: {video_id}")
                return self._save_error_result(video_id, "No transcript available")
            
            # Step 2: Perform LLM analysis
            logger.info(f"Performing LLM analysis for video_id: {video_id}")
            analysis_results = self._perform_llm_analysis(transcript)
            
            if not analysis_results['success']:
                logger.error(f"LLM analysis failed for video_id: {video_id}")
                return self._save_error_result(video_id, analysis_results['error'])
            
            # Step 3: Save results to database
            processing_duration = int(time.time() - start_time)
            result_data = {
                'video_id': video_id,
                'summary': analysis_results['summary'],
                'topics': analysis_results['topics'],
                'sentiment': analysis_results['sentiment'],
                'confidence_score': analysis_results['confidence'],
                'llm_provider': self.llm_client.provider.value,
                'llm_model': analysis_results.get('model', 'unknown'),
                'processing_duration_seconds': processing_duration,
                'transcript_used': transcript[:1000],  # Store first 1000 chars
                'processing_metadata': {
                    'video_url': video_url,
                    'platform': platform,
                    'transcript_length': len(transcript),
                    'llm_usage': analysis_results.get('usage', {})
                }
            }
            
            saved_result = self.db_manager.save_analysis(result_data)
            
            if saved_result:
                logger.info(f"Successfully processed video_id: {video_id} in {processing_duration}s")
                return {
                    'success': True,
                    'message': 'Video processed successfully',
                    'data': saved_result.to_dict(),
                    'cached': False
                }
            else:
                logger.error(f"Failed to save analysis for video_id: {video_id}")
                return self._save_error_result(video_id, "Failed to save analysis results")
                
        except Exception as e:
            logger.error(f"Unexpected error processing video_id: {video_id}: {e}")
            return self._save_error_result(video_id, f"Unexpected error: {str(e)}")
    
    def _perform_llm_analysis(self, content: str) -> Dict[str, Any]:
        """
        Perform comprehensive LLM analysis on content
        
        Args:
            content: Text content to analyze
            
        Returns:
            Dictionary containing analysis results
        """
        try:
            results = {
                'success': False,
                'summary': None,
                'topics': [],
                'sentiment': 'neutral',
                'confidence': 0,
                'model': None,
                'usage': {},
                'error': None
            }
            
            # Generate summary
            summary_response = self.llm_client.generate_response(
                self.summary_prompt.format(content=content)
            )
            
            if summary_response['success']:
                results['summary'] = summary_response['response'].strip()
                results['model'] = summary_response.get('model')
                results['usage'] = summary_response.get('usage', {})
            else:
                results['error'] = f"Summary generation failed: {summary_response['error']}"
                return results
            
            # Extract topics
            topics_response = self.llm_client.generate_response(
                self.topics_prompt.format(content=content)
            )
            
            if topics_response['success']:
                try:
                    topics_text = topics_response['response'].strip()
                    # Try to parse JSON response
                    if topics_text.startswith('[') and topics_text.endswith(']'):
                        results['topics'] = json.loads(topics_text)
                    else:
                        # Fallback: extract topics from text
                        results['topics'] = self._extract_topics_from_text(topics_text)
                except json.JSONDecodeError:
                    # Fallback: extract topics from text
                    results['topics'] = self._extract_topics_from_text(topics_response['response'])
            else:
                logger.warning(f"Topic extraction failed: {topics_response['error']}")
                results['topics'] = []
            
            # Analyze sentiment
            sentiment_response = self.llm_client.generate_response(
                self.sentiment_prompt.format(content=content)
            )
            
            if sentiment_response['success']:
                try:
                    sentiment_data = json.loads(sentiment_response['response'].strip())
                    results['sentiment'] = sentiment_data.get('sentiment', 'neutral')
                    results['confidence'] = sentiment_data.get('confidence', 0)
                except (json.JSONDecodeError, KeyError):
                    # Fallback: extract sentiment from text
                    sentiment_data = self._extract_sentiment_from_text(sentiment_response['response'])
                    results['sentiment'] = sentiment_data['sentiment']
                    results['confidence'] = sentiment_data['confidence']
            else:
                logger.warning(f"Sentiment analysis failed: {sentiment_response['error']}")
                results['sentiment'] = 'neutral'
                results['confidence'] = 0
            
            results['success'] = True
            return results
            
        except Exception as e:
            logger.error(f"Error during LLM analysis: {e}")
            results['error'] = f"Analysis error: {str(e)}"
            return results
    
    def _extract_topics_from_text(self, text: str) -> List[str]:
        """Extract topics from free-form text response"""
        topics = []
        
        # Try to parse as JSON first
        text = text.strip()
        if text.startswith('[') and text.endswith(']'):
            try:
                topics = json.loads(text)
                if isinstance(topics, list):
                    return [str(topic).strip() for topic in topics[:5]]
            except json.JSONDecodeError:
                pass
        
        # Look for comma-separated topics
        if ',' in text:
            # Try to parse as comma-separated list
            potential_topics = [topic.strip().strip('"\'[]') for topic in text.split(',')]
            topics = [topic for topic in potential_topics if len(topic) > 1 and len(topic) < 50]
        
        # If no comma-separated topics found, extract keywords
        if not topics:
            # Simple keyword extraction (in production, use more sophisticated NLP)
            words = re.findall(r'\b[A-Za-z]{4,}\b', text.lower())
            # Filter out common words and limit to 5
            common_words = {'this', 'that', 'with', 'from', 'they', 'know', 'want', 'been', 'good', 'much', 'some', 'time', 'very', 'when', 'come', 'here', 'just', 'like', 'long', 'make', 'many', 'over', 'such', 'take', 'than', 'them', 'well', 'were', 'will', 'would', 'about', 'after', 'again', 'before', 'could', 'first', 'found', 'great', 'never', 'other', 'right', 'should', 'still', 'those', 'under', 'where', 'while', 'these', 'through', 'during', 'without', 'another', 'because', 'between', 'against', 'nothing', 'someone', 'everyone', 'something'}
            keywords = [word for word in words if word not in common_words]
            topics = list(set(keywords))[:5]
        
        return topics[:5]  # Limit to 5 topics
    
    def _extract_sentiment_from_text(self, text: str) -> Dict[str, Any]:
        """Extract sentiment from free-form text response"""
        text = text.strip()
        
        # Try to parse as JSON first
        if text.startswith('{') and text.endswith('}'):
            try:
                sentiment_data = json.loads(text)
                if isinstance(sentiment_data, dict) and 'sentiment' in sentiment_data:
                    return {
                        'sentiment': sentiment_data.get('sentiment', 'neutral'),
                        'confidence': sentiment_data.get('confidence', 70)
                    }
            except json.JSONDecodeError:
                pass
        
        text_lower = text.lower()
        
        # Simple keyword-based sentiment analysis
        positive_words = ['positive', 'good', 'great', 'excellent', 'amazing', 'wonderful', 'fantastic', 'awesome', 'love', 'best', 'happy', 'excited', 'optimistic']
        negative_words = ['negative', 'bad', 'terrible', 'awful', 'horrible', 'worst', 'hate', 'sad', 'angry', 'disappointed', 'frustrated', 'pessimistic']
        
        positive_count = sum(1 for word in positive_words if word in text_lower)
        negative_count = sum(1 for word in negative_words if word in text_lower)
        
        if positive_count > negative_count:
            sentiment = 'positive'
            confidence = min(50 + positive_count * 10, 90)
        elif negative_count > positive_count:
            sentiment = 'negative'
            confidence = min(50 + negative_count * 10, 90)
        else:
            sentiment = 'neutral'
            confidence = 70
        
        return {
            'sentiment': sentiment,
            'confidence': confidence
        }
    
    def _save_error_result(self, video_id: str, error_message: str) -> Dict[str, Any]:
        """Save error result to database"""
        try:
            error_data = {
                'video_id': video_id,
                'summary': None,
                'topics': [],
                'sentiment': None,
                'confidence_score': 0,
                'error_message': error_message,
                'llm_provider': self.llm_client.provider.value,
                'processing_duration_seconds': 0,
                'transcript_used': None
            }
            
            self.db_manager.save_analysis(error_data)
            
            return {
                'success': False,
                'message': f'Processing failed: {error_message}',
                'data': error_data,
                'cached': False
            }
        except Exception as e:
            logger.error(f"Failed to save error result: {e}")
            return {
                'success': False,
                'message': f'Processing and error saving failed: {error_message}',
                'data': None,
                'cached': False
            }
    
    def get_analysis(self, video_id: str) -> Optional[Dict[str, Any]]:
        """
        Get analysis result for a video
        
        Args:
            video_id: Unique video identifier
            
        Returns:
            Analysis result dictionary or None if not found
        """
        result = self.db_manager.get_analysis_by_video_id(video_id)
        return result.to_dict() if result else None
    
    def get_processing_stats(self) -> Dict[str, Any]:
        """Get processing statistics"""
        return self.db_manager.get_processing_stats()
    
    def reprocess_video(self, video_id: str, video_url: str, platform: str = 'auto') -> Dict[str, Any]:
        """
        Force reprocessing of a video
        
        Args:
            video_id: Unique video identifier
            video_url: Video URL
            platform: Platform name
            
        Returns:
            Processing result
        """
        logger.info(f"Force reprocessing video_id: {video_id}")
        return self.process_video(video_id, video_url, platform, force_reprocess=True)