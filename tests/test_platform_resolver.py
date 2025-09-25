"""
Unit tests for the Platform Resolver module.

This module contains comprehensive tests for the platform detection functionality,
including tests for all supported platforms, edge cases, and error handling.
"""

import unittest
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import from the resolver package
from resolver.platform_resolver import PlatformResolver, detect_platform, get_platform_info


class TestPlatformResolver(unittest.TestCase):
    """Test cases for the PlatformResolver class."""
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        self.resolver = PlatformResolver()
    
    def test_youtube_detection(self):
        """Test YouTube URL detection."""
        youtube_urls = [
            "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
            "https://youtube.com/watch?v=ABC123&feature=share",
            "https://youtu.be/dQw4w9WgXcQ",
            "https://www.youtube.com/embed/dQw4w9WgXcQ",
            "https://www.youtube.com/v/dQw4w9WgXcQ",
            "https://www.youtube.com/shorts/ABC123DEF",
            "https://m.youtube.com/watch?v=dQw4w9WgXcQ",
            "https://studio.youtube.com/channel/UC1234567890",
            "https://music.youtube.com/watch?v=dQw4w9WgXcQ",
            "https://tv.youtube.com/watch/dQw4w9WgXcQ",
            "https://www.youtubekids.com/watch?v=dQw4w9WgXcQ",
        ]
        
        for url in youtube_urls:
            with self.subTest(url=url):
                result = self.resolver.detect_platform(url)
                self.assertEqual(result, 'youtube', f"Failed to detect YouTube for URL: {url}")
    
    def test_instagram_detection(self):
        """Test Instagram URL detection."""
        instagram_urls = [
            "https://www.instagram.com/p/ABC123DEF/",
            "https://instagram.com/reel/ABC123DEF/",
            "https://www.instagram.com/tv/ABC123DEF/",
            "https://www.instagram.com/stories/username/1234567890/",
            "https://www.instagram.com/highlights/1234567890/",
            "https://www.instagram.com/username/",
            "https://www.instagram.com/username/feed/",
            "https://www.instagram.com/username/reels/",
            "https://m.instagram.com/p/ABC123DEF/",
            "https://instagr.am/p/ABC123DEF/",
            "https://instagr.am/reel/ABC123DEF/",
            "https://instagr.am/username/",
        ]
        
        for url in instagram_urls:
            with self.subTest(url=url):
                result = self.resolver.detect_platform(url)
                self.assertEqual(result, 'instagram', f"Failed to detect Instagram for URL: {url}")
    
    def test_tiktok_detection(self):
        """Test TikTok URL detection."""
        tiktok_urls = [
            "https://www.tiktok.com/@username/video/1234567890123456789",
            "https://tiktok.com/@username",
            "https://www.tiktok.com/discover/",
            "https://www.tiktok.com/tag/trending",
            "https://www.tiktok.com/music/original-sound-1234567890",
            "https://m.tiktok.com/v/1234567890123456789.html",
            "https://vm.tiktok.com/ABC123/",
            "https://www.tiktok.com/t/ABC123DEF/",
            "https://business.tiktok.com/",
            "https://developers.tiktok.com/",
        ]
        
        for url in tiktok_urls:
            with self.subTest(url=url):
                result = self.resolver.detect_platform(url)
                self.assertEqual(result, 'tiktok', f"Failed to detect TikTok for URL: {url}")
    
    def test_twitter_detection(self):
        """Test Twitter/X URL detection."""
        twitter_urls = [
            "https://twitter.com/username/status/1234567890123456789",
            "https://twitter.com/username/statuses/1234567890123456789",
            "https://twitter.com/username/media",
            "https://twitter.com/username/likes",
            "https://twitter.com/username/with_replies",
            "https://twitter.com/search?q=trending",
            "https://twitter.com/hashtag/trending",
            "https://mobile.twitter.com/username/status/1234567890123456789",
            "https://x.com/username/status/1234567890123456789",
            "https://x.com/username/media",
            "https://x.com/search?q=trending",
            "https://t.co/ABC123",
            "https://twitter.com/i/spaces/1234567890",
            "https://x.com/i/spaces/1234567890",
        ]
        
        for url in twitter_urls:
            with self.subTest(url=url):
                result = self.resolver.detect_platform(url)
                self.assertEqual(result, 'twitter', f"Failed to detect Twitter for URL: {url}")
    
    def test_facebook_detection(self):
        """Test Facebook URL detection."""
        facebook_urls = [
            "https://www.facebook.com/username/posts/1234567890123456",
            "https://facebook.com/username/videos/1234567890123456/",
            "https://www.facebook.com/username/photos/",
            "https://www.facebook.com/watch/",
            "https://www.facebook.com/groups/groupname/",
            "https://www.facebook.com/events/1234567890/",
            "https://www.facebook.com/username/",
            "https://www.facebook.com/profile.php?id=1234567890",
            "https://m.facebook.com/username/",
            "https://business.facebook.com/",
            "https://fb.gg/username",
            "https://gaming.facebook.com/",
            "https://messenger.com/t/username",
            "https://m.me/username",
        ]
        
        for url in facebook_urls:
            with self.subTest(url=url):
                result = self.resolver.detect_platform(url)
                self.assertEqual(result, 'facebook', f"Failed to detect Facebook for URL: {url}")
    
    def test_other_platforms(self):
        """Test detection of other supported platforms."""
        test_cases = [
            # LinkedIn
            ("https://www.linkedin.com/in/username/", "linkedin"),
            ("https://www.linkedin.com/company/companyname/", "linkedin"),
            
            # Snapchat
            ("https://www.snapchat.com/add/username", "snapchat"),
            ("https://www.snapchat.com/discover/", "snapchat"),
            
            # Pinterest
            ("https://www.pinterest.com/pin/1234567890/", "pinterest"),
            ("https://www.pinterest.com/username/", "pinterest"),
            
            # Reddit
            ("https://www.reddit.com/r/subreddit/", "reddit"),
            ("https://www.reddit.com/u/username/", "reddit"),
            
            # Twitch
            ("https://www.twitch.tv/username", "twitch"),
            ("https://www.twitch.tv/videos/1234567890", "twitch"),
            
            # Discord
            ("https://discord.com/channels/1234567890/1234567890", "discord"),
            ("https://discord.com/invite/ABC123", "discord"),
            
            # Telegram
            ("https://t.me/username", "telegram"),
            ("https://telegram.org/", "telegram"),
            
            # WhatsApp
            ("https://www.whatsapp.com/", "whatsapp"),
            ("https://wa.me/1234567890", "whatsapp"),
            
            # Vimeo
            ("https://vimeo.com/123456789", "vimeo"),
            ("https://vimeo.com/ondemand/movie", "vimeo"),
            
            # Dailymotion
            ("https://www.dailymotion.com/video/ABC123", "dailymotion"),
            ("https://www.dailymotion.com/user/username", "dailymotion"),
        ]
        
        for url, expected_platform in test_cases:
            with self.subTest(url=url):
                result = self.resolver.detect_platform(url)
                self.assertEqual(result, expected_platform, f"Failed to detect {expected_platform} for URL: {url}")
    
    def test_malformed_urls(self):
        """Test handling of malformed URLs."""
        malformed_urls = [
            "",
            "not-a-url",
            "http://",
            "https://",
            "invalid-url",
            "ftp://example.com",
            "javascript:alert('test')",
            "data:text/plain;base64,SGVsbG8gV29ybGQ=",
            None,  # This should be handled gracefully
        ]
        
        for url in malformed_urls:
            with self.subTest(url=url):
                result = self.resolver.detect_platform(url)
                self.assertEqual(result, 'unknown', f"Failed to handle malformed URL: {url}")
    
    def test_unknown_platforms(self):
        """Test URLs from unknown platforms."""
        unknown_urls = [
            "https://www.example.com/video/123",
            "https://unknown-platform.com/post/123",
            "https://random-site.org/content/abc",
            "https://github.com/username/repo",
            "https://stackoverflow.com/questions/123/question-title",
            "https://medium.com/@username/article-title",
        ]
        
        for url in unknown_urls:
            with self.subTest(url=url):
                result = self.resolver.detect_platform(url)
                self.assertEqual(result, 'unknown', f"Should return 'unknown' for URL: {url}")
    
    def test_url_type_detection(self):
        """Test URL type detection for different platforms."""
        test_cases = [
            # YouTube
            ("https://www.youtube.com/watch?v=dQw4w9WgXcQ", "video"),
            ("https://www.youtube.com/shorts/ABC123DEF", "shorts"),
            ("https://www.youtube.com/channel/UC1234567890", "channel"),
            ("https://www.youtube.com/playlist?list=ABC123", "playlist"),
            
            # Instagram
            ("https://www.instagram.com/p/ABC123DEF/", "post"),
            ("https://www.instagram.com/reel/ABC123DEF/", "reel"),
            ("https://www.instagram.com/stories/username/1234567890/", "story"),
            ("https://www.instagram.com/tv/ABC123DEF/", "igtv"),
            ("https://www.instagram.com/highlights/1234567890/", "highlight"),
            ("https://www.instagram.com/username/", "profile"),
            
            # TikTok
            ("https://www.tiktok.com/@username/video/1234567890123456789", "video"),
            ("https://www.tiktok.com/@username", "profile"),
            ("https://www.tiktok.com/tag/trending", "hashtag"),
            
            # Twitter
            ("https://twitter.com/username/status/1234567890123456789", "tweet"),
            ("https://twitter.com/username/media", "media"),
            ("https://twitter.com/hashtag/trending", "hashtag"),
            ("https://twitter.com/username/", "profile"),
        ]
        
        for url, expected_type in test_cases:
            with self.subTest(url=url):
                info = self.resolver.get_platform_info(url)
                self.assertEqual(info['url_type'], expected_type, f"Failed to detect URL type for: {url}")
    
    def test_confidence_levels(self):
        """Test confidence level determination."""
        # High confidence URLs (exact domain match)
        high_confidence_urls = [
            "https://youtube.com/watch?v=dQw4w9WgXcQ",
            "https://instagram.com/p/ABC123DEF/",
            "https://tiktok.com/@username/video/1234567890",
            "https://twitter.com/username/status/1234567890",
            "https://x.com/username/status/1234567890",
        ]
        
        for url in high_confidence_urls:
            with self.subTest(url=url):
                info = self.resolver.get_platform_info(url)
                self.assertEqual(info['confidence'], 'high', f"Should have high confidence for: {url}")
        
        # Medium confidence URLs (pattern match but not exact domain)
        # This would be URLs that match patterns but don't have exact domain matches
        # For this test, we'll use URLs that should be detected but might have lower confidence
    
    def test_convenience_functions(self):
        """Test the convenience functions."""
        # Test detect_platform function
        result = detect_platform("https://www.youtube.com/watch?v=dQw4w9WgXcQ")
        self.assertEqual(result, 'youtube')
        
        # Test get_platform_info function
        info = get_platform_info("https://www.instagram.com/reel/ABC123DEF/")
        self.assertEqual(info['platform'], 'instagram')
        self.assertEqual(info['url_type'], 'reel')
        self.assertIn('confidence', info)
        self.assertIn('description', info)
    
    def test_platform_extension(self):
        """Test adding and removing platforms."""
        # Add a new platform
        new_platform = "custom_platform"
        patterns = [r'customplatform\.com/', r'cp\.com/']
        
        self.resolver.add_platform(new_platform, patterns)
        
        # Test detection
        test_url = "https://customplatform.com/video/123"
        result = self.resolver.detect_platform(test_url)
        self.assertEqual(result, new_platform)
        
        # Test listing platforms
        platforms = self.resolver.list_platforms()
        self.assertIn(new_platform, platforms)
        
        # Remove platform
        self.resolver.remove_platform(new_platform)
        
        # Test that it's no longer detected
        result = self.resolver.detect_platform(test_url)
        self.assertEqual(result, 'unknown')
        
        # Test that it's no longer in the list
        platforms = self.resolver.list_platforms()
        self.assertNotIn(new_platform, platforms)
    
    def test_case_sensitivity(self):
        """Test case sensitivity handling."""
        test_cases = [
            ("https://WWW.YOUTUBE.COM/WATCH?V=ABC123", "youtube"),
            ("https://www.Instagram.com/p/ABC123DEF/", "instagram"),
            ("https://WWW.TIKTOK.COM/@USERNAME/VIDEO/1234567890", "tiktok"),
            ("https://Twitter.com/username/status/1234567890", "twitter"),
        ]
        
        for url, expected_platform in test_cases:
            with self.subTest(url=url):
                result = self.resolver.detect_platform(url)
                self.assertEqual(result, expected_platform, f"Should handle case insensitivity for: {url}")
    
    def test_protocol_handling(self):
        """Test different protocol handling."""
        test_cases = [
            ("https://www.youtube.com/watch?v=ABC123", "youtube"),
            ("http://www.youtube.com/watch?v=ABC123", "youtube"),
            ("//www.youtube.com/watch?v=ABC123", "youtube"),  # Protocol-relative URL
            ("www.youtube.com/watch?v=ABC123", "youtube"),    # No protocol
            ("youtube.com/watch?v=ABC123", "youtube"),        # No protocol or www
        ]
        
        for url, expected_platform in test_cases:
            with self.subTest(url=url):
                result = self.resolver.detect_platform(url)
                self.assertEqual(result, expected_platform, f"Should handle protocol variations for: {url}")


