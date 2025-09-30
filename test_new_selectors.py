#!/usr/bin/env python3
"""
Test script for the new YouTube selectors based on current DOM structure
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from scrapers.youtube_selenium_scraper import YouTubeSeleniumScraper
import logging

# Enable debug logging to see selector attempts
logging.basicConfig(level=logging.DEBUG)

def test_new_selectors():
    """Test the updated selectors with real YouTube content"""
    print("🔍 Testing New YouTube Selectors")
    print("=" * 50)
    
    scraper = YouTubeSeleniumScraper()
    
    try:
        # Test with a popular video that should have likes, comments, etc.
        test_videos = [
            "https://www.youtube.com/watch?v=dQw4w9WgXcQ",  # Rick Roll (popular)
            "https://www.youtube.com/watch?v=9bZkp7q19f0",  # Gangnam Style
            "https://www.youtube.com/watch?v=kJQP7kiw5Fk"   # Despacito
        ]
        
        for i, video_url in enumerate(test_videos, 1):
            print(f"\n📹 Test {i}: {video_url}")
            print("-" * 40)
            
            try:
                video_data = scraper.scrape_video_details(video_url)
                
                if video_data:
                    print("✅ Video data extracted successfully!")
                    print(f"📝 Title: {video_data.get('title', 'N/A')}")
                    print(f"📺 Channel: {video_data.get('channel', 'N/A')}")
                    print(f"🔗 Channel URL: {video_data.get('channel_url', 'N/A')}")
                    print(f"👀 Views: {video_data.get('views', 'N/A'):,}" if video_data.get('views') else "👀 Views: N/A")
                    print(f"👍 Likes: {video_data.get('likes', 'N/A'):,}" if video_data.get('likes') else "👍 Likes: N/A")
                    print(f"💬 Comments: {video_data.get('comments', 'N/A'):,}" if video_data.get('comments') else "💬 Comments: N/A")
                    print(f"⏱️ Duration: {video_data.get('duration', 'N/A')}")
                    print(f"📅 Upload Date: {video_data.get('published_at', 'N/A')}")
                    
                    # Check engagement metrics
                    engagement = video_data.get('engagement_metrics', {})
                    print(f"\n📊 Engagement Metrics:")
                    print(f"   Views: {engagement.get('views', 0):,}")
                    print(f"   Likes: {engagement.get('likes', 0):,}")
                    print(f"   Comments: {engagement.get('comments', 0):,}")
                    
                    # Success indicators
                    success_indicators = []
                    if video_data.get('title') and video_data['title'] != 'N/A':
                        success_indicators.append("✅ Title")
                    if video_data.get('channel') and video_data['channel'] != 'N/A':
                        success_indicators.append("✅ Channel")
                    if video_data.get('views', 0) > 0:
                        success_indicators.append("✅ Views")
                    if video_data.get('likes', 0) > 0:
                        success_indicators.append("✅ Likes")
                    if video_data.get('comments', 0) > 0:
                        success_indicators.append("✅ Comments")
                    
                    print(f"\n🎯 Extraction Success: {' | '.join(success_indicators)}")
                    
                else:
                    print("❌ No video data extracted")
                    
            except Exception as e:
                print(f"❌ Error testing video: {str(e)}")
            
            print("\n" + "="*50)
        
        # Test channel scraping with new selectors
        print("\n📺 Testing Channel Scraping")
        print("-" * 40)
        
        channel_url = "https://www.youtube.com/@YouTube"
        videos = scraper.scrape_channel_videos(channel_url, max_videos=3)
        
        if videos:
            print(f"✅ Channel scraping successful! Found {len(videos)} videos")
            for i, video in enumerate(videos, 1):
                print(f"\n  Video {i}:")
                print(f"    📝 Title: {video.get('title', 'N/A')}")
                print(f"    📺 Channel: {video.get('channel', 'N/A')}")
                print(f"    👀 Views: {video.get('views', 'N/A'):,}" if video.get('views') else "    👀 Views: N/A")
                print(f"    👍 Likes: {video.get('likes', 'N/A'):,}" if video.get('likes') else "    👍 Likes: N/A")
                print(f"    ⏱️ Duration: {video.get('duration', 'N/A')}")
        else:
            print("❌ Channel scraping failed")
        
    except Exception as e:
        print(f"❌ Error during testing: {str(e)}")
    
    finally:
        scraper.close()
        print("\n🧹 Cleanup completed")
    
    print("\n✨ Selector Testing Completed!")

def test_selector_specificity():
    """Test specific selectors mentioned in the user's HTML"""
    print("\n🎯 Testing Specific Selectors")
    print("=" * 50)
    
    # Test the exact selectors from the user's HTML
    test_selectors = {
        'channel_name': 'a.yt-simple-endpoint.style-scope.yt-formatted-string[href*="/@"]',
        'like_button': 'div.yt-spec-touch-feedback-shape__fill',
        'touch_feedback': 'yt-touch-feedback-shape'
    }
    
    scraper = YouTubeSeleniumScraper()
    
    try:
        # Navigate to a test video
        test_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
        scraper._setup_driver_for_youtube()
        scraper.driver.get(test_url)
        
        import time
        time.sleep(5)  # Wait for page to load
        
        # Parse with BeautifulSoup
        soup = scraper.parse_with_bs4()
        
        print(f"📄 Testing selectors on: {test_url}")
        
        for selector_name, selector in test_selectors.items():
            try:
                elements = soup.select(selector)
                print(f"🔍 {selector_name}: '{selector}'")
                print(f"   Found {len(elements)} elements")
                
                if elements:
                    for i, elem in enumerate(elements[:3]):  # Show first 3
                        text = elem.get_text().strip()[:50]  # First 50 chars
                        print(f"   [{i+1}] Text: '{text}'")
                        if elem.get('href'):
                            print(f"       Href: '{elem.get('href')}'")
                else:
                    print("   ❌ No elements found")
                    
            except Exception as e:
                print(f"   ❌ Error: {str(e)}")
            
            print()
    
    except Exception as e:
        print(f"❌ Error during selector testing: {str(e)}")
    
    finally:
        scraper.close()

if __name__ == "__main__":
    test_new_selectors()
    test_selector_specificity()
