#!/usr/bin/env python3
"""
Test script for scraper functionality
Tests WebDriverManager, SeleniumScraper, YouTubeSeleniumScraper, and InstagramSeleniumScraper
"""

import sys
import os
import time
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils.webdriver_manager import WebDriverManager
from scrapers.selenium_scraper import SeleniumScraper
from scrapers.youtube_selenium_scraper import YouTubeSeleniumScraper
from scrapers.instagram_selenium_scraper import InstagramSeleniumScraper

def test_selenium_scraper():
    """Test basic Selenium scraper functionality"""
    print("Testing basic Selenium scraper...")
    
    try:
        # Initialize WebDriverManager
        manager = WebDriverManager()
        driver_path = manager.get_driver_path()
        
        if not driver_path:
            print("⚠️  No ChromeDriver found. Skipping basic scraper test.")
            return True
        
        print(f"✓ WebDriverManager initialized (driver: {driver_path})")
        
        # Initialize scraper with proper setup
        scraper = SeleniumScraper("test_selenium", rate_limit_delay=0.5)
        if not scraper.setup_driver(headless=True):
            print("✗ Failed to setup WebDriver")
            return False
        
        print("✓ SeleniumScraper initialized successfully")
        
        # Test basic functionality
        test_url = "https://httpbin.org/user-agent"
        scraper.driver.get(test_url)
        print(f"✓ Successfully accessed test URL: {test_url}")
        
        # Test HTML parsing
        html_content = scraper.get_page_source()
        soup = scraper.parse_with_bs4()
        print(f"✓ Successfully parsed HTML with BeautifulSoup")
        
        scraper.close_driver()
        print("✓ Basic scraper test completed\n")
        return True
        
    except Exception as e:
        print(f"❌ Basic scraper test failed: {e}")
        return False

def test_youtube_scraper():
    """Test YouTube scraper functionality"""
    print("Testing YouTube scraper...")
    
    try:
        # Initialize WebDriverManager
        driver_manager = WebDriverManager()
        driver_path = driver_manager.get_driver_path()
        
        if not driver_path:
            print("✗ Failed to get ChromeDriver path")
            return False
        
        print(f"✓ WebDriverManager initialized (driver: {driver_path})")
        
        # Create YouTube scraper
        from scrapers.youtube_selenium_scraper import YouTubeSeleniumScraper
        scraper = YouTubeSeleniumScraper()
        
        # Setup the driver
        if not scraper.setup_driver(headless=True):
            print("✗ Failed to setup WebDriver")
            return False
        
        print("✓ YouTubeSeleniumScraper initialized successfully")
        
        # Test channel scraping
        channel_url = "https://www.youtube.com/@YouTube"
        print(f"Testing channel scraping: {channel_url}")
        
        try:
            videos = scraper.scrape_channel_videos(channel_url, max_videos=5)
            print(f"✓ Successfully scraped {len(videos)} videos from channel")
            if videos:
                print(f"  - Sample video: {videos[0].get('title', 'N/A')}")
                print(f"  - Views: {videos[0].get('views', 'N/A')}")
        except Exception as e:
            print(f"✗ Failed to scrape channel: {e}")
        
        # Test video details scraping
        video_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
        print(f"Testing video details scraping: {video_url}")
        
        try:
            video_details = scraper.scrape_video_details(video_url)
            if video_details:
                print("✓ Successfully scraped video info:")
                print(f"  - Title: {video_details.get('title', 'N/A')}")
                print(f"  - Channel: {video_details.get('channel', 'N/A')}")
                print(f"  - Views: {video_details.get('views', 'N/A')}")
            else:
                print("✗ Failed to scrape video info")
        except Exception as e:
            print(f"✗ Video scraping failed: {e}")
        
        scraper.close_driver()
        print("✓ YouTube scraper test completed\n")
        return True
        
    except Exception as e:
        print(f"❌ YouTube scraper test failed: {e}")
        return False

