from flask import Flask, request, jsonify
from flask_cors import CORS
import json
import time
import os
import re
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException, NoSuchElementException, StaleElementReferenceException
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from sentence_transformers import SentenceTransformer
import urllib.parse
from datetime import datetime
import instaloader
from instaloader import Profile, Hashtag, Post
import requests

# Import platform resolver
from platform_resolver import PlatformResolver, detect_platform, get_platform_info

# Initialize Flask app
app = Flask(__name__)
# Enable CORS for all routes
CORS(app)

# Initialize embedding model
try:
    # Fix for 'Cannot copy out of meta tensor' error
    import torch
    import os
    
    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    # Initialize with device specification and additional parameters to avoid meta tensor error
    embedder = SentenceTransformer('all-MiniLM-L6-v2', device=device)
    # Force model to CPU if needed to avoid meta tensor issues
    if device == 'cuda' and torch.cuda.is_available():
        try:
            # Use to_empty() instead of to() for meta tensors
            embedder = embedder.to_empty(device) if hasattr(embedder, 'to_empty') else embedder.to(device)
        except RuntimeError as e:
            if "Cannot copy out of meta tensor" in str(e):
                print("CUDA meta tensor error detected, falling back to CPU")
                embedder.to('cpu')
            else:
                raise e
except Exception as e:
    print(f"Error initializing SentenceTransformer: {str(e)}")
    # Fallback to simple embedding if model fails to load
    embedder = None

# Initialize platform resolver
platform_resolver = PlatformResolver()

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

# Mistral API Configuration
MISTRAL_API_URL = "https://api.mistral.ai/v1/chat/completions"
MISTRAL_API_KEY = os.getenv('MISTRAL_API_KEY', '')  # Load from environment variable

# Instagram credentials (load from environment variables)
INSTA_USER = os.getenv('INSTAGRAM_USERNAME', '')  # Load from environment variable
INSTA_PASS = os.getenv('INSTAGRAM_PASSWORD', '')  # Load from environment variable


# Setup Chrome options for Selenium
def get_chrome_options():
    chrome_options = Options()
    chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1280,720")
    chrome_options.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
    return chrome_options


def login_to_instagram(driver):
    """Login to Instagram using direct credentials"""
    if not INSTA_USER or not INSTA_PASS:
        print("Instagram credentials not set. Proceeding without login.")
        return False

    try:
        print("Logging in to Instagram...")
        driver.get("https://www.instagram.com/accounts/login/")

        # Wait for login page to load with retry mechanism
        loaded = False
        for attempt in range(3):
            try:
                WebDriverWait(driver, 15).until(
                    EC.presence_of_element_located((By.NAME, "username"))
                )
                loaded = True
                break
            except TimeoutException:
                print(f"Login page load attempt {attempt + 1} failed. Retrying...")
                if attempt < 2:
                    driver.refresh()
                    time.sleep(5)
        
        if not loaded:
            print("Login page failed to load after multiple attempts")
            return False

        # Fill credentials with explicit waits and error handling
        try:
            username_field = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.NAME, "username"))
            )
            password_field = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.NAME, "password"))
            )
            
            # Clear fields before entering text
            username_field.clear()
            password_field.clear()
            
            # Type slowly to mimic human behavior
            for char in INSTA_USER:
                username_field.send_keys(char)
                time.sleep(0.1)
            
            for char in INSTA_PASS:
                password_field.send_keys(char)
                time.sleep(0.1)
                
            # Click login button with explicit wait
            login_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//button[@type='submit']"))
            )
            login_button.click()
            
            # Wait for login to complete with multiple fallback strategies
            login_success = False
            for wait_attempt in range(2):
                try:
                    WebDriverWait(driver, 15).until(
                        EC.any_of(
                            EC.presence_of_element_located((By.XPATH, "//div[@class='_aagx']")),
                            EC.presence_of_element_located((By.XPATH, "//span[contains(text(), 'Search')]")),
                            EC.presence_of_element_located((By.XPATH, "//a[contains(@href, '/direct/inbox/')]")),
                            EC.presence_of_element_located((By.XPATH, "//a[contains(@href, '/explore/')]")),
                            EC.presence_of_element_located((By.XPATH, "//svg[@aria-label='Home']")),
                            EC.presence_of_element_located((By.XPATH, "//svg[@aria-label='Search']")),
                            EC.presence_of_element_located((By.XPATH, "//svg[@aria-label='Explore']")),
                            EC.presence_of_element_located((By.XPATH, "//svg[@aria-label='Reels']")),
                            EC.presence_of_element_located((By.XPATH, "//svg[@aria-label='Direct']")),
                            EC.presence_of_element_located((By.XPATH, "//svg[@aria-label='Profile']")),
                            EC.presence_of_element_located((By.XPATH, "//div[contains(@class, 'x9f619')]")),  # Generic Instagram container
                        )
                    )
                    login_success = True
                    break
                except TimeoutException:
                    print(f"Login verification attempt {wait_attempt + 1} timed out")
                    if wait_attempt == 0:
                        # Try one more time with shorter wait
                        time.sleep(3)
            
            if not login_success:
                print("Could not confirm successful login, but continuing...")
                
        except Exception as e:
            print(f"Error during login form interaction: {str(e)}")
            return False

        # Handle various post-login prompts with better error handling
        prompt_handlers = [
            ("Save Your Login Info?", "//button[contains(text(), 'Not Now')]"),
            ("Save login info", "//button[contains(text(), 'Not Now')]"),
            ("notifications", "//button[contains(text(), 'Not Now')]"),
            ("Turn on Notifications", "//button[contains(text(), 'Not Now')]"),
        ]
        
        for prompt_name, xpath in prompt_handlers:
            try:
                button = WebDriverWait(driver, 3).until(
                    EC.element_to_be_clickable((By.XPATH, xpath))
                )
                button.click()
                print(f"Clicked 'Not Now' for {prompt_name} prompt")
                time.sleep(1)
            except:
                pass  # No prompt appeared

        # Additional verification: try to access home page to confirm session
        try:
            driver.get("https://www.instagram.com/")
            time.sleep(5)
            current_url = driver.current_url
            print(f"After login, current URL: {current_url}")
            
            if "login" not in current_url:
                print("Login session verified - can access main page")
                return True
            else:
                print("Login session failed - still redirected to login")
                return False
        except Exception as e:
            print(f"Additional verification failed: {e}")
            return False

    except Exception as e:
        print(f"Login failed: {str(e)}")
        return False


