"""
Sentiment analysis functionality
"""

from typing import Dict
import re


def analyze_sentiment(text: str) -> Dict[str, any]:
    """
    Analyze sentiment of the given text
    
    Args:
        text: Text to analyze
        
    Returns:
        Dictionary with sentiment analysis results
    """
    if not text or not text.strip():
        return {
            'label': 'neutral',
            'score': 0.5,
            'confidence': 0.0
        }
    
    # Simple rule-based sentiment analysis (can be enhanced with ML models)
    text_lower = text.lower()
    
    # Positive indicators
    positive_words = [
        'amazing', 'awesome', 'great', 'excellent', 'fantastic', 'wonderful',
        'love', 'like', 'enjoy', 'happy', 'excited', 'perfect', 'best',
        'good', 'nice', 'beautiful', 'incredible', 'outstanding', 'brilliant',
        'fun', 'funny', 'laugh', 'smile', 'joy', 'blessed', 'grateful'
    ]
    
    # Negative indicators
    negative_words = [
        'terrible', 'awful', 'bad', 'horrible', 'hate', 'dislike', 'angry',
        'sad', 'disappointed', 'frustrated', 'annoying', 'worst', 'boring',
        'stupid', 'dumb', 'ugly', 'disgusting', 'pathetic', 'useless',
        'fail', 'failure', 'problem', 'issue', 'concern', 'worry'
    ]
    
    # Count positive and negative words
    positive_count = sum(1 for word in positive_words if word in text_lower)
    negative_count = sum(1 for word in negative_words if word in text_lower)
    
    # Calculate sentiment score
    total_words = len(text_lower.split())
    sentiment_score = (positive_count - negative_count) / max(total_words, 1)
    
    # Determine sentiment label
    if positive_count > negative_count:
        label = 'positive'
        confidence = min(positive_count / max(total_words, 1) * 10, 1.0)
    elif negative_count > positive_count:
        label = 'negative'
        confidence = min(negative_count / max(total_words, 1) * 10, 1.0)
    else:
        label = 'neutral'
        confidence = 0.5
    
    # Additional sentiment indicators
    emoji_sentiment = _analyze_emoji_sentiment(text)
    punctuation_sentiment = _analyze_punctuation_sentiment(text)
    
    # Combine sentiments
    if emoji_sentiment != 'neutral':
        if emoji_sentiment == label:
            confidence = min(confidence * 1.2, 1.0)
        else:
            confidence *= 0.8
    
    return {
        'label': label,
        'score': sentiment_score,
        'confidence': round(confidence, 3),
        'positive_indicators': positive_count,
        'negative_indicators': negative_count,
        'emoji_sentiment': emoji_sentiment,
        'punctuation_sentiment': punctuation_sentiment
    }


def _analyze_emoji_sentiment(text: str) -> str:
    """Analyze sentiment based on emojis"""
    positive_emojis = ['😊', '😄', '😃', '😁', '😆', '😂', '🤣', '😍', '🥰', '😘', '💕', '❤️', '💜', '🧡', '💛', '💚', '💙', '🖤', '🤍', '🤎', '💯', '🔥', '✨', '🎉', '🎊', '🌟', '⭐', '👍', '👏', '🙌', '✅', '✔️']
    negative_emojis = ['😢', '😭', '😞', '😔', '😟', '😕', '🙁', '☹️', '😣', '😖', '😫', '😩', '🥺', '😰', '😨', '😧', '😦', '😥', '😓', '😒', '🙄', '😤', '😠', '😡', '🤬', '👎', '💔', '🚫', '❌', '⚠️', '😱']
    
    positive_count = sum(1 for emoji in positive_emojis if emoji in text)
    negative_count = sum(1 for emoji in negative_emojis if emoji in text)
    
    if positive_count > negative_count:
        return 'positive'
    elif negative_count > positive_count:
        return 'negative'
    else:
        return 'neutral'


def _analyze_punctuation_sentiment(text: str) -> str:
    """Analyze sentiment based on punctuation patterns"""
    exclamation_count = text.count('!')
    question_count = text.count('?')
    
    if exclamation_count > 2:
        return 'positive'  # Excitement
    elif question_count > 2:
        return 'negative'  # Confusion/concern
    else:
        return 'neutral'