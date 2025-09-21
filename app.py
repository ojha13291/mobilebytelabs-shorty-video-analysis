import streamlit as st

# Set page config must be the first Streamlit command
st.set_page_config(
    page_title="Instagram Reels Analyzer",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded"
)

import requests
import time
import os
import re
import json
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

# Initialize embedding model
try:
    # Fix for 'Cannot copy out of meta tensor' error
    import torch
    import os
    
    # Disable Streamlit's file watcher for torch modules to prevent __path__._path errors
    os.environ['STREAMLIT_WATCH_EXCLUDE_PATHS'] = 'torch,sentence_transformers'
    
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
                st.warning("CUDA meta tensor error detected, falling back to CPU")
                embedder.to('cpu')
            else:
                raise e
except Exception as e:
    st.error(f"Error initializing SentenceTransformer: {str(e)}")
    # Fallback to simple embedding if model fails to load
    embedder = None

# Mistral API Configuration
MISTRAL_API_URL = "https://api.mistral.ai/v1/chat/completions"
MISTRAL_API_KEY = "demo_pai_key"  # Direct API key

# Instagram credentials (replace with your actual credentials)
INSTA_USER = "demo_username"  # REPLACE WITH YOUR USERNAME
INSTA_PASS = "demo_password"  # REPLACE WITH YOUR PASSWORD


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
        st.warning("Instagram credentials not set. Proceeding without login.")
        return False

    try:
        st.info("Logging in to Instagram...")
        driver.get("https://www.instagram.com/accounts/login/")

        # Wait for login page to load
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.NAME, "username"))
        )

        # Fill credentials
        username_field = driver.find_element(By.NAME, "username")
        password_field = driver.find_element(By.NAME, "password")

        username_field.send_keys(INSTA_USER)
        password_field.send_keys(INSTA_PASS)

        # Click login button
        login_button = driver.find_element(By.XPATH, '//button[@type="submit"]')
        login_button.click()

        # Wait for login to complete
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.XPATH, "//a[contains(@href, '/accounts/')]"))
        )

        # Dismiss save login info prompt
        try:
            WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.XPATH, "//div[text()='Not Now']"))
            ).click()
        except:
            pass

        # Dismiss notifications prompt
        try:
            WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.XPATH, "//button[text()='Not Now']"))
            ).click()
        except:
            pass

        st.success("Logged in successfully!")
        return True

    except Exception as e:
        st.error(f"Login failed: {str(e)}")
        return False


def call_mistral_api(prompt: str) -> str:
    """Call Mistral API with the given prompt"""
    headers = {
        "Authorization": f"Bearer {MISTRAL_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "mistral-tiny",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.7,
        "max_tokens": 500
    }
    try:
        response = requests.post(MISTRAL_API_URL, headers=headers, json=payload, timeout=30)
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"]
    except Exception as e:
        st.error(f"Mistral API error: {str(e)}")
        return ""


def get_webdriver():
    """Create and return a Chrome WebDriver instance"""
    try:
        # Use webdriver_manager to handle ChromeDriver
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=get_chrome_options())
        return driver
    except Exception as e:
        st.error(f"Failed to create WebDriver: {str(e)}")
        return None