def get_webdriver():
    """Initialize and return a Chrome WebDriver"""
    try:
        chrome_options = get_chrome_options()
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        return driver
    except Exception as e:
        print(f"Failed to initialize WebDriver: {str(e)}")
        return None


def call_mistral_api(prompt):
    """Call Mistral AI API for text generation"""
    if not MISTRAL_API_KEY:
        print("Mistral API key not set")
        return None

    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Authorization": f"Bearer {MISTRAL_API_KEY}"
    }

    payload = {
        "model": "mistral-tiny",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.7,
        "max_tokens": 200
    }

    try:
        response = requests.post(MISTRAL_API_URL, headers=headers, json=payload)
        response.raise_for_status()
        result = response.json()
        return result["choices"][0]["message"]["content"]
    except Exception as e:
        print(f"Mistral API error: {str(e)}")
        return None


def extract_instagram_data(driver, url):
    """Extract data from an Instagram reel"""
    try:
        print(f"Extracting data from: {url}")
        driver.get(url)
        time.sleep(5)  # Wait for page to load

        # Extract reel ID from URL
        reel_id = url.split("/reel/")[1].split("/")[0]
        
        # Format the Reel_link URL to match Instagram reel link structure
        # Instead of using blob URL, use the standard Instagram reel URL format
        video_url = f"https://www.instagram.com/reel/{reel_id}/"
        
        # Keep the original video source extraction for backup
        original_video_src = ""
        try:
            video_element = driver.find_element(By.TAG_NAME, "video")
            original_video_src = video_element.get_attribute("src")
        except:
            try:
                # Alternative method to find video
                video_element = driver.find_element(By.XPATH, "//video[@type='video/mp4']")
                original_video_src = video_element.get_attribute("src")
            except:
                print("Could not find video element")

        # Get caption
        caption = ""
        try:
            caption_element = driver.find_element(By.XPATH, "//h1")
            caption = caption_element.text
        except:
            try:
                # Alternative method to find caption
                caption_element = driver.find_element(By.XPATH, "//div[contains(@class, '_a9zs')]")
                caption = caption_element.text
            except:
                print("Could not find caption element")

        # Get creator info
        creator = {}
        try:
            username_element = driver.find_element(By.XPATH, "//a[@role='link' and @tabindex='0']/div/div/span")
            username = username_element.text
            profile_link = driver.find_element(By.XPATH, "//a[@role='link' and @tabindex='0']").get_attribute("href")
            creator = {
                "username": username,
                "profile": profile_link
            }
        except:
            print("Could not find creator info")

        # Get metrics (likes, views) - updated selectors
        likes = 0
        views = 0
        try:
            # Updated selector for metrics
            metrics_spans = driver.find_elements(By.XPATH,
                                                 '//span[contains(@class, "x193iq5w") or contains(@class, "x1lliihq")]')

            # Alternative: look for specific text patterns
            page_source = driver.page_source
            likes_match = re.search(r'(\d+[\d,.]*[KkMm]?)\s*likes', page_source, re.IGNORECASE)
            views_match = re.search(r'(\d+[\d,.]*[KkMm]?)\s*views', page_source, re.IGNORECASE)

            if likes_match:
                likes_text = likes_match.group(1).replace(",", "").replace(".", "")
                if "K" in likes_text or "k" in likes_text:
                    likes = int(float(likes_text.lower().replace("k", "")) * 1000)
                elif "M" in likes_text or "m" in likes_text:
                    likes = int(float(likes_text.lower().replace("m", "")) * 1000000)
                elif likes_text.isdigit():
                    likes = int(likes_text)

            if views_match:
                views_text = views_match.group(1).replace(",", "").replace(".", "")
                if "K" in views_text or "k" in views_text:
                    views = int(float(views_text.lower().replace("k", "")) * 1000)
                elif "M" in views_text or "m" in views_text:
                    views = int(float(views_text.lower().replace("m", "")) * 1000000)
                elif views_text.isdigit():
                    views = int(views_text)

            # If regex fails, try to find with spans
            if likes == 0 and views == 0:
                for span in metrics_spans:
                    text = span.text.lower()
                    # Extract likes
                    if "like" in text or "likes" in text:
                        likes_text = text.replace("likes", "").replace("like", "").replace(",", "").replace(".", "").strip()
                        if "k" in likes_text:
                            likes = int(float(likes_text.replace("k", "")) * 1000)
                        elif "m" in likes_text:
                            likes = int(float(likes_text.replace("m", "")) * 1000000)
                        elif likes_text.isdigit():
                            likes = int(likes_text)
                    
                    # Extract views
                    if "view" in text or "views" in text:
                        views_text = text.replace("views", "").replace("view", "").replace(",", "").replace(".", "").strip()
                        if "k" in views_text:
                            views = int(float(views_text.replace("k", "")) * 1000)
                        elif "m" in views_text:
                            views = int(float(views_text.replace("m", "")) * 1000000)
                        elif views_text.isdigit():
                            views = int(views_text)
        except Exception as e:
            print(f"Could not find metrics: {str(e)}")

        # Get upload date
        upload_date = ""
        try:
            time_element = driver.find_element(By.TAG_NAME, "time")
            upload_date = time_element.get_attribute("datetime")
        except:
            print("Could not find upload date")

        # Extract comments
        top_comments = []
        try:
            # Improved comment loading with WebDriverWait
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//ul[contains(@class, '_a9ym')]"))
            )
            
            # Find comment section
            comment_section = driver.find_element(By.XPATH, "//ul[contains(@class, '_a9ym')]")
            
            # Find all comment elements
            comment_elements = comment_section.find_elements(By.XPATH, ".//div[contains(@class, '_a9zr')]")
            
            # Process up to 5 comments
            for i, comment_element in enumerate(comment_elements[:5]):
                try:
                    # Extract username
                    username = comment_element.find_element(By.XPATH, ".//a[@role='link']").text
                    
                    # Extract comment text
                    comment_text = ""
                    try:
                        comment_text = comment_element.find_element(By.XPATH, ".//span[contains(@class, '_aacl _aaco')]").text
                    except:
                        try:
                            # Alternative method
                            comment_text = comment_element.find_element(By.XPATH, ".//div[contains(@class, '_a9zs')]").text
                        except:
                            print(f"Could not extract text for comment {i+1}")
                    
                    # Extract timestamp
                    timestamp = ""
                    try:
                        time_element = comment_element.find_element(By.TAG_NAME, "time")
                        timestamp = time_element.get_attribute("datetime")
                    except:
                        try:
                            # Alternative: get relative time
                            time_text = comment_element.find_element(By.XPATH, ".//time").text
                            timestamp = time_text
                        except:
                            print(f"Could not extract timestamp for comment {i+1}")
                    
                    # Add to comments list
                    if username and comment_text:
                        top_comments.append({
                            "user": username,
                            "comment": comment_text,
                            "timestamp": timestamp
                        })
                        
                except StaleElementReferenceException:
                    print(f"Stale element reference for comment {i+1}")
                    continue
                except Exception as e:
                    print(f"Error processing comment {i+1}: {str(e)}")
                    continue
        except Exception as e:
            print(f"Error extracting comments: {str(e)}")

        # Construct reel data dictionary
        # Ensure Reel_link URL has reel_id at the end
        if video_url and reel_id and "?" not in video_url:
            # Add reel_id as a parameter to the video URL
            video_url = f"{video_url}?reel_id={reel_id}"
        elif video_url and reel_id:
            # URL already has parameters, append reel_id
            video_url = f"{video_url}&reel_id={reel_id}"
            
        reel_data = {
            "reel_id": reel_id,
            "Reel_link": video_url,
            "caption": caption,
            "creator": creator,
            "likes": likes,
            "views": views,
            "upload_date": upload_date,
            "top_comments": top_comments
        }

        return reel_data

    except Exception as e:
        print(f"Error extracting Instagram data: {str(e)}")
        return None


