"""
Dependencies and shared objects for the API
"""

import os
import torch
from sentence_transformers import SentenceTransformer
from typing import Optional

# Global instances
_embedder: Optional[SentenceTransformer] = None


def get_embedder() -> Optional[SentenceTransformer]:
    """
    Get or create the sentence transformer embedder instance
    
    Returns:
        Optional[SentenceTransformer]: The embedder instance or None if initialization fails
    """
    global _embedder
    
    if _embedder is None:
        try:
            # Fix for 'Cannot copy out of meta tensor' error
            device = 'cuda' if torch.cuda.is_available() else 'cpu'
            # Initialize with device specification and additional parameters to avoid meta tensor error
            _embedder = SentenceTransformer('all-MiniLM-L6-v2', device=device)
            # Force model to CPU if needed to avoid meta tensor issues
            if device == 'cuda' and torch.cuda.is_available():
                try:
                    # Use to_empty() instead of to() for meta tensors
                    _embedder = _embedder.to_empty(device) if hasattr(_embedder, 'to_empty') else _embedder.to(device)
                except RuntimeError as e:
                    if "Cannot copy out of meta tensor" in str(e):
                        print("CUDA meta tensor error detected, falling back to CPU")
                        _embedder.to('cpu')
                    else:
                        raise e
        except Exception as e:
            print(f"Error initializing SentenceTransformer: {str(e)}")
            # Fallback to simple embedding if model fails to load
            _embedder = None
    
    return _embedder


def get_mistral_config() -> dict:
    """
    Get Mistral API configuration
    
    Returns:
        dict: Configuration dictionary with API URL and key
    """
    return {
        'api_url': "https://api.mistral.ai/v1/chat/completions",
        'api_key': os.getenv('MISTRAL_API_KEY', '')
    }


def get_instagram_credentials() -> dict:
    """
    Get Instagram credentials from environment variables
    
    Returns:
        dict: Dictionary with username and password
    """
    return {
        'username': os.getenv('INSTAGRAM_USERNAME', ''),
        'password': os.getenv('INSTAGRAM_PASSWORD', '')
    }