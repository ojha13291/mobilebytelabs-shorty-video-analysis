"""
Video analysis and AI processing functionality
"""

import json
import requests
from typing import Dict, List, Any, Optional
from datetime import datetime

from api.dependencies import get_embedder, get_mistral_config
from api.schemas import ReelData, AnalysisResult
from analyzer.sentiment import analyze_sentiment
from analyzer.embedding import generate_embeddings
from analyzer.summarizer import summarize_content


class VideoAnalyzer:
    """
    Main class for analyzing social media videos/reels
    """
    
    def __init__(self):
        """Initialize the video analyzer with required dependencies"""
        self.embedder = get_embedder()
        self.mistral_config = get_mistral_config()
    
    def analyze_reels_batch(self, reels_data: List[Dict], analysis_type: str = 'comprehensive') -> List[Dict]:
        """
        Analyze a batch of reels
        
        Args:
            reels_data: List of reel data dictionaries
            analysis_type: Type of analysis ('basic', 'sentiment', 'comprehensive')
            
        Returns:
            List of analysis results
        """
        results = []
        
        for reel_data in reels_data:
            try:
                analysis_result = self.analyze_single_reel(reel_data, analysis_type)
                results.append(analysis_result)
            except Exception as e:
                results.append({
                    'error': f'Analysis failed: {str(e)}',
                    'url': reel_data.get('url', 'unknown'),
                    'status': 'failed'
                })
        
        return results
    
    def analyze_single_reel(self, reel_data: Dict, analysis_type: str = 'comprehensive') -> Dict:
        """
        Analyze a single reel
        
        Args:
            reel_data: Dictionary containing reel data
            analysis_type: Type of analysis ('basic', 'sentiment', 'comprehensive')
            
        Returns:
            Dictionary containing analysis results
        """
        # Basic analysis
        basic_analysis = {
            'url': reel_data.get('url'),
            'platform': reel_data.get('platform'),
            'engagement_score': self._calculate_engagement_score(reel_data),
            'content_quality': self._assess_content_quality(reel_data),
            'timestamp': datetime.now().isoformat()
        }
        
        if analysis_type == 'basic':
            return basic_analysis
        
        # Sentiment analysis
        text_content = self._extract_text_content(reel_data)
        sentiment_result = analyze_sentiment(text_content)
        
        sentiment_analysis = {
            **basic_analysis,
            'sentiment': sentiment_result,
            'emotional_tone': self._determine_emotional_tone(sentiment_result),
        }
        
        if analysis_type == 'sentiment':
            return sentiment_analysis
        
        # Comprehensive analysis
        comprehensive_analysis = {
            **sentiment_analysis,
            'summary': summarize_content(text_content),
            'key_themes': self._extract_key_themes(text_content),
            'engagement_prediction': self._predict_engagement(reel_data, sentiment_result),
            'recommendations': self._generate_recommendations(reel_data, sentiment_result),
            'embeddings': generate_embeddings(text_content, self.embedder) if self.embedder else None,
            'ai_analysis': self._call_mistral_api_for_analysis(reel_data, sentiment_result)
        }
        
        return comprehensive_analysis
    
    def _calculate_engagement_score(self, reel_data: Dict) -> float:
        """Calculate engagement score based on likes, comments, shares, and views"""
        likes = reel_data.get('likes', 0) or 0
        comments = reel_data.get('comments', 0) or 0
        shares = reel_data.get('shares', 0) or 0
        views = reel_data.get('views', 1) or 1  # Avoid division by zero
        
        # Simple engagement rate calculation
        engagement_rate = (likes + comments + shares) / max(views, 1)
        
        # Normalize to 0-100 scale
        normalized_score = min(engagement_rate * 100, 100)
        
        return round(normalized_score, 2)
    
    def _assess_content_quality(self, reel_data: Dict) -> str:
        """Assess content quality based on available data"""
        has_description = bool(reel_data.get('description', '').strip())
        has_hashtags = bool(reel_data.get('hashtags', []))
        has_media = bool(reel_data.get('media_url', ''))
        
        quality_score = 0
        if has_description:
            quality_score += 30
        if has_hashtags:
            quality_score += 20
        if has_media:
            quality_score += 30
        
        # Bonus for engagement
        engagement_score = self._calculate_engagement_score(reel_data)
        if engagement_score > 10:
            quality_score += 20
        
        if quality_score >= 80:
            return "Excellent"
        elif quality_score >= 60:
            return "Good"
        elif quality_score >= 40:
            return "Average"
        else:
            return "Needs Improvement"
    
    def _extract_text_content(self, reel_data: Dict) -> str:
        """Extract text content from reel data for analysis"""
        text_parts = []
        
        if reel_data.get('title'):
            text_parts.append(reel_data['title'])
        
        if reel_data.get('description'):
            text_parts.append(reel_data['description'])
        
        if reel_data.get('hashtags'):
            text_parts.extend(reel_data['hashtags'])
        
        return ' '.join(text_parts)
    
    def _determine_emotional_tone(self, sentiment_result: Dict) -> str:
        """Determine emotional tone from sentiment analysis"""
        sentiment_label = sentiment_result.get('label', 'neutral')
        score = sentiment_result.get('score', 0)
        
        if sentiment_label == 'positive':
            return 'optimistic' if score > 0.8 else 'positive'
        elif sentiment_label == 'negative':
            return 'critical' if score > 0.8 else 'negative'
        else:
            return 'neutral'
    
    def _extract_key_themes(self, text_content: str) -> List[str]:
        """Extract key themes from text content"""
        # Simple keyword extraction (can be enhanced with more sophisticated NLP)
        common_words = ['the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by']
        words = text_content.lower().split()
        
        # Filter out common words and short words
        keywords = [word for word in words if len(word) > 3 and word not in common_words]
        
        # Return top 5 most frequent keywords as themes
        from collections import Counter
        word_counts = Counter(keywords)
        return [word for word, count in word_counts.most_common(5)]
    
    def _predict_engagement(self, reel_data: Dict, sentiment_result: Dict) -> str:
        """Predict engagement based on content and sentiment"""
        engagement_score = self._calculate_engagement_score(reel_data)
        sentiment_label = sentiment_result.get('label', 'neutral')
        
        if engagement_score > 15 and sentiment_label in ['positive', 'neutral']:
            return "High engagement expected"
        elif engagement_score > 5 and sentiment_label != 'negative':
            return "Moderate engagement expected"
        else:
            return "Low engagement expected"
    
    def _generate_recommendations(self, reel_data: Dict, sentiment_result: Dict) -> List[str]:
        """Generate recommendations based on analysis"""
        recommendations = []
        
        # Content quality recommendations
        if not reel_data.get('description', '').strip():
            recommendations.append("Add a descriptive caption to improve engagement")
        
        if not reel_data.get('hashtags', []):
            recommendations.append("Use relevant hashtags to increase discoverability")
        
        # Sentiment-based recommendations
        sentiment_label = sentiment_result.get('label', 'neutral')
        if sentiment_label == 'negative':
            recommendations.append("Consider adjusting tone to be more positive for better engagement")
        
        # Engagement recommendations
        engagement_score = self._calculate_engagement_score(reel_data)
        if engagement_score < 5:
            recommendations.append("Low engagement detected - consider posting at optimal times")
        
        if not recommendations:
            recommendations.append("Content looks good - keep up the great work!")
        
        return recommendations[:3]  # Return top 3 recommendations
    
    def _call_mistral_api_for_analysis(self, reel_data: Dict, sentiment_result: Dict) -> Optional[Dict]:
        """Call Mistral API for advanced analysis"""
        if not self.mistral_config['api_key']:
            return None
        
        text_content = self._extract_text_content(reel_data)
        
        prompt = f"""
        Analyze this social media content and provide insights:
        
        Content: {text_content}
        Platform: {reel_data.get('platform', 'unknown')}
        Engagement Score: {self._calculate_engagement_score(reel_data)}
        Sentiment: {sentiment_result}
        
        Please provide:
        1. Content quality assessment
        2. Audience appeal analysis
        3. Viral potential score (0-100)
        4. Specific improvement suggestions
        
        Format as JSON with keys: quality_assessment, audience_appeal, viral_potential, suggestions
        """
        
        try:
            response = requests.post(
                self.mistral_config['api_url'],
                headers={
                    'Authorization': f'Bearer {self.mistral_config["api_key"]}',
                    'Content-Type': 'application/json'
                },
                json={
                    'model': 'mistral-tiny',
                    'messages': [{'role': 'user', 'content': prompt}],
                    'temperature': 0.7,
                    'max_tokens': 500
                }
            )
            
            if response.status_code == 200:
                result = response.json()
                content = result['choices'][0]['message']['content']
                return json.loads(content)
            else:
                return {'error': f'Mistral API error: {response.status_code}'}
        
        except Exception as e:
            return {'error': f'API call failed: {str(e)}'}