def parse_count(count_text):
    """Parse count values like '1.2M', '4.5K' to integers"""
    try:
        if not count_text:
            return 0
            
        count_text = count_text.strip().replace(',', '')
        
        if 'K' in count_text or 'k' in count_text:
            return int(float(count_text.replace('K', '').replace('k', '')) * 1000)
        elif 'M' in count_text or 'm' in count_text:
            return int(float(count_text.replace('M', '').replace('m', '')) * 1000000)
        elif 'B' in count_text or 'b' in count_text:
            return int(float(count_text.replace('B', '').replace('b', '')) * 1000000000)
        else:
            return int(float(count_text))
    except:
        return 0


def analyze_reel_with_ai(reel_data):
    """Analyze reel data using Mistral AI"""
    try:
        caption = reel_data.get("caption", "")
        comments = reel_data.get("top_comments", [])
        
        # Prepare comments text for analysis
        comments_text = "\n".join([f"{c.get('user', '')}: {c.get('comment', '')}" for c in comments])
        
        # Generate AI summary
        summary_prompt = f"Summarize this Instagram reel content in one sentence: {caption}\n\nComments:\n{comments_text}"
        ai_summary = call_mistral_api(summary_prompt) or "Summary unavailable"

        # Categorization
        category_prompt = f"Classify this Instagram reel content into one or more categories: {caption}. " \
                          "Options: Comedy, Animals, Skits, Fails, Dance, Kids, Acting. " \
                          "Return only the category names separated by commas."
        category_result = call_mistral_api(category_prompt) or ""
        category_list = [cat.strip() for cat in category_result.split(",") if cat.strip()]

        # Sentiment analysis
        sentiment_prompt = f"Analyze the sentiment of this Instagram content: {caption}. " \
                           "Return only one of these: Positive, Negative, Funny, Relatable, Trolling."
        sentiment = call_mistral_api(sentiment_prompt) or "Unknown"

        # Comment summary
        comment_prompt = f"Summarize the theme of these Instagram comments: {comments_text}. " \
                         "Return a one-sentence summary."
        comment_summary = call_mistral_api(comment_prompt) or "No comment summary"

        # Embeddings
        embeddings = []
        if embedder is not None:
            try:
                embedding_text = f"{caption} {ai_summary}"
                embeddings = embedder.encode(embedding_text).tolist()
            except Exception as e:
                print(f"Embedding generation failed: {str(e)}")
                # Create a fallback embedding with correct dimensions
                embeddings = [0.0] * 384  # Standard dimension for all-MiniLM-L6-v2
        else:
            print("Embedder not initialized, using zero vector fallback")
            embeddings = [0.0] * 384  # Standard dimension for all-MiniLM-L6-v2

        return {
            "ai_summary": ai_summary,
            "category": category_list,
            "sentiment": sentiment,
            "top_comment_summary": comment_summary,
            "embeddings": embeddings[:10]  # First 10 dimensions
        }

    except Exception as e:
        print(f"AI analysis error: {str(e)}")
        return {
            "ai_summary": "Analysis failed",
            "category": [],
            "sentiment": "Unknown",
            "top_comment_summary": "Analysis failed",
            "embeddings": []
        }


