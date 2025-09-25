"""
Text summarization functionality
"""

from typing import List, Optional
import re


def summarize_content(text: str, max_length: int = 150) -> str:
    """
    Summarize the given text content
    
    Args:
        text: Text to summarize
        max_length: Maximum length of the summary
        
    Returns:
        Summarized text
    """
    if not text or not text.strip():
        return "No content available"
    
    # Clean the text
    text = text.strip()
    
    # If text is already short enough, return as is
    if len(text) <= max_length:
        return text
    
    # Simple extractive summarization
    sentences = _split_into_sentences(text)
    
    if not sentences:
        return text[:max_length] + "..."
    
    # Score sentences based on various factors
    sentence_scores = []
    for i, sentence in enumerate(sentences):
        score = 0
        
        # Position score (first and last sentences are important)
        if i == 0 or i == len(sentences) - 1:
            score += 2
        
        # Length score (prefer medium-length sentences)
        if 10 <= len(sentence.split()) <= 30:
            score += 1
        
        # Keyword score (sentences with important words)
        keywords = _extract_keywords(text)
        keyword_count = sum(1 for keyword in keywords if keyword.lower() in sentence.lower())
        score += keyword_count * 0.5
        
        # Sentiment score (sentences with strong sentiment)
        if _has_strong_sentiment(sentence):
            score += 1
        
        sentence_scores.append((sentence, score))
    
    # Sort by score and select top sentences
    sentence_scores.sort(key=lambda x: x[1], reverse=True)
    
    # Build summary
    summary_sentences = []
    current_length = 0
    
    for sentence, score in sentence_scores:
        if current_length + len(sentence) <= max_length:
            summary_sentences.append(sentence)
            current_length += len(sentence)
        else:
            break
    
    # Sort sentences by original order
    summary_sentences.sort(key=lambda x: sentences.index(x))
    
    summary = ' '.join(summary_sentences)
    
    # Ensure we don't exceed max_length
    if len(summary) > max_length:
        summary = summary[:max_length].rsplit(' ', 1)[0] + "..."
    
    return summary if summary else text[:max_length] + "..."


def _split_into_sentences(text: str) -> List[str]:
    """Split text into sentences"""
    # Simple sentence splitting (can be improved with proper NLP)
    sentences = re.split(r'[.!?]+', text)
    return [s.strip() for s in sentences if s.strip()]


def _extract_keywords(text: str) -> List[str]:
    """Extract important keywords from text"""
    # Simple keyword extraction (can be improved with TF-IDF or other methods)
    words = re.findall(r'\b\w+\b', text.lower())
    
    # Filter out common stop words
    stop_words = {
        'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by',
        'a', 'an', 'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has',
        'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may', 'might',
        'this', 'that', 'these', 'those', 'i', 'you', 'he', 'she', 'it', 'we', 'they',
        'me', 'him', 'her', 'us', 'them', 'my', 'your', 'his', 'her', 'its', 'our', 'their'
    }
    
    # Count word frequencies
    word_counts = {}
    for word in words:
        if word not in stop_words and len(word) > 3:
            word_counts[word] = word_counts.get(word, 0) + 1
    
    # Return most frequent words as keywords
    sorted_words = sorted(word_counts.items(), key=lambda x: x[1], reverse=True)
    return [word for word, count in sorted_words[:10]]


def _has_strong_sentiment(sentence: str) -> bool:
    """Check if sentence has strong sentiment"""
    positive_words = [
        'amazing', 'awesome', 'great', 'excellent', 'fantastic', 'wonderful',
        'love', 'like', 'enjoy', 'happy', 'excited', 'perfect', 'best',
        'good', 'nice', 'beautiful', 'incredible', 'outstanding', 'brilliant'
    ]
    
    negative_words = [
        'terrible', 'awful', 'bad', 'horrible', 'hate', 'dislike', 'angry',
        'sad', 'disappointed', 'frustrated', 'annoying', 'worst', 'boring',
        'stupid', 'dumb', 'ugly', 'disgusting', 'pathetic', 'useless'
    ]
    
    sentence_lower = sentence.lower()
    
    # Check for strong positive or negative words
    has_positive = any(word in sentence_lower for word in positive_words)
    has_negative = any(word in sentence_lower for word in negative_words)
    
    return has_positive or has_negative