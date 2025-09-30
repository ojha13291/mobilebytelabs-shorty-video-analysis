"""
YouTube Selenium scraper with enhanced reliability
"""

import time
import random
import logging
import re
import json
from typing import Dict, List, Any, Optional
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, WebDriverException
from urllib.parse import urlparse, parse_qs

from scrapers.selenium_scraper import SeleniumScraper

logger = logging.getLogger(__name__)

# YouTube API fallback (optional)
try:
    from googleapiclient.discovery import build
    from googleapiclient.errors import HttpError
    YOUTUBE_API_AVAILABLE = True
except ImportError:
    YOUTUBE_API_AVAILABLE = False
    logger.info("YouTube API client not available. Install google-api-python-client for API fallback.")


class YouTubeSeleniumScraper(SeleniumScraper):
    """
    YouTube-specific Selenium scraper
    """
    
    def __init__(self):
        """Initialize YouTube scraper"""
        super().__init__("youtube", rate_limit_delay=1.5)
        self.base_url = "https://www.youtube.com"
        # Initialize driver on first use
        self._driver_initialized = False
        
        # Updated YouTube selectors based on current DOM structure (2024)
        self.selectors = {
            'video_container': [
                'ytd-rich-item-renderer',
                'ytd-video-renderer',
                'ytd-grid-video-renderer',
                'ytd-compact-video-renderer'
            ],
            'video_title': [
                'a#video-title',
                'h3.ytd-video-renderer a',
                '#video-title',
                'a[aria-describedby]',
                'h1.ytd-video-primary-info-renderer'
            ],
            'video_views': [
                'span.inline-metadata-item:first-child',
                'span.style-scope.ytd-video-meta-block',
                '#metadata-line span:first-child',
                'span[aria-label*="views"]',
                'span.view-count'
            ],
            'video_duration': [
                'span.ytd-thumbnail-overlay-time-status-renderer',
                'span.style-scope.ytd-thumbnail-overlay-time-status-renderer',
                '.ytp-time-duration',
                'span[class*="duration"]'
            ],
            'channel_name': [
                'a.yt-simple-endpoint.style-scope.yt-formatted-string',
                'yt-formatted-string#channel-name a',
                '#channel-name a',
                'a[href*="/channel/"]',
                'a[href*="/@"]'
            ],
            'video_description': [
                'yt-formatted-string#description',
                '#description',
                'meta[name="description"]',
                'div[id="description"]'
            ],
            'like_count': [
                'button[aria-label*="like"] span',
                '#top-level-buttons-computed button:first-child span',
                'yt-formatted-string[aria-label*="likes"]',
                'div.yt-spec-touch-feedback-shape__fill',
                'yt-touch-feedback-shape'
            ],
            'comment_count': [
                'h2#count span',
                'yt-formatted-string.count-text',
                '#comments h2 span',
                'span[class*="count-text"]'
            ]
        }
    
    def _find_element_by_selectors(self, soup, selectors: List[str], multiple: bool = False):
        """
        Find element(s) using multiple CSS selectors as fallbacks
        
        Args:
            soup: BeautifulSoup object
            selectors: List of CSS selectors to try
            multiple: Whether to find multiple elements
            
        Returns:
            Element(s) or None
        """
        for selector in selectors:
            try:
                if multiple:
                    elements = soup.select(selector)
                    if elements:
                        return elements
                else:
                    element = soup.select_one(selector)
                    if element:
                        return element
            except Exception as e:
                logger.debug(f"Selector '{selector}' failed: {str(e)}")
                continue
        return [] if multiple else None
    
    def _extract_video_id_from_url(self, url: str) -> str:
        """
        Extract video ID from YouTube URL
        
        Args:
            url: YouTube video URL
            
        Returns:
            Video ID or empty string
        """
        try:
            parsed_url = urlparse(url)
            if 'youtube.com' in parsed_url.netloc:
                if 'watch' in parsed_url.path:
                    return parse_qs(parsed_url.query).get('v', [''])[0]
                elif '/embed/' in parsed_url.path:
                    return parsed_url.path.split('/embed/')[-1].split('?')[0]
            elif 'youtu.be' in parsed_url.netloc:
                return parsed_url.path.lstrip('/')
        except Exception as e:
            logger.warning(f"Error extracting video ID from {url}: {str(e)}")
        return ''
    
    def _extract_engagement_data_advanced(self, soup) -> Dict[str, Any]:
        """
        Advanced extraction of engagement data using current YouTube DOM structure
        
        Args:
            soup: BeautifulSoup object
            
        Returns:
            Dictionary with engagement metrics
        """
        engagement_data = {
            'likes': 0,
            'comments': 0,
            'views': 0,
            'channel': '',
            'channel_url': ''
        }
        
        try:
            # Extract channel name using the provided HTML structure
            # <a class="yt-simple-endpoint style-scope yt-formatted-string" href="/@Xatumi">Xatumi</a>
            channel_selectors = [
                'a.yt-simple-endpoint.style-scope.yt-formatted-string[href*="/@"]',
                'a.yt-simple-endpoint.style-scope.yt-formatted-string',
                'yt-formatted-string#channel-name a',
                '#channel-name a'
            ]
            
            for selector in channel_selectors:
                try:
                    channel_elem = soup.select_one(selector)
                    if channel_elem:
                        engagement_data['channel'] = channel_elem.get_text().strip()
                        href = channel_elem.get('href', '')
                        if href:
                            engagement_data['channel_url'] = f"https://www.youtube.com{href}" if not href.startswith('http') else href
                        break
                except Exception as e:
                    logger.debug(f"Channel selector '{selector}' failed: {str(e)}")
                    continue
            
            # Extract likes using Selenium for dynamic content with improved approach
            if hasattr(self, 'driver') and self.driver:
                try:
                    # Wait a bit for dynamic content to load
                    import time
                    time.sleep(2)
                    
                    # Look for like button with various approaches
                    like_button_strategies = [
                        # Strategy 1: Find by aria-label containing like count
                        {
                            'xpath': "//button[@aria-label and contains(@aria-label, 'like')]",
                            'extract_from': 'aria-label'
                        },
                        # Strategy 2: Find like button by segmented button structure
                        {
                            'xpath': "//div[@id='top-level-buttons-computed']//button[1]",
                            'extract_from': 'text'
                        },
                        # Strategy 3: Find by button with like icon
                        {
                            'xpath': "//button[contains(@aria-label, 'like') or contains(@title, 'like')]",
                            'extract_from': 'both'
                        },
                        # Strategy 4: Find by segmented button container
                        {
                            'xpath': "//ytd-segmented-like-dislike-button-renderer//button[1]",
                            'extract_from': 'text'
                        }
                    ]
                    
                    for strategy in like_button_strategies:
                        try:
                            like_buttons = self.driver.find_elements(By.XPATH, strategy['xpath'])
                            
                            for button in like_buttons:
                                likes_found = 0
                                
                                # Extract based on strategy
                                if strategy['extract_from'] in ['aria-label', 'both']:
                                    aria_label = button.get_attribute('aria-label')
                                    if aria_label and 'like' in aria_label.lower():
                                        likes_found = self.parse_count(aria_label)
                                        if likes_found > 0:
                                            engagement_data['likes'] = likes_found
                                            logger.debug(f"Found likes via aria-label: {likes_found}")
                                            break
                                
                                if strategy['extract_from'] in ['text', 'both'] and likes_found == 0:
                                    button_text = button.text.strip()
                                    if button_text and any(char.isdigit() for char in button_text):
                                        likes_found = self.parse_count(button_text)
                                        if likes_found > 0:
                                            engagement_data['likes'] = likes_found
                                            logger.debug(f"Found likes via button text: {likes_found}")
                                            break
                                
                                # Also try to get text from child elements
                                if likes_found == 0:
                                    try:
                                        child_spans = button.find_elements(By.TAG_NAME, 'span')
                                        for span in child_spans:
                                            span_text = span.text.strip()
                                            if span_text and any(char.isdigit() for char in span_text):
                                                likes_found = self.parse_count(span_text)
                                                if likes_found > 0:
                                                    engagement_data['likes'] = likes_found
                                                    logger.debug(f"Found likes via child span: {likes_found}")
                                                    break
                                    except Exception:
                                        pass
                            
                            if engagement_data['likes'] > 0:
                                break
                                
                        except Exception as e:
                            logger.debug(f"Like extraction strategy failed: {str(e)}")
                            continue
                
                except Exception as e:
                    logger.debug(f"Selenium like extraction failed: {str(e)}")
            
            # Extract views using multiple approaches
            view_selectors = [
                'span.view-count',
                'span[class*="view-count"]',
                'span.inline-metadata-item',
                'meta[itemprop="interactionCount"]'
            ]
            
            for selector in view_selectors:
                try:
                    view_elem = soup.select_one(selector)
                    if view_elem:
                        view_text = view_elem.get('content', '') or view_elem.get_text().strip()
                        if view_text and ('view' in view_text.lower() or any(char.isdigit() for char in view_text)):
                            views = self.parse_count(view_text)
                            if views > 0:
                                engagement_data['views'] = views
                                break
                except Exception as e:
                    logger.debug(f"View selector '{selector}' failed: {str(e)}")
                    continue
            
            # Extract comment count
            comment_selectors = [
                'h2#count span',
                'yt-formatted-string.count-text',
                'span[class*="count-text"]',
                '#comments h2 span'
            ]
            
            for selector in comment_selectors:
                try:
                    comment_elem = soup.select_one(selector)
                    if comment_elem:
                        comment_text = comment_elem.get_text().strip()
                        if comment_text and any(char.isdigit() for char in comment_text):
                            comments = self.parse_count(comment_text)
                            if comments > 0:
                                engagement_data['comments'] = comments
                                break
                except Exception as e:
                    logger.debug(f"Comment selector '{selector}' failed: {str(e)}")
                    continue
            
        except Exception as e:
            logger.warning(f"Error in advanced engagement extraction: {str(e)}")
        
        return engagement_data
    
    def _setup_driver_for_youtube(self):
        """Setup driver with YouTube-specific configurations"""
        if not self._driver_initialized:
            if not self.setup_driver(headless=True):
                logger.error("Failed to initialize WebDriver")
                return False
            
            # Enable JavaScript for YouTube and remove automation detection
            try:
                self.driver.execute_script("""
                    try {
                        Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
                    } catch(e) {}
                    try {
                        Object.defineProperty(navigator, 'plugins', {get: () => [1, 2, 3, 4, 5]});
                    } catch(e) {}
                    try {
                        Object.defineProperty(navigator, 'languages', {get: () => ['en-US', 'en']});
                    } catch(e) {}
                """)
            except Exception as e:
                logger.debug(f"JavaScript execution warning: {str(e)}")
            
            self._driver_initialized = True
        return True
        
    def scrape_channel_videos(self, channel_url: str, max_videos: int = 10) -> List[Dict[str, Any]]:
        """
        Scrape videos from a YouTube channel with improved reliability
        
        Args:
            channel_url: YouTube channel URL
            max_videos: Maximum number of videos to scrape
            
        Returns:
            List of video data
        """
        try:
            logger.info(f"Scraping YouTube channel: {channel_url}")
            
            # Setup driver
            if not self._setup_driver_for_youtube():
                return []
            
            # Ensure we're on the videos page
            if '/videos' not in channel_url:
                if channel_url.endswith('/'):
                    channel_url = channel_url + 'videos'
                else:
                    channel_url = channel_url + '/videos'
            
            # Navigate to channel videos page
            self.driver.get(channel_url)
            time.sleep(random.uniform(3, 5))
            
            # Wait for page to load
            self.wait_for_page_load()
            
            # Try multiple approaches to find videos tab
            videos_tab_selectors = [
                "//yt-formatted-string[text()='Videos']",
                "//paper-tab[contains(@aria-label, 'Videos')]",
                "//a[contains(@href, '/videos')]",
                "//div[contains(@class, 'tab-content')]//a[contains(text(), 'Videos')]"
            ]
            
            for selector in videos_tab_selectors:
                try:
                    videos_tab = WebDriverWait(self.driver, 5).until(
                        EC.element_to_be_clickable((By.XPATH, selector))
                    )
                    videos_tab.click()
                    time.sleep(random.uniform(2, 3))
                    logger.info("Successfully clicked Videos tab")
                    break
                except TimeoutException:
                    continue
            else:
                logger.warning("Videos tab not found, continuing with current page")
            
            videos = []
            
            # Progressive scrolling to load more videos
            for scroll_attempt in range(5):
                # Scroll to load more videos
                self.scroll_to_load_content(scroll_pause_time=2.0, max_scrolls=2)
                
                # Parse with BeautifulSoup
                soup = self.parse_with_bs4()
                
                # Try multiple container selectors
                video_elements = self._find_element_by_selectors(
                    soup, self.selectors['video_container'], multiple=True
                )
                
                if video_elements:
                    logger.info(f"Found {len(video_elements)} video elements")
                    break
                    
                time.sleep(1)
            
            if not video_elements:
                logger.warning("No video elements found")
                return []
            
            # Extract video data
            for element in video_elements[:max_videos]:
                try:
                    video_data = self._extract_video_data_improved(element)
                    if video_data:
                        videos.append(video_data)
                        
                except Exception as e:
                    logger.warning(f"Error extracting video data: {str(e)}")
                    continue
            
            logger.info(f"Successfully scraped {len(videos)} videos from channel")
            return videos
            
        except Exception as e:
            logger.error(f"Error scraping YouTube channel {channel_url}: {str(e)}")
            return []
    
    def _extract_video_data_improved(self, element) -> Optional[Dict[str, Any]]:
        """
        Improved video data extraction with multiple selector fallbacks
        
        Args:
            element: BeautifulSoup element
            
        Returns:
            Video data dictionary or None
        """
        try:
            # Extract title and URL using multiple selectors
            title_elem = self._find_element_by_selectors(element, self.selectors['video_title'])
            if not title_elem:
                return None
            
            title = title_elem.get('title', '') or title_elem.get_text().strip()
            video_url = title_elem.get('href', '')
            
            if video_url:
                if not video_url.startswith('http'):
                    video_url = f"https://www.youtube.com{video_url}"
            
            # Extract video ID
            video_id = self._extract_video_id_from_url(video_url)
            
            # Use advanced engagement extraction for better accuracy
            engagement_data = self._extract_engagement_data_advanced(element)
            
            # Extract channel info (with fallback to advanced method)
            channel_elem = self._find_element_by_selectors(element, self.selectors['channel_name'])
            channel = channel_elem.get_text().strip() if channel_elem else engagement_data.get('channel', '')
            channel_url = ''
            if channel_elem and channel_elem.get('href'):
                channel_url = f"https://www.youtube.com{channel_elem.get('href')}"
            elif engagement_data.get('channel_url'):
                channel_url = engagement_data['channel_url']
            
            # Extract view count (with fallback to advanced method)
            views_elem = self._find_element_by_selectors(element, self.selectors['video_views'])
            views_text = views_elem.get_text().strip() if views_elem else ''
            views = self.parse_count(views_text) or engagement_data.get('views', 0)
            
            # Extract duration using multiple selectors
            duration_elem = self._find_element_by_selectors(element, self.selectors['video_duration'])
            duration = duration_elem.get_text().strip() if duration_elem else ''
            
            # Extract thumbnail URL
            thumbnail_elem = element.find('img')
            thumbnail_url = ''
            if thumbnail_elem:
                thumbnail_url = thumbnail_elem.get('src', '') or thumbnail_elem.get('data-src', '')
            
            # Extract upload date (if available)
            upload_date = ''
            date_patterns = [
                'span[aria-label*="ago"]',
                'span.style-scope.ytd-video-meta-block:last-child',
                '#metadata-line span:last-child'
            ]
            date_elem = self._find_element_by_selectors(element, date_patterns)
            if date_elem:
                upload_date = date_elem.get_text().strip()
            
            # Create comprehensive video data
            video_data = {
                'platform': 'youtube',
                'video_id': video_id,
                'title': self.clean_text(title),
                'url': video_url,
                'channel': channel,
                'channel_url': channel_url,
                'views': views,
                'duration': duration,
                'upload_date': upload_date,
                'thumbnail_url': thumbnail_url,
                'scraped_at': time.strftime('%Y-%m-%d %H:%M:%S'),
                'hashtags': self.extract_hashtags(title),
                'engagement_metrics': {
                    'views': views,
                    'likes': engagement_data.get('likes', 0),
                    'comments': engagement_data.get('comments', 0),
                    'shares': 0
                }
            }
            
            return video_data
            
        except Exception as e:
            logger.warning(f"Error extracting improved video data: {str(e)}")
            return None
    
    def scrape_search_results(self, query: str, max_videos: int = 10) -> List[Dict[str, Any]]:
        """
        Scrape videos from YouTube search results with improved reliability
        
        Args:
            query: Search query
            max_videos: Maximum number of videos
            
        Returns:
            List of video data
        """
        try:
            logger.info(f"Scraping YouTube search results for: {query}")
            
            # Setup driver
            if not self._setup_driver_for_youtube():
                return []
            
            # Navigate to search results
            search_url = f"{self.base_url}/results?search_query={query.replace(' ', '+')}"
            self.driver.get(search_url)
            time.sleep(random.uniform(3, 5))
            
            # Wait for search results with multiple selectors
            search_selectors = [
                (By.TAG_NAME, "ytd-item-section-renderer"),
                (By.CSS_SELECTOR, "ytd-video-renderer"),
                (By.CSS_SELECTOR, "[class*='video-renderer']"),
                (By.CSS_SELECTOR, "div#contents")
            ]
            
            search_loaded = False
            for by, selector in search_selectors:
                try:
                    WebDriverWait(self.driver, 8).until(
                        EC.presence_of_element_located((by, selector))
                    )
                    search_loaded = True
                    break
                except TimeoutException:
                    continue
            
            if not search_loaded:
                logger.warning("Search results load timeout, continuing with current state")
            
            videos = []
            
            # Progressive scrolling to load more results
            for scroll_attempt in range(3):
                # Scroll to load more results
                self.scroll_to_load_content(scroll_pause_time=2.0, max_scrolls=2)
                
                # Parse with BeautifulSoup
                soup = self.parse_with_bs4()
                
                # Try multiple container selectors for search results
                search_container_selectors = [
                    'ytd-video-renderer',
                    'ytd-rich-item-renderer',
                    'ytd-grid-video-renderer'
                ]
                
                video_elements = []
                for selector in search_container_selectors:
                    elements = soup.find_all(selector)
                    if elements:
                        video_elements = elements
                        logger.info(f"Found {len(elements)} video elements using selector: {selector}")
                        break
                
                if video_elements:
                    break
                    
                time.sleep(1)
            
            if not video_elements:
                logger.warning("No video elements found in search results")
                return []
            
            # Extract video data from search results
            for element in video_elements[:max_videos]:
                try:
                    video_data = self._extract_video_data_improved(element)
                    if video_data:
                        videos.append(video_data)
                        
                except Exception as e:
                    logger.warning(f"Error extracting search video data: {str(e)}")
                    continue
            
            logger.info(f"Successfully scraped {len(videos)} videos from search")
            return videos
            
        except Exception as e:
            logger.error(f"Error scraping YouTube search results for '{query}': {str(e)}")
            return []
    
    def scrape_video_details(self, video_url: str) -> Optional[Dict[str, Any]]:
        """
        Scrape detailed information from a specific YouTube video
        
        Args:
            video_url: YouTube video URL
            
        Returns:
            Detailed video data or None
        """
        try:
            logger.info(f"Scraping YouTube video details: {video_url}")
            
            # Initialize driver if not already done
            if not self._driver_initialized:
                if not self.setup_driver():
                    logger.error("Failed to initialize WebDriver")
                    return None
                self._driver_initialized = True
            
            self.driver.get(video_url)
            time.sleep(random.uniform(3, 5))
            
            # Wait for video page to load
            WebDriverWait(self.driver, 15).until(
                EC.presence_of_element_located((By.ID, "title"))
            )
            
            # Parse with BeautifulSoup
            soup = self.parse_with_bs4()
            
            # Extract detailed video data
            video_data = {
                'platform': 'youtube',
                'url': video_url,
                'scraped_at': time.strftime('%Y-%m-%d %H:%M:%S')
            }
            
            # Extract title
            try:
                title_elem = soup.find('h1', {'id': 'title'})
                video_data['title'] = title_elem.get_text().strip() if title_elem else ''
            except Exception as e:
                logger.warning(f"Error extracting title: {str(e)}")
                video_data['title'] = ''
            
            # Extract channel info
            try:
                channel_elem = soup.find('yt-formatted-string', {'id': 'channel-name'})
                if channel_elem:
                    channel_link = channel_elem.find('a')
                    video_data['channel'] = channel_link.get_text().strip() if channel_link else ''
                    video_data['channel_url'] = f"https://www.youtube.com{channel_link.get('href', '')}" if channel_link else ''
            except Exception as e:
                logger.warning(f"Error extracting channel info: {str(e)}")
                video_data['channel'] = ''
                video_data['channel_url'] = ''
            
            # Extract view count
            try:
                view_elem = soup.find('span', {'id': 'info-text'})
                if view_elem:
                    view_text = view_elem.get_text()
                    views = self.parse_count(view_text)
                    video_data['views'] = views
            except Exception as e:
                logger.warning(f"Error extracting view count: {str(e)}")
                video_data['views'] = 0
            
            # Extract like/dislike counts
            try:
                # Look for like button with multiple XPath selectors for better reliability
                like_selectors = [
                    "//button[contains(@aria-label, 'like')]//span",
                    "//div[@id='top-level-buttons-computed']//span[contains(@class, 'yt-core-attributed-string')]",
                    "//yt-formatted-string[contains(@aria-label, 'likes')]",
                    "//span[contains(@class, 'yt-core-attributed-string') and contains(text(), 'likes')]"
                ]
                
                likes = 0
                for selector in like_selectors:
                    try:
                        like_elems = self.driver.find_elements(By.XPATH, selector)
                        for elem in like_elems:
                            if elem.text.strip():
                                likes_text = elem.text.strip()
                                likes = self.parse_count(likes_text)
                                if likes > 0:
                                    break
                        if likes > 0:
                            break
                    except:
                        continue
                
                video_data['likes'] = likes
            except Exception as e:
                logger.warning(f"Error extracting like count: {str(e)}")
                video_data['likes'] = 0
            
            # Extract comment count
            try:
                # Look for comment count with multiple XPath selectors
                comment_selectors = [
                    "//h2[@id='count']//span",
                    "//yt-formatted-string[contains(@class, 'count-text')]",
                    "//span[contains(@class, 'count-text')]",
                    "//div[contains(@id, 'comments')]//span[contains(text(), 'comments')]"
                ]
                
                comments = 0
                for selector in comment_selectors:
                    try:
                        comment_elems = self.driver.find_elements(By.XPATH, selector)
                        for elem in comment_elems:
                            if elem.text.strip():
                                comment_text = elem.text.strip()
                                comments = self.parse_count(comment_text)
                                if comments > 0:
                                    break
                        if comments > 0:
                            break
                    except:
                        continue
                
                video_data['comments'] = comments
            except Exception as e:
                logger.warning(f"Error extracting comment count: {str(e)}")
                video_data['comments'] = 0
            
            # Extract description
            try:
                desc_elem = soup.find('yt-formatted-string', {'id': 'description'})
                video_data['description'] = desc_elem.get_text().strip() if desc_elem else ''
            except Exception as e:
                logger.warning(f"Error extracting description: {str(e)}")
                video_data['description'] = ''
            
            # Extract hashtags and mentions
            description = video_data.get('description', '')
            video_data['hashtags'] = self.extract_hashtags(description)
            video_data['mentions'] = self.extract_mentions(description)
            
            # Extract publication date
            try:
                date_elem = soup.find('div', {'id': 'date'})
                if date_elem:
                    video_data['published_at'] = date_elem.get_text().strip()
            except Exception as e:
                logger.warning(f"Error extracting publication date: {str(e)}")
                video_data['published_at'] = ''
            
            # Extract transcript (if available)
            try:
                # Try to expand transcript
                transcript_button = self.driver.find_element(By.XPATH, "//button[contains(@aria-label, 'transcript')]")
                if transcript_button:
                    transcript_button.click()
                    time.sleep(1)
                    
                    # Re-parse page to get transcript
                    soup = self.parse_with_bs4()
                    transcript_elem = soup.find('div', {'id': 'transcript'})
                    video_data['transcript'] = transcript_elem.get_text().strip() if transcript_elem else ''
            except Exception as e:
                logger.warning(f"Error extracting transcript: {str(e)}")
                video_data['transcript'] = ''
            
            # Compile engagement metrics with actual scraped data
            video_data['engagement_metrics'] = {
                'views': video_data.get('views', 0),
                'likes': video_data.get('likes', 0),
                'comments': video_data.get('comments', 0),
                'shares': 0
            }
            
            logger.info(f"Successfully scraped detailed video data: {video_data['title']}")
            return video_data
            
        except Exception as e:
            logger.error(f"Error scraping YouTube video details {video_url}: {str(e)}")
            # Return basic video data with error information
            return self._create_fallback_video_data(video_url, str(e))
    
    def _extract_video_data(self, element) -> Optional[Dict[str, Any]]:
        """
        Extract video data from a YouTube rich item element (fallback to improved method)
        
        Args:
            element: BeautifulSoup element
            
        Returns:
            Video data dictionary or None
        """
        # Use the improved extraction method
        return self._extract_video_data_improved(element)
    
    def _extract_search_video_data(self, element) -> Optional[Dict[str, Any]]:
        """
        Extract video data from a YouTube search result element (fallback to improved method)
        
        Args:
            element: BeautifulSoup element
            
        Returns:
            Video data dictionary or None
        """
        # Use the improved extraction method for search results too
        return self._extract_video_data_improved(element)
    
    def scrape_reels(self, target: str, max_reels: int = 10) -> List[Dict[str, Any]]:
        """
        Scrape YouTube videos (treating them as reels)
        
        Args:
            target: Target to scrape (channel name, search query, or video URL)
            max_reels: Maximum number of videos to scrape
            
        Returns:
            List of video data
        """
        try:
            logger.info(f"Scraping YouTube videos for target: {target}")
            
            # Determine target type and scrape accordingly
            if "youtube.com/channel/" in target or "youtube.com/c/" in target or "youtube.com/@" in target:
                # Channel URL
                return self.scrape_channel_videos(target, max_reels)
            elif "youtube.com/watch" in target:
                # Single video URL
                video_data = self.scrape_video_details(target)
                return [video_data] if video_data else []
            else:
                # Search query
                return self.scrape_search_results(target, max_reels)
                
        except Exception as e:
            logger.error(f"Error scraping YouTube reels for {target}: {str(e)}")
            return []
    
    def scrape_user_profile(self, username: str) -> Optional[Dict[str, Any]]:
        """
        Scrape YouTube channel profile
        
        Args:
            username: YouTube channel username or handle
            
        Returns:
            Channel profile data or None
        """
        try:
            # Construct channel URL
            if username.startswith('@'):
                channel_url = f"{self.base_url}/{username}"
            else:
                channel_url = f"{self.base_url}/@{username}"
            
            logger.info(f"Scraping YouTube channel profile: {channel_url}")
            
            self.driver.get(channel_url)
            time.sleep(random.uniform(3, 5))
            
            # Wait for channel page to load
            WebDriverWait(self.driver, 15).until(
                EC.presence_of_element_located((By.ID, "channel-header"))
            )
            
            # Parse with BeautifulSoup
            soup = self.parse_with_bs4()
            
            profile_data = {
                'platform': 'youtube',
                'username': username,
                'profile_url': channel_url,
                'scraped_at': time.strftime('%Y-%m-%d %H:%M:%S')
            }
            
            # Extract channel name
            try:
                name_elem = soup.find('yt-formatted-string', {'id': 'channel-name'})
                profile_data['channel_name'] = name_elem.get_text().strip() if name_elem else username
            except Exception as e:
                logger.warning(f"Error extracting channel name: {str(e)}")
                profile_data['channel_name'] = username
            
            # Extract subscriber count
            try:
                sub_elem = soup.find('yt-formatted-string', {'id': 'subscriber-count'})
                if sub_elem:
                    sub_text = sub_elem.get_text()
                    profile_data['subscribers'] = self.parse_count(sub_text)
            except Exception as e:
                logger.warning(f"Error extracting subscriber count: {str(e)}")
                profile_data['subscribers'] = 0
            
            # Extract channel description
            try:
                desc_elem = soup.find('yt-formatted-string', {'id': 'description'})
                profile_data['description'] = desc_elem.get_text().strip() if desc_elem else ''
            except Exception as e:
                logger.warning(f"Error extracting channel description: {str(e)}")
                profile_data['description'] = ''
            
            # Extract channel links
            try:
                links_elem = soup.find('div', {'id': 'links-container'})
                if links_elem:
                    link_elements = links_elem.find_all('a')
                    profile_data['links'] = [link.get('href', '') for link in link_elements if link.get('href')]
            except Exception as e:
                logger.warning(f"Error extracting channel links: {str(e)}")
                profile_data['links'] = []
            
            # Extract social media links from description
            description = profile_data.get('description', '')
            profile_data['social_links'] = self._extract_social_links(description)
            
            logger.info(f"Successfully scraped YouTube channel profile: {profile_data['channel_name']}")
            return profile_data
            
        except Exception as e:
            logger.error(f"Error scraping YouTube channel profile {username}: {str(e)}")
            return None
    
    def _extract_social_links(self, text: str) -> List[str]:
        """
        Extract social media links from text
        
        Args:
            text: Text to extract links from
            
        Returns:
            List of social media URLs
        """
        import re
        
        # Common social media patterns
        social_patterns = [
            r'instagram\.com/[^\s]+',
            r'twitter\.com/[^\s]+',
            r'tiktok\.com/[^\s]+',
            r'facebook\.com/[^\s]+',
            r'linkedin\.com/[^\s]+',
            r't\.me/[^\s]+'  # Telegram
        ]
        
        social_links = []
        for pattern in social_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            social_links.extend(matches)
        
        return social_links

    def close(self):
        """Close the WebDriver"""
        if hasattr(self, 'driver') and self.driver:
            self.driver.quit()

    def _create_fallback_video_data(self, video_url: str, error_message: str) -> Dict[str, Any]:
        """
        Create fallback video data when scraping fails
        
        Args:
            video_url: The video URL
            error_message: Error message for debugging
            
        Returns:
            Basic video data with error information
        """
        from urllib.parse import urlparse, parse_qs
        
        try:
            # Extract video ID from URL
            parsed_url = urlparse(video_url)
            if parsed_url.hostname and 'youtube.com' in parsed_url.hostname:
                video_id = parse_qs(parsed_url.query).get('v', [''])[0]
            else:
                video_id = ''
        except:
            video_id = ''
        
        return {
            'platform': 'youtube',
            'title': 'Video unavailable',
            'description': f'Scraping failed: {error_message}',
            'views': 0,
            'likes': 0,
            'comments': 0,
            'shares': 0,
            'duration': '',
            'upload_date': '',
            'channel_name': '',
            'video_id': video_id,
            'url': video_url,
            'is_channel': False,
            'scraping_error': True,
            'error_message': error_message,
            'scraped_at': time.strftime('%Y-%m-%d %H:%M:%S'),
            'engagement_metrics': {
                'views': 0,
                'likes': 0,
                'comments': 0
            }
        }
    
    def _get_youtube_api_key(self) -> Optional[str]:
        """
        Get YouTube API key from environment variables
        
        Returns:
            API key or None
        """
        import os
        return os.getenv('YOUTUBE_API_KEY')
    
    def _scrape_with_api_fallback(self, video_id: str) -> Optional[Dict[str, Any]]:
        """
        Fallback method using YouTube Data API
        
        Args:
            video_id: YouTube video ID
            
        Returns:
            Video data or None
        """
        if not YOUTUBE_API_AVAILABLE:
            logger.warning("YouTube API client not available")
            return None
        
        api_key = self._get_youtube_api_key()
        if not api_key:
            logger.warning("YouTube API key not found in environment variables")
            return None
        
        try:
            # Build YouTube API service
            youtube = build('youtube', 'v3', developerKey=api_key)
            
            # Get video details
            request = youtube.videos().list(
                part='snippet,statistics,contentDetails',
                id=video_id
            )
            response = request.execute()
            
            if not response.get('items'):
                logger.warning(f"No video found with ID: {video_id}")
                return None
            
            video_item = response['items'][0]
            snippet = video_item.get('snippet', {})
            statistics = video_item.get('statistics', {})
            content_details = video_item.get('contentDetails', {})
            
            # Parse duration from ISO 8601 format
            duration = content_details.get('duration', '')
            if duration:
                duration = self._parse_iso_duration(duration)
            
            video_data = {
                'platform': 'youtube',
                'video_id': video_id,
                'title': snippet.get('title', ''),
                'description': snippet.get('description', ''),
                'channel': snippet.get('channelTitle', ''),
                'channel_url': f"https://www.youtube.com/channel/{snippet.get('channelId', '')}",
                'views': int(statistics.get('viewCount', 0)),
                'likes': int(statistics.get('likeCount', 0)),
                'comments': int(statistics.get('commentCount', 0)),
                'duration': duration,
                'published_at': snippet.get('publishedAt', ''),
                'thumbnail_url': snippet.get('thumbnails', {}).get('high', {}).get('url', ''),
                'url': f"https://www.youtube.com/watch?v={video_id}",
                'scraped_at': time.strftime('%Y-%m-%d %H:%M:%S'),
                'hashtags': self.extract_hashtags(snippet.get('description', '')),
                'mentions': self.extract_mentions(snippet.get('description', '')),
                'engagement_metrics': {
                    'views': int(statistics.get('viewCount', 0)),
                    'likes': int(statistics.get('likeCount', 0)),
                    'comments': int(statistics.get('commentCount', 0)),
                    'shares': 0
                },
                'api_fallback': True
            }
            
            logger.info(f"Successfully retrieved video data via API: {video_data['title']}")
            return video_data
            
        except HttpError as e:
            logger.error(f"YouTube API error: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"Error using YouTube API fallback: {str(e)}")
            return None
    
    def _parse_iso_duration(self, duration: str) -> str:
        """
        Parse ISO 8601 duration format (PT4M13S) to readable format (4:13)
        
        Args:
            duration: ISO 8601 duration string
            
        Returns:
            Readable duration string
        """
        try:
            import re
            
            # Remove PT prefix
            duration = duration.replace('PT', '')
            
            # Extract hours, minutes, seconds
            hours = re.search(r'(\d+)H', duration)
            minutes = re.search(r'(\d+)M', duration)
            seconds = re.search(r'(\d+)S', duration)
            
            h = int(hours.group(1)) if hours else 0
            m = int(minutes.group(1)) if minutes else 0
            s = int(seconds.group(1)) if seconds else 0
            
            if h > 0:
                return f"{h}:{m:02d}:{s:02d}"
            else:
                return f"{m}:{s:02d}"
                
        except Exception as e:
            logger.warning(f"Error parsing duration {duration}: {str(e)}")
            return duration
    
    def scrape_video_details_with_fallback(self, video_url: str) -> Optional[Dict[str, Any]]:
        """
        Scrape video details with API fallback
        
        Args:
            video_url: YouTube video URL
            
        Returns:
            Video data or None
        """
        # Try Selenium scraping first
        video_data = self.scrape_video_details(video_url)
        
        # If scraping failed or returned minimal data, try API fallback
        if not video_data or video_data.get('scraping_error') or not video_data.get('title'):
            logger.info("Selenium scraping failed, trying API fallback...")
            video_id = self._extract_video_id_from_url(video_url)
            if video_id:
                api_data = self._scrape_with_api_fallback(video_id)
                if api_data:
                    return api_data
        
        return video_data