def scrape_instagram_reels(driver, target: str, max_reels: int = 10) -> list:
    """Scrape public Instagram reels using Selenium"""
    reels = []

    try:
        if target.startswith('https://'):
            url = target
        elif target.startswith('@'):
            username = target[1:]
            url = f"https://www.instagram.com/{username}/"
        elif target.startswith('#'):
            hashtag = target[1:]
            hashtag = hashtag.rstrip('/').strip()
            
            print(f"Searching for hashtag: #{hashtag}")
            
            # Strategy: Use Instagram's search functionality
            try:
                # Navigate to search page
                driver.get("https://www.instagram.com/explore/search/")
                time.sleep(8)
                
                # Look for search input field
                search_inputs = driver.find_elements(By.XPATH, '//input[@type="text"] | //input[@placeholder*="Search"] | //input[@aria-label*="Search"]')
                
                if search_inputs:
                    search_input = search_inputs[0]
                    # Clear and enter hashtag
                    search_input.clear()
                    search_input.send_keys(f"#{hashtag}")
                    time.sleep(3)
                    
                    # Press Enter to search
                    search_input.send_keys(Keys.RETURN)
                    time.sleep(5)
                    
                    # Also try clicking any search suggestions
                    try:
                        suggestions = driver.find_elements(By.XPATH, f'//div[contains(text(), "#{hashtag}")] | //span[contains(text(), "#{hashtag}")]')
                        if suggestions:
                            suggestions[0].click()
                            time.sleep(5)
                    except:
                        pass
                        
                    print(f"Searched for hashtag: #{hashtag}")
                else:
                    # Fallback: try direct URL with hashtag
                    driver.get(f"https://www.instagram.com/explore/tags/{hashtag}/")
                    time.sleep(8)
                    
            except Exception as e:
                print(f"Search approach failed: {e}")
                # Fallback: try direct hashtag URL
                try:
                    driver.get(f"https://www.instagram.com/explore/tags/{hashtag}/")
                    time.sleep(8)
                except:
                    # Final fallback: main feed
                    driver.get("https://www.instagram.com/")
                    time.sleep(8)
            
            current_url = driver.current_url
            print(f"Current URL after search: {current_url}")
            
            # Skip the URL navigation for hashtag searches since we're already on the page
            print("Proceeding with content extraction from current page...")
        else:
            url = f"https://www.instagram.com/{target}/"
            print(f"Navigating to: {url}")
            driver.get(url)
            time.sleep(10)  # Increased time for initial load
        
        # Debug: Check what page we actually landed on
        current_url = driver.current_url
        page_title = driver.title
        print(f"Current URL: {current_url}")
        print(f"Page title: {page_title}")
        
        # Take a screenshot for debugging
        try:
            debug_filename = f"debug_hashtag_{target.replace('#', '')}.png" if target.startswith('#') else f"debug_{target.replace('/', '_')}.png"
            driver.save_screenshot(debug_filename)
            print(f"Saved debug screenshot: {debug_filename}")
        except:
            pass

        # Special handling for hashtag pages
        if target.startswith('#'):
            print("Using hashtag-specific loading strategy...")
            # For hashtag pages, use a more patient approach
            loaded = False
            for attempt in range(5):  # More attempts for hashtags
                try:
                    # First, just wait for the page to start loading
                    WebDriverWait(driver, 20).until(
                        EC.presence_of_element_located((By.TAG_NAME, "body"))
                    )
                    
                    # Wait a bit more for dynamic content
                    time.sleep(8)  # Increased wait time
                    
                    # Try multiple strategies to find posts on the main feed
                    post_elements = []
                    
                    # Strategy 1: Look for direct post links
                    post_elements.extend(driver.find_elements(By.XPATH, '//a[contains(@href, "/p/")] | //a[contains(@href, "/reel/")]'))
                    
                    # Strategy 2: Look for article elements (posts are often in articles)
                    article_posts = driver.find_elements(By.XPATH, '//article//a[contains(@href, "/p/") or contains(@href, "/reel/")]')
                    post_elements.extend(article_posts)
                    
                    # Strategy 3: Look for div elements with post links
                    div_posts = driver.find_elements(By.XPATH, '//div[contains(@class, "_ac7v")]//a | //div[contains(@class, "_aabd")]//a')
                    for div_post in div_posts:
                        href = div_post.get_attribute('href')
                        if href and ('/p/' in href or '/reel/' in href):
                            post_elements.append(div_post)
                    
                    # Strategy 4: Look for any clickable elements that might be posts
                    clickable_elements = driver.find_elements(By.XPATH, '//div[@role="button"]//a[contains(@href, "/")]')
                    for element in clickable_elements:
                        href = element.get_attribute('href')
                        if href and ('/p/' in href or '/reel/' in href):
                            post_elements.append(element)
                    
                    # Remove duplicates by href
                    seen_hrefs = set()
                    unique_posts = []
                    for post in post_elements:
                        try:
                            href = post.get_attribute('href')
                            if href and href not in seen_hrefs:
                                seen_hrefs.add(href)
                                unique_posts.append(post)
                        except:
                            continue
                    
                    if unique_posts:
                        print(f"Found {len(unique_posts)} unique post elements on attempt {attempt + 1}")
                        loaded = True
                        break
                    
                    # If no posts found, try scrolling to trigger loading
                    print(f"No posts found on attempt {attempt + 1}, trying scroll...")
                    driver.execute_script("window.scrollTo(0, 1000);")  # Scroll further
                    time.sleep(5)  # Longer wait after scroll
                    
                    # Check again after scrolling
                    post_elements = driver.find_elements(By.XPATH, '//a[contains(@href, "/p/")] | //a[contains(@href, "/reel/")]')
                    if post_elements:
                        print(f"Found {len(post_elements)} post elements after scrolling")
                        loaded = True
                        break
                        
                except TimeoutException:
                    print(f"Hashtag page loading attempt {attempt + 1} timed out. Retrying...")
                    if attempt < 4:  # Don't refresh on last attempt
                        driver.refresh()
                        time.sleep(12)  # Longer wait after refresh
            
            if not loaded:
                print("Hashtag page loading failed. Will try to proceed with available content...")
        else:
            # For profile pages, use standard loading
            loaded = False
            for attempt in range(3):
                try:
                    WebDriverWait(driver, 15).until(
                        EC.presence_of_element_located((By.TAG_NAME, "article"))
                    )
                    loaded = True
                    break
                except TimeoutException:
                    print(f"Page loading attempt {attempt + 1} timed out. Retrying...")
                    if attempt < 2:  # Don't refresh on last attempt
                        driver.refresh()
                        time.sleep(8)  # Longer wait after refresh
            
            if not loaded:
                print("Page loading failed after multiple attempts. Proceeding anyway...")

        # More aggressive scrolling to load content
        print("Starting content loading through scrolling...")
        for scroll_attempt in range(10):  # More scroll attempts
            # Scroll to different positions to trigger content loading
            scroll_position = scroll_attempt * 600  # Scroll further each time
            driver.execute_script(f"window.scrollTo(0, {scroll_position});")
            time.sleep(4)  # Wait for content to load
            
            # Also try scrolling to bottom occasionally
            if scroll_attempt % 2 == 0:
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(3)
            
            # Check if we found any posts during scrolling using multiple strategies
            current_posts = []
            
            # Strategy 1: Direct post links
            direct_posts = driver.find_elements(By.XPATH, '//a[contains(@href, "/p/")] | //a[contains(@href, "/reel/")]')
            current_posts.extend(direct_posts)
            
            # Strategy 2: Look for articles (posts are often in articles)
            article_posts = driver.find_elements(By.XPATH, '//article')
            current_posts.extend(article_posts)
            
            # Strategy 3: Look for specific Instagram class patterns
            ig_posts = driver.find_elements(By.XPATH, '//div[contains(@class, "_aagv")] | //div[contains(@class, "_aabd")] | //div[contains(@class, "_ac7v")]')
            current_posts.extend(ig_posts)
            
            if len(current_posts) > 3:  # If we found enough posts, stop scrolling
                print(f"Found {len(current_posts)} posts after {scroll_attempt + 1} scrolls, stopping early")
                break

        # Multiple strategies to find reels
        reel_urls = set()
        
        # For hashtag searches, also look for posts containing the hashtag
        if target.startswith('#'):
            hashtag = target[1:]
            print(f"Looking for content with hashtag: #{hashtag}")
            
            # Strategy: Look for posts that mention the hashtag
            try:
                # Use multiple strategies to find posts on the main feed
                all_post_links = []
                
                # Strategy 1: Direct post/reel links
                direct_links = driver.find_elements(By.XPATH, '//a[contains(@href, "/p/")] | //a[contains(@href, "/reel/")]')
                all_post_links.extend(direct_links)
                
                # Strategy 2: Look for article elements (posts are often wrapped in articles)
                articles = driver.find_elements(By.XPATH, '//article')
                for article in articles:
                    # Look for links within each article
                    article_links = article.find_elements(By.XPATH, './/a[contains(@href, "/p/") or contains(@href, "/reel/")]')
                    all_post_links.extend(article_links)
                
                # Strategy 3: Look for Instagram's specific post container classes
                post_containers = driver.find_elements(By.XPATH, '//div[contains(@class, "_aagv")] | //div[contains(@class, "_aabd")] | //div[contains(@class, "_ac7v")]')
                for container in post_containers:
                    container_links = container.find_elements(By.XPATH, './/a[contains(@href, "/p/") or contains(@href, "/reel/")]')
                    all_post_links.extend(container_links)
                
                # Strategy 4: Look for any clickable divs that might contain posts
                clickable_divs = driver.find_elements(By.XPATH, '//div[@role="button"]')
                for div in clickable_divs:
                    # Check if clicking this div might lead to a post
                    onclick = div.get_attribute('onclick')
                    if onclick and ('/p/' in onclick or '/reel/' in onclick):
                        # Try to find links within this div
                        div_links = div.find_elements(By.XPATH, './/a[contains(@href, "/p/") or contains(@href, "/reel/")]')
                        all_post_links.extend(div_links)
                
                print(f"Found {len(all_post_links)} total post links on page using multiple strategies")
                
                # Remove duplicates and filter valid URLs
                seen_urls = set()
                unique_posts = []
                
                for element in all_post_links:
                    try:
                        url = element.get_attribute('href')
                        if url and ("/reel/" in url or "/p/" in url) and url not in seen_urls:
                            seen_urls.add(url)
                            unique_posts.append(url)
                    except:
                        continue
                
                # For hashtag searches, we'll take any posts we find (Instagram's algorithm should show relevant content)
                for post_url in unique_posts[:max_reels]:  # Limit to max_reels
                    reel_urls.add(post_url)
                        
                print(f"Collected {len(reel_urls)} unique post URLs for hashtag analysis")
            except Exception as e:
                print(f"Error collecting posts from feed: {e}")
        
        # Strategy 1: Look for direct reel links
        try:
            reel_elements = driver.find_elements(By.XPATH, '//a[contains(@href, "/reel/")]')
            for element in reel_elements:
                try:
                    url = element.get_attribute('href')
                    if url and "/reel/" in url:
                        reel_urls.add(url)
                except:
                    continue
        except:
            pass

        # Strategy 2: Look for video posts (reels are often classified as videos)
        try:
            video_elements = driver.find_elements(By.XPATH, '//a[.//video] | //a[.//div[contains(@class, "video")]]')
            for element in video_elements:
                try:
                    url = element.get_attribute('href')
                    if url and ("/reel/" in url or "/p/" in url):
                        reel_urls.add(url)
                except:
                    continue
        except:
            pass

        # Strategy 3: Look for post links in general and filter later
        try:
            post_elements = driver.find_elements(By.XPATH, '//a[contains(@href, "/p/")] | //a[contains(@href, "/reel/")]')
            for element in post_elements:
                try:
                    url = element.get_attribute('href')
                    if url and ("/reel/" in url or "/p/" in url):
                        reel_urls.add(url)
                except:
                    continue
        except:
            pass

        # Strategy 4: For hashtag pages, look for post grid items
        if target.startswith('#'):
            try:
                # Look for post grid items
                grid_items = driver.find_elements(By.XPATH, '//div[contains(@class, "_aagv")]//a | //article//a | //div[role="button"]//a')
                for element in grid_items:
                    try:
                        url = element.get_attribute('href')
                        if url and ("/reel/" in url or "/p/" in url):
                            reel_urls.add(url)
                    except:
                        continue
            except:
                pass
            
            # Strategy 5: Look for any clickable elements that might be posts
            try:
                clickable_posts = driver.find_elements(By.XPATH, '//div[contains(@class, "_aabd")]//a | //div[contains(@class, "_aagw")]//a')
                for element in clickable_posts:
                    try:
                        url = element.get_attribute('href')
                        if url and ("/reel/" in url or "/p/" in url):
                            reel_urls.add(url)
                    except:
                        continue
            except:
                pass

        if not reel_urls:
            print("No reels found on this page")
            return []

        print(f"Found {len(reel_urls)} potential reels")

        # Process up to max_reels
        for i, reel_url in enumerate(list(reel_urls)[:max_reels]):
            try:
                print(f"Processing reel {i + 1}: {reel_url}")

                # Extract data from reel
                reel_data = extract_instagram_data(driver, reel_url)
                if reel_data:
                    reels.append(reel_data)

                # Navigate back to original page
                driver.get(reel_url)
                time.sleep(3)  # Wait for page to reload

            except Exception as e:
                print(f"Skipped reel due to error: {str(e)}")
                continue

    except Exception as e:
        print(f"Scraping error: {str(e)}")

    return reels


