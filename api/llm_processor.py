"""
LLM Processing Service for video analysis
"""

import requests
import json
import time
from typing import Dict, Any, Optional, List
from datetime import datetime
import os
from flask_sqlalchemy import SQLAlchemy
from api.models import db, LLMAnalysisResult

class LLMProcessor:
    """
    Service for processing video content using LLM APIs
    """
    
    def __init__(self, provider: str = 'mistral'):
        self.provider = provider
        self.api_key = self._get_api_key()
        self.api_url = self._get_api_url()
        self.model = self._get_model()
        self.temperature = float(os.getenv('LLM_TEMPERATURE', '0.7'))
        self.max_tokens = int(os.getenv('LLM_MAX_TOKENS', '1000'))
        self.timeout = int(os.getenv('LLM_TIMEOUT', '30'))
    
    def _get_api_key(self) -> str:
        """Get API key based on provider"""
        if self.provider == 'mistral':
            return os.getenv('MISTRAL_API_KEY', '')
        elif self.provider == 'openrouter':
            return os.getenv('OPENROUTER_API_KEY', '')
        elif self.provider == 'ollama':
            return ''  # Ollama doesn't require API key for local
        return ''
    
    def _get_api_url(self) -> str:
        """Get API URL based on provider"""
        if self.provider == 'mistral':
            return os.getenv('MISTRAL_API_URL', 'https://api.mistral.ai/v1/chat/completions')
        elif self.provider == 'openrouter':
            return 'https://openrouter.ai/api/v1/chat/completions'
        elif self.provider == 'ollama':
            return os.getenv('OLLAMA_API_URL', 'http://localhost:11434/api/generate')
        return ''
    
    def _get_model(self) -> str:
        """Get model name based on provider"""
        if self.provider == 'mistral':
            return os.getenv('MISTRAL_MODEL', 'mistral-tiny')
        elif self.provider == 'openrouter':
            return os.getenv('OPENROUTER_MODEL', 'mistralai/mistral-small-3.1-24b-instruct:free')
        elif self.provider == 'ollama':
            return os.getenv('OLLAMA_MODEL', 'mistral')
        return 'mistral-tiny'
    
    def process_video(self, video_id: str, video_url: str, platform: str, 
                     transcript: Optional[str] = None, metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Process a video using LLM
        
        Args:
            video_id: Unique video identifier
            video_url: Video URL
            platform: Platform name
            transcript: Optional transcript text
            metadata: Optional metadata
            
        Returns:
            Dictionary with analysis results
        """
        start_time = time.time()
        
        try:
            # Check if we already have cached results
            cached_result = self._get_cached_result(video_id)
            if cached_result:
                cached_result['cached'] = True
                return cached_result
            
            # Create new analysis result
            analysis_result = LLMAnalysisResult(
                video_id=video_id,
                video_url=video_url,
                platform=platform,
                llm_provider=self.provider
            )
            
            # Add to database session
            db.session.add(analysis_result)
            db.session.flush()  # Get the ID without committing
            
            # Prepare content for analysis
            content = self._prepare_content(transcript, metadata)
            
            # Generate summary
            summary = self._generate_summary(content, platform)
            analysis_result.summary = summary
            
            # Analyze sentiment
            sentiment_result = self._analyze_sentiment(content)
            analysis_result.sentiment = sentiment_result['sentiment']
            analysis_result.confidence_score = sentiment_result['confidence']
            
            # Extract topics
            topics = self._extract_topics(content)
            analysis_result.set_topics(topics)
            
            # Store transcript if available
            if transcript:
                analysis_result.transcript_used = transcript[:1000]  # Limit transcript length
            
            # Calculate processing duration
            analysis_result.processing_duration_seconds = time.time() - start_time
            
            # Commit to database
            db.session.commit()
            
            return analysis_result.to_dict()
            
        except Exception as e:
            # Handle errors
            error_message = f"Unexpected error: {str(e)}"
            
            # Try to save error to database if we have an analysis result
            try:
                if 'analysis_result' in locals():
                    analysis_result.error_message = error_message
                    analysis_result.processing_duration_seconds = time.time() - start_time
                    db.session.commit()
            except:
                pass  # Don't let database errors mask the original error
            
            # Return error response
            return {
                'video_id': video_id,
                'video_url': video_url,
                'platform': platform,
                'llm_provider': self.provider,
                'summary': None,
                'sentiment': None,
                'confidence_score': 0,
                'topics': [],
                'transcript_used': transcript,
                'processing_duration_seconds': time.time() - start_time,
                'error_message': error_message,
                'cached': False
            }
    
    def _get_cached_result(self, video_id: str) -> Optional[Dict[str, Any]]:
        """Get cached analysis result"""
        try:
            cached_result = LLMAnalysisResult.query.filter_by(video_id=video_id).first()
            if cached_result:
                return cached_result.to_dict()
        except Exception as e:
            print(f"Error retrieving cached result: {e}")
        return None
    
    def _prepare_content(self, transcript: Optional[str], metadata: Optional[Dict[str, Any]]) -> str:
        """Prepare content for analysis"""
        content_parts = []
        
        if metadata:
            title = metadata.get('title', '')
            description = metadata.get('description', '')
            tags = metadata.get('tags', [])
            
            # Check if this is a channel/profile
            if metadata.get('is_channel', False) and metadata.get('channel_data'):
                channel_data = metadata['channel_data']
                content_parts.append("📝 Channel/Profile Information:")
                
                if 'username' in channel_data or 'channel_name' in channel_data:
                    name = channel_data.get('username') or channel_data.get('channel_name', 'Unknown')
                    content_parts.append(f"Name: {name}")
                
                if 'subscribers' in channel_data or 'followers' in channel_data:
                    followers = channel_data.get('subscribers') or channel_data.get('followers', 'Unknown')
                    content_parts.append(f"Followers: {followers}")
                
                if 'total_videos' in channel_data or 'posts_count' in channel_data:
                    content_count = channel_data.get('total_videos') or channel_data.get('posts_count', 'Unknown')
                    content_parts.append(f"Content Count: {content_count}")
                
                if 'biography' in channel_data:
                    content_parts.append(f"Biography: {channel_data['biography']}")
                
                if 'channel_description' in channel_data:
                    content_parts.append(f"Channel Description: {channel_data['channel_description']}")
                
                if 'is_verified' in channel_data:
                    content_parts.append(f"Verified: {'Yes' if channel_data['is_verified'] else 'No'}")
                
                content_parts.append("")
            
            if title:
                content_parts.append(f"Title: {title}")
            if description:
                content_parts.append(f"Description: {description}")
            if tags:
                content_parts.append(f"Tags: {', '.join(tags)}")
        
        if transcript:
            content_parts.append(f"Transcript: {transcript}")
        
        return "\n\n".join(content_parts) if content_parts else "No content available for analysis."
    
    def _generate_summary(self, content: str, platform: str) -> str:
        """Generate content summary using LLM"""
        # Check if this is channel/profile content
        if "Channel/Profile Information:" in content:
            prompt = f"""
            Analyze the following {platform} channel/profile content and provide a comprehensive summary:
            
            {content}
            
            Please provide:
            1. A brief overview of the channel/profile (2-3 sentences)
            2. Key themes, topics, or focus areas
            3. Audience engagement potential based on content and metrics
            4. Overall brand/personality assessment
            
            Channel/Profile Summary:
            """
        else:
            prompt = f"""
            Analyze the following {platform} video content and provide a concise summary:
            
            {content}
            
            Please provide:
            1. A brief summary (2-3 sentences)
            2. Key themes or topics discussed
            3. Overall tone and style
            
            Summary:
            """
        
        return self._call_llm_api(prompt) or "Summary unavailable"
    
    def test_connection(self) -> bool:
        """Test the LLM API connection"""
        try:
            if not self.api_key and self.provider != 'ollama':
                return False
            
            # Simple test prompt
            test_prompt = "Hello, this is a test. Please respond with 'OK'."
            response = self._call_llm_api(test_prompt)
            
            return bool(response and len(response.strip()) > 0)
        except Exception as e:
            print(f"LLM connection test failed: {e}")
            return False
    
    def _analyze_sentiment(self, content: str) -> Dict[str, Any]:
        """Analyze sentiment using LLM"""
        # Check if this is channel/profile content
        if "Channel/Profile Information:" in content:
            prompt = f"""
            Analyze the overall sentiment and brand perception of this channel/profile content:
            
            {content}
            
            Respond with ONLY a JSON object in this exact format:
            {{
                "sentiment": "positive|negative|neutral",
                "confidence": 0.0-1.0,
                "explanation": "brief explanation of brand perception"
            }}
            """
        else:
            prompt = f"""
            Analyze the sentiment of the following content:
            
            {content}
            
            Respond with ONLY a JSON object in this exact format:
            {{
                "sentiment": "positive|negative|neutral",
                "confidence": 0.0-1.0,
                "explanation": "brief explanation"
            }}
            """
        
        response = self._call_llm_api(prompt)
        
        try:
            # Try to parse JSON response
            result = json.loads(response)
            return {
                'sentiment': result.get('sentiment', 'neutral'),
                'confidence': float(result.get('confidence', 0.5))
            }
        except:
            # Fallback to keyword-based analysis
            return self._fallback_sentiment_analysis(content)
    
    def _extract_topics(self, content: str) -> List[str]:
        """Extract topics using LLM"""
        # Check if this is channel/profile content
        if "Channel/Profile Information:" in content:
            prompt = f"""
            Extract the main themes, content focus areas, and brand characteristics from this channel/profile. 
            Respond with ONLY a comma-separated list of themes/characteristics (3-5 maximum):
            
            {content}
            
            Themes/Characteristics:
            """
        else:
            prompt = f"""
            Extract the main topics and themes from this content. 
            Respond with ONLY a comma-separated list of topics (3-5 topics maximum):
            
            {content}
            
            Topics:
            """
        
        response = self._call_llm_api(prompt)
        
        if response and response != "Topics unavailable":
            # Split by comma and clean up
            topics = [topic.strip() for topic in response.split(',') if topic.strip()]
            return topics[:5]  # Limit to 5 topics
        
        return []
    
    def _fallback_sentiment_analysis(self, content: str) -> Dict[str, Any]:
        """Fallback sentiment analysis using keywords"""
        positive_words = ['amazing', 'awesome', 'great', 'love', 'best', 'fantastic', 'wonderful', 'excellent', 'good', 'happy', 'nice']
        negative_words = ['terrible', 'awful', 'bad', 'worst', 'hate', 'horrible', 'disappointing', 'sad', 'angry', 'poor']
        
        content_lower = content.lower()
        
        positive_count = sum(1 for word in positive_words if word in content_lower)
        negative_count = sum(1 for word in negative_words if word in content_lower)
        
        if positive_count > negative_count:
            sentiment = 'positive'
            confidence = min(positive_count * 0.2, 0.8)
        elif negative_count > positive_count:
            sentiment = 'negative'
            confidence = min(negative_count * 0.2, 0.8)
        else:
            sentiment = 'neutral'
            confidence = 0.5
        
        return {
            'sentiment': sentiment,
            'confidence': confidence
        }
    
    def _call_llm_api(self, prompt: str) -> str:
        """Call the LLM API"""
        if not self.api_key and self.provider != 'ollama':
            return f"{self.provider.capitalize()} API key not configured"
        
        try:
            if self.provider == 'mistral':
                return self._call_mistral_api(prompt)
            elif self.provider == 'openrouter':
                return self._call_openrouter_api(prompt)
            elif self.provider == 'ollama':
                return self._call_ollama_api(prompt)
            else:
                return "Unsupported LLM provider"
        except requests.exceptions.RequestException as e:
            print(f"Network error calling {self.provider} API: {e}")
            return f"Network error: {str(e)}"
        except json.JSONDecodeError as e:
            print(f"JSON error in {self.provider} API response: {e}")
            return f"Invalid API response format"
        except KeyError as e:
            print(f"Missing field in {self.provider} API response: {e}")
            return f"Unexpected API response format"
        except Exception as e:
            print(f"Error calling {self.provider} API: {e}")
            return f"{self.provider.capitalize()} API error: {str(e)}"
    
    def _call_mistral_api(self, prompt: str) -> str:
        """Call Mistral API"""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": self.model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": self.temperature,
            "max_tokens": self.max_tokens
        }
        
        response = requests.post(self.api_url, headers=headers, json=payload, timeout=self.timeout)
        response.raise_for_status()
        
        result = response.json()
        return result['choices'][0]['message']['content'].strip()
    
    def _call_openrouter_api(self, prompt: str) -> str:
        """Call OpenRouter API"""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://your-app.com",  # Replace with your app URL
            "X-Title": "Video Analyzer"  # Replace with your app name
        }
        
        payload = {
            "model": self.model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": self.temperature,
            "max_tokens": self.max_tokens
        }
        
        response = requests.post(self.api_url, headers=headers, json=payload, timeout=self.timeout)
        response.raise_for_status()
        
        result = response.json()
        return result['choices'][0]['message']['content'].strip()
    
    def _call_ollama_api(self, prompt: str) -> str:
        """Call Ollama API"""
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": self.temperature,
                "num_predict": self.max_tokens
            }
        }
        
        response = requests.post(self.api_url, json=payload, timeout=self.timeout)
        response.raise_for_status()
        
        result = response.json()
        return result.get('response', 'No response from Ollama').strip()
    
    def process_and_save_video(self, video_data: Dict[str, Any]) -> Optional[LLMAnalysisResult]:
        """
        Process video data and save results to database
        
        Args:
            video_data: Dictionary containing video information
            
        Returns:
            LLMAnalysisResult object if successful, None otherwise
        """
        try:
            video_id = video_data.get('video_id', '')
            video_url = video_data.get('url', '')
            platform = video_data.get('platform', 'unknown')
            transcript = video_data.get('transcript', '')
            
            # Extract metadata
            metadata = {
                'title': video_data.get('title', ''),
                'description': video_data.get('description', ''),
                'tags': video_data.get('tags', []),
                'duration': video_data.get('duration', ''),
                'views': video_data.get('views', ''),
                'likes': video_data.get('likes', ''),
                'channel': video_data.get('channel', ''),
                'upload_date': video_data.get('upload_date', ''),
                'is_channel': video_data.get('is_channel', False),
                'channel_data': video_data.get('channel_data', {})
            }
            
            # Process the video
            result_dict = self.process_video(
                video_id=video_id,
                video_url=video_url,
                platform=platform,
                transcript=transcript,
                metadata=metadata
            )
            
            # Return the saved result from database
            if result_dict and not result_dict.get('error_message'):
                return LLMAnalysisResult.query.filter_by(video_id=video_id).first()
            
            return None
            
        except Exception as e:
            print(f"Error in process_and_save_video: {e}")
            return None