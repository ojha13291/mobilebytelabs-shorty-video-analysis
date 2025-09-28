"""
Unit tests for LLM Processor module
"""

import pytest
import json
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime

from llm_processor.processor import LLMProcessor
from llm_processor.database import DatabaseManager, LLMAnalysisResult
from llm_processor.llm_client import LLMClient, LLMProvider
from llm_processor.transcript_extractor import TranscriptExtractor


class TestLLMProcessor:
    """Test cases for LLM Processor"""
    
    @pytest.fixture
    def mock_db_manager(self):
        """Create mock database manager"""
        mock = Mock(spec=DatabaseManager)
        return mock
    
    @pytest.fixture
    def mock_llm_client(self):
        """Create mock LLM client"""
        mock = Mock(spec=LLMClient)
        mock.provider = LLMProvider.MISTRAL
        return mock
    
    @pytest.fixture
    def mock_transcript_extractor(self):
        """Create mock transcript extractor"""
        mock = Mock(spec=TranscriptExtractor)
        return mock
    
    @pytest.fixture
    def processor(self, mock_db_manager, mock_llm_client, mock_transcript_extractor):
        """Create LLM processor with mocked dependencies"""
        return LLMProcessor(
            database_manager=mock_db_manager,
            llm_client=mock_llm_client,
            transcript_extractor=mock_transcript_extractor
        )
    
    def test_process_video_cached_result(self, processor, mock_db_manager):
        """Test processing when result is already cached"""
        # Arrange
        video_id = "test_video_123"
        video_url = "https://youtube.com/watch?v=test123"
        
        mock_result = Mock()
        mock_result.to_dict.return_value = {
            'video_id': video_id,
            'summary': 'Test summary',
            'topics': ['topic1', 'topic2'],
            'sentiment': 'positive',
            'confidence_score': 85
        }
        
        mock_db_manager.analysis_exists.return_value = True
        mock_db_manager.get_analysis_by_video_id.return_value = mock_result
        
        # Act
        result = processor.process_video(video_id, video_url)
        
        # Assert
        assert result['success'] is True
        assert result['cached'] is True
        assert result['message'] == 'Analysis retrieved from cache'
        assert result['data']['video_id'] == video_id
        
        mock_db_manager.analysis_exists.assert_called_once_with(video_id)
        mock_db_manager.get_analysis_by_video_id.assert_called_once_with(video_id)
    
    def test_process_video_no_transcript(self, processor, mock_db_manager, mock_transcript_extractor):
        """Test processing when no transcript is available"""
        # Arrange
        video_id = "test_video_123"
        video_url = "https://youtube.com/watch?v=test123"
        
        mock_db_manager.analysis_exists.return_value = False
        mock_transcript_extractor.extract_transcript.return_value = None
        
        # Act
        result = processor.process_video(video_id, video_url)
        
        # Assert
        assert result['success'] is False
        assert 'No transcript available' in result['message']
        
        mock_db_manager.save_analysis.assert_called_once()
        saved_data = mock_db_manager.save_analysis.call_args[0][0]
        assert saved_data['error_message'] == 'No transcript available'
    
    @patch('llm_processor.processor.time.time')
    def test_process_video_successful_analysis(self, mock_time, processor, mock_db_manager, 
                                             mock_llm_client, mock_transcript_extractor):
        """Test successful video processing with LLM analysis"""
        # Arrange
        video_id = "test_video_123"
        video_url = "https://youtube.com/watch?v=test123"
        transcript = "This is a test video about technology and innovation."
        
        mock_db_manager.analysis_exists.return_value = False
        mock_transcript_extractor.extract_transcript.return_value = transcript
        mock_time.side_effect = [0, 5]  # Start and end time for duration calculation
        
        # Mock LLM responses
        mock_llm_client.generate_response.side_effect = [
            {
                'success': True,
                'response': 'This video discusses technology and innovation.',
                'model': 'mistral-small',
                'usage': {'prompt_tokens': 100, 'completion_tokens': 50}
            },
            {
                'success': True,
                'response': '["technology", "innovation", "test", "video", "content"]',
                'model': 'mistral-small',
                'usage': {'prompt_tokens': 100, 'completion_tokens': 30}
            },
            {
                'success': True,
                'response': '{"sentiment": "positive", "confidence": 85}',
                'model': 'mistral-small',
                'usage': {'prompt_tokens': 100, 'completion_tokens': 25}
            }
        ]
        
        mock_saved_result = Mock()
        mock_saved_result.to_dict.return_value = {
            'video_id': video_id,
            'summary': 'This video discusses technology and innovation.',
            'topics': ['technology', 'innovation', 'test', 'video', 'content'],
            'sentiment': 'positive',
            'confidence_score': 85
        }
        mock_db_manager.save_analysis.return_value = mock_saved_result
        
        # Act
        result = processor.process_video(video_id, video_url)
        
        # Assert
        assert result['success'] is True
        assert result['cached'] is False
        assert result['data']['video_id'] == video_id
        assert result['data']['summary'] == 'This video discusses technology and innovation.'
        assert result['data']['topics'] == ['technology', 'innovation', 'test', 'video', 'content']
        assert result['data']['sentiment'] == 'positive'
        assert result['data']['confidence_score'] == 85
        
        # Verify LLM client was called 3 times (summary, topics, sentiment)
        assert mock_llm_client.generate_response.call_count == 3
        
        # Verify database save was called
        mock_db_manager.save_analysis.assert_called_once()
        saved_data = mock_db_manager.save_analysis.call_args[0][0]
        assert saved_data['video_id'] == video_id
        assert saved_data['processing_duration_seconds'] == 5
    
    def test_process_video_llm_failure(self, processor, mock_db_manager, mock_llm_client, 
                                     mock_transcript_extractor):
        """Test processing when LLM analysis fails"""
        # Arrange
        video_id = "test_video_123"
        video_url = "https://youtube.com/watch?v=test123"
        transcript = "Test content"
        
        mock_db_manager.analysis_exists.return_value = False
        mock_transcript_extractor.extract_transcript.return_value = transcript
        
        # Mock LLM failure
        mock_llm_client.generate_response.return_value = {
            'success': False,
            'error': 'LLM service unavailable'
        }
        
        # Act
        result = processor.process_video(video_id, video_url)
        
        # Assert
        assert result['success'] is False
        assert 'Processing failed' in result['message']
        
        mock_db_manager.save_analysis.assert_called_once()
        saved_data = mock_db_manager.save_analysis.call_args[0][0]
        assert 'LLM service unavailable' in saved_data['error_message']
    
    def test_extract_topics_from_json_response(self, processor):
        """Test topic extraction from JSON response"""
        # Arrange
        json_response = '["technology", "innovation", "AI", "machine learning", "future"]'
        
        # Act
        topics = processor._extract_topics_from_text(json_response)
        
        # Assert
        assert topics == ["technology", "innovation", "AI", "machine learning", "future"]
    
    def test_extract_topics_from_comma_separated_text(self, processor):
        """Test topic extraction from comma-separated text"""
        # Arrange
        text_response = "technology, innovation, AI, machine learning, future"
        
        # Act
        topics = processor._extract_topics_from_text(text_response)
        
        # Assert
        assert topics == ["technology", "innovation", "AI", "machine learning", "future"]
    
    def test_extract_topics_fallback_to_keywords(self, processor):
        """Test topic extraction fallback to keyword extraction"""
        # Arrange
        text_response = "This video is about technology and innovation in the modern world"
        
        # Act
        topics = processor._extract_topics_from_text(text_response)
        
        # Assert
        assert len(topics) > 0
        assert all(len(topic) >= 4 for topic in topics)  # Keywords should be 4+ chars
    
    def test_extract_sentiment_from_json_response(self, processor):
        """Test sentiment extraction from JSON response"""
        # Arrange
        json_response = '{"sentiment": "positive", "confidence": 90}'
        
        # Act
        sentiment_data = processor._extract_sentiment_from_text(json_response)
        
        # Assert
        assert sentiment_data['sentiment'] == 'positive'
        assert sentiment_data['confidence'] == 90
    
    def test_extract_sentiment_from_keyword_text(self, processor):
        """Test sentiment extraction from keyword-based text"""
        # Arrange
        text_response = "The sentiment is positive and optimistic"
        
        # Act
        sentiment_data = processor._extract_sentiment_from_text(text_response)
        
        # Assert
        assert sentiment_data['sentiment'] == 'positive'
        assert sentiment_data['confidence'] >= 50
    
    def test_extract_sentiment_negative_keywords(self, processor):
        """Test sentiment extraction with negative keywords"""
        # Arrange
        text_response = "This is terrible and awful"
        
        # Act
        sentiment_data = processor._extract_sentiment_from_text(text_response)
        
        # Assert
        assert sentiment_data['sentiment'] == 'negative'
        assert sentiment_data['confidence'] >= 50
    
    def test_get_analysis(self, processor, mock_db_manager):
        """Test getting analysis result"""
        # Arrange
        video_id = "test_video_123"
        mock_result = Mock()
        mock_result.to_dict.return_value = {
            'video_id': video_id,
            'summary': 'Test summary'
        }
        mock_db_manager.get_analysis_by_video_id.return_value = mock_result
        
        # Act
        result = processor.get_analysis(video_id)
        
        # Assert
        assert result is not None
        assert result['video_id'] == video_id
        assert result['summary'] == 'Test summary'
        
        mock_db_manager.get_analysis_by_video_id.assert_called_once_with(video_id)
    
    def test_get_analysis_not_found(self, processor, mock_db_manager):
        """Test getting analysis when not found"""
        # Arrange
        video_id = "nonexistent_video"
        mock_db_manager.get_analysis_by_video_id.return_value = None
        
        # Act
        result = processor.get_analysis(video_id)
        
        # Assert
        assert result is None
        mock_db_manager.get_analysis_by_video_id.assert_called_once_with(video_id)
    
    def test_get_processing_stats(self, processor, mock_db_manager):
        """Test getting processing statistics"""
        # Arrange
        expected_stats = {
            'total_analyses': 100,
            'successful_analyses': 95,
            'failed_analyses': 5
        }
        mock_db_manager.get_processing_stats.return_value = expected_stats
        
        # Act
        stats = processor.get_processing_stats()
        
        # Assert
        assert stats == expected_stats
        mock_db_manager.get_processing_stats.assert_called_once()
    
    def test_reprocess_video(self, processor):
        """Test force reprocessing of a video"""
        # Arrange
        video_id = "test_video_123"
        video_url = "https://youtube.com/watch?v=test123"
        
        with patch.object(processor, 'process_video') as mock_process:
            mock_process.return_value = {
                'success': True,
                'message': 'Video processed successfully',
                'cached': False
            }
            
            # Act
            result = processor.reprocess_video(video_id, video_url)
            
            # Assert
            mock_process.assert_called_once_with(video_id, video_url, 'auto', force_reprocess=True)
            assert result['success'] is True
    
    def test_error_handling_unexpected_exception(self, processor, mock_db_manager, 
                                               mock_transcript_extractor):
        """Test error handling for unexpected exceptions"""
        # Arrange
        video_id = "test_video_123"
        video_url = "https://youtube.com/watch?v=test123"
        
        mock_db_manager.analysis_exists.return_value = False
        mock_transcript_extractor.extract_transcript.side_effect = Exception("Unexpected error")
        
        # Act
        result = processor.process_video(video_id, video_url)
        
        # Assert
        assert result['success'] is False
        assert 'Unexpected error' in result['message']
        
        mock_db_manager.save_analysis.assert_called_once()
        saved_data = mock_db_manager.save_analysis.call_args[0][0]
        assert 'Unexpected error' in saved_data['error_message']