def scrape_with_instaloader(target: str, max_reels: int = 10) -> list:
    """Scrape Instagram reels using Instaloader"""
    reels = []
    L = instaloader.Instaloader()
    
    # Add delay to avoid rate limiting
    L.download_delay = 3.0
    L.request_timeout = 45
    
    # Set user agent to avoid detection
    L.context.user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'

    # Login if credentials are available - try multiple approaches
    login_successful = False
    if INSTA_USER and INSTA_PASS:
        try:
            # First try regular login
            L.login(INSTA_USER, INSTA_PASS)
            print("Logged in to Instagram using Instaloader")
            login_successful = True
        except Exception as e:
            print(f"Instaloader login failed: {str(e)}")
            # Try loading session from file if it exists
            try:
                L.load_session_from_file(INSTA_USER)
                print("Loaded existing session for Instaloader")
                login_successful = True
            except Exception as e2:
                print(f"Session loading failed: {str(e2)}. Proceeding without login.")
    
    # If login failed, try to proceed anonymously with more conservative settings
    if not login_successful:
        print("Proceeding with anonymous Instaloader access")
        L.download_delay = 5.0  # Increase delay for anonymous access

    try:
        if target.startswith('@'):
            # Profile scraping
            profile_name = target[1:]
            print(f"Fetching profile: {profile_name}")
            profile = Profile.from_username(L.context, profile_name)
            posts = profile.get_posts()
        elif target.startswith('#'):
            # Hashtag scraping - improved approach
            hashtag_name = target[1:].strip().lower()
            print(f"Fetching hashtag: #{hashtag_name}")
            try:
                hashtag = Hashtag.from_name(L.context, hashtag_name)
                posts = hashtag.get_posts()
            except Exception as e:
                print(f"Failed to get hashtag posts: {str(e)}")
                # Fallback: try to get top posts for hashtag
                try:
                    # Try to get top posts instead of recent
                    posts = hashtag.get_top_posts()
                    print("Using top posts for hashtag")
                except Exception as e2:
                    print(f"Failed to get top posts: {str(e2)}")
                    posts = []
        elif target.startswith('https://'):
            # Direct URL
            print(f"Fetching direct URL: {target}")
            try:
                shortcode = target.split("/reel/")[1].strip("/")
                post = Post.from_shortcode(L.context, shortcode)
                posts = [post]
            except Exception as e:
                print(f"Failed to get direct URL: {str(e)}")
                posts = []
        else:
            # Assume profile
            print(f"Fetching profile: {target}")
            profile = Profile.from_username(L.context, target)
            posts = profile.get_posts()

        count = 0
        print(f"Starting to process posts...")
        
        for post in posts:
            if count >= max_reels:
                break

            try:
                # More flexible reel detection
                is_reel = False
                
                # Check if it's a video post (reels are videos)
                if post.is_video:
                    is_reel = True
                
                # Additional check for reel-specific patterns
                if hasattr(post, 'typename') and 'Reel' in str(post.typename):
                    is_reel = True
                    
                # For hashtag posts, accept any video as potential reel
                if target.startswith('#') and post.is_video:
                    is_reel = True

                if is_reel:
                    print(f"Processing reel {count + 1} of {max_reels}")

                    # Get comments with error handling
                    top_comments = []
                    try:
                        comments = list(post.get_comments())[:5]  # Top 5 comments
                        for comment in comments:
                            try:
                                top_comments.append({
                                    "user": comment.owner.username,
                                    "comment": comment.text,
                                    "timestamp": comment.created_at_utc.isoformat()
                                })
                            except:
                                continue
                    except Exception as e:
                        print(f"Failed to get comments: {str(e)}")

                    # Get creator info
                    creator = {
                        "username": post.owner_username,
                        "profile": f"https://www.instagram.com/{post.owner_username}/"
                    }

                    # Get video URL with fallback
                    video_url = post.video_url or f"https://www.instagram.com/reel/{post.shortcode}/"
                    reel_id = post.shortcode
                    
                    # Ensure Reel_link URL has reel_id at the end
                    if video_url and reel_id and "?" not in video_url:
                        video_url = f"{video_url}?reel_id={reel_id}"
                    elif video_url and reel_id:
                        video_url = f"{video_url}&reel_id={reel_id}"
                    
                    # Get view count with fallback
                    views = getattr(post, 'video_view_count', 0) or 0
                    
                    reel_data = {
                        "reel_id": reel_id,
                        "Reel_link": video_url,
                        "caption": post.caption or "",
                        "creator": creator,
                        "likes": post.likes or 0,
                        "views": views,
                        "upload_date": post.date_utc.isoformat() if post.date_utc else "",
                        "top_comments": top_comments
                    }

                    reels.append(reel_data)
                    count += 1
                    
                    # Add delay between processing to avoid rate limits
                    time.sleep(1)

            except Exception as e:
                print(f"Skipped post: {str(e)}")
                continue

        print(f"Successfully processed {count} reels")
        return reels

    except Exception as e:
        print(f"Instaloader error: {str(e)}")
        return []


