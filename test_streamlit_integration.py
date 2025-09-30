#!/usr/bin/env python3
"""
Test script to verify the Streamlit app integration with enhanced YouTube scraper
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """Test that all required imports work"""
    print("🧪 Testing Streamlit App Imports...")
    
    try:
        # Test core imports
        import streamlit as st
        print("✅ Streamlit imported successfully")
        
        # Test project component imports
        from scrapers.youtube_selenium_scraper import YouTubeSeleniumScraper
        print("✅ Enhanced YouTube scraper imported successfully")
        
        from scrapers.instagram_selenium_scraper import InstagramSeleniumScraper
        print("✅ Instagram scraper imported successfully")
        
        from analyzer.video_analyzer import VideoAnalyzer
        print("✅ Video analyzer imported successfully")
        
        from resolver.platform_resolver import PlatformResolver
        print("✅ Platform resolver imported successfully")
        
        # Test the integrated analyzer class
        from integrated_streamlit_app import IntegratedVideoAnalyzer
        print("✅ Integrated analyzer imported successfully")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def test_analyzer_initialization():
    """Test that the integrated analyzer can be initialized"""
    print("\n🔧 Testing Analyzer Initialization...")
    
    try:
        from integrated_streamlit_app import IntegratedVideoAnalyzer
        
        # Initialize the analyzer
        analyzer = IntegratedVideoAnalyzer()
        print("✅ IntegratedVideoAnalyzer initialized successfully")
        
        # Check components
        if analyzer.youtube_scraper:
            print("✅ YouTube scraper component initialized")
        else:
            print("❌ YouTube scraper component failed to initialize")
        
        if analyzer.video_analyzer:
            print("✅ Video analyzer component initialized")
        else:
            print("❌ Video analyzer component failed to initialize")
        
        if analyzer.platform_resolver:
            print("✅ Platform resolver component initialized")
        else:
            print("❌ Platform resolver component failed to initialize")
        
        # Test YouTube scraper methods
        if hasattr(analyzer.youtube_scraper, 'scrape_video_details_with_fallback'):
            print("✅ Enhanced YouTube scraper methods available")
        else:
            print("❌ Enhanced YouTube scraper methods not found")
        
        # Cleanup
        if analyzer.youtube_scraper:
            analyzer.youtube_scraper.close()
        
        return True
        
    except Exception as e:
        print(f"❌ Analyzer initialization error: {e}")
        return False

def test_url_detection():
    """Test URL detection and platform resolution"""
    print("\n🔍 Testing URL Detection...")
    
    try:
        from integrated_streamlit_app import IntegratedVideoAnalyzer
        
        analyzer = IntegratedVideoAnalyzer()
        
        # Test URLs
        test_urls = [
            ("https://www.youtube.com/watch?v=dQw4w9WgXcQ", "youtube", "video"),
            ("https://www.youtube.com/@YouTube", "youtube", "channel"),
            ("https://www.youtube.com/channel/UCuAXFkgsw1L7xaCfnd5JJOw", "youtube", "channel"),
            ("https://www.instagram.com/instagram/", "instagram", "profile"),
        ]
        
        for url, expected_platform, content_type in test_urls:
            detected_platform = analyzer.platform_resolver.detect_platform(url)
            
            if detected_platform == expected_platform:
                print(f"✅ {content_type.title()} URL detected correctly: {expected_platform}")
            else:
                print(f"❌ {content_type.title()} URL detection failed: expected {expected_platform}, got {detected_platform}")
        
        # Cleanup
        if analyzer.youtube_scraper:
            analyzer.youtube_scraper.close()
        
        return True
        
    except Exception as e:
        print(f"❌ URL detection test error: {e}")
        return False

def test_enhanced_scraper_features():
    """Test enhanced scraper features"""
    print("\n🚀 Testing Enhanced Scraper Features...")
    
    try:
        from scrapers.youtube_selenium_scraper import YouTubeSeleniumScraper
        
        scraper = YouTubeSeleniumScraper()
        
        # Check for enhanced methods
        enhanced_methods = [
            'scrape_video_details_with_fallback',
            '_extract_engagement_data_advanced',
            '_find_element_by_selectors',
            '_extract_video_id_from_url',
            '_scrape_with_api_fallback'
        ]
        
        for method in enhanced_methods:
            if hasattr(scraper, method):
                print(f"✅ Enhanced method available: {method}")
            else:
                print(f"❌ Enhanced method missing: {method}")
        
        # Check selectors
        if hasattr(scraper, 'selectors') and scraper.selectors:
            print(f"✅ Enhanced selectors configured: {len(scraper.selectors)} selector groups")
            
            # Check specific selector groups
            required_selectors = ['video_title', 'channel_name', 'like_count', 'video_views']
            for selector_group in required_selectors:
                if selector_group in scraper.selectors:
                    selector_count = len(scraper.selectors[selector_group])
                    print(f"✅ {selector_group}: {selector_count} fallback selectors")
                else:
                    print(f"❌ Missing selector group: {selector_group}")
        else:
            print("❌ Enhanced selectors not configured")
        
        # Cleanup
        scraper.close()
        
        return True
        
    except Exception as e:
        print(f"❌ Enhanced scraper test error: {e}")
        return False

def main():
    """Run all integration tests"""
    print("🎬 Streamlit Integration Test Suite")
    print("=" * 50)
    
    tests = [
        ("Import Tests", test_imports),
        ("Analyzer Initialization", test_analyzer_initialization),
        ("URL Detection", test_url_detection),
        ("Enhanced Scraper Features", test_enhanced_scraper_features)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n📋 Running: {test_name}")
        print("-" * 30)
        
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ Test suite error in {test_name}: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 Test Results Summary:")
    print("-" * 30)
    
    passed = 0
    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\n🎯 Overall: {passed}/{len(results)} tests passed")
    
    if passed == len(results):
        print("🎉 All integration tests passed! Streamlit app is ready to use.")
        print("\n🚀 To run the app:")
        print("   streamlit run integrated_streamlit_app.py")
    else:
        print("⚠️  Some tests failed. Check the output above for details.")
    
    return passed == len(results)

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
