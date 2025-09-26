"""
Unit tests for video data fetcher module
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
import json
from datetime import datetime

# Import the modules we want to test
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from video_data_fetcher import VideoDataFetcher, fetch_video_metadata
from video_data_fetcher.base_fetcher import VideoMetadata, BaseVideoFetcher
from video_data_fetcher.youtube_fetcher import YouTubeFetcher
from video_data_fetcher.instagram_fetcher import InstagramFetcher
from video_data_fetcher.tiktok_fetcher import TikTokFetcher
from video_data_fetcher.twitter_fetcher import TwitterFetcher


class TestVideoMetadata(unittest.TestCase):
    """Test the VideoMetadata class."""
    
    def test_video_metadata_creation(self):
        """Test creating VideoMetadata object."""
        metadata = VideoMetadata(
            platform="youtube",
            title="Test Video",
            description="Test description",
            thumbnail_url="https://example.com/thumb.jpg",
            duration=300,
            views=1000,
            published_at="2023-01-01T00:00:00Z",
            url="https://youtube.com/watch?v=test"
        )
        
        self.assertEqual(metadata.platform, "youtube")
        self.assertEqual(metadata.title, "Test Video")
        self.assertEqual(metadata.description, "Test description")
        self.assertEqual(metadata.thumbnail_url, "https://example.com/thumb.jpg")
        self.assertEqual(metadata.duration, 300)
        self.assertEqual(metadata.views, 1000)
        self.assertEqual(metadata.published_at, "2023-01-01T00:00:00Z")
        self.assertEqual(metadata.url, "https://youtube.com/watch?v=test")
        self.assertIsNotNone(metadata.fetched_at)
    
    def test_video_metadata_to_dict(self):
        """Test converting VideoMetadata to dictionary."""
        metadata = VideoMetadata(
            platform="youtube",
            title="Test Video",
            description="Test description"
        )
        
        result = metadata.to_dict()
        
        self.assertEqual(result['platform'], "youtube")
        self.assertEqual(result['title'], "Test Video")
        self.assertEqual(result['description'], "Test description")
        self.assertIn('fetched_at', result)
    
    def test_video_metadata_is_valid(self):
        """Test VideoMetadata validation."""
        # Valid metadata - platform and title are required
        metadata = VideoMetadata(platform="youtube", title="Test Video", url="https://example.com")
        self.assertTrue(metadata.is_valid())
    
        # Invalid metadata (missing title) - empty string is falsy
        metadata = VideoMetadata(platform="youtube", title="", url="https://example.com")
        self.assertFalse(metadata.is_valid())  # Empty string is invalid
        
        # Invalid metadata (missing platform)
        metadata = VideoMetadata(platform="", title="Test Video", url="https://example.com")
        self.assertFalse(metadata.is_valid())


class TestBaseVideoFetcher(unittest.TestCase):
    """Test the BaseVideoFetcher class."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Use YouTubeFetcher since BaseVideoFetcher is abstract
        self.fetcher = YouTubeFetcher()
    
    def test_format_duration_iso8601(self):
        """Test duration formatting for ISO 8601 format."""
        self.assertEqual(self.fetcher.format_duration("PT4M13S"), 253)
        self.assertEqual(self.fetcher.format_duration("PT1H30M45S"), 5445)
        self.assertEqual(self.fetcher.format_duration("PT30S"), 30)
        self.assertIsNone(self.fetcher.format_duration(""))
    
    def test_format_duration_mm_ss(self):
        """Test duration formatting for MM:SS format."""
        self.assertEqual(self.fetcher.format_duration("4:13"), 253)
        self.assertEqual(self.fetcher.format_duration("1:30:45"), 5445)
        self.assertEqual(self.fetcher.format_duration("30"), 30)
    
    def test_format_views(self):
        """Test view count formatting."""
        self.assertEqual(self.fetcher.format_views("1.2K"), 1200)
        self.assertEqual(self.fetcher.format_views("1.5M"), 1500000)
        self.assertEqual(self.fetcher.format_views("2B"), 2000000000)
        self.assertEqual(self.fetcher.format_views("1,234"), 1234)
        self.assertEqual(self.fetcher.format_views("1234"), 1234)
        self.assertIsNone(self.fetcher.format_views(""))
    
    def test_parse_html(self):
        """Test HTML parsing."""
        html = "<html><body><h1>Test</h1></body></html>"
        soup = self.fetcher.parse_html(html)
        self.assertIsNotNone(soup)
        self.assertEqual(soup.find('h1').text, "Test")