# API Routes
@app.route('/api/analyze', methods=['POST'])
def analyze_reels():
    data = request.json
    if not data or 'target' not in data:
        return jsonify({'error': 'Missing target parameter'}), 400
    
    target = data.get('target')
    max_reels = data.get('max_reels', 10)
    use_login = data.get('use_login', True)
    scraping_method = data.get('scraping_method', 'instaloader')  # 'selenium' or 'instaloader'
    
    # Detect platform from target URL
    detected_platform = platform_resolver.detect_platform(target)
    
    # If platform is unknown, try to detect from target format
    if detected_platform == 'unknown':
        # Check if it's a username (no URL indicators)
        if not target.startswith(('http://', 'https://', 'www.')) and '/' not in target:
            # Assume Instagram username for backward compatibility
            detected_platform = 'instagram'
            print(f"Assuming Instagram platform for target: {target}")
        else:
            print(f"Could not detect platform for target: {target}")
            return jsonify({
                'error': f'Could not detect social media platform from target: {target}. Please provide a valid URL.',
                'detected_platform': 'unknown',
                'supported_platforms': ['youtube', 'instagram', 'tiktok', 'twitter', 'facebook']
            }), 400
    
    # Validate platform support for current scraping methods
    supported_platforms = ['instagram']  # Currently only Instagram is fully supported
    
    if detected_platform not in supported_platforms:
        return jsonify({
            'error': f'Platform "{detected_platform}" is not currently supported for content analysis.',
            'detected_platform': detected_platform,
            'supported_platforms': supported_platforms,
            'message': 'Platform detection successful, but content analysis is only available for Instagram currently.'
        }), 400
    
    print(f"Detected platform: {detected_platform} for target: {target}")
    
    results = []
    
    try:
        if scraping_method.lower() == 'instaloader':
            print(f"Using Instaloader method for target: {target}")
            reels = scrape_with_instaloader(target, max_reels=max_reels)
            
            # If Instaloader fails, fallback to Selenium
            if not reels:
                print("Instaloader failed, falling back to Selenium method")
                scraping_method = 'selenium'
        
        if scraping_method.lower() == 'selenium':
            print(f"Using Selenium method for target: {target}")
            driver = get_webdriver()
            if not driver:
                return jsonify({'error': 'Failed to initialize browser'}), 500
            
            try:
                # Login if requested
                if use_login:
                    login_success = login_to_instagram(driver)
                    if not login_success:
                        print("Proceeding without login - some content might be unavailable")
                
                reels = scrape_instagram_reels(driver, target, max_reels=max_reels)
                
            finally:
                if driver:
                    driver.quit()
        
        # Process the reels through AI analysis
        if reels:
            print(f"Processing {len(reels)} reels through AI analysis")
            for reel in reels:
                try:
                    ai_analysis = analyze_reel_with_ai(reel)
                    
                    # Create final output structure
                    full_result = {
                        "reel_id": reel.get("reel_id", ""),
                        "Reel_link": reel.get("Reel_link", ""),
                        "caption": reel.get("caption", ""),
                        "creator": reel.get("creator", {}),
                        "ai_summary": ai_analysis.get("ai_summary", ""),
                        "category": ai_analysis.get("category", []),
                        "likes": reel.get("likes", 0),
                        "views": reel.get("views", 0),
                        "sentiment": ai_analysis.get("sentiment", ""),
                        "top_comment_summary": ai_analysis.get("top_comment_summary", ""),
                        "embeddings": ai_analysis.get("embeddings", []),
                        "top_comments": reel.get("top_comments", [])
                    }
                    
                    results.append(full_result)
                except Exception as e:
                    print(f"Error analyzing reel: {str(e)}")
                    continue
        else:
            print("No reels found to analyze")
        
        return jsonify({
            'status': 'success',
            'detected_platform': detected_platform,
            'target': target,
            'count': len(results),
            'method_used': scraping_method,
            'results': results
        })
        
    except Exception as e:
        print(f"API error: {str(e)}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({
        'status': 'ok',
        'version': '1.0.0',
        'timestamp': datetime.now().isoformat()
    })