def extract_instagram_data(driver, reel_url: str) -> dict:
    """Extract data from a single Instagram reel with improved comment extraction"""
    try:
        driver.get(reel_url)
        time.sleep(5)  # Additional sleep to ensure page loads

        # Get direct video URL from meta tags - more reliable
        video_url = ""
        try:
            # First try: get from meta property="og:video"
            video_element = driver.find_element(By.XPATH, '//meta[@property="og:video"]')
            video_url = video_element.get_attribute("content")

            # If not found, try alternative meta tags
            if not video_url:
                video_element = driver.find_element(By.XPATH, '//meta[@property="og:video:secure_url"]')
                video_url = video_element.get_attribute("content")
        except NoSuchElementException:
            try:
                # Fallback to video element
                video_element = driver.find_element(By.TAG_NAME, "video")
                video_url = video_element.get_attribute("src")
            except:
                pass

        # Get caption - updated selector
        caption = ""
        try:
            # Try multiple possible selectors for caption
            try:
                caption_element = driver.find_element(By.XPATH, '//div[contains(@data-ad-preview, "message")]')
            except:
                try:
                    caption_element = driver.find_element(By.XPATH,
                                                          '//div[contains(@class, "_a9zs") or contains(@class, "_a9zr")]')
                except:
                    caption_element = driver.find_element(By.XPATH, '//h1[contains(@class, "_ap3a")]')
            caption = caption_element.text
        except NoSuchElementException:
            pass

        # Get creator info
        creator = {"username": "", "profile": ""}
        try:
            creator_element = driver.find_element(By.XPATH, '//header//a[contains(@href, "/")]')
            creator["username"] = creator_element.text.strip()
            creator["profile"] = creator_element.get_attribute("href")
        except NoSuchElementException:
            pass

        # Get metrics (likes and views) - updated selectors
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
                        likes_text = text.replace("likes", "").replace("like", "").replace(",", "").replace(".",
                                                                                                            "").strip()
                        if "k" in likes_text:
                            likes = int(float(likes_text.replace("k", "")) * 1000)
                        elif "m" in likes_text:
                            likes = int(float(likes_text.replace("m", "")) * 1000000)
                        elif likes_text.isdigit():
                            likes = int(likes_text)
                    # Extract views
                    elif "view" in text or "views" in text:
                        views_text = text.replace("views", "").replace("view", "").replace(",", "").replace(".",
                                                                                                            "").strip()
                        if "k" in views_text:
                            views = int(float(views_text.replace("k", "")) * 1000)
                        elif "m" in views_text:
                            views = int(float(views_text.replace("m", "")) * 1000000)
                        elif views_text.isdigit():
                            views = int(views_text)
        except:
            pass

        # Get upload date
        upload_date = ""
        try:
            time_element = driver.find_element(By.TAG_NAME, "time")
            upload_date = time_element.get_attribute("datetime")
        except:
            pass

        # Get top comments - IMPROVED COMMENT EXTRACTION WITH MULTIPLE SELECTORS
        top_comments = []
        try:
            # Wait for comments section to load - try multiple possible selectors
            try:
                # First try to scroll to load comments if they're not immediately visible
                driver.execute_script("window.scrollBy(0, 500);")  # Scroll down to trigger comment loading
                time.sleep(2)  # Wait for scroll to complete
                
                # Try multiple selectors with increased timeout
                WebDriverWait(driver, 15).until(
                    EC.presence_of_element_located((By.XPATH, "//div[contains(@class, '_a9zr') or contains(@class, 'x1lliihq') or contains(@class, 'xdj266r') or contains(@class, 'x78zum5')]"))
                )
                
                # Debug info
                st.info("Comment section detected, attempting to extract comments")
            except TimeoutException:
                # Try scrolling down to load comments
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(3)  # Wait for potential comments to load after scroll

            # Try multiple selectors for comment containers
            comment_containers = []
            selectors = [
                "//div[contains(@class, '_a9zr')]",  # Classic selector
                "//div[contains(@class, 'x1lliihq')][contains(@class, 'x1plvlek')]",  # New UI selector
                "//ul[contains(@class, 'x78zum5')]//ul//div[contains(@class, 'x1lliihq')]",  # Another possible structure
                "//div[contains(@role, 'button')]/following-sibling::div//span[contains(@class, 'x1lliihq')]",  # Yet another structure
                "//div[contains(@class, 'xdj266r')]",  # Additional possible class
                "//ul[contains(@class, 'x78zum5')]//div[contains(@class, '_a9zs')]",  # Comments in list
                "//div[contains(@class, '_ae5q')]//span",  # Another UI variation
                "//div[contains(@class, '_ab8w')]//span[string-length(text()) > 5]",  # Text content in comments
                "//div[@role='button']//span[string-length(text()) > 5]"  # Clickable comment elements
            ]
            
            for selector in selectors:
                try:
                    found_containers = driver.find_elements(By.XPATH, selector)
                    if found_containers:
                        comment_containers = found_containers
                        st.info(f"Found {len(comment_containers)} comments using selector: {selector}")
                        break
                except Exception as e:
                    continue

            # If still no comments found, try one more approach - look for text that appears to be comments
            if not comment_containers:
                try:
                    # Try scrolling again to ensure comments are loaded
                    driver.execute_script("window.scrollBy(0, 700);")  # Scroll further down
                    time.sleep(2)  # Wait for scroll to complete
                    
                    # Look for any elements that might contain user-generated content
                    potential_comments = driver.find_elements(By.XPATH, 
                        "//span[contains(@class, 'x1lliihq') and string-length(text()) > 5]")
                    if potential_comments:
                        comment_containers = potential_comments
                        st.info(f"Found {len(comment_containers)} potential comments using fallback method")
                    else:
                        # Last resort - try to find any text content that might be comments
                        potential_comments = driver.find_elements(By.XPATH, 
                            "//span[string-length(text()) > 10 and not(contains(@class, 'xo1l8bm'))]")
                        if potential_comments:
                            comment_containers = potential_comments
                            st.info(f"Found {len(comment_containers)} potential comments using last resort method")
                except Exception as e:
                    pass

            # Process top 5 comments
            for i in range(min(5, len(comment_containers))):
                try:
                    comment = comment_containers[i]
                    
                    # Try to determine if this is actually a comment (not caption)
                    # Skip first element if it matches the caption
                    if i == 0 and comment.text.strip() == caption.strip():
                        continue

                    # Extract username - try multiple approaches
                    username = "Unknown"
                    try:
                        # Try different ways to find username
                        username_selectors = [
                            ".//h3[contains(@class, '_a9zc')]",
                            "./preceding-sibling::div//span[contains(@class, 'x1lliihq')]",
                            "./parent::div/preceding-sibling::div//span",
                            ".//a[contains(@class, 'x1i10hfl')]"
                        ]
                        
                        for selector in username_selectors:
                            try:
                                user_element = comment.find_element(By.XPATH, selector)
                                potential_username = user_element.text.strip()
                                if potential_username and len(potential_username) < 30:  # Username shouldn't be too long
                                    username = potential_username
                                    break
                            except:
                                continue
                    except:
                        pass

                    # Extract comment text
                    comment_text = ""
                    try:
                        # First try direct text
                        comment_text = comment.text.strip()
                        
                        # If that doesn't work, try finding specific elements
                        if not comment_text:
                            text_selectors = [
                                ".//div[contains(@class, '_a9zs')]",
                                ".//span[contains(@class, 'x1lliihq')]",
                                "."
                            ]
                            
                            for selector in text_selectors:
                                try:
                                    text_element = comment.find_element(By.XPATH, selector)
                                    potential_text = text_element.text.strip()
                                    if potential_text:
                                        comment_text = potential_text
                                        break
                                except:
                                    continue
                    except:
                        pass

                    # Extract timestamp
                    timestamp = ""
                    try:
                        time_selectors = [
                            ".//time",
                            "./parent::div//time",
                            "./following-sibling::div//time"
                        ]
                        
                        for selector in time_selectors:
                            try:
                                time_element = comment.find_element(By.XPATH, selector)
                                timestamp = time_element.get_attribute("datetime")
                                if timestamp:
                                    break
                            except:
                                continue
                    except:
                        pass

                    # Only add if we have comment text and it's not just the username
                    if comment_text and comment_text != username and len(comment_text) > 1:
                        # Clean up the comment text (remove username if it appears at the beginning)
                        if comment_text.startswith(username):
                            comment_text = comment_text[len(username):].strip()
                            
                        top_comments.append({
                            "user": username,
                            "comment": comment_text,
                            "timestamp": timestamp
                        })
                except StaleElementReferenceException:
                    # Re-locate comments if elements become stale
                    for selector in selectors:
                        try:
                            found_containers = driver.find_elements(By.XPATH, selector)
                            if found_containers:
                                comment_containers = found_containers
                                break
                        except:
                            continue
                    continue
                except Exception as e:
                    st.warning(f"Comment extraction error: {str(e)}")
                    continue
        except TimeoutException:
            st.warning("Comments section not found")
        except Exception as e:
            st.warning(f"Top comments extraction failed: {str(e)}")

        # Extract reel ID from URL
        reel_id_match = re.search(r'/reel/([^/]+)', reel_url)
        reel_id = reel_id_match.group(1) if reel_id_match else f"reel_{int(time.time())}"

        return {
            "reel_id": reel_id,
            "Reel_link": video_url,
            "caption": caption,
            "creator": creator,
            "likes": likes,
            "views": views,
            "upload_date": upload_date,
            "top_comments": top_comments
        }

    except Exception as e:
        st.error(f"Error extracting data: {str(e)}")
        return {}


