# Multi-Platform Video Data Fetcher API

A comprehensive REST API for extracting video metadata from multiple social media platforms including YouTube, Instagram, TikTok, and Twitter.

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- pip package manager
- Virtual environment (recommended)

### Installation
```bash
# Clone the repository
git clone https://github.com/yourusername/multi-platform-video-fetcher.git
cd multi-platform-video-fetcher

# Install dependencies
pip install -r requirements.txt

# Start the service
python api.py
```

The API will be available at `http://localhost:5001`

## 📋 API Endpoints

### Health Check
Check if the service is running and healthy.

**Endpoint:** `GET /health`

**Response:**
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "timestamp": "2024-01-15T12:34:56.789012",
  "services": {
    "api": "healthy",
    "scraper": "healthy",
    "analyzer": "healthy"
  },
  "uptime": 3600.5
}
```

### Analyze Video
Extract metadata from a video URL from any supported platform.

**Endpoint:** `POST /api/analyze`

**Request Body:**
```json
{
  "target": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
  "include_analysis": true,
  "max_reels": 1
}
```

**Parameters:**
- `target` (string, required): The video URL to analyze
- `include_analysis` (boolean, optional): Include AI-powered analysis (default: false)
- `max_reels` (integer, optional): Maximum number of reels to analyze (default: 1)

**Response:**
```json
{
  "status": "success",
  "count": 1,
  "results": [
    {
      "title": "Rick Astley - Never Gonna Give You Up (Official Video)",
      "description": "The official video for Rick Astley's 1987 hit...",
      "platform": "youtube",
      "view_count": 1200000000,
      "like_count": 8900000,
      "upload_date": "2009-10-24",
      "duration": "213",
      "thumbnail_url": "https://i.ytimg.com/vi/dQw4w9WgXcQ/maxresdefault.jpg",
      "success": true
    }
  ],
  "processing_time": 2.5,
  "errors": []
}
```

### Service Metrics
Get performance metrics and usage statistics.

**Endpoint:** `GET /api/metrics`

**Response:**
```json
{
  "total_requests": 150,
  "successful_requests": 145,
  "failed_requests": 5,
  "average_processing_time": 8.5,
  "last_request_time": "2024-01-15T12:34:56",
  "uptime_seconds": 7200,
  "success_rate": 96.67
}
```

### Configuration
Get current service configuration (sanitized for security).

**Endpoint:** `GET /api/config`

**Response:**
```json
{
  "service": {
    "host": "0.0.0.0",
    "port": 5001,
    "debug": false,
    "max_reels_default": 10
  },
  "platforms": {
    "supported": ["youtube", "instagram", "tiktok", "twitter"],
    "enabled": ["youtube", "instagram", "tiktok", "twitter"]
  }
}
```

## 🔧 Configuration

### Environment Variables

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `SERVICE_HOST` | Service host address | 0.0.0.0 | No |
| `SERVICE_PORT` | Service port | 5001 | No |
| `DEBUG` | Debug mode | false | No |
| `MAX_REELS_DEFAULT` | Default max reels | 10 | No |

### Supported Platforms

The API supports the following platforms:
- **YouTube**: Video titles, descriptions, view counts, like counts, upload dates
- **Instagram**: Reel metadata, captions, creator info, engagement metrics
- **TikTok**: Video information, creator details, engagement statistics
- **Twitter**: Video metadata from tweets

## 📊 Response Formats

### Successful Response
```json
{
  "status": "success",
  "count": 1,
  "results": [
    {
      "title": "Video Title",
      "description": "Video description...",
      "platform": "youtube",
      "view_count": 1000000,
      "like_count": 50000,
      "upload_date": "2024-01-15",
      "duration": "180",
      "thumbnail_url": "https://example.com/thumbnail.jpg",
      "creator": {
        "username": "creator_name",
        "profile_url": "https://example.com/creator",
        "subscriber_count": 100000
      },
      "success": true
    }
  ],
  "processing_time": 1.5,
  "errors": []
}
```

### Error Response
```json
{
  "status": "error",
  "error": "Invalid URL format",
  "code": "INVALID_URL",
  "details": "URL must be a valid video link from supported platforms",
  "timestamp": "2024-01-15T12:34:56.789Z",
  "request_id": "req_abc123"
}
```

## 🚨 Error Codes

| Code | Description | Solution |
|------|-------------|----------|
| `INVALID_URL` | Malformed or unsupported URL | Check URL format and platform support |
| `CONTENT_NOT_FOUND` | Video not found or unavailable | Verify video exists and is public |
| `PLATFORM_ERROR` | Platform-specific error | Check platform status and retry |
| `RATE_LIMIT_EXCEEDED` | Too many requests | Wait before retrying |
| `NETWORK_ERROR` | Connection issues | Check internet connectivity |
| `CONFIGURATION_ERROR` | Service configuration issue | Check environment variables |

## 💡 Usage Examples

### cURL Examples

#### Analyze YouTube Video
```bash
curl -X POST http://localhost:5001/api/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "target": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
    "include_analysis": true
  }'
```

#### Analyze Instagram Reel
```bash
curl -X POST http://localhost:5001/api/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "target": "https://www.instagram.com/reel/ABC123DEF/",
    "include_analysis": true
  }'
```

#### Check Service Health
```bash
curl http://localhost:5001/health
```

### Python Examples

#### Basic Usage
```python
import requests
import json

# API base URL
BASE_URL = "http://localhost:5001"

