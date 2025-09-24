"""
AI Analysis service for Instagram Reels
Provides content analysis using Mistral AI and embeddings
"""
import logging
import requests
import json
from typing import List, Optional, Dict, Any
from datetime import datetime
import torch
from sentence_transformers import SentenceTransformer

from ..models import ReelData, ReelAnalysis
from ..config import config

logger = logging.getLogger(__name__)

class AIAnalyzer:
    """AI analysis service for reel content"""
    
    def __init__(self):
        self.embedder = None
        self._setup_embedding_model()
    
    def _setup_embedding_model(self):
        """Setup the sentence transformer model for embeddings"""
        try:
            device = 'cuda' if torch.cuda.is_available() else 'cpu'
            self.embedder = SentenceTransformer('all-MiniLM-L6-v2', device=device)
            
            # Handle potential meta tensor issues
            if device == 'cuda' and torch.cuda.is_available():
                try:
                    if hasattr(self.embedder, 'to_empty'):
                        self.embedder = self.embedder.to_empty(device)
                    else:
                        self.embedder = self.embedder.to(device)
                except RuntimeError as e:
                    if "Cannot copy out of meta tensor" in str(e):
                        logger.warning("CUDA meta tensor error detected, falling back to CPU")
                        self.embedder.to('cpu')
                    else:
                        raise
            
            logger.info("Successfully initialized embedding model")
            
        except Exception as e:
            logger.error(f"Failed to initialize embedding model: {e}")
            self.embedder = None
    
    def _call_mistral_api(self, prompt: str) -> Optional[str]:
        """Call Mistral AI API for text generation"""
        if not config.mistral.api_key:
            logger.error("Mistral API key not configured")
            return None
        
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "Authorization": f"Bearer {config.mistral.api_key}"
        }
        
        payload = {
            "model": config.mistral.model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": config.mistral.temperature,
            "max_tokens": config.mistral.max_tokens
        }
        
        try:
            response = requests.post(
                config.mistral.api_url, 
                headers=headers, 
                json=payload, 
                timeout=30
            )
            response.raise_for_status()
            
            result = response.json()
            return result["choices"][0]["message"]["content"].strip()
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Mistral API request failed: {e}")
            return None
        except (KeyError, IndexError) as e:
            logger.error(f"Failed to parse Mistral API response: {e}")
            return None
    
    def _generate_summary(self, caption: str, comments: List[str]) -> str:
        """Generate AI summary of reel content"""
        comments_text = " ".join(comments[:5])  # Use top 5 comments
        
        prompt = f"""
        Analyze this Instagram reel and provide a concise summary:
        
        Caption: {caption}
        Top Comments: {comments_text}
        
        Please provide:
        1. A brief summary of what the reel is about (1-2 sentences)
        2. The main theme or topic
        3. Key points or message
        
        Keep the response concise and informative.
        """
        
        return self._call_mistral_api(prompt)
    
    def _categorize_content(self, caption: str, comments: List[str]) -> List[str]:
        """Categorize the reel content"""
        comments_text = " ".join(comments[:3])
        
        prompt = f"""
        Categorize this Instagram reel content into relevant categories:
        
        Caption: {caption}
        Sample Comments: {comments_text}
        
        Available categories: Comedy, Entertainment, Education, Technology, Fashion, Beauty, Fitness, Food, Travel, Music, Dance, Art, Sports, Gaming, Lifestyle, Business, News, Politics, Science, Health, DIY, Pets, Nature, Photography, Motivation, Other
        
        Return only the most relevant categories (max 3) as a comma-separated list.
        Example: Comedy, Entertainment, Music
        """
        
        result = self._call_mistral_api(prompt)
        if result:
            categories = [cat.strip() for cat in result.split(',')]
            return [cat for cat in categories if cat and cat != 'Other']
        
        return ["Entertainment"]  # Default category
    
    def _analyze_sentiment(self, caption: str, comments: List[str]) -> str:
        """Analyze sentiment of the reel content"""
        comments_text = " ".join(comments[:5])
        
        prompt = f"""
        Analyze the sentiment of this Instagram reel:
        
        Caption: {caption}
        Comments: {comments_text}
        
        Classify the overall sentiment as one of: Positive, Negative, Neutral, Mixed
        Consider both the caption tone and comment reactions.
        
        Return only the sentiment classification.
        """
        
        result = self._call_mistral_api(prompt)
        return result if result in ["Positive", "Negative", "Neutral", "Mixed"] else "Neutral"
    
    def _summarize_comments(self, comments: List[str]) -> str:
        """Summarize the main themes in comments"""
        if not comments:
            return "No comments available"
        
        comments_text = " ".join(comments[:10])  # Use up to 10 comments
        
        prompt = f"""
        Analyze these Instagram comments and summarize the main themes and reactions:
        
        Comments: {comments_text}
        
        Provide a brief summary (1-2 sentences) of:
        1. Main themes in the comments
        2. Overall reaction/engagement type
        3. Any notable patterns
        
        Keep it concise and informative.
        """
        
        return self._call_mistral_api(prompt)
    
    def _extract_keywords(self, caption: str, comments: List[str]) -> List[str]:
        """Extract key topics and keywords"""
        text = f"{caption} {' '.join(comments[:3])}"
        
        prompt = f"""
        Extract the main keywords and topics from this text:
        
        Text: {text}
        
        Return the top 5-7 most relevant keywords/topics as a comma-separated list.
        Focus on proper nouns, key themes, and important concepts.
        """
        
        result = self._call_mistral_api(prompt)
        if result:
            keywords = [kw.strip() for kw in result.split(',')]
            return [kw for kw in keywords if len(kw) > 2][:7]  # Max 7 keywords
        
        return []
    
    def generate_embeddings(self, text: str) -> Optional[List[float]]:
        """Generate embeddings for text content"""
        if not self.embedder:
            logger.warning("Embedding model not available")
            return None
        
        try:
            embedding = self.embedder.encode(text, convert_to_tensor=False)
            return embedding.tolist()
        except Exception as e:
            logger.error(f"Failed to generate embeddings: {e}")
            return None
    
    def analyze_reel(self, reel: ReelData) -> ReelAnalysis:
        """Perform comprehensive AI analysis on a reel"""
        logger.info(f"Analyzing reel {reel.reel_id}")
        
        # Prepare text data
        caption = reel.caption or ""
        comments_text = [comment.comment for comment in reel.top_comments]
        
        # Generate analysis components
        summary = self._generate_summary(caption, comments_text) or "Analysis unavailable"
        categories = self._categorize_content(caption, comments_text) or ["Entertainment"]
        sentiment = self._analyze_sentiment(caption, comments_text) or "Neutral"
        comment_summary = self._summarize_comments(comments_text) or "No comments analysis available"
        keywords = self._extract_keywords(caption, comments_text)
        
        analysis = ReelAnalysis(
            summary=summary,
            category=categories,
            sentiment=sentiment,
            top_comment_summary=comment_summary,
            keywords=keywords
        )
        
        logger.info(f"Completed analysis for reel {reel.reel_id}")
        return analysis
    
    def analyze_batch(self, reels: List[ReelData]) -> List[ReelData]:
        """Analyze multiple reels"""
        logger.info(f"Starting batch analysis for {len(reels)} reels")
        
        for i, reel in enumerate(reels):
            try:
                # Perform AI analysis
                analysis = self.analyze_reel(reel)
                reel.analysis = analysis
                
                # Generate embeddings for caption
                if reel.caption:
                    embeddings = self.generate_embeddings(reel.caption)
                    reel.embeddings = embeddings
                
                logger.info(f"Analyzed reel {i+1}/{len(reels)}: {reel.reel_id}")
                
            except Exception as e:
                logger.error(f"Failed to analyze reel {reel.reel_id}: {e}")
                # Continue with other reels even if one fails
                continue
        
        logger.info(f"Completed batch analysis for {len(reels)} reels")
        return reels