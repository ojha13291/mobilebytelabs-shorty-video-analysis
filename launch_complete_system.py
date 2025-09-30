#!/usr/bin/env python3
"""
Complete Video Sentiment Analysis System Launcher
Launches both API server and Streamlit interface with full monitoring
"""

import subprocess
import time
import sys
import os
import signal
import requests
import webbrowser
from threading import Thread
import json
from datetime import datetime
import psutil

def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 8):
        print("❌ Python 3.8+ is required")
        sys.exit(1)
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor} detected")

def check_dependencies():
    """Check if all required dependencies are installed"""
    required_packages = [
        'streamlit', 'flask', 'flask-cors', 'flask-sqlalchemy',
        'selenium', 'webdriver-manager', 'pandas', 'numpy',
        'plotly', 'requests', 'beautifulsoup4', 'psutil'
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print(f"❌ Missing packages: {', '.join(missing_packages)}")
        print("Installing missing packages...")
        subprocess.check_call([sys.executable, '-m', 'pip', 'install'] + missing_packages)
    
    print("✅ All dependencies available")

def check_api_server(host='localhost', port=5000):
    """Check if API server is running"""
    try:
        response = requests.get(f'http://{host}:{port}/health', timeout=2)
        return response.status_code == 200
    except requests.exceptions.RequestException:
        return False

def start_api_server():
    """Start the Flask API server"""
    print("🚀 Starting API server...")
    
    api_process = subprocess.Popen([
        sys.executable, 'api/app.py'
    ], cwd=os.getcwd(),
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
    text=True
    )
    
    # Wait for server to start
    for i in range(30):  # Wait up to 30 seconds
        if check_api_server():
            print("✅ API server started successfully")
            return api_process
        time.sleep(1)
    
    print("❌ Failed to start API server")
    return None

def start_streamlit_app():
    """Start the Streamlit application"""
    print("🚀 Starting Streamlit application...")
    
    streamlit_process = subprocess.Popen([
        sys.executable, '-m', 'streamlit', 'run', 'streamlit_app.py',
        '--server.port', '8501',
        '--server.headless', 'true',
        '--browser.gatherUsageStats', 'false'
    ], cwd=os.getcwd(),
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
    text=True
    )
    
    # Wait for Streamlit to start
    time.sleep(5)
    print("✅ Streamlit application started")
    return streamlit_process

def monitor_processes(api_process, streamlit_process):
    """Monitor running processes"""
    def monitor():
        while True:
            api_status = "Running" if api_process.poll() is None else "Stopped"
            streamlit_status = "Running" if streamlit_process.poll() is None else "Stopped"
            
            # Get memory usage
            api_memory = 0
            streamlit_memory = 0
            
            if api_process.poll() is None:
                try:
                    api_memory = psutil.Process(api_process.pid).memory_info().rss / 1024 / 1024
                except:
                    pass
            
            if streamlit_process.poll() is None:
                try:
                    streamlit_memory = psutil.Process(streamlit_process.pid).memory_info().rss / 1024 / 1024
                except:
                    pass
            
            # Clear line and print status
            print(f"\r🔄 API: {api_status} ({api_memory:.1f}MB) | Streamlit: {streamlit_status} ({streamlit_memory:.1f}MB)", end='', flush=True)
            
            if api_process.poll() is not None and streamlit_process.poll() is not None:
                break
            
            time.sleep(2)
    
    monitor_thread = Thread(target=monitor, daemon=True)
    monitor_thread.start()

def create_system_info():
    """Create system information file"""
    info = {
        "timestamp": datetime.now().isoformat(),
        "python_version": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
        "platform": sys.platform,
        "api_endpoint": "http://localhost:5000",
        "streamlit_url": "http://localhost:8501",
        "endpoints": {
            "health_check": "http://localhost:5000/health",
            "analyze_video": "http://localhost:5000/api/analyze",
            "batch_analyze": "http://localhost:5000/api/batch_analyze",
            "dashboard": "http://localhost:8501"
        },
        "features": [
            "Real-time video sentiment analysis",
            "Multi-platform support (YouTube, Instagram, TikTok, Twitter, Facebook)",
            "Advanced analytics dashboard",
            "Batch processing capabilities",
            "Interactive visualizations",
            "Export and reporting features",
            "Video comparison tools",
            "Word cloud and topic analysis"
        ]
    }
    
    with open('system_info.json', 'w') as f:
        json.dump(info, f, indent=2)
    
    return info

def signal_handler(signum, frame):
    """Handle shutdown signals"""
    print("\n\n🛑 Shutting down gracefully...")
    sys.exit(0)

def main():
    """Main launcher function"""
    
    print("🎬 Video Sentiment Analysis System - Complete Launcher")
    print("=" * 60)
    
    # Set up signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        # Pre-flight checks
        check_python_version()
        check_dependencies()
        
        # Create system info
        system_info = create_system_info()
        
        print("\n📋 System Information:")
        print(f"   API Endpoint: {system_info['api_endpoint']}")
        print(f"   Streamlit URL: {system_info['streamlit_url']}")
        print(f"   Python Version: {system_info['python_version']}")
        print(f"   Platform: {system_info['platform']}")
        
        # Start API server
        api_process = start_api_server()
        if not api_process:
            print("❌ Failed to start API server")
            return
        
        # Start Streamlit app
        streamlit_process = start_streamlit_app()
        if not streamlit_process:
            print("❌ Failed to start Streamlit app")
            api_process.terminate()
            return
        
        # Monitor processes
        monitor_processes(api_process, streamlit_process)
        
        print("\n🎉 System started successfully!")
        print(f"📊 API Server: http://localhost:5000")
        print(f"🎨 Streamlit App: http://localhost:8501")
        print(f"📋 System Info: system_info.json")
        
        # Open browser automatically
        try:
            webbrowser.open('http://localhost:8501')
            print("🌐 Opening Streamlit app in browser...")
        except:
            print("ℹ️  Please manually open: http://localhost:8501")
        
        print("\n🔧 Available Commands:")
        print("   Press Ctrl+C to shutdown gracefully")
        print("   API logs: Check terminal output")
        print("   Streamlit logs: Check terminal output")
        
        # Wait for processes
        try:
            while True:
                time.sleep(1)
                if api_process.poll() is not None or streamlit_process.poll() is not None:
                    break
        except KeyboardInterrupt:
            pass
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
    
    finally:
        # Cleanup
        print("\n🧹 Cleaning up...")
        
        if 'api_process' in locals():
            try:
                api_process.terminate()
                api_process.wait(timeout=5)
            except:
                api_process.kill()
        
        if 'streamlit_process' in locals():
            try:
                streamlit_process.terminate()
                streamlit_process.wait(timeout=5)
            except:
                streamlit_process.kill()
        
        print("✅ Cleanup complete")
        print("👋 Thank you for using Video Sentiment Analysis System!")

if __name__ == "__main__":
    main()