def analyze_video(url, include_analysis=False):
    """Analyze a video and return metadata"""
    
    payload = {
        "target": url,
        "include_analysis": include_analysis
    }
    
    response = requests.post(f"{BASE_URL}/api/analyze", json=payload)
    
    if response.status_code == 200:
        data = response.json()
        if data["status"] == "success" and data["results"]:
            return data["results"][0]
        else:
            raise Exception(f"Analysis failed: {data.get('error', 'Unknown error')}")
    else:
        raise Exception(f"HTTP {response.status_code}: {response.text}")

# Example usage
video_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
try:
    metadata = analyze_video(video_url, include_analysis=True)
    print(f"Title: {metadata['title']}")
    print(f"Platform: {metadata['platform']}")
    print(f"Views: {metadata.get('view_count', 'N/A')}")
    print(f"Likes: {metadata.get('like_count', 'N/A')}")
except Exception as e:
    print(f"Error: {e}")
```

#### Batch Processing
```python
def analyze_multiple_videos(urls):
    """Analyze multiple videos"""
    results = []
    
    for url in urls:
        try:
            metadata = analyze_video(url)
            results.append({
                "url": url,
                "success": True,
                "data": metadata
            })
        except Exception as e:
            results.append({
                "url": url,
                "success": False,
                "error": str(e)
            })
    
    return results

# Batch processing example
urls = [
    "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
    "https://www.instagram.com/reel/ABC123DEF/",
    "https://www.tiktok.com/@user/video/1234567890"
]

results = analyze_multiple_videos(urls)
for result in results:
    if result["success"]:
        print(f"✅ {result['data']['title']} - {result['data']['platform']}")
    else:
        print(f"❌ Failed: {result['error']}")
```

### JavaScript/Node.js Examples

```javascript
const axios = require('axios');

class VideoDataFetcher {
    constructor(baseUrl = 'http://localhost:5001') {
        this.baseUrl = baseUrl;
    }

    async analyzeVideo(url, includeAnalysis = false) {
        try {
            const response = await axios.post(`${this.baseUrl}/api/analyze`, {
                target: url,
                include_analysis: includeAnalysis
            });
            
            const data = response.data;
            if (data.status === 'success' && data.results && data.results.length > 0) {
                return data.results[0];
            } else {
                throw new Error(`Analysis failed: ${data.error || 'Unknown error'}`);
            }
        } catch (error) {
            if (error.response) {
                throw new Error(`HTTP ${error.response.status}: ${JSON.stringify(error.response.data)}`);
            } else {
                throw error;
            }
        }
    }

    async getHealth() {
        try {
            const response = await axios.get(`${this.baseUrl}/health`);
            return response.data;
        } catch (error) {
            throw new Error(`Health check failed: ${error.message}`);
        }
    }
}

// Usage example
const fetcher = new VideoDataFetcher();

async function main() {
    try {
        // Check service health
        const health = await fetcher.getHealth();
        console.log('Service status:', health.status);

        // Analyze a video
        const metadata = await fetcher.analyzeVideo(
            'https://www.youtube.com/watch?v=dQw4w9WgXcQ',
            true
        );
        
        console.log('Video metadata:');
        console.log(`Title: ${metadata.title}`);
        console.log(`Platform: ${metadata.platform}`);
        console.log(`Views: ${metadata.view_count || 'N/A'}`);
        console.log(`Likes: ${metadata.like_count || 'N/A'}`);
        
    } catch (error) {
        console.error('Error:', error.message);
    }
}

main();
```

## 🐳 Docker Usage

### Basic Docker Run
```bash
docker run -d \
  --name video-fetcher \
  -p 5001:5001 \
  multi-platform-video-fetcher:latest
```

### Docker Compose
```yaml
version: '3.8'

services:
  video-fetcher:
    image: multi-platform-video-fetcher:latest
    ports:
      - "5001:5001"
    environment:
      - SERVICE_HOST=0.0.0.0
      - SERVICE_PORT=5001
      - DEBUG=false
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:5001/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
```

## 🔒 Security Considerations

- Input validation for all URLs
- Rate limiting to prevent abuse
- No storage of sensitive data
- HTTPS enforcement in production
- CORS configuration for cross-origin requests

## 📈 Rate Limiting

The API implements rate limiting to prevent abuse:
- **General requests**: 100 requests per minute per IP
- **Analysis requests**: 20 requests per minute per IP
- **Batch requests**: 5 requests per minute per IP

## 🧪 Testing

### Run Tests
```bash
# Run all tests
python -m pytest tests/ -v

# Run with coverage
python -m pytest tests/ --cov=video_data_fetcher --cov-report=html

# Run specific test file
python -m pytest tests/test_video_data_fetcher.py -v
```

### Load Testing
```bash
# Using curl for basic load testing
for i in {1..10}; do
  curl -X POST http://localhost:5001/api/analyze \
    -H "Content-Type: application/json" \
    -d '{"target": "https://www.youtube.com/watch?v=dQw4w9WgXcQ"}' &
done
wait
```

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

### Development Setup
```bash
# Install development dependencies
pip install -r requirements.txt
pip install pytest pytest-cov black flake8 mypy

# Run tests before committing
python -m pytest tests/ -v

# Format code
black video_data_fetcher/ tests/

# Check code style
flake8 video_data_fetcher/ tests/
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Flask** for the web framework
- **Requests** for HTTP client functionality
- **BeautifulSoup** for HTML parsing
- **pytest** for testing framework
- The open-source community for excellent libraries and tools