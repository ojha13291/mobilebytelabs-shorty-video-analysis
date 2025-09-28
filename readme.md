# Multi-Platform Video Data Fetcher

A powerful, modular microservice for extracting video metadata from multiple social media platforms including YouTube, Instagram, TikTok, and Twitter. Built with Python, this service provides comprehensive video content analysis including title, description, view counts, engagement metrics, and more.

## 📋 Table of Contents

- [🌟 Features](#-features)
- [🏗️ Architecture Overview](#️-architecture-overview)
- [🚀 Quick Start](#-quick-start)
  - [Prerequisites](#prerequisites)
  - [Installation](#installation)
  - [Configuration](#configuration)
  - [Running the Service](#running-the-service)
  - [Verification](#verification)
- [📖 Usage Examples](#-usage-examples)
  - [Python Integration](#python-integration)
  - [Command Line](#command-line)
  - [JavaScript/Node.js](#javascriptnodejs)
- [🔌 API Endpoints](#-api-endpoints)
- [🧪 Testing](#-testing)
- [🐳 Docker Deployment](#-docker-deployment)
- [🔒 Security Considerations](#-security-considerations)
- [🤝 Contributing](#-contributing)
- [📄 License](#-license)

## 🌟 Features

### Multi-Platform Support
- **YouTube**: Video titles, descriptions, view counts, like counts, upload dates
- **Instagram**: Reel metadata, captions, creator info, engagement metrics
- **TikTok**: Video information, creator details, engagement statistics
- **Twitter**: Video metadata from tweets

### Core Capabilities
- **Metadata Extraction**: Title, description, view counts, like counts, upload dates
- **Platform Detection**: Automatic platform detection from URLs
- **Batch Processing**: Fetch metadata for multiple videos simultaneously
- **Error Handling**: Comprehensive error handling with detailed error messages
- **Extensible Architecture**: Easy to add new platforms

### Technical Features
- **Modular Design**: Clean separation of platform-specific fetchers
- **Comprehensive Testing**: Unit tests with mocked HTTP responses
- **Type Safety**: Strong typing with Python type hints
- **Async Support**: Asynchronous processing capabilities
- **Rate Limiting**: Built-in rate limiting and retry mechanisms

## 🏗️ Architecture Overview

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Platform      │    │   Video Data     │    │   Individual    │
│   Resolver      │───▶│   Fetcher        │───▶│   Platform      │
│                 │    │                  │    │   Fetchers      │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                │                        │
                                │                        ▼
                                │                ┌─────────────────┐
                                └────────────────│   Base Fetcher  │
                                                 │   (Abstract)    │
                                                 └─────────────────┘
```

### Platform Fetchers
- **YouTubeFetcher**: Handles YouTube video metadata extraction
- **InstagramFetcher**: Manages Instagram Reel and post metadata
- **TikTokFetcher**: Extracts TikTok video information
- **TwitterFetcher**: Fetches Twitter video metadata

## 🚀 Quick Start

### Prerequisites

- **Python 3.8+** (Python 3.8, 3.9, 3.10, or 3.11)
- **pip** for package management
- **Virtual environment** (recommended)

### Installation

#### 1. Clone the Repository
```bash
git clone https://github.com/yourusername/multi-platform-video-fetcher.git
cd multi-platform-video-fetcher
```

#### 2. Set Up Environment
```bash
# Copy the example environment file
cp .env.example .env

# Edit .env with your configuration (optional)
```

#### 3. Install Dependencies
```bash
# Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install Python dependencies
pip install -r requirements.txt
```

#### 4. Run the Service
```bash
# Start the video data fetcher service
python api.py

# Service will be available at http://localhost:5001
# Health check: http://localhost:5001/health
```

### Verification

Once running, verify your installation:
```bash
# Health check
curl http://localhost:5001/health

# Test with a YouTube video
curl -X POST http://localhost:5001/api/analyze \
  -H "Content-Type: application/json" \
  -d '{"target": "https://www.youtube.com/watch?v=dQw4w9WgXcQ"}'
```

## 📖 Usage Examples

### Python Integration

#### Basic Usage
```python
from video_data_fetcher import fetch_video_metadata

# Fetch metadata for a single video
metadata = fetch_video_metadata('https://www.youtube.com/watch?v=dQw4w9WgXcQ')
print(f"Title: {metadata['title']}")
print(f"Views: {metadata['view_count']}")
print(f"Platform: {metadata['platform']}")
```

#### Batch Processing
```python
from video_data_fetcher import fetch_batch_video_metadata

# Fetch metadata for multiple videos
urls = [
    'https://www.youtube.com/watch?v=dQw4w9WgXcQ',
    'https://www.instagram.com/reel/ABC123DEF/',
    'https://www.tiktok.com/@user/video/1234567890'
]

results = fetch_batch_video_metadata(urls)
for result in results:
    if result['success']:
        print(f"✅ {result['title']} - {result['platform']}")
    else:
        print(f"❌ Error: {result['error']}")
```

#### Advanced Usage with Custom Fetcher
```python
from video_data_fetcher import VideoDataFetcher

# Create fetcher with custom timeout
fetcher = VideoDataFetcher(timeout=60)

# Get supported platforms
platforms = fetcher.get_supported_platforms()
print(f"Supported platforms: {platforms}")

# Fetch with custom settings
metadata = fetcher.fetch_metadata('https://www.youtube.com/watch?v=dQw4w9WgXcQ')
```

### Command Line Examples

#### Using curl
```bash
# YouTube video analysis
curl -X POST http://localhost:5001/api/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "target": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
    "include_analysis": true
  }'

# Instagram Reel analysis
curl -X POST http://localhost:5001/api/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "target": "https://www.instagram.com/reel/ABC123DEF/",
    "include_analysis": true
  }'
```

### JavaScript/Node.js Integration

```javascript
const axios = require('axios');

class VideoDataFetcher {
    constructor(baseUrl = 'http://localhost:5001') {
        this.baseUrl = baseUrl;
    }

    async fetchMetadata(url) {
        try {
            const response = await axios.post(`${this.baseUrl}/api/analyze`, {
                target: url,
                include_analysis: true
            });
            
            return response.data;
        } catch (error) {
            console.error('❌ Fetch failed:', error.response?.data || error.message);
            throw error;
        }
    }

    async fetchBatchMetadata(urls) {
        const results = [];
        for (const url of urls) {
            try {
                const result = await this.fetchMetadata(url);
                results.push(result);
            } catch (error) {
                results.push({ error: error.message, url, success: false });
            }
        }
        return results;
    }
}

// Usage example
const fetcher = new VideoDataFetcher();

fetcher.fetchMetadata('https://www.youtube.com/watch?v=dQw4w9WgXcQ')
    .then(result => {
        console.log('📊 Video Metadata:');
        console.log(`Title: ${result.results[0].title}`);
        console.log(`Platform: ${result.results[0].platform}`);
        console.log(`Views: ${result.results[0].view_count}`);
    })
    .catch(err => console.error('Failed:', err));
```

## 🔌 API Endpoints

### Health Check
```
GET /health
```
Returns the status of the service.

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
```
POST /api/analyze
```
Analyzes a video from any supported platform.

**Request Body:**
```json
{
  "target": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
  "include_analysis": true,
  "max_reels": 1
}
```

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
```
GET /api/metrics
```
Returns service performance metrics.

### Configuration
```
GET /api/config
```
Returns current service configuration.

## 🧪 Testing

### Run All Tests
```bash
# Run all tests
python -m pytest tests/ -v

# Run with coverage
python -m pytest tests/ --cov=video_data_fetcher --cov-report=html

# Run specific test file
python -m pytest tests/test_video_data_fetcher.py -v
```

### Test Coverage
The project includes comprehensive unit tests for:
- Platform detection and resolution
- Individual platform fetchers (YouTube, Instagram, TikTok, Twitter)
- Error handling and edge cases
- Batch processing functionality
- Mock HTTP responses for reliable testing

## 🐳 Docker Deployment

### Basic Deployment
```bash
# Build the Docker image
docker build -t multi-platform-video-fetcher .

# Run the container
docker run -d \
  --name video-fetcher \
  -p 5001:5001 \
  multi-platform-video-fetcher
```

### Docker Compose
```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

## 🔒 Security Considerations

### Input Validation
- All URLs are validated before processing
- Input sanitization to prevent injection attacks
- Rate limiting to prevent abuse

### External Dependencies
- Secure handling of API keys and credentials
- Environment variable configuration for sensitive data
- No hardcoded secrets in the codebase

### Network Security
- HTTPS enforcement in production
- CORS configuration for cross-origin requests
- Request timeout configurations

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

### Development Setup
```bash
# Install development dependencies
pip install -r requirements.txt
pip install pytest pytest-cov black flake8

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

- **Sentence Transformers** for AI-powered text analysis
- **Flask** for the web framework
- **Requests** for HTTP client functionality
- **BeautifulSoup** for HTML parsing
- **pytest** for testing framework