class TestLLMProcessorIntegration:
    """Integration tests for LLM Processor"""
    
    def test_full_processing_pipeline_mocked(self):
        """Test full processing pipeline with mocked dependencies"""
        # Arrange
        video_id = "integration_test_video"
        video_url = "https://youtube.com/watch?v=integration123"
        transcript = "This is an amazing video about artificial intelligence and machine learning. The content is very positive and informative."
        
        with patch('llm_processor.processor.DatabaseManager') as mock_db_class, \
             patch('llm_processor.processor.LLMClient') as mock_llm_class, \
             patch('llm_processor.processor.TranscriptExtractor') as mock_extractor_class:
            
            # Setup mocks
            mock_db = mock_db_class.return_value
            mock_llm = mock_llm_class.return_value
            mock_extractor = mock_extractor_class.return_value
            
            mock_db.analysis_exists.return_value = False
            mock_extractor.extract_transcript.return_value = transcript
            
            # Mock LLM responses
            mock_llm.generate_response.side_effect = [
                {
                    'success': True,
                    'response': 'This video discusses artificial intelligence and machine learning in a positive manner.',
                    'model': 'mistral-small',
                    'usage': {'prompt_tokens': 100, 'completion_tokens': 60}
                },
                {
                    'success': True,
                    'response': '["artificial intelligence", "machine learning", "technology", "education", "innovation"]',
                    'model': 'mistral-small',
                    'usage': {'prompt_tokens': 100, 'completion_tokens': 40}
                },
                {
                    'success': True,
                    'response': '{"sentiment": "positive", "confidence": 88}',
                    'model': 'mistral-small',
                    'usage': {'prompt_tokens': 100, 'completion_tokens': 25}
                }
            ]
            
            mock_saved_result = Mock()
            mock_saved_result.to_dict.return_value = {
                'video_id': video_id,
                'summary': 'This video discusses artificial intelligence and machine learning in a positive manner.',
                'topics': ['artificial intelligence', 'machine learning', 'technology', 'education', 'innovation'],
                'sentiment': 'positive',
                'confidence_score': 88
            }
            mock_db.save_analysis.return_value = mock_saved_result
            
            # Create processor
            processor = LLMProcessor()
            
            # Act
            result = processor.process_video(video_id, video_url)
            
            # Assert
            assert result['success'] is True
            assert result['data']['sentiment'] == 'positive'
            assert len(result['data']['topics']) == 5
            assert result['data']['confidence_score'] == 88
            assert 'artificial intelligence' in result['data']['topics']


if __name__ == '__main__':
    pytest.main([__file__])