class TestYouTubeFetcher(unittest.TestCase):
    """Test the YouTubeFetcher class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.fetcher = YouTubeFetcher()
    
    def test_can_fetch_youtube_urls(self):
        """Test URL detection for YouTube."""
        youtube_urls = [
            "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
            "https://youtu.be/dQw4w9WgXcQ",
            "https://www.youtube.com/shorts/dQw4w9WgXcQ",
            "https://m.youtube.com/watch?v=dQw4w9WgXcQ"
        ]
        
        for url in youtube_urls:
            self.assertTrue(self.fetcher.can_fetch(url), f"Should detect {url} as YouTube")
        
        non_youtube_urls = [
            "https://www.instagram.com/reel/test/",
            "https://www.tiktok.com/@user/video/123",
            "https://twitter.com/user/status/123"
        ]
        
        for url in non_youtube_urls:
            self.assertFalse(self.fetcher.can_fetch(url), f"Should not detect {url} as YouTube")
    
    def test_extract_video_id(self):
        """Test YouTube video ID extraction."""
        test_cases = [
            ("https://www.youtube.com/watch?v=dQw4w9WgXcQ", "dQw4w9WgXcQ"),
            ("https://youtu.be/dQw4w9WgXcQ", "dQw4w9WgXcQ"),
            ("https://www.youtube.com/shorts/dQw4w9WgXcQ", "dQw4w9WgXcQ"),
            ("https://m.youtube.com/watch?v=dQw4w9WgXcQ", "dQw4w9WgXcQ"),
            ("https://www.youtube.com/watch?v=invalid", None),  # Too short
            ("https://www.google.com/", None)
        ]
        
        for url, expected in test_cases:
            result = self.fetcher._extract_video_id(url)
            self.assertEqual(result, expected, f"Video ID extraction failed for {url}")
    
    @patch('requests.Session')
    def test_fetch_with_scraping(self, mock_session_class):
        """Test YouTube metadata fetching with scraping."""
        # Mock response
        mock_response = Mock()
        mock_response.text = '''
        <html>
        <head>
            <meta property="og:title" content="Test YouTube Video">
            <meta property="og:description" content="Test description">
            <meta property="og:image" content="https://example.com/thumb.jpg">
            <title>Test YouTube Video - YouTube</title>
        </head>
        <body></body>
        </html>
        '''
        mock_response.raise_for_status.return_value = None
        
        mock_session = Mock()
        mock_session.get.return_value = mock_response
        mock_session_class.return_value = mock_session
        
        # Create fetcher AFTER setting up the mock
        fetcher = YouTubeFetcher()
        
        # Test fetching
        result = fetcher._fetch_with_scraping("https://www.youtube.com/watch?v=test123")
        
        self.assertEqual(result.platform, "youtube")
        # YouTube fetcher extracts title from og:title meta tag
        self.assertEqual(result.title, "Test YouTube Video")
        self.assertEqual(result.description, "Test description")
        self.assertEqual(result.thumbnail_url, "https://example.com/thumb.jpg")


class TestInstagramFetcher(unittest.TestCase):
    """Test the InstagramFetcher class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.fetcher = InstagramFetcher()
    
    def test_can_fetch_instagram_urls(self):
        """Test URL detection for Instagram."""
        instagram_urls = [
            "https://www.instagram.com/reel/test123/",
            "https://www.instagram.com/p/test123/",
            "https://m.instagram.com/reel/test123/",
            "https://instagr.am/p/test123/"
        ]
        
        for url in instagram_urls:
            self.assertTrue(self.fetcher.can_fetch(url), f"Should detect {url} as Instagram")
        
        non_instagram_urls = [
            "https://www.youtube.com/watch?v=test",
            "https://www.tiktok.com/@user/video/123",
            "https://twitter.com/user/status/123"
        ]
        
        for url in non_instagram_urls:
            self.assertFalse(self.fetcher.can_fetch(url), f"Should not detect {url} as Instagram")
    
    @patch('requests.Session')
    def test_fetch_metadata(self, mock_session_class):
        """Test Instagram metadata fetching."""
        # Mock response
        mock_response = Mock()
        mock_response.text = '''
        <html>
        <head>
            <meta property="og:title" content="Test Instagram Post">
            <meta property="og:description" content="Test description">
            <meta property="og:image" content="https://example.com/insta.jpg">
        </head>
        <body></body>
        </html>
        '''
        mock_response.raise_for_status.return_value = None
        
        mock_session = Mock()
        mock_session.get.return_value = mock_response
        mock_session_class.return_value = mock_session
        
        # Create fetcher AFTER setting up the mock
        fetcher = InstagramFetcher()
        
        # Test fetching
        result = fetcher.fetch_metadata("https://www.instagram.com/reel/test123/")
        
        self.assertEqual(result.platform, "instagram")
        # Instagram fetcher extracts title from og:title meta tag
        self.assertEqual(result.title, "Test Instagram Post")
        self.assertEqual(result.description, "Test description")
        self.assertEqual(result.thumbnail_url, "https://example.com/insta.jpg")


