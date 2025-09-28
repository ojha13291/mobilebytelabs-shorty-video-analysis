"""
LLM Client for multiple providers (Mistral, OpenRouter, Ollama)
"""

import os
import json
import logging
import time
from enum import Enum
from typing import Dict, Any, Optional, List
import requests
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)


class LLMProvider(Enum):
    """Supported LLM providers"""
    MISTRAL = "mistral"
    OPENROUTER = "openrouter"
    OLLAMA = "ollama"


class BaseLLMClient(ABC):
    """Abstract base class for LLM clients"""
    
    @abstractmethod
    def generate_response(self, prompt: str, **kwargs) -> Dict[str, Any]:
        """Generate response from LLM"""
        pass
    
    @abstractmethod
    def is_available(self) -> bool:
        """Check if the LLM service is available"""
        pass


class MistralClient(BaseLLMClient):
    """Mistral AI API client"""
    
    def __init__(self, api_key: Optional[str] = None, model: str = "mistral-tiny"):
        self.api_key = api_key or os.getenv('MISTRAL_API_KEY')
        self.model = model
        self.api_url = os.getenv('MISTRAL_API_URL', 'https://api.mistral.ai/v1/chat/completions')
        self.timeout = int(os.getenv('LLM_TIMEOUT', '30'))
        self.max_tokens = int(os.getenv('LLM_MAX_TOKENS', '1000'))
        self.temperature = float(os.getenv('LLM_TEMPERATURE', '0.7'))
    
    def is_available(self) -> bool:
        """Check if Mistral API is available"""
        return bool(self.api_key)
    
    def generate_response(self, prompt: str, **kwargs) -> Dict[str, Any]:
        """Generate response using Mistral API"""
        if not self.is_available():
            raise ValueError("Mistral API key not configured")
        
        headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }
        
        data = {
            'model': kwargs.get('model', self.model),
            'messages': [
                {'role': 'system', 'content': 'You are a helpful assistant that analyzes video content.'},
                {'role': 'user', 'content': prompt}
            ],
            'temperature': kwargs.get('temperature', self.temperature),
            'max_tokens': kwargs.get('max_tokens', self.max_tokens),
            'stream': False
        }
        
        try:
            start_time = time.time()
            response = requests.post(
                self.api_url,
                headers=headers,
                json=data,
                timeout=self.timeout
            )
            
            if response.status_code != 200:
                logger.error(f"Mistral API error: {response.status_code} - {response.text}")
                return {
                    'success': False,
                    'error': f'API error: {response.status_code}',
                    'response': None
                }
            
            result = response.json()
            duration = time.time() - start_time
            
            return {
                'success': True,
                'response': result['choices'][0]['message']['content'],
                'model': result.get('model', self.model),
                'usage': result.get('usage', {}),
                'duration_seconds': duration
            }
            
        except requests.exceptions.Timeout:
            logger.error("Mistral API request timed out")
            return {
                'success': False,
                'error': 'Request timeout',
                'response': None
            }
        except Exception as e:
            logger.error(f"Error calling Mistral API: {e}")
            return {
                'success': False,
                'error': str(e),
                'response': None
            }


class OpenRouterClient(BaseLLMClient):
    """OpenRouter API client"""
    
    TEXT_MODELS = {
        "Mistral Small": "mistralai/mistral-small-3.2-24b-instruct:free",
        "Mistral 3.1": "mistralai/mistral-small-3.1-24b-instruct:free",
        "Gemma": "google/gemma-3-4b-it:free",
    }
    
    def __init__(self, api_key: Optional[str] = None, model: str = "Mistral Small"):
        self.api_key = api_key or os.getenv('OPENROUTER_API_KEY')
        self.model_name = model
        self.model_id = self.TEXT_MODELS.get(model, model)
        self.api_url = os.getenv('OPENROUTER_API_URL', 'https://openrouter.ai/api/v1/chat/completions')
        self.timeout = int(os.getenv('LLM_TIMEOUT', '30'))
        self.max_tokens = int(os.getenv('LLM_MAX_TOKENS', '1000'))
        self.temperature = float(os.getenv('LLM_TEMPERATURE', '0.7'))
    
    def is_available(self) -> bool:
        """Check if OpenRouter API is available"""
        return bool(self.api_key)
    
    def generate_response(self, prompt: str, **kwargs) -> Dict[str, Any]:
        """Generate response using OpenRouter API"""
        if not self.is_available():
            raise ValueError("OpenRouter API key not configured")
        
        headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json',
            'HTTP-Referer': 'https://your-app-url.com',  # Replace with your app URL
            'X-Title': 'Video Sentiment Analyzer'
        }
        
        data = {
            'model': kwargs.get('model', self.model_id),
            'messages': [
                {'role': 'system', 'content': 'You are a helpful assistant that analyzes video content.'},
                {'role': 'user', 'content': prompt}
            ],
            'temperature': kwargs.get('temperature', self.temperature),
            'max_tokens': kwargs.get('max_tokens', self.max_tokens),
            'stream': False
        }
        
        try:
            start_time = time.time()
            response = requests.post(
                self.api_url,
                headers=headers,
                json=data,
                timeout=self.timeout
            )
            
            if response.status_code != 200:
                logger.error(f"OpenRouter API error: {response.status_code} - {response.text}")
                return {
                    'success': False,
                    'error': f'API error: {response.status_code}',
                    'response': None
                }
            
            result = response.json()
            duration = time.time() - start_time
            
            return {
                'success': True,
                'response': result['choices'][0]['message']['content'],
                'model': result.get('model', self.model_id),
                'usage': result.get('usage', {}),
                'duration_seconds': duration
            }
            
        except requests.exceptions.Timeout:
            logger.error("OpenRouter API request timed out")
            return {
                'success': False,
                'error': 'Request timeout',
                'response': None
            }
        except Exception as e:
            logger.error(f"Error calling OpenRouter API: {e}")
            return {
                'success': False,
                'error': str(e),
                'response': None
            }


