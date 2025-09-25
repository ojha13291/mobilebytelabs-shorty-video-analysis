"""
Text embedding functionality
"""

from typing import List, Optional
import numpy as np


def generate_embeddings(text: str, embedder) -> Optional[List[float]]:
    """
    Generate embeddings for the given text using the provided embedder
    
    Args:
        text: Text to generate embeddings for
        embedder: SentenceTransformer embedder instance
        
    Returns:
        List of embedding vectors or None if generation fails
    """
    if not text or not text.strip():
        return None
    
    if not embedder:
        return None
    
    try:
        # Generate embedding
        embedding = embedder.encode(text, convert_to_numpy=True)
        
        # Convert to list for JSON serialization
        return embedding.tolist()
    
    except Exception as e:
        print(f"Error generating embeddings: {str(e)}")
        return None


def generate_batch_embeddings(texts: List[str], embedder) -> List[Optional[List[float]]]:
    """
    Generate embeddings for multiple texts
    
    Args:
        texts: List of texts to generate embeddings for
        embedder: SentenceTransformer embedder instance
        
    Returns:
        List of embedding vectors
    """
    if not texts or not embedder:
        return []
    
    try:
        # Generate embeddings for all texts at once
        embeddings = embedder.encode(texts, convert_to_numpy=True)
        
        # Convert to list format
        return [embedding.tolist() for embedding in embeddings]
    
    except Exception as e:
        print(f"Error generating batch embeddings: {str(e)}")
        return [None] * len(texts)


def calculate_similarity(embedding1: List[float], embedding2: List[float]) -> float:
    """
    Calculate cosine similarity between two embeddings
    
    Args:
        embedding1: First embedding vector
        embedding2: Second embedding vector
        
    Returns:
        Cosine similarity score (0-1)
    """
    if not embedding1 or not embedding2:
        return 0.0
    
    try:
        # Convert to numpy arrays
        vec1 = np.array(embedding1)
        vec2 = np.array(embedding2)
        
        # Calculate cosine similarity
        similarity = np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))
        
        return float(similarity)
    
    except Exception as e:
        print(f"Error calculating similarity: {str(e)}")
        return 0.0