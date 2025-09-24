"""
Main entry point for Instagram Reels Microservice
"""
import sys
import os

# Add the src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from instagram_reels_microservice import run_service

if __name__ == '__main__':
    run_service()