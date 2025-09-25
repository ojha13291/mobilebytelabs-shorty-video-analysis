# Shorty Video Analysis

A powerful, modular microservice for analyzing short-form video content from Instagram Reels with AI-powered insights. Built with Python Flask, this service provides comprehensive video content analysis including sentiment analysis, categorization, and engagement metrics to help creators and businesses understand their video performance and audience engagement.

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
  - [Advanced Analytics](#advanced-analytics)
- [🔌 API Endpoints](#-api-endpoints)
  - [Health Check](#health-check)
  - [Video Analysis](#video-analysis)
  - [Service Metrics](#service-metrics)
  - [Configuration](#configuration)
- [🐳 Docker Deployment](#-docker-deployment)
  - [Basic Deployment](#basic-deployment)
  - [Production Deployment](#production-deployment)
  - [Kubernetes](#kubernetes-deployment)
- [📊 Monitoring & Observability](#-monitoring--observability)
- [🔒 Security Considerations](#-security-considerations)
- [🐛 Error Handling](#-error-handling)
- [🤝 Contributing](#-contributing)
- [📚 Additional Resources](#-additional-resources)
- [📄 License](#-license)
- [🙏 Acknowledgments](#-acknowledgments)


**Target Examples:**
- `"@natgeo"` - Analyze reels from National Geographic
- `"#travel"` - Analyze reels with #travel hashtag
- `"https://instagram.com/reel/ABC123DEF/"` - Analyze specific reel

**Response:**
```json
{
  "status": "success",
  "count": 5,
  "results": [
    {
      "reel_id": "CxYZ123ABC",
      "reel_url": "https://www.instagram.com/reel/CxYZ123ABC/",
      "caption": "Amazing sunset timelapse 🌅 #sunset #photography",
      "creator": {
        "username": "photographer_jane",
        "followers_count": 15420,
        "following_count": 342
      },
      "views": 1234,
      "likes": 567,
      "comments_count": 45,
      "posted_at": "2024-01-15T15:30:45.123456",
      "hashtags": ["#sunset", "#photography"],
      "analysis": {
        "summary": "A stunning timelapse video of a sunset with vibrant colors.",
        "category": ["Photography", "Nature", "Art"],
        "sentiment": "Positive",
        "keywords": ["sunset", "timelapse", "photography", "nature"]
      }
    }
  ],
  "processing_time": 8.5
}
```

### 📈 Service Metrics
```
GET /api/metrics
```
Returns Shorty Video Analysis service performance metrics and usage statistics.

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

### ⚙️ Configuration
```
GET /api/config
```
Returns current service configuration (sanitized for security).

**Response:**
```json
{
  "service": {
    "host": "0.0.0.0",
    "port": 5001,
    "debug": false,
    "max_reels_default": 10
  },
  "instagram": {
    "use_login": true,
    "scraping_method": "instaloader"
  },
  "ai": {
    "model": "mistral",
    "enabled": true
  }
}
```

## 🛠️ Quick Start

### Prerequisites

- **Python 3.8+** (Python 3.8, 3.9, 3.10, or 3.11)
- **Mistral AI API key** (sign up at [Mistral AI](https://mistral.ai/))
- **Instagram credentials** (optional, for enhanced scraping)
- **Docker** (optional, for containerized deployment)

### 🚀 Installation Steps

#### 1. Clone the Repository
```bash
git clone https://github.com/yourusername/shorty-video-analysis.git
cd shorty-video-analysis
```

#### 2. Set Up Environment
```bash
# Copy the example environment file
cp .env.example .env

# Edit .env with your configuration
# Required: Add your Mistral AI API key
# Optional: Add Instagram credentials for enhanced access
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
# Start the Shorty Video Analysis service
python main.py

# Service will be available at http://localhost:5001
# Health check: http://localhost:5001/health
```

### 🐳 Docker Deployment (Alternative)

#### Option A: Docker Build
```bash
# Build the Docker image
docker build -t shorty-video-analysis .

# Run with environment file
docker run -p 5001:5001 --env-file .env shorty-video-analysis
```

#### Option B: Docker Compose
```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

### ✅ Verification

Once running, verify your installation:
```bash
# Health check
curl http://localhost:5001/health

# Expected response:
{
  "status": "healthy",
  "version": "1.0.0",
  "services": {
    "api": "healthy",
    "scraper": "healthy",
    "analyzer": "healthy"
  }
}
```

## 📊 Response Format

### Successful Analysis Response
```json
{
  "status": "success",
  "count": 2,
  "results": [
    {
      "reel_id": "CxYZ123ABC",
      "reel_url": "https://www.instagram.com/reel/CxYZ123ABC/",
      "video_url": "https://instagram.fxyz.com/v/t50.12345-16/123456_789.mp4",
      "caption": "Amazing sunset timelapse 🌅 #sunset #photography",
      "creator": {
        "username": "photographer_jane",
        "profile_url": "https://www.instagram.com/photographer_jane/",
        "full_name": "Jane Doe",
        "followers_count": 15420,
        "following_count": 342
      },
      "likes": 1234,
      "views": 5678,
      "comments_count": 45,
      "posted_at": "2024-01-15T15:30:45.123456",
      "hashtags": ["#sunset", "#photography"],
      "mentions": [],
      "top_comments": [
        {
          "user": "user123",
          "comment": "Beautiful shot! 😍",
          "timestamp": "2024-01-15T16:00:00",
          "likes": 12
        }
      ],
      "analysis": {
        "summary": "A stunning timelapse video of a sunset with vibrant colors and smooth transitions.",
        "category": ["Photography", "Nature", "Art"],
        "sentiment": "Positive",
        "top_comment_summary": "Viewers are impressed by the beauty and quality of the sunset footage.",
        "keywords": ["sunset", "timelapse", "photography", "nature", "colors"]
      },
      "embeddings": [0.123, 0.456, 0.789, ...]
    }
  ],
  "processing_time": 8.5,
  "errors": []
}
```

## 🔧 Configuration

### Environment Variables

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `MISTRAL_API_KEY` | Mistral AI API key | None | Yes |
| `INSTAGRAM_USERNAME` | Instagram username | None | No |
| `INSTAGRAM_PASSWORD` | Instagram password | None | No |
| `SERVICE_HOST` | Service host | 0.0.0.0 | No |
| `SERVICE_PORT` | Service port | 5001 | No |
| `MAX_REELS_DEFAULT` | Default max reels | 10 | No |
| `DEBUG` | Debug mode | false | No |

### Scraping Methods

**Instaloader (Recommended):**
- Faster and more reliable
- Better error handling
- Supports batch operations
- Requires Instagram credentials for full access

**Selenium:**
- Browser-based scraping
- Good for edge cases
- Slower but more flexible
- Useful when Instaloader fails

## 🧪 Usage Examples

### Basic Video Analysis

#### Analyze Instagram Profile Reels
```python
import requests

# Configure API endpoint
API_URL = "http://localhost:5001"

def analyze_creator_profile(username, max_reels=5):
    """Analyze reels from an Instagram creator profile"""
    
    payload = {
        "target": f"@{username}",
        "max_reels": max_reels,
        "use_login": True,
        "scraping_method": "instaloader",
        "include_analysis": True,
        "include_comments": True
    }
    
    response = requests.post(f"{API_URL}/api/analyze", json=payload)
    
    if response.status_code == 200:
        data = response.json()
        print(f"📊 Analyzed {data['count']} reels from @{username}")
        
        for reel in data['results']:
            print(f"\n🎬 Reel: {reel['reel_id']}")
            print(f"👀 Views: {reel['views']:,}")
            print(f"❤️  Likes: {reel['likes']:,}")
            print(f"💬 Comments: {reel['comments_count']:,}")
            
            if reel['analysis']:
                print(f"🏷️  Categories: {', '.join(reel['analysis']['category'])}")
                print(f"📝 Summary: {reel['analysis']['summary']}")
                print(f"😊 Sentiment: {reel['analysis']['sentiment']}")
    else:
        print(f"❌ Error: {response.json()}")

# Example usage
analyze_creator_profile("natgeo", max_reels=3)
```

#### Analyze Hashtag Performance
```python
def analyze_hashtag_performance(hashtag, max_reels=10):
    """Analyze performance of reels with specific hashtag"""
    
    payload = {
        "target": f"#{hashtag}",
        "max_reels": max_reels,
        "include_analysis": True,
        "scraping_method": "instaloader"
    }
    
    response = requests.post(f"{API_URL}/api/analyze", json=payload)
    
    if response.status_code == 200:
        data = response.json()
        reels = data['results']
        
        # Calculate average engagement
        total_views = sum(reel['views'] for reel in reels)
        total_likes = sum(reel['likes'] for reel in reels)
        avg_engagement = (total_likes / total_views * 100) if total_views > 0 else 0
        
        print(f"📈 Hashtag Analysis: #{hashtag}")
        print(f"🎥 Total Reels: {len(reels)}")
        print(f"👀 Total Views: {total_views:,}")
        print(f"❤️  Total Likes: {total_likes:,}")
        print(f"📊 Avg Engagement: {avg_engagement:.1f}%")
        
        # Show top performing reel
        if reels:
            top_reel = max(reels, key=lambda x: x['views'])
            print(f"🏆 Top Reel: {top_reel['views']:,} views")
            print(f"📝 Caption: {top_reel['caption'][:100]}...")

# Example usage
analyze_hashtag_performance("travel", max_reels=15)
```

### Command Line Examples

#### Basic cURL Request
```bash
# Analyze a creator's recent reels
curl -X POST http://localhost:5001/api/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "target": "@natgeo",
    "max_reels": 5,
    "include_analysis": true,
    "include_comments": true
  }'
```

#### Analyze Trending Hashtag
```bash
# Analyze trending travel content
curl -X POST http://localhost:5001/api/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "target": "#travel2024",
    "max_reels": 10,
    "scraping_method": "instaloader"
  }'
```

#### Get Service Metrics
```bash
# Check service performance
curl http://localhost:5001/api/metrics
```

### JavaScript/Node.js Integration

```javascript
const axios = require('axios');

class ShortyVideoAnalyzer {
    constructor(baseUrl = 'http://localhost:5001') {
        this.baseUrl = baseUrl;
    }

    async analyzeProfile(username, maxReels = 10) {
        try {
            const response = await axios.post(`${this.baseUrl}/api/analyze`, {
                target: `@${username}`,
                max_reels: maxReels,
                include_analysis: true,
                include_comments: true
            });
            
            const data = response.data;
            console.log(`📊 Analyzed ${data.count} reels from @${username}`);
            
            return data.results.map(reel => ({
                id: reel.reel_id,
                views: reel.views,
                likes: reel.likes,
                comments: reel.comments_count,
                engagement: ((reel.likes / reel.views) * 100).toFixed(1),
                summary: reel.analysis?.summary,
                sentiment: reel.analysis?.sentiment,
                categories: reel.analysis?.category
            }));
            
        } catch (error) {
            console.error('❌ Analysis failed:', error.response?.data || error.message);
            throw error;
        }
    }

    async getMetrics() {
        try {
            const response = await axios.get(`${this.baseUrl}/api/metrics`);
            return response.data;
        } catch (error) {
            console.error('❌ Failed to get metrics:', error.message);
            throw error;
        }
    }
}

// Usage example
const analyzer = new ShortyVideoAnalyzer();

analyzer.analyzeProfile('instagram', 5)
    .then(results => {
        console.log('📈 Analysis Results:');
        results.forEach(reel => {
            console.log(`🎬 ${reel.id}: ${reel.views} views, ${reel.engagement}% engagement`);
        });
    })
    .catch(err => console.error('Failed:', err));
```

### Advanced Analytics Example

```python
def comprehensive_analysis(username, max_reels=20):
    """Perform comprehensive video analysis with insights"""
    
    payload = {
        "target": f"@{username}",
        "max_reels": max_reels,
        "include_analysis": True,
        "include_comments": True
    }
    
    response = requests.post(f"{API_URL}/api/analyze", json=payload)
    
    if response.status_code == 200:
        data = response.json()
        reels = data['results']
        
        # Performance metrics
        total_views = sum(reel['views'] for reel in reels)
        total_likes = sum(reel['likes'] for reel in reels)
        total_comments = sum(reel['comments_count'] for reel in reels)
        
        # Content analysis
        categories = {}
        sentiments = {'Positive': 0, 'Neutral': 0, 'Negative': 0}
        
        for reel in reels:
            # Count categories
            for cat in reel['analysis']['category']:
                categories[cat] = categories.get(cat, 0) + 1
            
            # Count sentiments
            sentiment = reel['analysis']['sentiment']
            if sentiment in sentiments:
                sentiments[sentiment] += 1
        
        print(f"📊 Comprehensive Analysis for @{username}")
        print(f"🎥 Total Reels Analyzed: {len(reels)}")
        print(f"👀 Total Views: {total_views:,}")
        print(f"❤️  Total Likes: {total_likes:,}")
        print(f"💬 Total Comments: {total_comments:,}")
        print(f"📊 Average Engagement: {(total_likes/total_views*100):.1f}%")
        print(f"\n🏷️  Top Categories:")
        for cat, count in sorted(categories.items(), key=lambda x: x[1], reverse=True)[:5]:
            print(f"   {cat}: {count} reels")
        print(f"\n😊 Sentiment Distribution:")
        for sentiment, count in sentiments.items():
            print(f"   {sentiment}: {count} reels")

# Run comprehensive analysis
comprehensive_analysis("natgeo", max_reels=15)
```

## 🐳 Docker Deployment Options

### Basic Deployment
```bash
docker run -d \
  --name shorty-video-analysis \
  -p 5001:5001 \
  -e MISTRAL_API_KEY=your_api_key \
  -e INSTAGRAM_USERNAME=your_username \
  -e INSTAGRAM_PASSWORD=your_password \
  shorty-video-analysis
```

### Production Deployment with Docker Compose
```bash
# Create production environment file
cp .env.example .env.production
# Edit .env.production with production values

# Start production services
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

### Kubernetes Deployment
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: shorty-video-analysis
spec:
  replicas: 3
  selector:
    matchLabels:
      app: shorty-video-analysis
  template:
    metadata:
      labels:
        app: shorty-video-analysis
    spec:
      containers:
      - name: shorty-video-analysis
        image: shorty-video-analysis:latest
        ports:
        - containerPort: 5001
        env:
        - name: MISTRAL_API_KEY
          valueFrom:
            secretKeyRef:
              name: mistral-secret
              key: api-key
        resources:
          requests:
            memory: "512Mi"
            cpu: "250m"
          limits:
            memory: "1Gi"
            cpu: "500m"
---
apiVersion: v1
kind: Service
metadata:
  name: shorty-video-analysis-service
spec:
  selector:
    app: shorty-video-analysis
  ports:
  - protocol: TCP
    port: 80
    targetPort: 5001
  type: LoadBalancer
```

## 📊 Monitoring & Observability

### Built-in Metrics
Shorty Video Analysis exposes comprehensive metrics at `/api/metrics`:
- **Request Metrics**: Count, latency, and status codes
- **Analysis Performance**: AI processing time and success rates
- **Content Processing**: Video analysis throughput
- **Error Tracking**: Detailed error categorization and rates

### Health Checks
- **Liveness**: `/health` endpoint for service availability
- **Readiness**: Validates AI service and external dependencies
- **Startup**: Configuration and environment validation

### Structured Logging
All logs include correlation IDs for request tracking:
```json
{
  "timestamp": "2024-01-15T10:30:00Z",
  "level": "INFO",
  "correlation_id": "abc123",
  "service": "shorty-video-analysis",
  "message": "Successfully analyzed short-form video",
  "video_id": "ABC123",
  "platform": "instagram",
  "analysis_time_ms": 1250,
  "ai_confidence": 0.85
}
```

### Performance Monitoring
- **Response Time**: Track API latency by endpoint
- **Resource Usage**: Memory, CPU, and disk utilization
- **Queue Health**: Monitor processing backlog
- **Alert Thresholds**: Configurable alerts for key metrics

## 🔒 Security Considerations

### API Key Management
- **Environment Variables**: Store all API keys in environment variables
- **Secrets Management**: Use Docker secrets or cloud key management in production
- **Key Rotation**: Regular rotation of Mistral AI and Instagram API keys
- **Usage Monitoring**: Track API usage and set up alerts for anomalies

### Rate Limiting & Throttling
- **Instagram API**: Respect platform rate limits and implement backoff strategies
- **AI Service**: Manage Mistral AI API quotas efficiently
- **Request Throttling**: Implement per-client rate limiting
- **Circuit Breakers**: Prevent cascade failures with circuit breaker patterns

### Data Protection
- **No Persistent Storage**: Shorty Video Analysis doesn't store user data by default
- **Log Sanitization**: Remove sensitive information from logs
- **HTTPS Enforcement**: All production traffic uses encrypted connections
- **Input Validation**: Comprehensive validation of all user inputs

### Network Security
- **VPN Support**: Optional VPN configuration for Instagram access
- **IP Whitelisting**: Restrict access to trusted IP ranges
- **Activity Monitoring**: Real-time monitoring for suspicious patterns
- **Secure Channels**: All external communications use secure protocols

## 🐛 Error Handling

### Error Response Format
All errors follow a consistent format for easy handling:
```json
{
  "error": "Brief error description",
  "code": "ERROR_CODE",
  "details": "Detailed explanation",
  "timestamp": "2024-01-15T12:34:56.789Z",
  "request_id": "req_abc123",
  "help_url": "https://github.com/yourusername/shorty-video-analysis/wiki/Error-Codes"
}
```

### Common Error Scenarios

#### Invalid Instagram URL
```json
{
  "error": "Invalid Instagram URL format",
  "code": "INVALID_URL",
  "details": "URL must be a valid Instagram reel or profile link",
  "example": "https://www.instagram.com/reel/ABC123DEF/",
  "timestamp": "2024-01-15T12:34:56.789Z",
  "request_id": "req_xyz789"
}
```

#### AI Service Unavailable
```json
{
  "error": "AI analysis service temporarily unavailable",
  "code": "AI_SERVICE_ERROR",
  "details": "Mistral AI service is experiencing issues. Please retry in 60 seconds",
  "retry_after": 60,
  "timestamp": "2024-01-15T12:34:56.789Z",
  "request_id": "req_abc123"
}
```

#### Rate Limiting
```json
{
  "error": "Rate limit exceeded",
  "code": "RATE_LIMIT_EXCEEDED",
  "details": "Too many requests. Please slow down your request rate",
  "retry_after": 300,
  "limit_type": "instagram_api",
  "timestamp": "2024-01-15T12:34:56.789Z",
  "request_id": "req_def456"
}
```

### Error Code Reference

| Code | Description | Solution |
|------|-------------|----------|
| `INVALID_URL` | Malformed Instagram URL | Check URL format and try again |
| `CONTENT_NOT_FOUND` | Reel/profile not found | Verify content exists and is public |
| `AI_SERVICE_ERROR` | Mistral AI issues | Retry after suggested delay |
| `RATE_LIMIT_EXCEEDED` | Too many requests | Wait before retrying |
| `AUTHENTICATION_ERROR` | Instagram login failed | Check credentials and try again |
| `CONFIGURATION_ERROR` | Missing environment vars | Verify all required config is set |
| `NETWORK_ERROR` | Connection issues | Check internet connectivity |
| `VALIDATION_ERROR` | Invalid input parameters | Review API documentation |

### Troubleshooting Guide

#### Service Won't Start
1. Check Python version (3.8+ required)
2. Verify all dependencies installed
3. Check environment variables are set
4. Review logs for specific errors

#### Instagram Scraping Fails
1. Verify Instagram credentials are correct
2. Check if account has 2FA enabled
3. Ensure account isn't rate-limited
4. Try different Instagram account

#### AI Analysis Returns Poor Results
1. Check Mistral API key is valid
2. Verify API quota hasn't been exceeded
3. Try with different video content
4. Check network connectivity to AI service

## 🤝 Contributing

We welcome contributions to Shorty Video Analysis! Whether you're fixing bugs, adding features, or improving documentation, your help is appreciated.

<<<<<<< Updated upstream
### 🚀 Quick Contributing Guide
=======
### GitHub Templates

We provide several GitHub templates to help streamline contributions:

- **🐛 [Bug Report](https://github.com/yourusername/instagram-reels-microservice/issues/new?template=bug_report.md)** - Report bugs and issues
- **✨ [Feature Request](https://github.com/yourusername/instagram-reels-microservice/issues/new?template=feature_request.md)** - Suggest new features
- **🌐 [Platform Support Request](https://github.com/yourusername/instagram-reels-microservice/issues/new?template=platform_support_request.md)** - Request support for new social media platforms
- **🔧 [API Issue](https://github.com/yourusername/instagram-reels-microservice/issues/new?template=api_issue.md)** - Report API-specific issues
- **📚 [Documentation Issue](https://github.com/yourusername/instagram-reels-microservice/issues/new?template=documentation_issue.md)** - Report documentation problems

When submitting pull requests, please use our [Pull Request Template](https://github.com/yourusername/instagram-reels-microservice/blob/main/.github/pull_request_template.md) to ensure all necessary information is included.

### Development Setup
>>>>>>> Stashed changes

#### 1. Fork and Clone
```bash
# Fork the repository on GitHub, then clone your fork
git clone https://github.com/yourusername/shorty-video-analysis.git
cd shorty-video-analysis
```

#### 2. Set Up Development Environment
```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install development dependencies
pip install -r requirements.txt
pip install -e .[dev]
```

#### 3. Create Feature Branch
```bash
git checkout -b feature/your-feature-name
# or
git checkout -b fix/issue-description
```

#### 4. Make Your Changes
- Write clean, well-documented code
- Add tests for new features
- Update documentation as needed
- Follow existing code style and patterns

#### 5. Test Your Changes
```bash
# Run the test suite
pytest tests/ -v

# Run linting
black src/
flake8 src/
mypy src/

# Test the service locally
python main.py
```

#### 6. Submit Pull Request
```bash
# Commit your changes
git add .
git commit -m "feat: add your feature description"

# Push to your fork
git push origin feature/your-feature-name

# Create Pull Request on GitHub
```

### 📋 Pull Request Guidelines

- **Clear Title**: Describe what your PR does
- **Detailed Description**: Explain the changes and why they're needed
- **Tests**: Include tests for new functionality
- **Documentation**: Update README/docs if needed
- **No Breaking Changes**: Or clearly document them

### 🐛 Reporting Issues

When reporting bugs or requesting features:

1. **Search existing issues** first
2. **Use issue templates** when available
3. **Provide clear reproduction steps** for bugs
4. **Include environment details** (OS, Python version, etc.)
5. **Add relevant code examples** or error logs

### 🎯 Areas for Contribution

- **Performance improvements**: Faster analysis, better caching
- **New features**: Support for other platforms, advanced analytics
- **Documentation**: Tutorials, examples, API docs
- **Testing**: More comprehensive test coverage
- **Bug fixes**: Help squash existing issues

### 📞 Getting Help

- **GitHub Issues**: For bug reports and feature requests
- **GitHub Discussions**: For questions and general discussion
- **Code Review**: All PRs get reviewed by maintainers

### 📄 Code of Conduct

Please note that this project follows a Code of Conduct. By participating, you agree to uphold this code:

- Be respectful and inclusive
- Welcome newcomers
- Focus on constructive feedback
- Respect different viewpoints and experiences

## 📚 Additional Resources

### 📖 Documentation
- [API Reference](https://github.com/yourusername/shorty-video-analysis/wiki/API-Reference)
- [Architecture Guide](https://github.com/yourusername/shorty-video-analysis/wiki/Architecture)
- [Deployment Guide](https://github.com/yourusername/shorty-video-analysis/wiki/Deployment)
- [Troubleshooting](https://github.com/yourusername/shorty-video-analysis/wiki/Troubleshooting)

### 🔧 Development Tools
- [Development Setup](https://github.com/yourusername/shorty-video-analysis/wiki/Development-Setup)
- [Testing Guide](https://github.com/yourusername/shorty-video-analysis/wiki/Testing)
- [Code Style Guide](https://github.com/yourusername/shorty-video-analysis/wiki/Code-Style)

### 🌟 Community
- [Discussions](https://github.com/yourusername/shorty-video-analysis/discussions)
- [Issues](https://github.com/yourusername/shorty-video-analysis/issues)
- [Releases](https://github.com/yourusername/shorty-video-analysis/releases)

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [Mistral AI](https://mistral.ai/) for providing advanced AI analysis capabilities
- [Instaloader](https://instaloader.github.io/) for Instagram data extraction
- [Sentence Transformers](https://www.sbert.net/) for embeddings generation
- The open-source community for the excellent libraries and tools
- Contributors who have helped improve this project

## 📞 Support

- 📧 Email: contact@example.com
- 🐛 Issues: [GitHub Issues](https://github.com/yourusername/shorty-video-analysis/issues)
- 💬 Discussions: [GitHub Discussions](https://github.com/yourusername/shorty-video-analysis/discussions)

---

<div align="center">
  <p>
    <strong>Shorty Video Analysis</strong> - Making short-form video content analysis accessible and powerful
  </p>
  <p>
    <a href="#table-of-contents">⬆️ Back to Top</a>
  </p>
</div>