@app.route('/api/detect-platform', methods=['POST'])
def detect_platform_endpoint():
    """
    Detect the social media platform from a given URL.
    
    Request body:
        {
            "url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
        }
    
    Response:
        {
            "platform": "youtube",
            "confidence": "high",
            "url_type": "video",
            "description": "Video sharing platform"
        }
    """
    data = request.json
    if not data or 'url' not in data:
        return jsonify({'error': 'Missing url parameter'}), 400
    
    url = data.get('url')
    if not url or not isinstance(url, str):
        return jsonify({'error': 'Invalid url parameter'}), 400
    
    try:
        # Get detailed platform information
        platform_info = platform_resolver.get_platform_info(url)
        
        return jsonify({
            'status': 'success',
            'url': url,
            'platform': platform_info['platform'],
            'confidence': platform_info['confidence'],
            'url_type': platform_info['url_type'],
            'description': platform_info['description']
        })
        
    except Exception as e:
        return jsonify({'error': f'Failed to detect platform: {str(e)}'}), 500


@app.route('/api/detect-platform/batch', methods=['POST'])
def detect_platform_batch_endpoint():
    """
    Detect platforms for multiple URLs in a single request.
    
    Request body:
        {
            "urls": [
                "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
                "https://www.instagram.com/reel/ABC123DEF/",
                "https://www.tiktok.com/@username/video/1234567890"
            ]
        }
    
    Response:
        {
            "status": "success",
            "count": 3,
            "results": [
                {
                    "url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
                    "platform": "youtube",
                    "confidence": "high",
                    "url_type": "video",
                    "description": "Video sharing platform"
                },
                ...
            ]
        }
    """
    data = request.json
    if not data or 'urls' not in data:
        return jsonify({'error': 'Missing urls parameter'}), 400
    
    urls = data.get('urls')
    if not isinstance(urls, list) or len(urls) == 0:
        return jsonify({'error': 'urls must be a non-empty list'}), 400
    
    # Limit batch size to prevent abuse
    if len(urls) > 100:
        return jsonify({'error': 'Maximum 100 URLs allowed per batch request'}), 400
    
    results = []
    errors = []
    
    for i, url in enumerate(urls):
        try:
            if not url or not isinstance(url, str):
                errors.append({
                    'index': i,
                    'url': url,
                    'error': 'Invalid URL format'
                })
                continue
            
            platform_info = platform_resolver.get_platform_info(url)
            results.append({
                'url': url,
                'platform': platform_info['platform'],
                'confidence': platform_info['confidence'],
                'url_type': platform_info['url_type'],
                'description': platform_info['description']
            })
            
        except Exception as e:
            errors.append({
                'index': i,
                'url': url,
                'error': str(e)
            })
    
    response = {
        'status': 'success',
        'count': len(results),
        'results': results
    }
    
    if errors:
        response['errors'] = errors
        response['error_count'] = len(errors)
    
    return jsonify(response)


