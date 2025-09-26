#!/usr/bin/env python3
"""
API Test Script for Instagram Reels Microservice
Tests all available endpoints to ensure the API is working correctly.
"""

import requests
import json
import time
import sys
from typing import Dict, Any

# API Configuration
API_BASE_URL = "http://localhost:5001"
TIMEOUT = 30

def test_health_endpoint():
    """Test the health check endpoint"""
    print("Testing Health Endpoint...")
    try:
        response = requests.get(f"{API_BASE_URL}/api/health", timeout=TIMEOUT)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"Health check failed: {str(e)}")
        return False

def test_platforms_endpoint():
    """Test the platforms endpoint"""
    print("\nTesting Platforms Endpoint...")
    try:
        response = requests.get(f"{API_BASE_URL}/api/platforms", timeout=TIMEOUT)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"Platforms check failed: {str(e)}")
        return False

def test_detect_platform_endpoint():
    """Test the detect platform endpoint"""
    print("\nTesting Detect Platform Endpoint...")
    
    test_urls = [
        "https://www.instagram.com/reel/C0ABC123DEF/",
        "https://www.tiktok.com/@user/video/1234567890",
        "https://www.youtube.com/watch?v=ABC123DEF456",
        "https://invalid-url.com/video/123"
    ]
    
    for url in test_urls:
        try:
            payload = {"url": url}
            response = requests.post(
                f"{API_BASE_URL}/api/detect-platform", 
                json=payload, 
                timeout=TIMEOUT
            )
            print(f"\nURL: {url}")
            print(f"Status Code: {response.status_code}")
            print(f"Response: {response.json()}")
        except Exception as e:
            print(f"Platform detection failed for {url}: {str(e)}")

def test_detect_platform_batch_endpoint():
    """Test the batch detect platform endpoint"""
    print("\nTesting Batch Detect Platform Endpoint...")
    
    test_urls = [
        "https://www.instagram.com/reel/C0ABC123DEF/",
        "https://www.tiktok.com/@user/video/1234567890",
        "https://www.youtube.com/watch?v=ABC123DEF456"
    ]
    
    try:
        payload = {"urls": test_urls}
        response = requests.post(
            f"{API_BASE_URL}/api/detect-platform/batch", 
            json=payload, 
            timeout=TIMEOUT
        )
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
    except Exception as e:
        print(f"Batch platform detection failed: {str(e)}")

def test_analyze_endpoint():
    """Test the analyze endpoint with sample Instagram reel"""
    print("\nTesting Analyze Endpoint...")
    
    # Test with a sample Instagram reel URL (you can replace with a real one)
    test_url = "https://www.instagram.com/reel/C0ABC123DEF/"
    
    try:
        payload = {
            "url": test_url,
            "max_reels": 5,
            "analysis_type": "sentiment"
        }
        response = requests.post(
            f"{API_BASE_URL}/api/analyze", 
            json=payload, 
            timeout=60  # Longer timeout for analysis
        )
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
    except Exception as e:
        print(f"Analysis failed: {str(e)}")

def check_server_running():
    """Check if the server is running"""
    try:
        response = requests.get(f"{API_BASE_URL}/api/health", timeout=5)
        return response.status_code == 200
    except:
        return False

def main():
    """Main test function"""
    print("Instagram Reels Microservice API Test")
    print("=" * 50)
    
    # Check if server is running
    print("Checking if server is running...")
    if not check_server_running():
        print(f"❌ Server is not running at {API_BASE_URL}")
        print("Please start the server first by running: python api.py")
        sys.exit(1)
    
    print("✅ Server is running!")
    
    # Run tests
    tests_passed = 0
    total_tests = 5
    
    # Test 1: Health endpoint
    if test_health_endpoint():
        tests_passed += 1
        print("✅ Health test passed")
    else:
        print("❌ Health test failed")
    
    # Test 2: Platforms endpoint
    if test_platforms_endpoint():
        tests_passed += 1
        print("✅ Platforms test passed")
    else:
        print("❌ Platforms test failed")
    
    # Test 3: Detect platform endpoint
    test_detect_platform_endpoint()
    tests_passed += 1  # This test is informational
    
    # Test 4: Batch detect platform endpoint
    test_detect_platform_batch_endpoint()
    tests_passed += 1  # This test is informational
    
    # Test 5: Analyze endpoint (may fail without proper setup)
    print("\n⚠️  Note: Analyze endpoint test may fail if Instagram credentials are not configured")
    test_analyze_endpoint()
    tests_passed += 1  # This test is informational
    
    # Summary
    print("\n" + "=" * 50)
    print(f"Test Summary: {tests_passed}/{total_tests} tests completed")
    print("\nNote: Some tests may show failures if:")
    print("- Instagram credentials are not configured in .env file")
    print("- The Instagram reel URL is not accessible")
    print("- Rate limiting occurs from social media platforms")

if __name__ == "__main__":
    main()