class TestTikTokFetcher(unittest.TestCase):
    """Test the TikTokFetcher class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.fetcher = TikTokFetcher()
    
    def test_can_fetch_tiktok_urls(self):
        """Test URL detection for TikTok."""
        tiktok_urls = [
            "https://www.tiktok.com/@user/video/1234567890",
            "https://m.tiktok.com/v/1234567890.html",
            "https://vm.tiktok.com/abc123/",
            "https://tiktok.com/t/abc123/"
        ]
        
        for url in tiktok_urls:
            self.assertTrue(self.fetcher.can_fetch(url), f"Should detect {url} as TikTok")
        
        non_tiktok_urls = [
            "https://www.youtube.com/watch?v=test",
            "https://www.instagram.com/reel/test/",
            "https://twitter.com/user/status/123"
        ]
        
        for url in non_tiktok_urls:
            self.assertFalse(self.fetcher.can_fetch(url), f"Should not detect {url} as TikTok")


class TestTwitterFetcher(unittest.TestCase):
    """Test the TwitterFetcher class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.fetcher = TwitterFetcher()
    
    def test_can_fetch_twitter_urls(self):
        """Test URL detection for Twitter/X."""
        twitter_urls = [
            "https://twitter.com/user/status/1234567890123456789",
            "https://x.com/user/status/1234567890123456789",
            "https://mobile.twitter.com/user/status/1234567890123456789",
            "https://m.twitter.com/user/status/1234567890123456789"
        ]
        
        for url in twitter_urls:
            self.assertTrue(self.fetcher.can_fetch(url), f"Should detect {url} as Twitter")
        
        non_twitter_urls = [
            "https://www.youtube.com/watch?v=test",
            "https://www.instagram.com/reel/test/",
            "https://www.tiktok.com/@user/video/123"
        ]
        
        for url in non_twitter_urls:
            self.assertFalse(self.fetcher.can_fetch(url), f"Should not detect {url} as Twitter")


class TestVideoDataFetcher(unittest.TestCase):
    """Test the main VideoDataFetcher class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.fetcher = VideoDataFetcher()
    
    def test_get_supported_platforms(self):
        """Test getting supported platforms."""
        platforms = self.fetcher.get_supported_platforms()
        expected_platforms = ['youtube', 'instagram', 'tiktok', 'twitter']
        
        for platform in expected_platforms:
            self.assertIn(platform, platforms)
    
    @patch('video_data_fetcher.youtube_fetcher.YouTubeFetcher.fetch_metadata')
    @patch('video_data_fetcher.fetcher.PlatformResolver.get_platform_info')
    def test_fetch_metadata_success(self, mock_platform_info, mock_fetch_metadata):
        """Test successful metadata fetching."""
        # Mock platform detection
        mock_platform_info.return_value = {
            'platform': 'youtube',
            'url_type': 'video',
            'confidence': 'high',
            'description': 'YouTube video URL detected'
        }
        
        # Mock fetcher response
        mock_metadata = VideoMetadata(
            platform="youtube",
            title="Test Video",
            description="Test description",
            url="https://www.youtube.com/watch?v=test"
        )
        mock_fetch_metadata.return_value = mock_metadata
        
        # Test fetching
        result = self.fetcher.fetch_metadata("https://www.youtube.com/watch?v=test")
        
        self.assertTrue(result['success'])
        self.assertEqual(result['platform'], 'youtube')
        self.assertEqual(result['title'], 'Test Video')
        self.assertEqual(result['description'], 'Test description')
    
    def test_fetch_metadata_unknown_platform(self):
        """Test fetching with unknown platform."""
        result = self.fetcher.fetch_metadata("https://unknown-platform.com/video/123")
        
        self.assertFalse(result['success'])
        self.assertIn('error', result)
        self.assertIn('Unable to detect platform', result['error'])
    
    def test_fetch_batch_metadata(self):
        """Test batch metadata fetching."""
        urls = [
            "https://www.youtube.com/watch?v=test1",
            "https://www.instagram.com/reel/test2/",
            "https://unknown-platform.com/video/123"
        ]
        
        results = self.fetcher.fetch_batch_metadata(urls)
        
        self.assertEqual(len(results), 3)
        # Each result should have success/error information
        for result in results:
            self.assertIn('success', result)
            self.assertIn('url', result)


class TestConvenienceFunctions(unittest.TestCase):
    """Test convenience functions."""
    
    @patch('video_data_fetcher.fetcher.VideoDataFetcher.fetch_metadata')
    def test_fetch_video_metadata(self, mock_fetch):
        """Test the fetch_video_metadata convenience function."""
        mock_fetch.return_value = {
            'success': True,
            'platform': 'youtube',
            'title': 'Test Video',
            'url': 'https://www.youtube.com/watch?v=test'
        }
        
        result = fetch_video_metadata("https://www.youtube.com/watch?v=test")
        
        self.assertTrue(result['success'])
        self.assertEqual(result['platform'], 'youtube')
        mock_fetch.assert_called_once_with("https://www.youtube.com/watch?v=test")


if __name__ == '__main__':
    unittest.main()