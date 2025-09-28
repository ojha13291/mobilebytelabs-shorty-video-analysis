"""
Database models and manager for LLM analysis results
"""

import os
import json
import logging
from datetime import datetime
from typing import Optional, List, Dict, Any
from sqlalchemy import create_engine, Column, String, DateTime, Text, JSON, Integer
from sqlalchemy.orm import declarative_base, sessionmaker, Session
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

logger = logging.getLogger(__name__)

Base = declarative_base()


class LLMAnalysisResult(Base):
    """Database model for LLM analysis results"""
    
    __tablename__ = 'llm_analysis_results'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    video_id = Column(String(255), nullable=False, unique=True, index=True)
    summary = Column(Text, nullable=True)
    topics = Column(JSON, nullable=True)  # List of strings
    sentiment = Column(String(50), nullable=True)  # positive|neutral|negative
    confidence_score = Column(Integer, nullable=True)  # 0-100
    processing_metadata = Column(JSON, nullable=True)  # Additional metadata
    error_message = Column(Text, nullable=True)
    llm_provider = Column(String(100), nullable=True)
    llm_model = Column(String(255), nullable=True)
    processing_duration_seconds = Column(Integer, nullable=True)
    transcript_used = Column(Text, nullable=True)
    processed_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert model instance to dictionary"""
        return {
            'video_id': self.video_id,
            'summary': self.summary,
            'topics': self.topics or [],
            'sentiment': self.sentiment,
            'confidence_score': self.confidence_score,
            'processing_metadata': self.processing_metadata or {},
            'error_message': self.error_message,
            'llm_provider': self.llm_provider,
            'llm_model': self.llm_model,
            'processing_duration_seconds': self.processing_duration_seconds,
            'transcript_used': self.transcript_used,
            'processed_at': self.processed_at.isoformat() if self.processed_at else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class DatabaseManager:
    """Manages database operations for LLM analysis results"""
    
    def __init__(self, database_url: Optional[str] = None):
        """
        Initialize database manager
        
        Args:
            database_url: Database connection URL. If None, uses DATABASE_URL env var
        """
        self.database_url = database_url or os.getenv('DATABASE_URL', 'sqlite:///llm_analysis.db')
        self.engine = create_engine(self.database_url, echo=False)
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        
        # Create tables
        self._create_tables()
    
    def _create_tables(self):
        """Create database tables if they don't exist"""
        try:
            Base.metadata.create_all(bind=self.engine)
            logger.info("Database tables created successfully")
        except SQLAlchemyError as e:
            logger.error(f"Error creating database tables: {e}")
            raise
    
    def get_session(self) -> Session:
        """Get database session"""
        return self.SessionLocal()
    
    def get_analysis_by_video_id(self, video_id: str) -> Optional[LLMAnalysisResult]:
        """
        Get analysis result by video ID
        
        Args:
            video_id: Unique video identifier
            
        Returns:
            LLMAnalysisResult instance or None if not found
        """
        with self.get_session() as session:
            return session.query(LLMAnalysisResult).filter(
                LLMAnalysisResult.video_id == video_id
            ).first()
    
    def analysis_exists(self, video_id: str) -> bool:
        """
        Check if analysis exists for video ID
        
        Args:
            video_id: Unique video identifier
            
        Returns:
            True if analysis exists, False otherwise
        """
        return self.get_analysis_by_video_id(video_id) is not None
    
    def save_analysis(self, analysis_data: Dict[str, Any]) -> Optional[LLMAnalysisResult]:
        """
        Save analysis result to database
        
        Args:
            analysis_data: Dictionary containing analysis results
            
        Returns:
            Saved LLMAnalysisResult instance or None if error
        """
        try:
            with self.get_session() as session:
                # Check if analysis already exists
                existing = self.get_analysis_by_video_id(analysis_data['video_id'])
                
                if existing:
                    # Update existing record
                    for key, value in analysis_data.items():
                        if hasattr(existing, key) and key not in ['id', 'created_at']:
                            setattr(existing, key, value)
                    existing.updated_at = datetime.utcnow()
                    result = existing
                else:
                    # Create new record
                    result = LLMAnalysisResult(**analysis_data)
                    session.add(result)
                
                session.commit()
                logger.info(f"Analysis saved for video_id: {analysis_data['video_id']}")
                return result
                
        except IntegrityError as e:
            logger.error(f"Integrity error saving analysis: {e}")
            return None
        except SQLAlchemyError as e:
            logger.error(f"Database error saving analysis: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error saving analysis: {e}")
            return None
    
    def get_analyses_by_sentiment(self, sentiment: str, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Get analyses by sentiment
        
        Args:
            sentiment: Sentiment type (positive|neutral|negative)
            limit: Maximum number of results
            
        Returns:
            List of analysis dictionaries
        """
        with self.get_session() as session:
            results = session.query(LLMAnalysisResult).filter(
                LLMAnalysisResult.sentiment == sentiment
            ).limit(limit).all()
            return [result.to_dict() for result in results]
    
    def get_analyses_by_topic(self, topic: str, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Get analyses containing specific topic
        
        Args:
            topic: Topic to search for
            limit: Maximum number of results
            
        Returns:
            List of analysis dictionaries
        """
        with self.get_session() as session:
            results = session.query(LLMAnalysisResult).filter(
                LLMAnalysisResult.topics.contains([topic])
            ).limit(limit).all()
            return [result.to_dict() for result in results]
    
    def get_recent_analyses(self, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Get recent analyses
        
        Args:
            limit: Maximum number of results
            
        Returns:
            List of analysis dictionaries
        """
        with self.get_session() as session:
            results = session.query(LLMAnalysisResult).order_by(
                LLMAnalysisResult.processed_at.desc()
            ).limit(limit).all()
            return [result.to_dict() for result in results]
    
    def get_processing_stats(self) -> Dict[str, Any]:
        """
        Get processing statistics

        Returns:
            Dictionary with processing statistics
        """
        try:
            with self.get_session() as session:
                total = session.query(LLMAnalysisResult).count()
                successful = session.query(LLMAnalysisResult).filter(
                    LLMAnalysisResult.error_message.is_(None)
                ).count()
                failed = total - successful
                
                # Average confidence score (excluding failed analyses)
                avg_confidence = session.query(
                    func.avg(LLMAnalysisResult.confidence_score)
                ).filter(
                    LLMAnalysisResult.error_message.is_(None)
                ).scalar() or 0
                
                # Sentiment distribution
                sentiment_dist = {}
                for sentiment in ['positive', 'neutral', 'negative']:
                    count = session.query(LLMAnalysisResult).filter(
                        LLMAnalysisResult.sentiment == sentiment,
                        LLMAnalysisResult.error_message.is_(None)
                    ).count()
                    sentiment_dist[sentiment] = count
                
                # Recent analyses (last 24 hours)
                recent_count = session.query(LLMAnalysisResult).filter(
                    LLMAnalysisResult.created_at >= datetime.utcnow() - timedelta(hours=24)
                ).count()
                
                # Top topics
                from sqlalchemy import func as sql_func
                topic_counts = session.query(
                    sql_func.unnest(LLMAnalysisResult.topics).label('topic'),
                    sql_func.count().label('count')
                ).filter(
                    LLMAnalysisResult.error_message.is_(None)
                ).group_by('topic').order_by(sql_func.count().desc()).limit(10).all()
                
                top_topics = [{'topic': topic, 'count': count} for topic, count in topic_counts]
                
                return {
                    'total_analyses': total,
                    'successful_analyses': successful,
                    'failed_analyses': failed,
                    'average_confidence_score': round(float(avg_confidence), 2),
                    'sentiment_distribution': sentiment_dist,
                    'recent_analyses': recent_count,
                    'top_topics': top_topics
                }
                
        except Exception as e:
            logger.error(f"Error getting processing stats: {e}")
            return {
                'total_analyses': 0,
                'successful_analyses': 0,
                'failed_analyses': 0,
                'average_confidence_score': 0,
                'sentiment_distribution': {},
                'recent_analyses': 0,
                'top_topics': []
            }
    
    def get_analyses_by_filter(self, sentiment: Optional[str] = None, 
                             topic: Optional[str] = None,
                             limit: int = 50, offset: int = 0) -> List[LLMAnalysisResult]:
        """Get analyses filtered by sentiment and/or topic"""
        try:
            with self.get_session() as session:
                query = session.query(LLMAnalysisResult)
                
                # Filter by sentiment
                if sentiment:
                    query = query.filter(LLMAnalysisResult.sentiment == sentiment)
                
                # Filter by topic (partial match)
                if topic:
                    query = query.filter(LLMAnalysisResult.topics.any(topic))
                
                # Filter out failed analyses
                query = query.filter(LLMAnalysisResult.error_message.is_(None))
                
                # Apply pagination
                query = query.order_by(LLMAnalysisResult.created_at.desc())
                query = query.limit(limit).offset(offset)
                
                return query.all()
                
        except Exception as e:
            logger.error(f"Error getting filtered analyses: {e}")
            return []
    
    def get_analyses_count(self, sentiment: Optional[str] = None, 
                          topic: Optional[str] = None) -> int:
        """Get total count of analyses matching filters"""
        try:
            with self.get_session() as session:
                query = session.query(LLMAnalysisResult)
                
                # Filter by sentiment
                if sentiment:
                    query = query.filter(LLMAnalysisResult.sentiment == sentiment)
                
                # Filter by topic (partial match)
                if topic:
                    query = query.filter(LLMAnalysisResult.topics.any(topic))
                
                # Filter out failed analyses
                query = query.filter(LLMAnalysisResult.error_message.is_(None))
                
                return query.count()
                
        except Exception as e:
            logger.error(f"Error getting analyses count: {e}")
            return 0
    
    def check_connection(self) -> bool:
        """Check database connection"""
        try:
            with self.get_session() as session:
                # Simple query to test connection
                session.execute("SELECT 1")
                return True
        except Exception as e:
            logger.error(f"Database connection check failed: {e}")
            return False