def analyze_reel_with_ai(reel: dict) -> dict:
    """Analyze a reel using Mistral AI and add enrichment"""
    if not reel.get('caption'):
        return {
            "ai_summary": "No caption available",
            "category": [],
            "sentiment": "Unknown",
            "top_comment_summary": "No comments",
            "embeddings": []
        }

    try:
        # Prepare inputs
        caption = reel['caption']
        comments = [c['comment'] for c in reel.get('top_comments', [])]
        comments_text = " ".join(comments[:3]) if comments else ""

        # Summarization
        summary_prompt = f"Summarize this Instagram reel in one sentence: {caption}"
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
                st.warning(f"Embedding generation failed: {str(e)}")
                # Create a fallback embedding with correct dimensions
                embeddings = [0.0] * 384  # Standard dimension for all-MiniLM-L6-v2
        else:
            st.warning("Embedder not initialized, using zero vector fallback")
            embeddings = [0.0] * 384  # Standard dimension for all-MiniLM-L6-v2

        return {
            "ai_summary": ai_summary,
            "category": category_list,
            "sentiment": sentiment,
            "top_comment_summary": comment_summary,
            "embeddings": embeddings[:10]  # First 10 dimensions
        }

    except Exception as e:
        st.error(f"AI analysis error: {str(e)}")
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
            url = f"https://www.instagram.com/explore/tags/{hashtag}/"
        else:
            url = f"https://www.instagram.com/{target}/"

        st.info(f"Navigating to: {url}")
        driver.get(url)
        time.sleep(5)  # Give more time for initial load

        # Wait for page to load
        try:
            WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.TAG_NAME, "article"))
            )
        except TimeoutException:
            st.warning("Page loading timed out. Trying to proceed...")

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
            st.warning("No reels found on this page")
            return []

        st.success(f"Found {len(reel_urls)} potential reels")

        # Process up to max_reels
        for i, url in enumerate(list(reel_urls)[:max_reels]):
            try:
                st.info(f"Processing reel {i + 1}: {url}")

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
                st.warning(f"Skipped reel due to error: {str(e)}")

    except Exception as e:
        st.error(f"Scraping error: {str(e)}")

    return reels