def test_instagram_scraper():
    """Test Instagram scraper functionality"""
    print("Testing Instagram scraper...")
    
    try:
        # Initialize WebDriverManager
        driver_manager = WebDriverManager()
        driver_path = driver_manager.get_driver_path()
        
        if not driver_path:
            print("✗ Failed to get ChromeDriver path")
            return False
        
        print(f"✓ WebDriverManager initialized (driver: {driver_path})")
        
        # Create Instagram scraper
        from scrapers.instagram_selenium_scraper import InstagramSeleniumScraper
        scraper = InstagramSeleniumScraper()
        
        # Setup the driver
        if not scraper.setup_driver(headless=True):
            print("✗ Failed to setup WebDriver")
            return False
        
        print("✓ InstagramSeleniumScraper initialized successfully")
        
        # Test profile scraping
        username = "instagram"
        print(f"Testing profile scraping: {username}")
        
        try:
            profile_data = scraper.scrape_user_profile(username)
            if profile_data:
                print("✓ Successfully scraped profile info:")
                print(f"  - Username: {profile_data.get('username', 'N/A')}")
                print(f"  - Bio: {profile_data.get('bio', 'N/A')[:50]}...")
                print(f"  - Followers: {profile_data.get('followers_count', 'N/A')}")
            else:
                print("✗ Failed to scrape profile info")
        except Exception as e:
            print(f"✗ Profile scraping failed: {e}")
        
        scraper.close_driver()
        print("✓ Instagram scraper test completed\n")
        return True
        
    except Exception as e:
        print(f"❌ Instagram scraper test failed: {e}")
        return False

def test_video_data_extraction():
    """Test video data extraction functionality"""
    print("Testing video data extraction...")
    
    try:
        # Initialize WebDriverManager
        driver_manager = WebDriverManager()
        driver_path = driver_manager.get_driver_path()
        
        if not driver_path:
            print("✗ Failed to get ChromeDriver path")
            return False
        
        print(f"✓ WebDriverManager initialized (driver: {driver_path})")
        
        # Create Selenium scraper
        from scrapers.selenium_scraper import SeleniumScraper
        scraper = SeleniumScraper("test", rate_limit_delay=0.5)
        
        # Setup the driver
        if not scraper.setup_driver(headless=True):
            print("✗ Failed to setup WebDriver")
            return False
        
        print("✓ SeleniumScraper initialized successfully")
        
        # Test video data extraction from different platforms
        test_urls = [
            "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
        ]
        
        for url in test_urls:
            try:
                # Navigate to the URL
                scraper.driver.get(url)
                time.sleep(3)
                
                # Parse with BeautifulSoup
                soup = scraper.parse_with_bs4()
                
                # Extract video data
                platform = 'youtube' if 'youtube.com' in url else 'instagram'
                videos = scraper.extract_video_data(soup, platform)
                
                if videos:
                    video_data = videos[0]  # Get first video
                    print(f"✓ Extracted video data from {url}:")
                    print(f"  - Platform: {video_data.get('platform', 'N/A')}")
                    print(f"  - Title: {video_data.get('title', 'N/A')}")
                    print(f"  - Views: {video_data.get('views', 'N/A')}")
                    print(f"  - Duration: {video_data.get('duration', 'N/A')}")
                    print(f"  - Description: {video_data.get('description', 'N/A')[:100]}...")
                else:
                    print(f"✗ No video data extracted from {url}")
            except Exception as e:
                print(f"✗ Failed to extract video data from {url}: {e}")
        
        scraper.close_driver()
        print("✓ Video data extraction test completed\n")
        return True
        
    except Exception as e:
        print(f"❌ Video data extraction test failed: {e}")
        return False

def main():
    """Run all scraper tests"""
    print("🚀 Starting scraper tests...\n")
    
    # Track test results
    test_results = []
    
    # Test basic Selenium scraper
    test_results.append(("Basic Selenium Scraper", test_selenium_scraper()))
    
    # Test YouTube scraper
    test_results.append(("YouTube Scraper", test_youtube_scraper()))
    
    # Test Instagram scraper
    test_results.append(("Instagram Scraper", test_instagram_scraper()))
    
    # Test generic video data extraction
    test_results.append(("Video Data Extraction", test_video_data_extraction()))
    
    # Print summary
    print("\n📊 Test Results Summary:")
    passed = sum(1 for _, result in test_results if result)
    total = len(test_results)
    
    for test_name, result in test_results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"  - {test_name}: {status}")
    
    print(f"\n🎯 Overall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests completed successfully!")
        return 0
    else:
        print("⚠️  Some tests failed. Check the output above for details.")
        return 1

if __name__ == "__main__":
    exit(main())