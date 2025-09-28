"""
Transcript extraction functionality for video content
"""

import os
import logging
import requests
from typing import Optional, Dict, Any
from urllib.parse import urlparse

logger = logging.getLogger(__name__)


class TranscriptExtractor:
    """Extracts transcripts/captions from video content"""
    
    def __init__(self):
        """Initialize transcript extractor"""
        self.supported_platforms = ['youtube', 'instagram', 'tiktok', 'twitter']
    
    def extract_transcript(self, video_url: str, platform: str = 'auto') -> Optional[str]:
        """
        Extract transcript from video URL
        
        Args:
            video_url: Video URL to extract transcript from
            platform: Platform name (auto-detected if not provided)
            
        Returns:
            Extracted transcript text or None if not available
        """
        try:
            if platform == 'auto':
                platform = self._detect_platform(video_url)
            
            if platform not in self.supported_platforms:
                logger.warning(f"Platform {platform} not supported for transcript extraction")
                return None
            
            logger.info(f"Extracting transcript from {platform} video: {video_url}")
            
            if platform == 'youtube':
                return self._extract_youtube_transcript(video_url)
            elif platform == 'instagram':
                return self._extract_instagram_caption(video_url)
            elif platform == 'tiktok':
                return self._extract_tiktok_transcript(video_url)
            elif platform == 'twitter':
                return self._extract_twitter_caption(video_url)
            else:
                logger.warning(f"Transcript extraction not implemented for {platform}")
                return None
                
        except Exception as e:
            logger.error(f"Error extracting transcript from {video_url}: {e}")
            return None
    
    def _detect_platform(self, video_url: str) -> str:
        """
        Detect platform from video URL
        
        Args:
            video_url: Video URL to analyze
            
        Returns:
            Platform name
        """
        parsed_url = urlparse(video_url)
        domain = parsed_url.netloc.lower()
        
        if 'youtube.com' in domain or 'youtu.be' in domain:
            return 'youtube'
        elif 'instagram.com' in domain:
            return 'instagram'
        elif 'tiktok.com' in domain:
            return 'tiktok'
        elif 'twitter.com' in domain or 'x.com' in domain:
            return 'twitter'
        else:
            return 'unknown'
    
    def _extract_youtube_transcript(self, video_url: str) -> Optional[str]:
        """
        Extract transcript from YouTube video
        
        Args:
            video_url: YouTube video URL
            
        Returns:
            Transcript text or None
        """
        try:
            # Extract video ID from URL
            video_id = self._extract_youtube_video_id(video_url)
            if not video_id:
                logger.error("Could not extract YouTube video ID")
                return None
            
            # Try to get transcript using YouTube API or scraping
            # For now, we'll use a mock approach - in production, you'd use
            # libraries like youtube-transcript-api or YouTube Data API
            logger.info(f"YouTube transcript extraction for video {video_id} - using mock data")
            
            # Mock transcript for demonstration
            mock_transcript = self._get_mock_transcript('youtube', video_id)
            return mock_transcript
            
        except Exception as e:
            logger.error(f"Error extracting YouTube transcript: {e}")
            return None
    
    def _extract_instagram_caption(self, video_url: str) -> Optional[str]:
        """
        Extract caption/description from Instagram reel/post
        
        Args:
            video_url: Instagram video URL
            
        Returns:
            Caption text or None
        """
        try:
            # Extract post ID from URL
            post_id = self._extract_instagram_post_id(video_url)
            if not post_id:
                logger.error("Could not extract Instagram post ID")
                return None
            
            logger.info(f"Instagram caption extraction for post {post_id}")
            
            # Mock caption for demonstration
            # In production, you'd use Instagram API or scraping
            mock_caption = self._get_mock_transcript('instagram', post_id)
            return mock_caption
            
        except Exception as e:
            logger.error(f"Error extracting Instagram caption: {e}")
            return None
    
    def _extract_tiktok_transcript(self, video_url: str) -> Optional[str]:
        """
        Extract transcript/description from TikTok video
        
        Args:
            video_url: TikTok video URL
            
        Returns:
            Transcript text or None
        """
        try:
            # Extract video ID from URL
            video_id = self._extract_tiktok_video_id(video_url)
            if not video_id:
                logger.error("Could not extract TikTok video ID")
                return None
            
            logger.info(f"TikTok transcript extraction for video {video_id}")
            
            # Mock transcript for demonstration
            mock_transcript = self._get_mock_transcript('tiktok', video_id)
            return mock_transcript
            
        except Exception as e:
            logger.error(f"Error extracting TikTok transcript: {e}")
            return None
    
    def _extract_twitter_caption(self, video_url: str) -> Optional[str]:
        """
        Extract caption/description from Twitter video
        
        Args:
            video_url: Twitter video URL
            
        Returns:
            Caption text or None
        """
        try:
            # Extract tweet ID from URL
            tweet_id = self._extract_twitter_tweet_id(video_url)
            if not tweet_id:
                logger.error("Could not extract Twitter tweet ID")
                return None
            
            logger.info(f"Twitter caption extraction for tweet {tweet_id}")
            
            # Mock caption for demonstration
            mock_caption = self._get_mock_transcript('twitter', tweet_id)
            return mock_caption
            
        except Exception as e:
            logger.error(f"Error extracting Twitter caption: {e}")
            return None
    
    def _extract_youtube_video_id(self, url: str) -> Optional[str]:
        """Extract YouTube video ID from URL"""
        import re
        
        # Various YouTube URL patterns
        patterns = [
            r'(?:v=|\/)([0-9A-Za-z_-]{11}).*',
            r'(?:embed\/)([0-9A-Za-z_-]{11})',
            r'(?:v\/)([0-9A-Za-z_-]{11})'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        
        return None
    
    def _extract_instagram_post_id(self, url: str) -> Optional[str]:
        """Extract Instagram post ID from URL"""
        import re
        
        # Instagram URL patterns
        patterns = [
            r'\/p\/([A-Za-z0-9_-]+)',
            r'\/reel\/([A-Za-z0-9_-]+)',
            r'\/tv\/([A-Za-z0-9_-]+)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        
        return None
    
    def _extract_tiktok_video_id(self, url: str) -> Optional[str]:
        """Extract TikTok video ID from URL"""
        import re
        
        # TikTok URL pattern
        pattern = r'\/video\/([0-9]+)'
        match = re.search(pattern, url)
        
        return match.group(1) if match else None
    
    def _extract_twitter_tweet_id(self, url: str) -> Optional[str]:
        """Extract Twitter tweet ID from URL"""
        import re
        
        # Twitter URL pattern
        pattern = r'\/status\/([0-9]+)'
        match = re.search(pattern, url)
        
        return match.group(1) if match else None
    
    def _get_mock_transcript(self, platform: str, content_id: str) -> str:
        """
        Get mock transcript for demonstration purposes
        
        Args:
            platform: Platform name
            content_id: Content identifier
            
        Returns:
            Mock transcript text
        """
        # This is for demonstration - in production, you'd implement
        # actual transcript extraction using appropriate APIs
        mock_transcripts = {
            'youtube': [
                "In this video, I'm going to show you how to make the perfect coffee at home. We'll cover everything from selecting the right beans to brewing techniques that will elevate your morning routine.",
                "Welcome back to my channel! Today we're discussing the latest trends in technology and how they're shaping our future. From AI to renewable energy, there's so much to explore.",
                "Hey everyone! In this tutorial, I'll walk you through the basics of photography composition. Whether you're a beginner or looking to improve your skills, these tips will help you take better photos."
            ],
            'instagram': [
                "Just finished an amazing workout! Feeling energized and ready to take on the day. Remember, consistency is key when it comes to fitness. 💪 #fitness #motivation #health",
                "Coffee and contemplation. Sometimes the best ideas come when you least expect them. What are you working on today? ☕ #coffee #productivity #mindfulness",
                "Sunset vibes from my favorite spot. Nature has a way of putting things into perspective. Grateful for these peaceful moments. 🌅 #sunset #nature #gratitude"
            ],
            'tiktok': [
                "POV: When you finally understand that complicated concept after studying for hours 📚✨ The feeling is unmatched! Who else can relate?",
                "Life hack: This simple trick will change how you organize your workspace forever! Trust me, your productivity will thank you later. 🚀",
                "Tell me you grew up in the 90s without telling me... I'll go first: I still remember the sound of dial-up internet connecting 😂 #90s #nostalgia"
            ],
            'twitter': [
                "Just launched my new project! After months of hard work, it's finally live. Check it out and let me know what you think. Feedback appreciated! 🚀",
                "Hot take: Remote work isn't just about location flexibility. It's about trusting people to manage their time and deliver results. The future is asynchronous.",
                "Reminder: Your mental health is just as important as your physical health. Take breaks, set boundaries, and prioritize self-care. You can't pour from an empty cup."
            ]
        }
        
        # Select mock transcript based on content ID hash
        import hashlib
        hash_val = int(hashlib.md5(content_id.encode()).hexdigest(), 16)
        transcripts = mock_transcripts.get(platform, ["No transcript available"])
        return transcripts[hash_val % len(transcripts)]
    
    def get_transcript_summary(self, video_url: str, max_length: int = 500) -> Optional[str]:
        """
        Get a summarized version of the transcript
        
        Args:
            video_url: Video URL
            max_length: Maximum length of summary
            
        Returns:
            Summarized transcript or None
        """
        transcript = self.extract_transcript(video_url)
        if not transcript:
            return None
        
        if len(transcript) <= max_length:
            return transcript
        
        # Simple truncation with ellipsis
        return transcript[:max_length].rsplit(' ', 1)[0] + '...'