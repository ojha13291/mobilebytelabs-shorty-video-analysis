#!/usr/bin/env python3
"""
Test script for the LLM processor and database integration
"""

import os
import sys
import json
from datetime import datetime

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from api.models import db, LLMAnalysisResult, ScrapingJob, init_db
from api.llm_processor import LLMProcessor

def test_llm_processor():
    """Test LLM processor functionality"""
    print("Testing LLM processor...")
    
    try:
        # Create test app for database context
        from flask import Flask
        app = Flask(__name__)
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test_llm_analysis.db'
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        
        # Initialize database
        init_db(app)
        
        with app.app_context():
            # Initialize processor
            processor = LLMProcessor()
            print("✓ LLM Processor initialized successfully")
            
            # Test video content processing
            test_video_data = {
                'title': 'Test Video Title',
                'description': 'This is a test video description with some content to analyze.',
                'tags': ['test', 'video', 'analysis']
            }
            
            # Process video content
            result = processor.process_video(
                video_id='test_video_123',
                video_url='https://youtube.com/watch?v=test123',
                platform='youtube',
                transcript='This is a test transcript of the video content.',
                metadata=test_video_data
            )
            
            print("✓ Video processing completed:")
            print(f"  - Summary: {result.get('summary', 'N/A')[:100]}...")
            print(f"  - Sentiment: {result.get('sentiment', 'N/A')}")
            print(f"  - Topics: {result.get('topics', [])}")
            print(f"  - Confidence: {result.get('confidence_score', 'N/A')}")
            
            return result
        
    except Exception as e:
        print(f"✗ LLM Processor test failed: {e}")
        return None

def test_database_operations():
    """Test database operations"""
    print("Testing database operations...")
    
    try:
        # Create test app for database
        from flask import Flask
        app = Flask(__name__)
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test_llm_analysis.db'
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        
        # Initialize database
        init_db(app)
        
        with app.app_context():
            # Create a test scraping job
            job = ScrapingJob(
                job_id='test_job_123',
                platform='youtube',
                target='test_channel'
            )
            job.status = 'completed'
            db.session.add(job)
            db.session.commit()
            print(f"✓ Created test scraping job (ID: {job.id})")
            
            # Create a test LLM analysis result
            result = LLMAnalysisResult(
                video_id='test123',
                video_url='https://youtube.com/watch?v=test123',
                platform='youtube',
                llm_provider='mistral'
            )
            result.summary = 'Test video summary'
            result.sentiment = 'positive'
            result.set_topics(['technology', 'education'])
            result.confidence_score = 0.85
            
            db.session.add(result)
            db.session.commit()
            print(f"✓ Created test LLM analysis result (ID: {result.id})")
            
            # Query the results
            saved_result = LLMAnalysisResult.query.filter_by(video_id='test123').first()
            if saved_result:
                print(f"✓ Successfully retrieved analysis result:")
                print(f"  - Video ID: {saved_result.video_id}")
                print(f"  - Platform: {saved_result.platform}")
                print(f"  - Sentiment: {saved_result.sentiment}")
                print(f"  - Topics: {saved_result.get_topics()}")
                print(f"  - Confidence: {saved_result.confidence_score}")
            
            # Clean up test data
            db.session.delete(result)
            db.session.delete(job)
            db.session.commit()
            print("✓ Cleaned up test data")
        
        return True
        
    except Exception as e:
        print(f"✗ Database operations test failed: {e}")
        return False

def test_integration():
    """Test full integration between LLM processor and database"""
    print("Testing LLM processor and database integration...")
    
    try:
        # Create test app for database
        from flask import Flask
        app = Flask(__name__)
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test_llm_analysis.db'
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        
        # Initialize database
        init_db(app)
        
        with app.app_context():
            # Initialize LLM processor
            processor = LLMProcessor()
            
            # Test video data
            test_video_data = {
                'video_id': 'integration_test_123',
                'title': 'Integration Test Video',
                'description': 'This is a test video for integration testing.',
                'platform': 'youtube',
                'tags': ['integration', 'test', 'llm'],
                'comments': [
                    {'text': 'This integration test looks promising!'},
                    {'text': 'Great work on the implementation.'}
                ]
            }
            
            # Process and save to database
            result = processor.process_and_save_video(test_video_data)
            
            if result:
                print("✓ Integration test successful:")
                print(f"  - Saved analysis result with ID: {result.id}")
                print(f"  - Video ID: {result.video_id}")
                print(f"  - Summary: {result.summary[:100]}...")
                print(f"  - Sentiment: {result.sentiment}")
                
                # Verify it was saved correctly
                saved_result = LLMAnalysisResult.query.filter_by(video_id='integration_test_123').first()
                if saved_result:
                    print("✓ Successfully retrieved saved result from database")
                else:
                    print("✗ Failed to retrieve saved result from database")
            else:
                print("✗ Integration test failed - no result returned")
        
        return result is not None
        
    except Exception as e:
        print(f"✗ Integration test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 Starting LLM processor and database tests...\n")
    
    try:
        # Test LLM processor
        llm_result = test_llm_processor()
        
        # Test database operations
        db_success = test_database_operations()
        
        # Test integration
        integration_success = test_integration()
        
        # Summary
        print("\n📊 Test Results Summary:")
        print(f"  - LLM Processor: {'✅ PASSED' if llm_result else '❌ FAILED'}")
        print(f"  - Database Operations: {'✅ PASSED' if db_success else '❌ FAILED'}")
        print(f"  - Integration: {'✅ PASSED' if integration_success else '❌ FAILED'}")
        
        if llm_result and db_success and integration_success:
            print("\n🎉 All tests completed successfully!")
            return 0
        else:
            print("\n⚠️  Some tests failed. Check the output above for details.")
            return 1
        
    except Exception as e:
        print(f"❌ Test suite failed: {e}")
        return 1

if __name__ == "__main__":
    exit(main())