@app.route('/api/platforms', methods=['GET'])
def get_supported_platforms():
    """
    Get a list of all supported social media platforms.
    
    Response:
        {
            "status": "success",
            "platforms": [
                {
                    "name": "youtube",
                    "description": "Video sharing platform"
                },
                {
                    "name": "instagram",
                    "description": "Photo and video sharing platform"
                },
                ...
            ],
            "count": 15
        }
    """
    try:
        platforms = platform_resolver.list_platforms()
        platform_descriptions = {
            'youtube': 'Video sharing platform',
            'instagram': 'Photo and video sharing platform',
            'tiktok': 'Short-form video platform',
            'twitter': 'Microblogging and social networking',
            'facebook': 'Social networking platform',
            'linkedin': 'Professional networking platform',
            'snapchat': 'Multimedia messaging app',
            'pinterest': 'Visual discovery and bookmarking',
            'reddit': 'Social news and discussion platform',
            'twitch': 'Live streaming platform',
            'discord': 'Voice, video, and text communication',
            'telegram': 'Cloud-based instant messaging',
            'whatsapp': 'Instant messaging and voice over IP',
            'vimeo': 'Video hosting and sharing platform',
            'dailymotion': 'Video sharing platform',
        }
        
        platform_list = []
        for platform in platforms:
            platform_list.append({
                'name': platform,
                'description': platform_descriptions.get(platform, 'Social media platform')
            })
        
        return jsonify({
            'status': 'success',
            'platforms': platform_list,
            'count': len(platform_list)
        })
        
    except Exception as e:
        return jsonify({'error': f'Failed to get platforms: {str(e)}'}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=False)