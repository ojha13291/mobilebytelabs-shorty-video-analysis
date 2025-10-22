#!/usr/bin/env python3
"""
Enhanced Video Analysis UI Interface
Streamlit-based frontend for video URL processing with complete pipeline integration
"""

import streamlit as st
import requests
import json
import time
from typing import Dict, Any, Optional
from datetime import datetime
import os

# Page configuration
st.set_page_config(
    page_title="Video Analysis Platform",
    page_icon="🎥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for polished UI
st.markdown("""
<style>
    /* Main container styling */
    .main {
        padding: 2rem;
    }
    
    /* Card styling */
    .card {
        background: white;
        border-radius: 10px;
        padding: 1.5rem;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        margin: 1rem 0;
    }
    
    /* Header styling */
    .header-container {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 10px;
        color: white;
        margin-bottom: 2rem;
    }
    
    /* Metric cards */
    .metric-card {
        background: #f8f9fa;
        border-radius: 8px;
        padding: 1rem;
        text-align: center;
        border-left: 4px solid #667eea;
    }
    
    /* Status badges */
    .status-badge {
        display: inline-block;
        padding: 0.25rem 0.75rem;
        border-radius: 20px;
        font-size: 0.85rem;
        font-weight: 600;
    }
    
    .status-success {
        background: #d4edda;
        color: #155724;
    }
    
    .status-error {
        background: #f8d7da;
        color: #721c24;
    }
    
    .status-processing {
        background: #fff3cd;
        color: #856404;
    }
    
    /* Result sections */
    .result-section {
        margin: 1.5rem 0;
        padding: 1rem;
        background: #f8f9fa;
        border-radius: 8px;
    }
    
    /* Sentiment indicators */
    .sentiment-positive {
        color: #28a745;
        font-weight: bold;
    }
    
    .sentiment-negative {
        color: #dc3545;
        font-weight: bold;
    }
    
    .sentiment-neutral {
        color: #6c757d;
        font-weight: bold;
    }
    
    /* Loading animation */
    .stSpinner > div {
        border-top-color: #667eea !important;
    }
</style>
""", unsafe_allow_html=True)

# Configuration
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:5001/api")

def init_session_state():
    """Initialize session state variables"""
    if 'analysis_results' not in st.session_state:
        st.session_state.analysis_results = None
    if 'processing' not in st.session_state:
        st.session_state.processing = False
    if 'error_message' not in st.session_state:
        st.session_state.error_message = None

def check_api_health() -> bool:
    """Check if the backend API is healthy"""
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=5)
        return response.status_code == 200
    except Exception as e:
        return False

def detect_platform(url: str) -> Optional[Dict[str, Any]]:
    """Detect platform from video URL"""
    try:
        response = requests.post(
            f"{API_BASE_URL}/detect",
            json={"url": url},
            timeout=10
        )
        if response.status_code == 200:
            return response.json()
        return None
    except Exception as e:
        st.error(f"Platform detection failed: {str(e)}")
        return None

