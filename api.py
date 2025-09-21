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
from selenium.common.exceptions import TimeoutException, NoSuchElementException, StaleElementReferenceException
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from sentence_transformers import SentenceTransformer
import urllib.parse
from datetime import datetime
import instaloader
from instaloader import Profile, Hashtag, Post
import requests

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

# Mistral API Configuration
MISTRAL_API_URL = "https://api.mistral.ai/v1/chat/completions"
MISTRAL_API_KEY = "bPj0wARXs5dk2L1ipFOdoqHMmQnXuMNv"  # Direct API key

# Instagram credentials (replace with your actual credentials)
INSTA_USER = "hixowa1088"  # REPLACE WITH YOUR USERNAME
INSTA_PASS = "raghu17869"  # REPLACE WITH YOUR PASSWORD


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

        # Wait for login page to load with more time and better error handling
        try:
            WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.NAME, "username"))
            )
        except TimeoutException:
            print("Login page did not load properly. Trying alternative approach...")
            # Try refreshing the page
            driver.refresh()
            time.sleep(5)

        # Fill credentials with explicit waits
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
                EC.element_to_be_clickable((By.XPATH, "//button[@type='submit']")
            ))
            login_button.click()
            
            # Wait for login to complete - try multiple possible elements
            try:
                WebDriverWait(driver, 20).until(
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
                    )
                )
            except TimeoutException:
                print("Could not confirm successful login, but continuing...")
        except Exception as e:
            print(f"Error during login form interaction: {str(e)}")
            return False

        # Check for "Save Your Login Info?" prompt and click "Not Now"
        try:
            not_now_button = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Not Now')]"))
            )
            not_now_button.click()
        except:
            pass  # No prompt appeared

        # Check for notifications prompt and click "Not Now"
        try:
            notifications_button = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Not Now')]"))
            )
            notifications_button.click()
        except:
            pass  # No prompt appeared

        print("Successfully logged in to Instagram")
        return True

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
            # Remove any trailing slashes and strip spaces that might be causing the issue
            hashtag = hashtag.rstrip('/').strip()
            # URL encode the hashtag to handle spaces and special characters
            hashtag = urllib.parse.quote(hashtag)
            url = f"https://www.instagram.com/explore/tags/{hashtag}"
        else:
            url = f"https://www.instagram.com/{target}/"

        print(f"Navigating to: {url}")
        driver.get(url)
        time.sleep(5)  # Give more time for initial load

        # Wait for page to load
        try:
            WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.TAG_NAME, "article"))
            )
        except TimeoutException:
            print("Page loading timed out. Trying to proceed...")

        # Scroll multiple times to load more content
        for _ in range(3):
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(3)

        # Find reel links - store URLs instead of elements
        reel_elements = driver.find_elements(By.XPATH, '//a[contains(@href, "/reel/")]')
        reel_urls = set()
        for element in reel_elements:
            try:
                url = element.get_attribute('href')
                if url and "/reel/" in url:
                    reel_urls.add(url)
            except StaleElementReferenceException:
                continue

        if not reel_urls:
            print("No reels found on this page")
            return []

        print(f"Found {len(reel_urls)} potential reels")

        # Process up to max_reels
        for i, url in enumerate(list(reel_urls)[:max_reels]):
            try:
                print(f"Processing reel {i + 1}: {url}")

                # Extract data from reel
                reel_data = extract_instagram_data(driver, url)
                if reel_data:
                    reels.append(reel_data)

                # Navigate back to profile page
                profile_url = url.split('/reel/')[0] + '/'
                driver.get(profile_url)
                time.sleep(3)  # Wait for profile to reload

                # Re-scroll to load content again
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(2)

            except Exception as e:
                print(f"Skipped reel due to error: {str(e)}")

    except Exception as e:
        print(f"Scraping error: {str(e)}")

    return reels


def scrape_with_instaloader(target: str, max_reels: int = 10) -> list:
    """Scrape Instagram reels using Instaloader"""
    reels = []
    L = instaloader.Instaloader()

    # Login if credentials are available
    if INSTA_USER and INSTA_PASS:
        try:
            L.login(INSTA_USER, INSTA_PASS)
            print("Logged in to Instagram using Instaloader")
        except Exception as e:
            print(f"Instaloader login failed: {str(e)}. Proceeding without login.")

    try:
        if target.startswith('@'):
            # Profile scraping
            profile_name = target[1:]
            print(f"Fetching profile: {profile_name}")
            profile = Profile.from_username(L.context, profile_name)
            posts = profile.get_posts()
        elif target.startswith('#'):
            # Hashtag scraping
            hashtag_name = target[1:]
            print(f"Fetching hashtag: #{hashtag_name}")
            posts = Hashtag.from_name(L.context, hashtag_name).get_posts()
        elif target.startswith('https://'):
            # Direct URL
            print(f"Fetching direct URL: {target}")
            shortcode = target.split("/reel/")[1].strip("/")
            post = Post.from_shortcode(L.context, shortcode)
            posts = [post]
        else:
            # Assume profile
            print(f"Fetching profile: {target}")
            profile = Profile.from_username(L.context, target)
            posts = profile.get_posts()

        count = 0
        for post in posts:
            if count >= max_reels:
                break

            if post.is_video and post.typename == 'GraphReel':  # Check if it's a reel
                try:
                    print(f"Processing reel {count + 1} of {max_reels}")

                    # Get comments
                    top_comments = []
                    for comment in post.get_comments()[:5]:  # Top 5 comments
                        top_comments.append({
                            "user": comment.owner.username,
                            "comment": comment.text,
                            "timestamp": comment.created_at_utc.isoformat()
                        })

                    # Get creator info
                    creator = {
                        "username": post.owner_username,
                        "profile": f"https://www.instagram.com/{post.owner_username}/"
                    }

                    # Ensure Reel_link URL has reel_id at the end
                    video_url = post.video_url
                    reel_id = post.shortcode
                    
                    if video_url and reel_id and "?" not in video_url:
                        # Add reel_id as a parameter to the video URL
                        video_url = f"{video_url}?reel_id={reel_id}"
                    elif video_url and reel_id:
                        # URL already has parameters, append reel_id
                        video_url = f"{video_url}&reel_id={reel_id}"
                    
                    reel_data = {
                        "reel_id": reel_id,
                        "Reel_link": video_url,
                        "caption": post.caption,
                        "creator": creator,
                        "likes": post.likes,
                        "views": post.video_view_count,
                        "upload_date": post.date_utc.isoformat(),
                        "top_comments": top_comments
                    }

                    reels.append(reel_data)
                    count += 1

                except Exception as e:
                    print(f"Skipped reel: {str(e)}")

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
    
    results = []
    
    try:
        if scraping_method.lower() == 'instaloader':
            reels = scrape_with_instaloader(target, max_reels=max_reels)
            
            for reel in reels:
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
                
        else:  # Use Selenium
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
                
                for reel in reels:
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
            finally:
                if driver:
                    driver.quit()
        
        return jsonify({
            'status': 'success',
            'count': len(results),
            'results': results
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({
        'status': 'ok',
        'version': '1.0.0',
        'timestamp': datetime.now().isoformat()
    })


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=False)