class TestPlatformResolverIntegration(unittest.TestCase):
    """Integration tests for the PlatformResolver."""
    
    def test_batch_processing(self):
        """Test processing multiple URLs efficiently."""
        urls = [
            "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
            "https://www.instagram.com/p/ABC123DEF/",
            "https://www.tiktok.com/@username/video/1234567890",
            "https://twitter.com/username/status/1234567890",
            "https://unknown-site.com/content/123",
        ]
        
        results = []
        for url in urls:
            platform = detect_platform(url)
            results.append((url, platform))
        
        expected_results = [
            ("https://www.youtube.com/watch?v=dQw4w9WgXcQ", "youtube"),
            ("https://www.instagram.com/p/ABC123DEF/", "instagram"),
            ("https://www.tiktok.com/@username/video/1234567890", "tiktok"),
            ("https://twitter.com/username/status/1234567890", "twitter"),
            ("https://unknown-site.com/content/123", "unknown"),
        ]
        
        self.assertEqual(results, expected_results)
    
    def test_performance_test(self):
        """Basic performance test to ensure reasonable execution time."""
        import time
        
        test_urls = [
            "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
            "https://www.instagram.com/p/ABC123DEF/",
            "https://www.tiktok.com/@username/video/1234567890",
            "https://twitter.com/username/status/1234567890",
            "https://unknown-site.com/content/123",
        ] * 100  # Test with 500 URLs
        
        start_time = time.time()
        
        for url in test_urls:
            detect_platform(url)
        
        end_time = time.time()
        execution_time = end_time - start_time
        
        # Should process 500 URLs in less than 1 second
        self.assertLess(execution_time, 1.0, f"Performance test failed: took {execution_time:.2f} seconds")


if __name__ == '__main__':
    # Run the tests
    unittest.main(verbosity=2)