def analyze_video(url: str) -> Optional[Dict[str, Any]]:
    """Trigger complete video analysis pipeline"""
    try:
        # Call the analyze endpoint
        response = requests.post(
            f"{API_BASE_URL}/analyze",
            json={
                "url": url,
                "include_llm_analysis": True,
                "include_sentiment": True,
                "include_topics": True
            },
            timeout=120  # Extended timeout for LLM processing
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            error_data = response.json()
            st.error(f"Analysis failed: {error_data.get('error', 'Unknown error')}")
            return None
            
    except requests.exceptions.Timeout:
        st.error("Request timed out. The video analysis is taking longer than expected.")
        return None
    except Exception as e:
        st.error(f"Analysis error: {str(e)}")
        return None

def render_header():
    """Render the application header"""
    st.markdown("""
    <div class="header-container">
        <h1>🎥 Video Analysis Platform</h1>
        <p style="font-size: 1.1rem; margin-top: 0.5rem;">
            Analyze videos from YouTube, Instagram, TikTok, and Twitter with AI-powered insights
        </p>
    </div>
    """, unsafe_allow_html=True)

def render_platform_badge(platform: str) -> str:
    """Render platform badge with icon"""
    platform_icons = {
        "youtube": "📺",
        "instagram": "📷",
        "tiktok": "🎵",
        "twitter": "🐦",
        "unknown": "❓"
    }
    icon = platform_icons.get(platform.lower(), "🎥")
    return f"{icon} {platform.upper()}"

def render_sentiment_indicator(sentiment: str, confidence: float = 0.0) -> str:
    """Render sentiment with color coding"""
    sentiment_lower = sentiment.lower()
    
    if "positive" in sentiment_lower:
        return f'<span class="sentiment-positive">😊 {sentiment} ({confidence:.1%})</span>'
    elif "negative" in sentiment_lower:
        return f'<span class="sentiment-negative">😞 {sentiment} ({confidence:.1%})</span>'
    else:
        return f'<span class="sentiment-neutral">😐 {sentiment} ({confidence:.1%})</span>'

def render_video_metadata(data: Dict[str, Any]):
    """Render video metadata section"""
    metadata = data.get("metadata", {})
    platform_info = data.get("platform_info", {})
    
    st.markdown("### 📊 Video Information")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <h4>Platform</h4>
            <p style="font-size: 1.5rem; margin: 0.5rem 0;">
                {render_platform_badge(platform_info.get('platform', 'Unknown'))}
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        views = metadata.get('views', 0)
        st.markdown(f"""
        <div class="metric-card">
            <h4>Views</h4>
            <p style="font-size: 1.5rem; margin: 0.5rem 0;">
                {views:,}
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        likes = metadata.get('likes', 0)
        st.markdown(f"""
        <div class="metric-card">
            <h4>Likes</h4>
            <p style="font-size: 1.5rem; margin: 0.5rem 0;">
                {likes:,}
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    # Video title and description
    if metadata.get('title'):
        st.markdown("#### 📝 Title")
        st.info(metadata['title'])
    
    if metadata.get('description'):
        st.markdown("#### 📄 Description")
        with st.expander("Show description"):
            st.write(metadata['description'])
    
    # Thumbnail
    if metadata.get('thumbnail'):
        st.markdown("#### 🖼️ Thumbnail")
        st.image(metadata['thumbnail'], use_column_width=True)

def render_llm_analysis(data: Dict[str, Any]):
    """Render LLM analysis results"""
    llm_analysis = data.get("llm_analysis", {})
    
    if not llm_analysis:
        st.warning("LLM analysis not available")
        return
    
    st.markdown("### 🤖 AI-Powered Analysis")
    
    # Summary
    if llm_analysis.get('summary'):
        st.markdown("#### 💡 Summary")
        st.success(llm_analysis['summary'])
    
    # Sentiment Analysis
    col1, col2 = st.columns(2)
    
    with col1:
        if llm_analysis.get('sentiment'):
            st.markdown("#### 😊 Sentiment Analysis")
            sentiment = llm_analysis['sentiment']
            confidence = llm_analysis.get('confidence_score', 0.0)
            st.markdown(
                render_sentiment_indicator(sentiment, confidence),
                unsafe_allow_html=True
            )
    
    with col2:
        if llm_analysis.get('processing_duration_seconds'):
            st.markdown("#### ⏱️ Processing Time")
            duration = llm_analysis['processing_duration_seconds']
            st.metric("Duration", f"{duration:.2f}s")
    
    # Topics
    if llm_analysis.get('topics'):
        st.markdown("#### 🏷️ Detected Topics")
        topics = llm_analysis['topics']
        if isinstance(topics, str):
            try:
                topics = json.loads(topics)
            except json.JSONDecodeError:
                topics = [topics]
        
        # Display topics as tags
        topics_html = ""
        for topic in topics[:10]:  # Limit to 10 topics
            topics_html += f'<span class="status-badge status-success" style="margin: 0.25rem;">{topic}</span>'
        st.markdown(topics_html, unsafe_allow_html=True)
    
    # Additional insights
    if llm_analysis.get('key_insights'):
        st.markdown("#### 🔍 Key Insights")
        insights = llm_analysis['key_insights']
        if isinstance(insights, list):
            for insight in insights:
                st.markdown(f"- {insight}")
        else:
            st.write(insights)

def render_engagement_metrics(data: Dict[str, Any]):
    """Render engagement metrics"""
    metadata = data.get("metadata", {})
    
    st.markdown("### 📈 Engagement Metrics")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        likes = metadata.get('likes', 0)
        st.metric("👍 Likes", f"{likes:,}")
    
    with col2:
        comments = metadata.get('comments', 0)
        st.metric("💬 Comments", f"{comments:,}")
    
    with col3:
        shares = metadata.get('shares', 0)
        st.metric("🔄 Shares", f"{shares:,}")
    
    with col4:
        # Calculate engagement rate
        views = metadata.get('views', 1)
        engagement = ((likes + comments + shares) / views * 100) if views > 0 else 0
        st.metric("📊 Engagement", f"{engagement:.2f}%")

def render_results(results: Dict[str, Any]):
    """Render complete analysis results"""
    if not results:
        return
    
    # Status indicator
    if results.get('success'):
        st.markdown(
            '<span class="status-badge status-success">✓ Analysis Complete</span>',
            unsafe_allow_html=True
        )
    else:
        st.markdown(
            '<span class="status-badge status-error">✗ Analysis Failed</span>',
            unsafe_allow_html=True
        )
        if results.get('error'):
            st.error(results['error'])
        return
    
    # Render sections
    render_video_metadata(results)
    st.divider()
    render_engagement_metrics(results)
    st.divider()
    render_llm_analysis(results)
    
    # Raw data expander
    with st.expander("🔧 View Raw Data"):
        st.json(results)

def main():
    """Main application logic"""
    init_session_state()
    render_header()
    
    # Sidebar
    with st.sidebar:
        st.markdown("### ⚙️ Configuration")
        
        # API health check
        if check_api_health():
            st.success("✓ API Connected")
        else:
            st.error("✗ API Offline")
            st.warning(f"Backend API: {API_BASE_URL}")
        
        st.divider()
        
        st.markdown("### 📖 Supported Platforms")
        st.markdown("""
        - 📺 YouTube
        - 📷 Instagram
        - 🎵 TikTok
        - 🐦 Twitter
        """)
        
        st.divider()
        
        st.markdown("### ℹ️ About")
        st.info("""
        This tool analyzes video content using:
        - Platform detection
        - Metadata extraction
        - AI-powered content analysis
        - Sentiment detection
        - Topic extraction
        """)
    
    # Main input section
    st.markdown("### 🔗 Enter Video URL")
    
    col1, col2 = st.columns([4, 1])
    
    with col1:
        video_url = st.text_input(
            "Video URL",
            placeholder="https://www.youtube.com/watch?v=...",
            label_visibility="collapsed"
        )
    
    with col2:
        analyze_button = st.button("🚀 Analyze", type="primary", use_container_width=True)
    
    # Example URLs
    with st.expander("📌 Try example URLs"):
        st.markdown("""
        - **YouTube**: `https://www.youtube.com/watch?v=dQw4w9WgXcQ`
        - **Instagram**: `https://www.instagram.com/reel/...`
        - **TikTok**: `https://www.tiktok.com/@user/video/...`
        """)
    
    # Process analysis
    if analyze_button:
        if not video_url:
            st.error("⚠️ Please enter a video URL")
        elif not video_url.startswith(("http://", "https://")):
            st.error("⚠️ Please enter a valid URL starting with http:// or https://")
        else:
            st.session_state.processing = True
            st.session_state.error_message = None
            
            # Show platform detection
            with st.spinner("🔍 Detecting platform..."):
                platform_info = detect_platform(video_url)
                if platform_info:
                    st.success(f"✓ Detected: {render_platform_badge(platform_info.get('platform', 'Unknown'))}")
            
            # Run analysis
            with st.spinner("⚙️ Processing video... This may take up to 2 minutes..."):
                progress_bar = st.progress(0)
                
                # Simulate progress
                for i in range(100):
                    time.sleep(0.02)
                    progress_bar.progress(i + 1)
                
                results = analyze_video(video_url)
                
                if results:
                    st.session_state.analysis_results = results
                    st.session_state.processing = False
                    st.success("✓ Analysis complete!")
                    st.balloons()
                else:
                    st.session_state.processing = False
                    st.error("✗ Analysis failed. Please check the URL and try again.")
    
    # Display results
    if st.session_state.analysis_results:
        st.divider()
        render_results(st.session_state.analysis_results)

if __name__ == "__main__":
    main()
