"""
Instagram scraping service for the microservice
Handles Instagram data extraction using multiple methods
"""
import logging
import time
import re
import instaloader
from typing import List, Optional, Dict, Any
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager

from .models import ReelData, CreatorInfo, Comment, ScrapingRequest
from .config import config

logger = logging.getLogger(__name__)

class InstagramScraper:
    """Instagram scraping service with multiple extraction methods"""
    
    def __init__(self):
        self.il = instaloader.Instaloader()
        self._setup_instaloader()
    
    def _setup_instaloader(self):
        """Setup instaloader with proper configuration"""
        self.il.download_pictures = False
        self.il.download_videos = False
        self.il.download_video_thumbnails = False
        self.il.download_geotags = False
        self.il.download_comments = True
        self.il.save_metadata = False
        self.il.compress_json = False
        
        # Login if credentials are available
        if config.instagram.use_login and config.instagram.username and config.instagram.password:
            try:
                self.il.login(config.instagram.username, config.instagram.password)
                logger.info("Successfully logged in to Instagram using Instaloader")
            except Exception as e:
                logger.warning(f"Failed to login with Instaloader: {e}")
    
    def _get_chrome_options(self) -> Options:
        """Get Chrome options for headless browsing"""
        chrome_options = Options()
        chrome_options.add_argument("--headless=new")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1280,720")
        chrome_options.add_argument(
            "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        )
        return chrome_options
    
    def _extract_with_instaloader(self, target: str, max_reels: int, include_comments: bool) -> List[ReelData]:
        """Extract reels using Instaloader library"""
        reels = []
        
        try:
            # Determine target type and extract accordingly
            if target.startswith('@'):
                # Profile extraction
                username = target[1:]
                profile = instaloader.Profile.from_username(self.il.context, username)
                
                posts = list(profile.get_posts())
                for post in posts[:max_reels]:
                    if post.is_video:
                        reel = self._convert_instaloader_post(post, include_comments)
                        if reel:
                            reels.append(reel)
                            
            elif target.startswith('#'):
                # Hashtag extraction
                hashtag = target[1:]
                hashtag_obj = instaloader.Hashtag.from_name(self.il.context, hashtag)
                
                posts = list(hashtag_obj.get_posts())
                for post in posts[:max_reels]:
                    if post.is_video:
                        reel = self._convert_instaloader_post(post, include_comments)
                        if reel:
                            reels.append(reel)
                            
            elif 'instagram.com' in target:
                # Direct URL extraction
                if '/reel/' in target:
                    shortcode = target.split('/reel/')[1].split('/')[0]
                    post = instaloader.Post.from_shortcode(self.il.context, shortcode)
                    
                    if post.is_video:
                        reel = self._convert_instaloader_post(post, include_comments)
                        if reel:
                            reels.append(reel)
            
            logger.info(f"Extracted {len(reels)} reels using Instaloader")
            
        except Exception as e:
            logger.error(f"Instaloader extraction failed: {e}")
            raise
        
        return reels
    
    def _convert_instaloader_post(self, post: instaloader.Post, include_comments: bool) -> Optional[ReelData]:
        """Convert Instaloader Post to ReelData"""
        try:
            # Extract hashtags and mentions from caption
            caption = post.caption or ""
            hashtags = re.findall(r'#\w+', caption)
            mentions = re.findall(r'@\w+', caption)
            
            # Get comments if requested
            comments = []
            if include_comments and post.comments > 0:
                try:
                    for comment in post.get_comments():
                        comments.append(Comment(
                            user=comment.owner.username,
                            comment=comment.text,
                            timestamp=comment.created_at_utc,
                            likes=comment.likes_count if hasattr(comment, 'likes_count') else None
                        ))
                        if len(comments) >= 10:  # Limit comments
                            break
                except Exception as e:
                    logger.warning(f"Failed to extract comments: {e}")
            
            # Create creator info
            creator = CreatorInfo(
                username=post.owner_username,
                profile_url=f"https://www.instagram.com/{post.owner_username}/",
                full_name=getattr(post.owner_profile, 'full_name', None),
                followers_count=getattr(post.owner_profile, 'followers', None),
                following_count=getattr(post.owner_profile, 'followees', None)
            )
            
            return ReelData(
                reel_id=post.shortcode,
                reel_url=f"https://www.instagram.com/reel/{post.shortcode}/",
                video_url=post.video_url,
                caption=caption,
                creator=creator,
                likes=post.likes,
                views=post.video_view_count if post.video_view_count else 0,
                comments_count=post.comments,
                posted_at=post.date_utc,
                hashtags=hashtags,
                mentions=mentions,
                top_comments=comments[:5],  # Top 5 comments
                raw_data={'instaloader_data': str(post)}
            )
            
        except Exception as e:
            logger.error(f"Failed to convert post {post.shortcode}: {e}")
            return None
    
    def _extract_with_selenium(self, target: str, max_reels: int, include_comments: bool) -> List[ReelData]:
        """Extract reels using Selenium WebDriver"""
        reels = []
        driver = None
        
        try:
            # Initialize WebDriver
            chrome_options = self._get_chrome_options()
            service = Service(ChromeDriverManager().install())
            driver = webdriver.Chrome(service=service, options=chrome_options)
            
            # Login if credentials are available
            if config.instagram.use_login and config.instagram.username and config.instagram.password:
                self._login_with_selenium(driver)
            
            # Extract based on target type
            if target.startswith('@'):
                reels = self._extract_profile_selenium(driver, target[1:], max_reels, include_comments)
            elif target.startswith('#'):
                reels = self._extract_hashtag_selenium(driver, target[1:], max_reels, include_comments)
            elif 'instagram.com' in target:
                reel = self._extract_single_reel_selenium(driver, target, include_comments)
                if reel:
                    reels.append(reel)
            
            logger.info(f"Extracted {len(reels)} reels using Selenium")
            
        except Exception as e:
            logger.error(f"Selenium extraction failed: {e}")
            raise
        
        finally:
            if driver:
                driver.quit()
        
        return reels
    
    def _login_with_selenium(self, driver: webdriver.Chrome):
        """Login to Instagram using Selenium"""
        try:
            driver.get("https://www.instagram.com/accounts/login/")
            time.sleep(3)
            
            # Fill credentials
            username_field = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.NAME, "username"))
            )
            password_field = driver.find_element(By.NAME, "password")
            
            username_field.send_keys(config.instagram.username)
            password_field.send_keys(config.instagram.password)
            
            # Click login
            login_button = driver.find_element(By.XPATH, '//button[@type="submit"]')
            login_button.click()
            
            # Wait for login to complete
            time.sleep(5)
            logger.info("Successfully logged in to Instagram using Selenium")
            
        except Exception as e:
            logger.warning(f"Failed to login with Selenium: {e}")
    
    def _extract_profile_selenium(self, driver: webdriver.Chrome, username: str, max_reels: int, include_comments: bool) -> List[ReelData]:
        """Extract reels from a profile using Selenium"""
        reels = []
        
        try:
            profile_url = f"https://www.instagram.com/{username}/"
            driver.get(profile_url)
            time.sleep(3)
            
            # Find reel links
            reel_links = driver.find_elements(By.XPATH, '//a[contains(@href, "/reel/")]')[:max_reels]
            
            for link in reel_links:
                reel_url = link.get_attribute("href")
                if reel_url:
                    reel = self._extract_single_reel_selenium(driver, reel_url, include_comments)
                    if reel:
                        reels.append(reel)
                        
        except Exception as e:
            logger.error(f"Failed to extract profile {username}: {e}")
            
        return reels
    
    def _extract_hashtag_selenium(self, driver: webdriver.Chrome, hashtag: str, max_reels: int, include_comments: bool) -> List[ReelData]:
        """Extract reels from a hashtag using Selenium"""
        reels = []
        
        try:
            hashtag_url = f"https://www.instagram.com/explore/tags/{hashtag}/"
            driver.get(hashtag_url)
            time.sleep(3)
            
            # Find post links
            post_links = driver.find_elements(By.XPATH, '//a[contains(@href, "/p/")]')[:max_reels]
            
            for link in post_links:
                post_url = link.get_attribute("href")
                if post_url:
                    reel = self._extract_single_reel_selenium(driver, post_url, include_comments)
                    if reel:
                        reels.append(reel)
                        
        except Exception as e:
            logger.error(f"Failed to extract hashtag #{hashtag}: {e}")
            
        return reels
    
    def _extract_single_reel_selenium(self, driver: webdriver.Chrome, reel_url: str, include_comments: bool) -> Optional[ReelData]:
        """Extract a single reel using Selenium"""
        try:
            driver.get(reel_url)
            time.sleep(3)
            
            # Extract basic information
            video_url = ""
            caption = ""
            likes = 0
            views = 0
            
            # Get video URL
            try:
                video_element = driver.find_element(By.TAG_NAME, "video")
                video_url = video_element.get_attribute("src")
            except:
                pass
            
            # Get caption
            try:
                caption_element = driver.find_element(By.XPATH, '//h1[contains(@class, "_ap3a")]')
                caption = caption_element.text
            except:
                pass
            
            # Get engagement metrics
            try:
                likes_element = driver.find_element(By.XPATH, '//span[contains(@class, "_aacl")]')
                likes_str = likes_element.text.replace(',', '')
                likes = int(likes_str) if likes_str.isdigit() else 0
            except:
                pass
            
            # Extract hashtags and mentions
            hashtags = re.findall(r'#\w+', caption)
            mentions = re.findall(r'@\w+', caption)
            
            # Get username from URL
            username = reel_url.split('/')[3] if len(reel_url.split('/')) > 3 else "unknown"
            
            creator = CreatorInfo(
                username=username,
                profile_url=f"https://www.instagram.com/{username}/"
            )
            
            # Extract shortcode from URL
            shortcode = reel_url.split('/reel/')[1].split('/')[0] if '/reel/' in reel_url else reel_url.split('/p/')[1].split('/')[0]
            
            return ReelData(
                reel_id=shortcode,
                reel_url=reel_url,
                video_url=video_url,
                caption=caption,
                creator=creator,
                likes=likes,
                views=views,
                comments_count=0,
                hashtags=hashtags,
                mentions=mentions
            )
            
        except Exception as e:
            logger.error(f"Failed to extract reel {reel_url}: {e}")
            return None
    
    def scrape_reels(self, request: ScrapingRequest) -> List[ReelData]:
        """Main scraping method that chooses the appropriate extraction method"""
        logger.info(f"Starting reel scraping for target: {request.target}")
        
        reels = []
        errors = []
        
        try:
            if request.scraping_method == "instaloader":
                reels = self._extract_with_instaloader(
                    request.target, 
                    request.max_reels, 
                    request.include_comments
                )
            elif request.scraping_method == "selenium":
                reels = self._extract_with_selenium(
                    request.target, 
                    request.max_reels, 
                    request.include_comments
                )
            else:
                raise ValueError(f"Unknown scraping method: {request.scraping_method}")
                
        except Exception as e:
            error_msg = f"Scraping failed: {str(e)}"
            logger.error(error_msg)
            errors.append(error_msg)
            raise
        
        logger.info(f"Successfully scraped {len(reels)} reels")
        return reels