class OllamaClient(BaseLLMClient):
    """Ollama local LLM client"""
    
    def __init__(self, api_url: Optional[str] = None, model: str = "mistral"):
        self.api_url = api_url or os.getenv('OLLAMA_API_URL', 'http://localhost:11434/api/generate')
        self.model = model or os.getenv('OLLAMA_MODEL', 'mistral')
        self.timeout = int(os.getenv('LLM_TIMEOUT', '60'))  # Longer timeout for local
        self.max_tokens = int(os.getenv('LLM_MAX_TOKENS', '1000'))
        self.temperature = float(os.getenv('LLM_TEMPERATURE', '0.7'))
    
    def is_available(self) -> bool:
        """Check if Ollama service is available"""
        try:
            response = requests.get(
                self.api_url.replace('/api/generate', '/api/tags'),
                timeout=5
            )
            return response.status_code == 200
        except:
            return False
    
    def generate_response(self, prompt: str, **kwargs) -> Dict[str, Any]:
        """Generate response using Ollama API"""
        if not self.is_available():
            raise ValueError("Ollama service not available")
        
        data = {
            'model': kwargs.get('model', self.model),
            'prompt': prompt,
            'stream': False,
            'options': {
                'temperature': kwargs.get('temperature', self.temperature),
                'num_predict': kwargs.get('max_tokens', self.max_tokens)
            }
        }
        
        try:
            start_time = time.time()
            response = requests.post(
                self.api_url,
                json=data,
                timeout=self.timeout
            )
            
            if response.status_code != 200:
                logger.error(f"Ollama API error: {response.status_code} - {response.text}")
                return {
                    'success': False,
                    'error': f'API error: {response.status_code}',
                    'response': None
                }
            
            result = response.json()
            duration = time.time() - start_time
            
            return {
                'success': True,
                'response': result.get('response', ''),
                'model': result.get('model', self.model),
                'usage': {
                    'prompt_tokens': result.get('prompt_eval_count', 0),
                    'completion_tokens': result.get('eval_count', 0),
                    'total_tokens': result.get('prompt_eval_count', 0) + result.get('eval_count', 0)
                },
                'duration_seconds': duration
            }
            
        except requests.exceptions.Timeout:
            logger.error("Ollama API request timed out")
            return {
                'success': False,
                'error': 'Request timeout',
                'response': None
            }
        except Exception as e:
            logger.error(f"Error calling Ollama API: {e}")
            return {
                'success': False,
                'error': str(e),
                'response': None
            }


class LLMClient:
    """Main LLM client that manages multiple providers"""
    
    def __init__(self, provider: str = "mistral", **kwargs):
        """
        Initialize LLM client
        
        Args:
            provider: LLM provider (mistral, openrouter, ollama)
            **kwargs: Additional configuration parameters
        """
        self.provider = LLMProvider(provider.lower())
        self.clients = {
            LLMProvider.MISTRAL: MistralClient(**kwargs),
            LLMProvider.OPENROUTER: OpenRouterClient(**kwargs),
            LLMProvider.OLLAMA: OllamaClient(**kwargs)
        }
        self.current_client = self.clients[self.provider]
    
    def generate_response(self, prompt: str, **kwargs) -> Dict[str, Any]:
        """Generate response using the configured provider"""
        return self.current_client.generate_response(prompt, **kwargs)
    
    def is_available(self) -> bool:
        """Check if the current provider is available"""
        return self.current_client.is_available()
    
    def switch_provider(self, provider: str) -> bool:
        """
        Switch to a different LLM provider
        
        Args:
            provider: New provider name
            
        Returns:
            True if switch successful, False otherwise
        """
        try:
            new_provider = LLMProvider(provider.lower())
            if new_provider in self.clients:
                self.provider = new_provider
                self.current_client = self.clients[new_provider]
                logger.info(f"Switched to {provider} provider")
                return True
            else:
                logger.error(f"Provider {provider} not supported")
                return False
        except ValueError:
            logger.error(f"Invalid provider: {provider}")
            return False
    
    def get_available_providers(self) -> List[str]:
        """Get list of available providers"""
        available = []
        for provider_name, client in self.clients.items():
            if client.is_available():
                available.append(provider_name.value)
        return available
    
    def get_best_available_provider(self) -> Optional[str]:
        """Get the best available provider"""
        available = self.get_available_providers()
        if not available:
            return None
        
        # Priority order: Mistral > OpenRouter > Ollama
        priority_order = ['mistral', 'openrouter', 'ollama']
        for provider in priority_order:
            if provider in available:
                return provider
        
        return available[0] if available else None
    
    def get_client_for_provider(self, provider: str) -> Optional[BaseLLMClient]:
        """Get client for specific provider"""
        try:
            provider_enum = LLMProvider(provider.lower())
            return self.clients.get(provider_enum)
        except ValueError:
            return None
    
    def get_model_for_provider(self, provider: str) -> str:
        """Get model name for specific provider"""
        if provider.lower() == 'mistral':
            return os.getenv('MISTRAL_MODEL', 'mistral-tiny')
        elif provider.lower() == 'openrouter':
            return os.getenv('OPENROUTER_MODEL', 'mistralai/mistral-small-3.1-24b-instruct:free')
        elif provider.lower() == 'ollama':
            return os.getenv('OLLAMA_MODEL', 'mistral')
        return 'unknown'