def scrape_with_instaloader(target: str, max_reels: int = 10) -> list:
    """Scrape Instagram reels using Instaloader"""
    reels = []
    L = instaloader.Instaloader()

    # Login if credentials are available
    if INSTA_USER and INSTA_PASS:
        try:
            L.login(INSTA_USER, INSTA_PASS)
            st.success("Logged in to Instagram using Instaloader")
        except Exception as e:
            st.warning(f"Instaloader login failed: {str(e)}. Proceeding without login.")

    try:
        if target.startswith('@'):
            # Profile scraping
            profile_name = target[1:]
            st.info(f"Fetching profile: {profile_name}")
            profile = Profile.from_username(L.context, profile_name)
            posts = profile.get_posts()
        elif target.startswith('#'):
            # Hashtag scraping
            hashtag_name = target[1:]
            st.info(f"Fetching hashtag: #{hashtag_name}")
            posts = Hashtag.from_name(L.context, hashtag_name).get_posts()
        elif target.startswith('https://'):
            # Direct URL
            st.info(f"Fetching direct URL: {target}")
            shortcode = target.split("/reel/")[1].strip("/")
            post = Post.from_shortcode(L.context, shortcode)
            posts = [post]
        else:
            # Assume profile
            st.info(f"Fetching profile: {target}")
            profile = Profile.from_username(L.context, target)
            posts = profile.get_posts()

        count = 0
        for post in posts:
            if count >= max_reels:
                break

            if post.is_video and post.typename == 'GraphReel':  # Check if it's a reel
                try:
                    st.info(f"Processing reel {count + 1} of {max_reels}")

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

                    reel_data = {
                        "reel_id": post.shortcode,
                        "Reel_link": post.video_url,
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
                    st.warning(f"Skipped reel: {str(e)}")

        return reels

    except Exception as e:
        st.error(f"Instaloader error: {str(e)}")
        return []


# Streamlit UI

# Sidebar for inputs
with st.sidebar:
    st.title("🎬 Instagram Reels Analyzer")
    st.markdown("Scrape and analyze public Instagram reels")

    target = st.text_input(
        "Enter Instagram URL, @profile, or #hashtag",
        value="https://www.instagram.com/only_comedy_vid/",
        key="target_input"
    )

    # Scraping method selection
    scraping_method = st.radio(
        "Scraping Method:",
        ("Selenium (Browser-based)", "Instaloader (API-based)"),
        index=0,
        help="Instaloader is more reliable but requires login. Selenium works without login but may be slower."
    )
    
    # Number of reels to fetch
    max_reels = st.slider(
        "Number of Reels to Fetch",
        min_value=1,
        max_value=20,
        value=10,
        step=1,
        help="Select how many reels you want to analyze. More reels will take longer to process."
    )

    # Add login toggle
    use_login = st.checkbox("Use Instagram Login", value=True)
    if use_login:
        st.info("Using direct credentials from code")

    analyze_btn = st.button("Analyze Reels", type="primary", use_container_width=True)

    st.markdown("---")
    st.markdown("### How to Use")
    st.info("1. Enter a public Instagram URL, profile, or hashtag\n"
            "2. Choose scraping method (Instaloader recommended)\n"
            "3. Enable login for better reliability\n"
            "4. Click 'Analyze Reels'\n"
            "5. View results in the analysis tabs")
    st.markdown("---")
    st.caption("Note: First run may take extra time to setup. Only public accounts work.")

# Main content
st.title("Instagram Reels Analysis")
st.caption(f"Analyzing content from: {target}")

# Initialize session state
if 'results' not in st.session_state:
    st.session_state.results = []
if 'status' not in st.session_state:
    st.session_state.status = "ready"

# Process when button is clicked
if analyze_btn and target:
    st.session_state.status = "processing"
    st.session_state.results = []

    # Use Instaloader if selected
    if "Instaloader" in scraping_method:
        with st.spinner("Scraping with Instaloader..."):
            reels = scrape_with_instaloader(target, max_reels=max_reels)

            if not reels:
                st.error("No public reels found. Try a different hashtag or profile.")
                st.session_state.status = "ready"
                st.stop()

            st.session_state.results = []
            progress_bar = st.progress(0)

            for i, reel in enumerate(reels):
                progress = (i + 1) / len(reels)
                progress_bar.progress(progress)

                st.write(f"Analyzing reel {i + 1} of {len(reels)}...")
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
                    "embeddings": ai_analysis.get("embeddings", [])
                }

                st.session_state.results.append(full_result)
                time.sleep(1)  # Avoid rate limiting

            st.session_state.status = "completed"
            st.success(f"Successfully analyzed {len(reels)} reels using Instaloader!")

    else:  # Use Selenium
        with st.spinner("Setting up browser for Instagram..."):
            driver = get_webdriver()
            if not driver:
                st.error("Failed to initialize browser. Please try again.")
                st.stop()

        try:
            # Login if requested
            if use_login:
                login_success = login_to_instagram(driver)
                if not login_success:
                    st.warning("Proceeding without login - some content might be unavailable")

            with st.status("Scraping Instagram...", expanded=True) as status:
                st.write(f"Searching for: {target}")
                reels = scrape_instagram_reels(driver, target, max_reels=max_reels)

                if not reels:
                    st.error("No public reels found. Try a different hashtag or profile.")
                    st.session_state.status = "ready"
                    st.stop()

                st.success(f"Found {len(reels)} reels! Starting AI analysis...")
                st.session_state.results = []

                progress_bar = st.progress(0)
                for i, reel in enumerate(reels):
                    progress = (i + 1) / len(reels)
                    progress_bar.progress(progress)

                    st.write(f"Analyzing reel {i + 1} of {len(reels)}...")
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
                        "embeddings": ai_analysis.get("embeddings", [])
                    }

                    st.session_state.results.append(full_result)
                    time.sleep(1)  # Avoid rate limiting

                st.session_state.status = "completed"
                status.update(label="Analysis complete!", state="complete", expanded=False)

        except Exception as e:
            st.error(f"Processing failed: {str(e)}")
            st.session_state.status = "error"
        finally:
            if driver:
                driver.quit()

