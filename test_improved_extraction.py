#!/usr/bin/env python3
"""
Test the improved extraction with the new selectors
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from scrapers.youtube_selenium_scraper import YouTubeSeleniumScraper
import logging

def test_improved_extraction():
    """Test the improved extraction methods"""
    print("🚀 Testing Improved YouTube Data Extraction")
    print("=" * 60)
    
    # Enable debug logging to see what's happening
    logging.basicConfig(level=logging.INFO)
    
    scraper = YouTubeSeleniumScraper()
    
    try:
        # Test with a well-known video that should have engagement data
        test_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
        print(f"📹 Testing with: {test_url}")
        print("-" * 60)
        
        # Use the enhanced method
        video_data = scraper.scrape_video_details(test_url)
        
        if video_data:
            print("✅ Video data extraction successful!")
            print()
            
            # Display all extracted data
            fields_to_show = [
                ('Title', 'title'),
                ('Channel', 'channel'),
                ('Channel URL', 'channel_url'),
                ('Views', 'views'),
                ('Likes', 'likes'),
                ('Comments', 'comments'),
                ('Duration', 'duration'),
                ('Upload Date', 'published_at'),
                ('Description', 'description')
            ]
            
            for display_name, field_name in fields_to_show:
                value = video_data.get(field_name, 'N/A')
                
                if field_name in ['views', 'likes', 'comments'] and isinstance(value, int) and value > 0:
                    print(f"📊 {display_name}: {value:,}")
                elif field_name == 'description' and value:
                    # Truncate description for display
                    desc_preview = value[:100] + "..." if len(value) > 100 else value
                    print(f"📝 {display_name}: {desc_preview}")
                elif value and value != 'N/A':
                    print(f"ℹ️  {display_name}: {value}")
                else:
                    print(f"❌ {display_name}: Not found")
            
            # Show engagement metrics summary
            engagement = video_data.get('engagement_metrics', {})
            print(f"\n📈 Engagement Summary:")
            print(f"   👀 Views: {engagement.get('views', 0):,}")
            print(f"   👍 Likes: {engagement.get('likes', 0):,}")
            print(f"   💬 Comments: {engagement.get('comments', 0):,}")
            
            # Calculate success rate
            successful_extractions = 0
            total_extractions = len(fields_to_show)
            
            for _, field_name in fields_to_show:
                value = video_data.get(field_name)
                if value and value != 'N/A' and value != '':
                    if field_name in ['views', 'likes', 'comments']:
                        if isinstance(value, int) and value > 0:
                            successful_extractions += 1
                    else:
                        successful_extractions += 1
            
            success_rate = (successful_extractions / total_extractions) * 100
            print(f"\n🎯 Extraction Success Rate: {success_rate:.1f}% ({successful_extractions}/{total_extractions})")
            
            # Show what worked
            if successful_extractions > 0:
                print(f"✅ Successfully extracted: ", end="")
                successful_fields = []
                for display_name, field_name in fields_to_show:
                    value = video_data.get(field_name)
                    if value and value != 'N/A' and value != '':
                        if field_name in ['views', 'likes', 'comments']:
                            if isinstance(value, int) and value > 0:
                                successful_fields.append(display_name)
                        else:
                            successful_fields.append(display_name)
                print(", ".join(successful_fields))
        
        else:
            print("❌ No video data extracted")
        
        print("\n" + "=" * 60)
        
        # Test channel extraction
        print("📺 Testing Channel Video Extraction")
        print("-" * 60)
        
        channel_url = "https://www.youtube.com/@YouTube"
        videos = scraper.scrape_channel_videos(channel_url, max_videos=2)
        
        if videos:
            print(f"✅ Found {len(videos)} videos from channel")
            for i, video in enumerate(videos, 1):
                print(f"\n  📹 Video {i}:")
                print(f"     Title: {video.get('title', 'N/A')}")
                print(f"     Channel: {video.get('channel', 'N/A')}")
                print(f"     Views: {video.get('views', 0):,}" if video.get('views') else "     Views: N/A")
                print(f"     Likes: {video.get('likes', 0):,}" if video.get('likes') else "     Likes: N/A")
        else:
            print("❌ No channel videos found")
    
    except Exception as e:
        print(f"❌ Error during testing: {str(e)}")
        import traceback
        traceback.print_exc()
    
    finally:
        scraper.close()
        print("\n🧹 Cleanup completed")
    
    print("\n✨ Improved Extraction Test Completed!")

if __name__ == "__main__":
    test_improved_extraction()
