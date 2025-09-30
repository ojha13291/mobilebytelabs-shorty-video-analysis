"""
Database models for LLM analysis results
"""

from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from typing import Optional, Dict, Any
import json

db = SQLAlchemy()

class LLMAnalysisResult(db.Model):
    """
    Model for storing LLM analysis results
    """
    __tablename__ = 'llm_analysis_results'
    
    id = db.Column(db.Integer, primary_key=True)
    video_id = db.Column(db.String(255), nullable=False, index=True)
    video_url = db.Column(db.String(500), nullable=False)
    platform = db.Column(db.String(50), nullable=False)
    llm_provider = db.Column(db.String(50), nullable=False, default='mistral')
    
    # Analysis results
    summary = db.Column(db.Text)
    sentiment = db.Column(db.String(50))
    confidence_score = db.Column(db.Float, default=0.0)
    topics = db.Column(db.Text)  # JSON string of topics list
    transcript_used = db.Column(db.Text)
    
    # Metadata
    processing_duration_seconds = db.Column(db.Float, default=0.0)
    error_message = db.Column(db.Text)
    cached = db.Column(db.Boolean, default=False)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __init__(self, video_id: str, video_url: str, platform: str, llm_provider: str = 'mistral'):
        self.video_id = video_id
        self.video_url = video_url
        self.platform = platform
        self.llm_provider = llm_provider
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert model to dictionary"""
        return {
            'video_id': self.video_id,
            'video_url': self.video_url,
            'platform': self.platform,
            'llm_provider': self.llm_provider,
            'summary': self.summary,
            'sentiment': self.sentiment,
            'confidence_score': self.confidence_score,
            'topics': json.loads(self.topics) if self.topics else [],
            'transcript_used': self.transcript_used,
            'processing_duration_seconds': self.processing_duration_seconds,
            'error_message': self.error_message,
            'cached': self.cached,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def set_topics(self, topics_list: list):
        """Set topics from a list"""
        self.topics = json.dumps(topics_list) if topics_list else None
    
    def get_topics(self) -> list:
        """Get topics as a list"""
        try:
            return json.loads(self.topics) if self.topics else []
        except (json.JSONDecodeError, TypeError):
            return []

class ScrapingJob(db.Model):
    """
    Model for tracking scraping jobs
    """
    __tablename__ = 'scraping_jobs'
    
    id = db.Column(db.Integer, primary_key=True)
    job_id = db.Column(db.String(255), unique=True, nullable=False, index=True)
    platform = db.Column(db.String(50), nullable=False)
    target = db.Column(db.String(255), nullable=False)
    status = db.Column(db.String(50), default='pending')  # pending, running, completed, failed
    
    # Results
    results_count = db.Column(db.Integer, default=0)
    error_message = db.Column(db.Text)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    started_at = db.Column(db.DateTime)
    completed_at = db.Column(db.DateTime)
    
    def __init__(self, job_id: str, platform: str, target: str):
        self.job_id = job_id
        self.platform = platform
        self.target = target

# Create indexes for better performance
def create_indexes():
    """Create database indexes for better performance"""
    pass  # Indexes are defined in the model classes above

def init_db(app):
    """Initialize the database with the Flask app"""
    db.init_app(app)
    with app.app_context():
        db.create_all()