# Display results
if st.session_state.results:
    st.subheader(f"Analysis Results: {len(st.session_state.results)} Reels")

    # Create tabs for each reel
    tabs = st.tabs([f"Reel {i + 1}" for i in range(len(st.session_state.results))])

    for idx, tab in enumerate(tabs):
        with tab:
            reel = st.session_state.results[idx]

            col1, col2 = st.columns([1, 2])

            with col1:
                # Handle video URL
                video_url = reel.get('Reel_link', '')
                if video_url and not video_url.startswith('blob:'):
                    st.video(video_url)
                else:
                    st.warning("Video URL not available or unsupported format")
                    if video_url:
                        st.caption(f"Video source: {video_url[:100]}...")

                st.metric("Likes", f"{reel.get('likes', 0):,}")
                st.metric("Views", f"{reel.get('views', 0):,}")

                if reel.get('creator'):
                    creator = reel['creator']
                    st.write(f"**Creator:** [{creator.get('username', '')}]({creator.get('profile', '')})")

                if reel.get('upload_date'):
                    try:
                        upload_date = datetime.fromisoformat(reel['upload_date'].rstrip('Z'))
                        st.write(f"**Upload Date:** {upload_date.strftime('%Y-%m-%d %H:%M:%S')}")
                    except:
                        st.write(f"**Upload Date:** {reel['upload_date']}")

            with col2:
                st.subheader("Content Analysis")

                # Handle caption display
                if reel.get('caption'):
                    st.write(f"**Caption:** {reel['caption']}")
                else:
                    st.warning("No caption available")

                st.write(f"**AI Summary:** {reel.get('ai_summary', 'N/A')}")
                st.write(f"**Sentiment:** {reel.get('sentiment', 'N/A')}")

                if reel.get('category'):
                    st.write(f"**Categories:** {', '.join(reel['category'])}")
                else:
                    st.write("**Categories:** Not detected")

                st.write(f"**Comments Summary:** {reel.get('top_comment_summary', 'N/A')}")

                if reel.get('embeddings'):
                    st.write(f"**Embeddings Preview:** {reel['embeddings'][:5]}")  # Show first 5 dimensions

            # Show top comments in expander
            if reel.get('top_comments'):
                with st.expander("Top Comments"):
                    for comment in reel['top_comments']:
                        st.info(
                            f"**{comment.get('user', 'User')}** ({comment.get('timestamp', '')}): {comment.get('comment', '')}")
            else:
                with st.expander("Comments"):
                    st.info("No comments extracted")

            # Show raw JSON in expander
            with st.expander("Raw JSON Data"):
                st.json(reel)

elif st.session_state.status == "processing":
    st.info("Processing... This may take a few minutes")
    st.image("https://i.gifer.com/origin/34/34338d26023e5515f6cc8969aa027bca_w200.gif", width=200)

elif analyze_btn and not target:
    st.warning("Please enter a URL, profile, or hashtag")

# Footer
st.divider()
st.caption("Instagram Reels Analyzer v10.0 | Powered by Mistral AI & Instaloader")