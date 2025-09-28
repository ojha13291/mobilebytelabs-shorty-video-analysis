"""
Video analyzer for social media content
"""

import json
import time
from typing import Dict, List, Any, Optional
from datetime import datetime


class VideoAnalyzer:
    """
    Analyzer for social media videos/reels
    """
    
    def __init__(self):
        """Initialize the video analyzer"""
        pass
    
    def analyze_reels_batch(self, reels_data: List[Dict[str, Any]], analysis_type: str = 'comprehensive') -> Dict[str, Any]:
        """
        Analyze a batch of reels
        
        Args:
            reels_data: List of reel data to analyze
            analysis_type: Type of analysis to perform
            
        Returns:
            Analysis results
        """
        if not reels_data:
            return {'error': 'No reels data provided'}
        
        results = {
            'total_reels': len(reels_data),
            'analysis_type': analysis_type,
            'timestamp': datetime.now().isoformat(),
            'reels_analysis': []
        }
        
        for reel in reels_data:
            try:
                analysis = self._analyze_single_reel(reel, analysis_type)
                results['reels_analysis'].append(analysis)
            except Exception as e:
                results['reels_analysis'].append({
                    'id': reel.get('id', 'unknown'),
                    'error': f'Analysis failed: {str(e)}'
                })
        
        # Add summary statistics
        results['summary'] = self._generate_summary(results['reels_analysis'])
        
        return results
    
    def _analyze_single_reel(self, reel_data: Dict[str, Any], analysis_type: str) -> Dict[str, Any]:
        """
        Analyze a single reel
        
        Args:
            reel_data: Reel data to analyze
            analysis_type: Type of analysis to perform
            
        Returns:
            Analysis results for the reel
        """
        analysis = {
            'id': reel_data.get('id', 'unknown'),
            'platform': reel_data.get('platform', 'unknown'),
            'analysis_type': analysis_type,
            'timestamp': datetime.now().isoformat()
        }
        
        # Basic engagement analysis
        analysis['engagement'] = self._analyze_engagement(reel_data)
        
        # Content analysis
        if analysis_type in ['comprehensive', 'content']:
            analysis['content'] = self._analyze_content(reel_data)
        
        # Sentiment analysis (mock)
        if analysis_type in ['comprehensive', 'sentiment']:
            analysis['sentiment'] = self._analyze_sentiment(reel_data)
        
        # Trend analysis
        if analysis_type in ['comprehensive', 'trends']:
            analysis['trends'] = self._analyze_trends(reel_data)
        
        return analysis
    
    def _analyze_engagement(self, reel_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze engagement metrics
        
        Args:
            reel_data: Reel data to analyze
            
        Returns:
            Engagement analysis results
        """
        likes = reel_data.get('likes', 0)
        comments = reel_data.get('comments', 0)
        shares = reel_data.get('shares', 0)
        
        total_engagement = likes + comments + shares
        
        # Mock engagement rate calculation
        engagement_rate = (total_engagement / max(likes, 1)) * 100 if likes > 0 else 0
        
        return {
            'likes': likes,
            'comments': comments,
            'shares': shares,
            'total_engagement': total_engagement,
            'engagement_rate': round(engagement_rate, 2),
            'engagement_level': self._get_engagement_level(engagement_rate)
        }
    
    def _analyze_content(self, reel_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze content characteristics
        
        Args:
            reel_data: Reel data to analyze
            
        Returns:
            Content analysis results
        """
        caption = reel_data.get('caption', '')
        hashtags = reel_data.get('hashtags', [])
        mentions = reel_data.get('mentions', [])
        
        return {
            'caption_length': len(caption),
            'hashtag_count': len(hashtags),
            'mention_count': len(mentions),
            'hashtags': hashtags,
            'mentions': mentions,
            'content_type': self._classify_content_type(caption),
            'topics': self._extract_topics(hashtags, caption)
        }
    
    def _analyze_sentiment(self, reel_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze sentiment (mock implementation)
        
        Args:
            reel_data: Reel data to analyze
            
        Returns:
            Sentiment analysis results
        """
        caption = reel_data.get('caption', '').lower()
        
        # Simple keyword-based sentiment analysis
        positive_words = ['amazing', 'awesome', 'great', 'love', 'best', 'fantastic', 'wonderful', 'excellent']
        negative_words = ['terrible', 'awful', 'bad', 'worst', 'hate', 'horrible', 'disappointing']
        
        positive_count = sum(1 for word in positive_words if word in caption)
        negative_count = sum(1 for word in negative_words if word in caption)
        
        if positive_count > negative_count:
            sentiment = 'positive'
            confidence = min(positive_count * 0.3, 0.9)
        elif negative_count > positive_count:
            sentiment = 'negative'
            confidence = min(negative_count * 0.3, 0.9)
        else:
            sentiment = 'neutral'
            confidence = 0.5
        
        return {
            'sentiment': sentiment,
            'confidence': round(confidence, 2),
            'positive_keywords': positive_count,
            'negative_keywords': negative_count
        }
    
    def _analyze_trends(self, reel_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze trend characteristics
        
        Args:
            reel_data: Reel data to analyze
            
        Returns:
            Trend analysis results
        """
        hashtags = reel_data.get('hashtags', [])
        
        # Mock trend analysis
        trending_hashtags = ['trending', 'viral', 'fyp', 'foryou', 'popular']
        trend_score = sum(1 for hashtag in hashtags if hashtag.lower() in trending_hashtags)
        
        return {
            'trend_score': trend_score,
            'trending_hashtags': [h for h in hashtags if h.lower() in trending_hashtags],
            'trend_potential': 'high' if trend_score >= 2 else 'medium' if trend_score == 1 else 'low'
        }
    
    def _get_engagement_level(self, engagement_rate: float) -> str:
        """
        Get engagement level based on engagement rate
        
        Args:
            engagement_rate: Engagement rate percentage
            
        Returns:
            Engagement level description
        """
        if engagement_rate >= 10:
            return 'excellent'
        elif engagement_rate >= 5:
            return 'good'
        elif engagement_rate >= 2:
            return 'average'
        else:
            return 'low'
    
    def _classify_content_type(self, caption: str) -> str:
        """
        Classify content type based on caption
        
        Args:
            caption: Caption text
            
        Returns:
            Content type classification
        """
        caption_lower = caption.lower()
        
        if any(word in caption_lower for word in ['tutorial', 'how to', 'guide', 'tips']):
            return 'educational'
        elif any(word in caption_lower for word in ['funny', 'comedy', 'joke', 'laugh']):
            return 'entertainment'
        elif any(word in caption_lower for word in ['product', 'review', 'unboxing', 'haul']):
            return 'product_review'
        elif any(word in caption_lower for word in ['travel', 'vacation', 'trip', 'adventure']):
            return 'travel'
        elif any(word in caption_lower for word in ['food', 'recipe', 'cooking', 'restaurant']):
            return 'food'
        else:
            return 'general'
    
    def _extract_topics(self, hashtags: List[str], caption: str) -> List[str]:
        """
        Extract topics from hashtags and caption
        
        Args:
            hashtags: List of hashtags
            caption: Caption text
            
        Returns:
            List of topics
        """
        topics = []
        
        # Extract topics from hashtags
        for hashtag in hashtags:
            topic = hashtag.replace('#', '').replace('_', ' ')
            if topic and topic not in topics:
                topics.append(topic)
        
        # Add content type as topic
        content_type = self._classify_content_type(caption)
        if content_type not in topics:
            topics.append(content_type)
        
        return topics[:5]  # Limit to top 5 topics
    
    def _generate_summary(self, analyses: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Generate summary statistics from multiple analyses
        
        Args:
            analyses: List of individual analyses
            
        Returns:
            Summary statistics
        """
        if not analyses:
            return {'error': 'No analyses to summarize'}
        
        total_reels = len(analyses)
        
        # Engagement summary
        engagement_rates = []
        total_likes = 0
        total_comments = 0
        total_shares = 0
        
        # Content summary
        content_types = {}
        all_topics = []
        
        # Sentiment summary
        sentiments = {'positive': 0, 'negative': 0, 'neutral': 0}
        
        for analysis in analyses:
            if 'engagement' in analysis:
                engagement = analysis['engagement']
                engagement_rates.append(engagement.get('engagement_rate', 0))
                total_likes += engagement.get('likes', 0)
                total_comments += engagement.get('comments', 0)
                total_shares += engagement.get('shares', 0)
            
            if 'content' in analysis:
                content = analysis['content']
                content_type = content.get('content_type', 'unknown')
                content_types[content_type] = content_types.get(content_type, 0) + 1
                
                topics = content.get('topics', [])
                all_topics.extend(topics)
            
            if 'sentiment' in analysis:
                sentiment = analysis['sentiment'].get('sentiment', 'neutral')
                sentiments[sentiment] = sentiments.get(sentiment, 0) + 1
        
        # Calculate averages
        avg_engagement_rate = sum(engagement_rates) / len(engagement_rates) if engagement_rates else 0
        
        # Most common topics
        topic_counts = {}
        for topic in all_topics:
            topic_counts[topic] = topic_counts.get(topic, 0) + 1
        top_topics = sorted(topic_counts.items(), key=lambda x: x[1], reverse=True)[:5]
        
        return {
            'total_reels': total_reels,
            'avg_engagement_rate': round(avg_engagement_rate, 2),
            'total_likes': total_likes,
            'total_comments': total_comments,
            'total_shares': total_shares,
            'content_types': content_types,
            'sentiment_distribution': sentiments,
            'top_topics': [{'topic': topic, 'count': count} for topic, count in top_topics]
        }


# Standalone function for backward compatibility
def analyze_reels(reels_data: List[Dict[str, Any]], analysis_type: str = 'comprehensive') -> Dict[str, Any]:
    """
    Standalone function to analyze reels for backward compatibility
    
    Args:
        reels_data: List of reel data to analyze
        analysis_type: Type of analysis to perform
        
    Returns:
        Analysis results
    """
    analyzer = VideoAnalyzer()
    return analyzer.analyze_reels_batch(reels_data, analysis_type)