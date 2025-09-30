"""
Enhanced Selenium-based scraper with BeautifulSoup for improved reliability
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import TimeoutException, NoSuchElementException, WebDriverException
from bs4 import BeautifulSoup
import time
import random
import logging
from typing import Dict, List, Any, Optional
import json
import re
from urllib.parse import urljoin, urlparse

from scrapers.base_scraper import BaseScraper

logger = logging.getLogger(__name__)


class SeleniumScraper(BaseScraper):
    """
    Enhanced scraper using Selenium WebDriver and BeautifulSoup
    """
    
    def __init__(self, platform_name: str, rate_limit_delay: float = 1.0):
        """
        Initialize Selenium scraper
        
        Args:
            platform_name: Name of the platform
            rate_limit_delay: Delay between requests
        """
        super().__init__(platform_name, rate_limit_delay)
        self.driver = None
        self.wait = None
        self.session_data = {}
        
    def setup_driver(self, headless: bool = True, user_agent: str = None) -> bool:
        """
        Setup Chrome WebDriver with optimal settings
        
        Args:
            headless: Run in headless mode
            user_agent: Custom user agent
            
        Returns:
            True if setup successful
        """
        try:
            chrome_options = Options()
            
            if headless:
                chrome_options.add_argument('--headless')
            
            # Essential arguments for stability
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument('--disable-blink-features=AutomationControlled')
            chrome_options.add_argument('--disable-extensions')
            chrome_options.add_argument('--disable-plugins')
            chrome_options.add_argument('--disable-images')  # Speed up loading
            chrome_options.add_argument('--disable-javascript')  # Optional, can be enabled per platform
            
            # Window size for consistent rendering
            chrome_options.add_argument('--window-size=1920,1080')
            
            # User agent
            if user_agent:
                chrome_options.add_argument(f'user-agent={user_agent}')
            else:
                # Default user agent that looks like a real browser
                chrome_options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
            
            # Exclude automation switches
            chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
            chrome_options.add_experimental_option('useAutomationExtension', False)
            
            # Preferences to reduce detection
            prefs = {
                "profile.managed_default_content_settings.images": 2,  # Block images for speed
                "profile.default_content_setting_values.notifications": 2,  # Block notifications
                "profile.managed_default_content_settings.stylesheets": 2,  # Block CSS for speed (optional)
            }
            chrome_options.add_experimental_option("prefs", prefs)
            
            self.driver = webdriver.Chrome(options=chrome_options)
            self.wait = WebDriverWait(self.driver, 10)
            
            # Execute script to remove webdriver property
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            
            logger.info(f"WebDriver initialized successfully for {self.platform_name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to setup WebDriver: {str(e)}")
            return False
    
    def safe_find_element(self, by: By, value: str, timeout: int = 10, multiple: bool = False) -> Optional[Any]:
        """
        Safely find element(s) with timeout and error handling
        
        Args:
            by: Selenium By method
            value: Selector value
            timeout: Timeout in seconds
            multiple: Find multiple elements
            
        Returns:
            Element(s) or None
        """
        try:
            wait = WebDriverWait(self.driver, timeout)
            if multiple:
                return wait.until(EC.presence_of_all_elements_located((by, value)))
            else:
                return wait.until(EC.presence_of_element_located((by, value)))
        except TimeoutException:
            logger.warning(f"Element not found: {by}={value}")
            return None
        except Exception as e:
            logger.error(f"Error finding element {by}={value}: {str(e)}")
            return None
    
    def scroll_to_load_content(self, scroll_pause_time: float = 1.0, max_scrolls: int = 5) -> None:
        """
        Scroll down to load more content
        
        Args:
            scroll_pause_time: Time to pause between scrolls
            max_scrolls: Maximum number of scrolls
        """
        last_height = self.driver.execute_script("return document.body.scrollHeight")
        
        for i in range(max_scrolls):
            # Scroll down to bottom
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            
            # Wait to load page
            time.sleep(scroll_pause_time)
            
            # Calculate new scroll height and compare with last scroll height
            new_height = self.driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height
    
    def get_page_source(self) -> str:
        """
        Get current page source
        
        Returns:
            Page HTML source
        """
        return self.driver.page_source if self.driver else ""
    
    def parse_with_bs4(self, html: str = None) -> BeautifulSoup:
        """
        Parse HTML with BeautifulSoup
        
        Args:
            html: HTML content (uses current page source if None)
            
        Returns:
            BeautifulSoup object
        """
        if html is None:
            html = self.get_page_source()
        
        return BeautifulSoup(html, 'html.parser')
    
    def extract_video_data(self, soup: BeautifulSoup, platform: str) -> List[Dict[str, Any]]:
        """
        Extract video data using BeautifulSoup
        
        Args:
            soup: BeautifulSoup object
            platform: Platform name
            
        Returns:
            List of video data dictionaries
        """
        videos = []
        
        try:
            # Platform-specific extraction logic
            if platform.lower() == 'youtube':
                videos = self._extract_youtube_videos(soup)
            elif platform.lower() == 'instagram':
                videos = self._extract_instagram_videos(soup)
            elif platform.lower() == 'tiktok':
                videos = self._extract_tiktok_videos(soup)
            elif platform.lower() == 'twitter':
                videos = self._extract_twitter_videos(soup)
            else:
                # Generic extraction
                videos = self._extract_generic_videos(soup)
                
        except Exception as e:
            logger.error(f"Error extracting video data for {platform}: {str(e)}")
        
        return videos
    
    def _extract_youtube_videos(self, soup: BeautifulSoup) -> List[Dict[str, Any]]:
        """
        Extract YouTube video data
        
        Args:
            soup: BeautifulSoup object
            
        Returns:
            List of YouTube video data
        """
        videos = []
        
        # Find video elements (YouTube specific selectors)
        video_elements = soup.find_all('ytd-rich-item-renderer')
        
        for element in video_elements[:10]:  # Limit to first 10
            try:
                # Extract video data
                title_elem = element.find('a', {'id': 'video-title'})
                if not title_elem:
                    continue
                
                title = title_elem.get('title', '')
                video_url = title_elem.get('href', '')
                if video_url:
                    video_url = urljoin('https://www.youtube.com', video_url)
                
                # Extract metadata
                metadata_elem = element.find('div', {'id': 'metadata-line'})
                views_text = metadata_elem.get_text() if metadata_elem else ''
                views = self.parse_count(views_text)
                
                # Extract channel info
                channel_elem = element.find('yt-formatted-string', {'class': 'style-scope ytd-channel-name'})
                channel = channel_elem.get_text().strip() if channel_elem else ''
                
                video_data = {
                    'platform': 'youtube',
                    'title': self.clean_text(title),
                    'url': video_url,
                    'views': views,
                    'channel': channel,
                    'scraped_at': time.strftime('%Y-%m-%d %H:%M:%S'),
                    'hashtags': self.extract_hashtags(title),
                    'engagement_metrics': {
                        'views': views,
                        'likes': 0,  # Would need additional API calls
                        'comments': 0
                    }
                }
                
                videos.append(video_data)
                
            except Exception as e:
                logger.warning(f"Error extracting YouTube video data: {str(e)}")
                continue
        
        return videos
    
    def _extract_instagram_videos(self, soup: BeautifulSoup) -> List[Dict[str, Any]]:
        """
        Extract Instagram video data
        
        Args:
            soup: BeautifulSoup object
            
        Returns:
            List of Instagram video data
        """
        videos = []
        
        # Find Instagram post elements
        post_elements = soup.find_all('article') or soup.find_all('div', class_=re.compile(r'.*post.*', re.I))
        
        for element in post_elements[:10]:
            try:
                # Extract post data
                caption_elem = element.find('h1') or element.find('span', class_=re.compile(r'.*caption.*', re.I))
                caption = caption_elem.get_text().strip() if caption_elem else ''
                
                # Extract likes
                likes_elem = element.find('span', class_=re.compile(r'.*like.*', re.I))
                likes_text = likes_elem.get_text() if likes_elem else ''
                likes = self.parse_count(likes_text)
                
                # Extract username
                username_elem = element.find('a', class_=re.compile(r'.*username.*', re.I))
                username = username_elem.get_text().strip() if username_elem else ''
                
                # Extract post URL
                link_elem = element.find('a', href=True)
                post_url = link_elem['href'] if link_elem else ''
                if post_url and not post_url.startswith('http'):
                    post_url = urljoin('https://www.instagram.com', post_url)
                
                video_data = {
                    'platform': 'instagram',
                    'title': self.clean_text(caption)[:100],  # Truncate for title
                    'description': self.clean_text(caption),
                    'url': post_url,
                    'username': username,
                    'likes': likes,
                    'scraped_at': time.strftime('%Y-%m-%d %H:%M:%S'),
                    'hashtags': self.extract_hashtags(caption),
                    'mentions': self.extract_mentions(caption),
                    'engagement_metrics': {
                        'likes': likes,
                        'comments': 0,
                        'shares': 0
                    }
                }
                
                videos.append(video_data)
                
            except Exception as e:
                logger.warning(f"Error extracting Instagram post data: {str(e)}")
                continue
        
        return videos
    
    def _extract_tiktok_videos(self, soup: BeautifulSoup) -> List[Dict[str, Any]]:
        """
        Extract TikTok video data
        
        Args:
            soup: BeautifulSoup object
            
        Returns:
            List of TikTok video data
        """
        videos = []
        
        # TikTok uses different structure, find video containers
        video_elements = soup.find_all('div', class_=re.compile(r'.*video.*', re.I))
        
        for element in video_elements[:10]:
            try:
                # Extract video data
                title_elem = element.find('h3') or element.find('div', class_=re.compile(r'.*title.*', re.I))
                title = title_elem.get_text().strip() if title_elem else ''
                
                # Extract stats
                stats_elem = element.find('div', class_=re.compile(r'.*stat.*', re.I))
                stats_text = stats_elem.get_text() if stats_elem else ''
                
                # Extract username
                user_elem = element.find('a', class_=re.compile(r'.*user.*', re.I))
                username = user_elem.get_text().strip() if user_elem else ''
                
                video_data = {
                    'platform': 'tiktok',
                    'title': self.clean_text(title),
                    'username': username,
                    'scraped_at': time.strftime('%Y-%m-%d %H:%M:%S'),
                    'hashtags': self.extract_hashtags(title),
                    'engagement_metrics': {
                        'views': self.parse_count(stats_text),
                        'likes': 0,
                        'comments': 0,
                        'shares': 0
                    }
                }
                
                videos.append(video_data)
                
            except Exception as e:
                logger.warning(f"Error extracting TikTok video data: {str(e)}")
                continue
        
        return videos
    
    def _extract_twitter_videos(self, soup: BeautifulSoup) -> List[Dict[str, Any]]:
        """
        Extract Twitter video data
        
        Args:
            soup: BeautifulSoup object
            
        Returns:
            List of Twitter video data
        """
        videos = []
        
        # Find tweet elements
        tweet_elements = soup.find_all('article') or soup.find_all('div', {'data-testid': 'tweet'})
        
        for element in tweet_elements[:10]:
            try:
                # Extract tweet text
                text_elem = element.find('div', {'lang': True}) or element.find('span', class_=re.compile(r'.*text.*', re.I))
                tweet_text = text_elem.get_text().strip() if text_elem else ''
                
                # Extract username
                username_elem = element.find('div', class_=re.compile(r'.*username.*', re.I))
                username = username_elem.get_text().strip() if username_elem else ''
                
                # Extract engagement
                like_elem = element.find('button', {'data-testid': 'like'})
                likes_text = like_elem.get_text() if like_elem else ''
                likes = self.parse_count(likes_text)
                
                video_data = {
                    'platform': 'twitter',
                    'title': self.clean_text(tweet_text)[:100],
                    'description': self.clean_text(tweet_text),
                    'username': username,
                    'likes': likes,
                    'scraped_at': time.strftime('%Y-%m-%d %H:%M:%S'),
                    'hashtags': self.extract_hashtags(tweet_text),
                    'mentions': self.extract_mentions(tweet_text),
                    'engagement_metrics': {
                        'likes': likes,
                        'retweets': 0,
                        'replies': 0
                    }
                }
                
                videos.append(video_data)
                
            except Exception as e:
                logger.warning(f"Error extracting Twitter data: {str(e)}")
                continue
        
        return videos
    
    def _extract_generic_videos(self, soup: BeautifulSoup) -> List[Dict[str, Any]]:
        """
        Generic video extraction for unknown platforms
        
        Args:
            soup: BeautifulSoup object
            
        Returns:
            List of generic video data
        """
        videos = []
        
        # Look for common video-related elements
        video_elements = soup.find_all(['video', 'iframe']) or soup.find_all('div', class_=re.compile(r'.*video.*', re.I))
        
        for element in video_elements[:10]:
            try:
                # Extract basic data
                title = element.get('title', '') or element.get('alt', '')
                src = element.get('src', '')
                
                # Look for text content nearby
                parent = element.find_parent()
                text_content = parent.get_text().strip() if parent else ''
                
                video_data = {
                    'platform': 'unknown',
                    'title': self.clean_text(title) if title else self.clean_text(text_content)[:100],
                    'url': src,
                    'description': self.clean_text(text_content),
                    'scraped_at': time.strftime('%Y-%m-%d %H:%M:%S'),
                    'hashtags': self.extract_hashtags(text_content),
                    'engagement_metrics': {}
                }
                
                videos.append(video_data)
                
            except Exception as e:
                logger.warning(f"Error extracting generic video data: {str(e)}")
                continue
        
        return videos
    
    def wait_for_page_load(self, timeout: int = 10) -> bool:
        """
        Wait for page to fully load
        
        Args:
            timeout: Maximum wait time
            
        Returns:
            True if page loaded successfully
        """
        try:
            WebDriverWait(self.driver, timeout).until(
                lambda driver: driver.execute_script("return document.readyState") == "complete"
            )
            return True
        except TimeoutException:
            logger.warning("Page load timeout")
            return False
    
    def close_driver(self):
        """Close the WebDriver and cleanup"""
        if self.driver:
            try:
                self.driver.quit()
                self.driver = None
                self.wait = None
                logger.info("WebDriver closed successfully")
            except Exception as e:
                logger.error(f"Error closing WebDriver: {str(e)}")
    
    def __enter__(self):
        """Context manager entry"""
        self.setup_driver()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.close_driver()
    
    def scrape_reels(self, target: str, max_reels: int = 10) -> List[Dict[str, Any]]:
        """
        Generic implementation of scrape_reels for SeleniumScraper
        
        Args:
            target: Target to scrape (URL, username, etc.)
            max_reels: Maximum number of reels to scrape
            
        Returns:
            List of scraped reel data
        """
        try:
            logger.info(f"Scraping reels for target: {target}")
            
            # Navigate to target
            self.driver.get(target)
            time.sleep(random.uniform(2, 4))
            
            # Wait for page to load
            self.wait_for_page_load()
            
            # Scroll to load content
            self.scroll_to_load_content(scroll_pause_time=2.0, max_scrolls=3)
            
            # Parse with BeautifulSoup
            soup = self.parse_with_bs4()
            
            # Determine platform from URL
            platform = 'unknown'
            if 'youtube.com' in target:
                platform = 'youtube'
            elif 'instagram.com' in target:
                platform = 'instagram'
            elif 'tiktok.com' in target:
                platform = 'tiktok'
            elif 'twitter.com' in target or 'x.com' in target:
                platform = 'twitter'
            
            # Extract video data
            videos = self.extract_video_data(soup, platform)
            
            return videos[:max_reels]
            
        except Exception as e:
            logger.error(f"Error scraping reels for {target}: {str(e)}")
            return []
    
    def scrape_user_profile(self, username: str) -> Optional[Dict[str, Any]]:
        """
        Generic implementation of scrape_user_profile for SeleniumScraper
        
        Args:
            username: Username to scrape
            
        Returns:
            User profile data or None if not found
        """
        try:
            logger.info(f"Scraping user profile: {username}")
            
            # This is a generic implementation - specific platforms should override
            profile_data = {
                'platform': self.platform_name,
                'username': username,
                'scraped_at': time.strftime('%Y-%m-%d %H:%M:%S'),
                'bio': '',
                'followers_count': 0,
                'following_count': 0,
                'posts_count': 0
            }
            
            return profile_data
            
        except Exception as e:
            logger.error(f"Error scraping user profile {username}: {str(e)}")
            return None