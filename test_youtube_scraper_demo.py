#!/usr/bin/env python3
"""
Demo script to test the improved YouTube scraper functionality
"""

import sys
import os
import json
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from scrapers.youtube_selenium_scraper import YouTubeSeleniumScraper

def test_youtube_video_scraping():
    """Test YouTube video scraping with improved functionality"""
    print("🎬 Testing Improved YouTube Scraper")
    print("=" * 50)
    
    # Initialize scraper
    scraper = YouTubeSeleniumScraper()
    
    try:
        # Test 1: Scrape a specific video
        print("\n📹 Test 1: Scraping specific video details")
        video_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
        print(f"Video URL: {video_url}")
        
        video_data = scraper.scrape_video_details(video_url)
        if video_data:
            print("✅ Video scraping successful!")
            print(f"Title: {video_data.get('title', 'N/A')}")
            print(f"Channel: {video_data.get('channel', 'N/A')}")
            print(f"Views: {video_data.get('views', 'N/A'):,}" if video_data.get('views') else "Views: N/A")
            print(f"Likes: {video_data.get('likes', 'N/A'):,}" if video_data.get('likes') else "Likes: N/A")
            print(f"Duration: {video_data.get('duration', 'N/A')}")
            print(f"Upload Date: {video_data.get('published_at', 'N/A')}")
            
            if video_data.get('hashtags'):
                print(f"Hashtags: {', '.join(video_data['hashtags'])}")
        else:
            print("❌ Video scraping failed")
        
        # Test 2: Scrape channel videos
        print("\n📺 Test 2: Scraping channel videos")
        channel_url = "https://www.youtube.com/@YouTube"
        print(f"Channel URL: {channel_url}")
        
        videos = scraper.scrape_channel_videos(channel_url, max_videos=5)
        if videos:
            print(f"✅ Channel scraping successful! Found {len(videos)} videos")
            for i, video in enumerate(videos[:3], 1):
                print(f"\n  Video {i}:")
                print(f"    Title: {video.get('title', 'N/A')}")
                print(f"    Views: {video.get('views', 'N/A'):,}" if video.get('views') else "    Views: N/A")
                print(f"    Duration: {video.get('duration', 'N/A')}")
        else:
            print("❌ Channel scraping failed or no videos found")
        
        # Test 3: Search for videos
        print("\n🔍 Test 3: Searching for videos")
        search_query = "python programming tutorial"
        print(f"Search Query: {search_query}")
        
        search_results = scraper.scrape_search_results(search_query, max_videos=3)
        if search_results:
            print(f"✅ Search successful! Found {len(search_results)} videos")
            for i, video in enumerate(search_results, 1):
                print(f"\n  Result {i}:")
                print(f"    Title: {video.get('title', 'N/A')}")
                print(f"    Channel: {video.get('channel', 'N/A')}")
                print(f"    Views: {video.get('views', 'N/A'):,}" if video.get('views') else "    Views: N/A")
        else:
            print("❌ Search failed or no results found")
        
        # Test 4: Test with API fallback (if available)
        print("\n🔄 Test 4: Testing API fallback functionality")
        if hasattr(scraper, 'scrape_video_details_with_fallback'):
            fallback_data = scraper.scrape_video_details_with_fallback(video_url)
            if fallback_data:
                print("✅ API fallback available and working")
                if fallback_data.get('api_fallback'):
                    print("   Used API fallback for data retrieval")
                else:
                    print("   Used Selenium scraping (API not needed)")
            else:
                print("⚠️  API fallback available but no data retrieved")
        else:
            print("⚠️  API fallback not available")
        
    except Exception as e:
        print(f"❌ Error during testing: {str(e)}")
    
    finally:
        # Clean up
        scraper.close()
        print("\n🧹 Cleanup completed")
    
    print("\n" + "=" * 50)
    print("✨ YouTube Scraper Demo Completed!")

def save_sample_data():
    """Save sample scraped data to JSON file"""
    print("\n💾 Saving sample data...")
    
    scraper = YouTubeSeleniumScraper()
    
    try:
        # Scrape a sample video
        video_data = scraper.scrape_video_details("https://www.youtube.com/watch?v=dQw4w9WgXcQ")
        
        if video_data:
            # Save to JSON file
            output_file = "sample_youtube_data.json"
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(video_data, f, indent=2, ensure_ascii=False)
            
            print(f"✅ Sample data saved to {output_file}")
        else:
            print("❌ No data to save")
    
    except Exception as e:
        print(f"❌ Error saving sample data: {str(e)}")
    
    finally:
        scraper.close()

if __name__ == "__main__":
    # Run the demo
    test_youtube_video_scraping()
    
    # Optionally save sample data
    save_sample_data()
