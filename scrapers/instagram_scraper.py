"""
Instagram scraper implementation
"""

import time
import random
from typing import Dict, List, Any, Optional
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from .base_scraper import BaseScraper


class InstagramScraper(BaseScraper):
    """
    Instagram scraper using Selenium
    """
    
    def __init__(self, username: str, password: str, rate_limit_delay: float = 2.0):
        """
        Initialize Instagram scraper
        
        Args:
            username: Instagram username
            password: Instagram password
            rate_limit_delay: Delay between requests
        """
        super().__init__("instagram", rate_limit_delay)
        self.username = username
        self.password = password
        self.driver = None
        self.is_logged_in = False
    
    def _setup_driver(self):
        """Setup Chrome driver with options"""
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
        
        self.driver = webdriver.Chrome(options=chrome_options)
        self.driver.implicitly_wait(10)
    
    def login_to_instagram(self) -> bool:
        """
        Login to Instagram
        
        Returns:
            True if login successful, False otherwise
        """
        try:
            if not self.driver:
                self._setup_driver()
            
            self.driver.get("https://www.instagram.com/")
            time.sleep(random.uniform(2, 4))
            
            # Find and fill username field
            username_field = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.NAME, "username"))
            )
            username_field.send_keys(self.username)
            
            # Find and fill password field
            password_field = self.driver.find_element(By.NAME, "password")
            password_field.send_keys(self.password)
            
            # Click login button
            login_button = self.driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
            login_button.click()
            
            # Wait for login to complete
            time.sleep(random.uniform(3, 5))
            
            # Check if login was successful
            if "login" not in self.driver.current_url.lower():
                self.is_logged_in = True
                print(f"Successfully logged in to Instagram as {self.username}")
                return True
            else:
                print("Login failed - still on login page")
                return False
                
        except TimeoutException:
            print("Login failed - timeout waiting for elements")
            return False
        except Exception as e:
            print(f"Login failed - error: {str(e)}")
            return False
    
    def scrape_user_profile(self, username: str) -> Optional[Dict[str, Any]]:
        """
        Scrape Instagram user profile
        
        Args:
            username: Instagram username (without @)
            
        Returns:
            User profile data or None if not found
        """
        if not self.is_logged_in:
            if not self.login_to_instagram():
                return None
        
        try:
            self.rate_limit()
            
            # Navigate to user profile
            profile_url = f"https://www.instagram.com/{username}/"
            self.driver.get(profile_url)
            time.sleep(random.uniform(2, 4))
            
            profile_data = {
                'username': username,
                'platform': 'instagram',
                'url': profile_url,
                'scraped_at': self.format_timestamp(time.time())
            }
            
            # Get profile picture
            try:
                profile_pic = self.driver.find_element(By.CSS_SELECTOR, "img[alt*='profile photo']")
                profile_data['profile_picture'] = profile_pic.get_attribute('src')
            except NoSuchElementException:
                profile_data['profile_picture'] = None
            
            # Get bio
            try:
                bio_element = self.driver.find_element(By.CSS_SELECTOR, "div[data-testid='UserProfileHeader'] h1")
                profile_data['bio'] = bio_element.text
            except NoSuchElementException:
                profile_data['bio'] = None
            
            # Get follower/following counts
            try:
                stats_elements = self.driver.find_elements(By.CSS_SELECTOR, "a[href*='followers'], a[href*='following']")
                for element in stats_elements:
                    text = element.text
                    if 'followers' in element.get_attribute('href'):
                        profile_data['followers'] = self.parse_count(text.split()[0])
                    elif 'following' in element.get_attribute('href'):
                        profile_data['following'] = self.parse_count(text.split()[0])
            except NoSuchElementException:
                profile_data['followers'] = 0
                profile_data['following'] = 0
            
            # Get post count
            try:
                post_count_element = self.driver.find_element(By.CSS_SELECTOR, "span:contains('posts')")
                profile_data['posts_count'] = self.parse_count(post_count_element.text.split()[0])
            except NoSuchElementException:
                profile_data['posts_count'] = 0
            
            return profile_data
            
        except Exception as e:
            print(f"Error scraping Instagram profile for {username}: {str(e)}")
            return None
    
    def scrape_reels(self, target: str, max_reels: int = 10) -> List[Dict[str, Any]]:
        """
        Scrape Instagram reels/posts
        
        Args:
            target: Target to scrape (username or hashtag)
            max_reels: Maximum number of reels to scrape
            
        Returns:
            List of scraped reel data
        """
        if not self.is_logged_in:
            if not self.login_to_instagram():
                return []
        
        reels_data = []
        
        try:
            # Determine if target is username or hashtag
            if target.startswith('#'):
                # Scrape by hashtag
                reels_data = self._scrape_hashtag(target[1:], max_reels)
            else:
                # Scrape by username
                reels_data = self._scrape_user_posts(target, max_reels)
            
            return reels_data
            
        except Exception as e:
            print(f"Error scraping Instagram reels for {target}: {str(e)}")
            return []
    
    def _scrape_user_posts(self, username: str, max_reels: int) -> List[Dict[str, Any]]:
        """
        Scrape posts from a specific user
        
        Args:
            username: Username to scrape
            max_reels: Maximum number of posts to scrape
            
        Returns:
            List of post data
        """
        try:
            # Navigate to user profile
            profile_url = f"https://www.instagram.com/{username}/"
            self.driver.get(profile_url)
            time.sleep(random.uniform(2, 4))
            
            posts_data = []
            
            # Find first post
            try:
                first_post = self.driver.find_element(By.CSS_SELECTOR, "article a")
                first_post.click()
                time.sleep(random.uniform(2, 3))
                
                for i in range(min(max_reels, 12)):  # Limit to avoid detection
                    post_data = self._extract_post_data()
                    if post_data:
                        posts_data.append(post_data)
                    
                    # Navigate to next post
                    try:
                        next_button = self.driver.find_element(By.CSS_SELECTOR, "button[aria-label='Next']")
                        next_button.click()
                        time.sleep(random.uniform(2, 3))
                    except NoSuchElementException:
                        break
                
                return posts_data
                
            except NoSuchElementException:
                print(f"No posts found for user {username}")
                return []
                
        except Exception as e:
            print(f"Error scraping user posts for {username}: {str(e)}")
            return []
    
    def _scrape_hashtag(self, hashtag: str, max_reels: int) -> List[Dict[str, Any]]:
        """
        Scrape posts by hashtag
        
        Args:
            hashtag: Hashtag to scrape (without #)
            max_reels: Maximum number of posts to scrape
            
        Returns:
            List of post data
        """
        try:
            hashtag_url = f"https://www.instagram.com/explore/tags/{hashtag}/"
            self.driver.get(hashtag_url)
            time.sleep(random.uniform(2, 4))
            
            posts_data = []
            
            # Find posts
            try:
                posts = self.driver.find_elements(By.CSS_SELECTOR, "article a")[:max_reels]
                
                for post in posts:
                    post.click()
                    time.sleep(random.uniform(2, 3))
                    
                    post_data = self._extract_post_data()
                    if post_data:
                        post_data['hashtag'] = hashtag
                        posts_data.append(post_data)
                    
                    # Close post modal
                    try:
                        close_button = self.driver.find_element(By.CSS_SELECTOR, "button[aria-label='Close']")
                        close_button.click()
                        time.sleep(random.uniform(1, 2))
                    except NoSuchElementException:
                        # Try pressing Escape key
                        from selenium.webdriver.common.keys import Keys
                        self.driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.ESCAPE)
                        time.sleep(random.uniform(1, 2))
                
                return posts_data
                
            except NoSuchElementException:
                print(f"No posts found for hashtag #{hashtag}")
                return []
                
        except Exception as e:
            print(f"Error scraping hashtag #{hashtag}: {str(e)}")
            return []
    
    def _extract_post_data(self) -> Optional[Dict[str, Any]]:
        """
        Extract data from current post
        
        Returns:
            Post data or None if extraction failed
        """
        try:
            post_data = {
                'platform': 'instagram',
                'scraped_at': self.format_timestamp(time.time())
            }
            
            # Get post URL
            post_data['url'] = self.driver.current_url
            
            # Get post type (photo/video)
            try:
                # Check for video
                video_element = self.driver.find_element(By.CSS_SELECTOR, "video")
                post_data['type'] = 'video'
                post_data['video_url'] = video_element.get_attribute('src')
            except NoSuchElementException:
                post_data['type'] = 'photo'
            
            # Get caption
            try:
                caption_element = self.driver.find_element(By.CSS_SELECTOR, "h1 + div span")
                caption = caption_element.text
                post_data['caption'] = self.clean_text(caption)
                post_data['hashtags'] = self.extract_hashtags(caption)
                post_data['mentions'] = self.extract_mentions(caption)
            except NoSuchElementException:
                post_data['caption'] = None
                post_data['hashtags'] = []
                post_data['mentions'] = []
            
            # Get likes count
            try:
                likes_element = self.driver.find_element(By.CSS_SELECTOR, "button:contains('like')")
                likes_text = likes_element.text
                post_data['likes'] = self.parse_count(likes_text.split()[0])
            except NoSuchElementException:
                post_data['likes'] = 0
            
            # Get comments count
            try:
                comments_element = self.driver.find_element(By.CSS_SELECTOR, "button:contains('comment')")
                comments_text = comments_element.text
                post_data['comments'] = self.parse_count(comments_text.split()[0])
            except NoSuchElementException:
                post_data['comments'] = 0
            
            # Get timestamp
            try:
                time_element = self.driver.find_element(By.CSS_SELECTOR, "time")
                datetime_attr = time_element.get_attribute('datetime')
                post_data['timestamp'] = datetime_attr
            except NoSuchElementException:
                post_data['timestamp'] = None
            
            return post_data
            
        except Exception as e:
            print(f"Error extracting post data: {str(e)}")
            return None
    
    def close(self):
        """Close the driver"""
        if self.driver:
            self.driver.quit()
            self.driver = None
            self.is_logged_in = False