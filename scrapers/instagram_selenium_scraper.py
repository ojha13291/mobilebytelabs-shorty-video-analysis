"""
Instagram Selenium scraper with enhanced reliability
"""

import time
import random
import logging
from typing import Dict, List, Any, Optional
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException, NoSuchElementException

from scrapers.selenium_scraper import SeleniumScraper

logger = logging.getLogger(__name__)


class InstagramSeleniumScraper(SeleniumScraper):
    """
    Instagram-specific Selenium scraper
    """
    
    def __init__(self):
        """Initialize Instagram scraper"""
        super().__init__("instagram", rate_limit_delay=2.0)
        self.base_url = "https://www.instagram.com"
        self.is_logged_in = False
        
    def login(self, username: str, password: str) -> bool:
        """
        Login to Instagram
        
        Args:
            username: Instagram username
            password: Instagram password
            
        Returns:
            True if login successful
        """
        try:
            logger.info(f"Attempting to login to Instagram as {username}")
            
            # Navigate to Instagram login page
            self.driver.get(f"{self.base_url}/accounts/login/")
            time.sleep(random.uniform(2, 4))
            
            # Wait for and fill username field
            username_field = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.NAME, "username"))
            )
            username_field.clear()
            username_field.send_keys(username)
            time.sleep(random.uniform(0.5, 1.5))
            
            # Fill password field
            password_field = self.driver.find_element(By.NAME, "password")
            password_field.clear()
            password_field.send_keys(password)
            time.sleep(random.uniform(0.5, 1.5))
            
            # Click login button
            login_button = self.driver.find_element(By.XPATH, "//button[@type='submit']")
            login_button.click()
            
            # Wait for login to complete
            time.sleep(random.uniform(3, 5))
            
            # Check if login was successful by looking for common elements
            try:
                # Look for profile icon or home feed
                WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, "//a[contains(@href, '/accounts/')]"))
                )
                self.is_logged_in = True
                logger.info("Instagram login successful")
                return True
                
            except TimeoutException:
                # Check for error messages
                error_elements = self.driver.find_elements(By.XPATH, "//div[@role='alert']")
                if error_elements:
                    error_text = error_elements[0].text
                    logger.error(f"Instagram login failed: {error_text}")
                else:
                    logger.error("Instagram login failed - no success indicators found")
                return False
                
        except Exception as e:
            logger.error(f"Instagram login error: {str(e)}")
            return False
    
    def scrape_user_profile(self, username: str) -> Optional[Dict[str, Any]]:
        """
        Scrape Instagram user profile
        
        Args:
            username: Instagram username
            
        Returns:
            User profile data or None
        """
        try:
            logger.info(f"Scraping Instagram profile: {username}")
            
            # Navigate to user profile
            profile_url = f"{self.base_url}/{username}/"
            self.driver.get(profile_url)
            time.sleep(random.uniform(2, 4))
            
            # Wait for profile to load
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "main"))
            )
            
            # Parse with BeautifulSoup for better data extraction
            soup = self.parse_with_bs4()
            
            # Extract profile data
            profile_data = {
                'platform': 'instagram',
                'username': username,
                'profile_url': profile_url,
                'scraped_at': time.strftime('%Y-%m-%d %H:%M:%S')
            }
            
            # Extract profile picture
            img_elements = soup.find_all('img')
            if img_elements:
                profile_data['profile_picture'] = img_elements[0].get('src', '')
            
            # Extract bio and stats using Selenium
            try:
                # Bio
                bio_element = self.driver.find_element(By.XPATH, "//div[contains(@class, 'bio')]").text
                profile_data['bio'] = bio_element
            except NoSuchElementException:
                profile_data['bio'] = ''
            
            # Stats (posts, followers, following)
            try:
                stats_elements = self.driver.find_elements(By.XPATH, "//span[contains(@class, 'count')]")
                if len(stats_elements) >= 3:
                    profile_data['posts_count'] = self.parse_count(stats_elements[0].text)
                    profile_data['followers_count'] = self.parse_count(stats_elements[1].text)
                    profile_data['following_count'] = self.parse_count(stats_elements[2].text)
            except NoSuchElementException:
                pass
            
            return profile_data
            
        except Exception as e:
            logger.error(f"Error scraping Instagram profile {username}: {str(e)}")
            return None
    
    def scrape_user_posts(self, username: str, max_posts: int = 10) -> List[Dict[str, Any]]:
        """
        Scrape posts from Instagram user
        
        Args:
            username: Instagram username
            max_posts: Maximum number of posts to scrape
            
        Returns:
            List of post data
        """
        try:
            logger.info(f"Scraping Instagram posts for user: {username}")
            
            # Navigate to user profile
            profile_url = f"{self.base_url}/{username}/"
            self.driver.get(profile_url)
            time.sleep(random.uniform(2, 4))
            
            posts = []
            post_links = []
            
            # Find post links
            try:
                # Look for post links
                post_elements = WebDriverWait(self.driver, 10).until(
                    EC.presence_of_all_elements_located((By.XPATH, "//a[contains(@href, '/p/')]"))
                )
                
                # Extract post URLs
                for element in post_elements[:max_posts]:
                    href = element.get_attribute('href')
                    if href and '/p/' in href:
                        post_links.append(href)
                
            except TimeoutException:
                logger.warning("No post links found on profile page")
                return posts
            
            # Scrape individual posts
            for post_url in post_links[:max_posts]:
                try:
                    post_data = self._scrape_single_post(post_url)
                    if post_data:
                        posts.append(post_data)
                    
                    # Rate limiting
                    time.sleep(random.uniform(2, 4))
                    
                except Exception as e:
                    logger.warning(f"Error scraping post {post_url}: {str(e)}")
                    continue
            
            return posts
            
        except Exception as e:
            logger.error(f"Error scraping Instagram posts for {username}: {str(e)}")
            return []
    
    def _scrape_single_post(self, post_url: str) -> Optional[Dict[str, Any]]:
        """
        Scrape a single Instagram post
        
        Args:
            post_url: URL of the post
            
        Returns:
            Post data or None
        """
        try:
            self.driver.get(post_url)
            time.sleep(random.uniform(2, 4))
            
            # Parse with BeautifulSoup
            soup = self.parse_with_bs4()
            
            post_data = {
                'platform': 'instagram',
                'url': post_url,
                'scraped_at': time.strftime('%Y-%m-%d %H:%M:%S')
            }
            
            # Extract post content
            try:
                # Look for caption text
                caption_elements = soup.find_all('span')
                for element in caption_elements:
                    text = element.get_text().strip()
                    if len(text) > 10:  # Basic filter for meaningful text
                        post_data['caption'] = text
                        break
            except Exception as e:
                logger.warning(f"Error extracting caption: {str(e)}")
                post_data['caption'] = ''
            
            # Extract engagement metrics
            try:
                # Look for like count
                like_elements = self.driver.find_elements(By.XPATH, "//button[contains(@aria-label, 'like')]//span")
                if like_elements:
                    likes_text = like_elements[0].text
                    post_data['likes'] = self.parse_count(likes_text)
                
                # Look for comment count
                comment_elements = self.driver.find_elements(By.XPATH, "//button[contains(@aria-label, 'comment')]//span")
                if comment_elements:
                    comments_text = comment_elements[0].text
                    post_data['comments'] = self.parse_count(comments_text)
                    
            except Exception as e:
                logger.warning(f"Error extracting engagement metrics: {str(e)}")
                post_data['likes'] = 0
                post_data['comments'] = 0
            
            # Extract hashtags and mentions
            caption = post_data.get('caption', '')
            post_data['hashtags'] = self.extract_hashtags(caption)
            post_data['mentions'] = self.extract_mentions(caption)
            
            # Extract media URLs
            try:
                img_elements = soup.find_all('img')
                if img_elements:
                    post_data['media_urls'] = [img.get('src', '') for img in img_elements if img.get('src')]
            except Exception as e:
                logger.warning(f"Error extracting media URLs: {str(e)}")
                post_data['media_urls'] = []
            
            return post_data
            
        except Exception as e:
            logger.error(f"Error scraping Instagram post {post_url}: {str(e)}")
            return None
    
    def scrape_hashtag_posts(self, hashtag: str, max_posts: int = 10) -> List[Dict[str, Any]]:
        """
        Scrape posts by hashtag
        
        Args:
            hashtag: Hashtag to search (without #)
            max_posts: Maximum number of posts
            
        Returns:
            List of post data
        """
        try:
            logger.info(f"Scraping Instagram posts for hashtag: #{hashtag}")
            
            # Navigate to hashtag page
            hashtag_url = f"{self.base_url}/explore/tags/{hashtag}/"
            self.driver.get(hashtag_url)
            time.sleep(random.uniform(2, 4))
            
            posts = []
            
            # Find post links on hashtag page
            try:
                post_elements = WebDriverWait(self.driver, 10).until(
                    EC.presence_of_all_elements_located((By.XPATH, "//a[contains(@href, '/p/')]"))
                )
                
                post_links = []
                for element in post_elements[:max_posts]:
                    href = element.get_attribute('href')
                    if href and '/p/' in href:
                        post_links.append(href)
                
                # Scrape individual posts
                for post_url in post_links:
                    post_data = self._scrape_single_post(post_url)
                    if post_data:
                        posts.append(post_data)
                    
                    # Rate limiting
                    time.sleep(random.uniform(2, 4))
                
            except TimeoutException:
                logger.warning("No posts found for hashtag")
            
            return posts
            
        except Exception as e:
            logger.error(f"Error scraping Instagram hashtag #{hashtag}: {str(e)}")
            return []
    
    def scrape_reels(self, target: str, max_reels: int = 10) -> List[Dict[str, Any]]:
        """
        Scrape Instagram reels
        
        Args:
            target: Target to scrape (username or hashtag)
            max_reels: Maximum number of reels
            
        Returns:
            List of reel data
        """
        try:
            logger.info(f"Scraping Instagram reels for target: {target}")
            
            # Determine if target is username or hashtag
            if target.startswith('#'):
                # Hashtag search
                hashtag = target[1:]  # Remove #
                posts = self.scrape_hashtag_posts(hashtag, max_reels)
            else:
                # User profile
                posts = self.scrape_user_posts(target, max_reels)
            
            # Filter for video content (reels)
            reels = []
            for post in posts:
                # Mark as reel if it has video-like characteristics
                post['is_reel'] = True
                post['content_type'] = 'reel'
                reels.append(post)
            
            return reels
            
        except Exception as e:
            logger.error(f"Error scraping Instagram reels for {target}: {str(e)}")
            return []
    
    def handle_rate_limiting(self):
        """Instagram-specific rate limiting"""
        # Instagram is more strict, so use longer delays
        delay = random.uniform(3.0, 6.0)
        logger.info(f"Instagram rate limiting: sleeping for {delay:.1f} seconds")
        time.sleep(delay)