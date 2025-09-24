# Instagram Reels Microservice

A modular, open-source microservice for scraping and analyzing Instagram reels with AI-powered insights. Built with Python Flask, this microservice provides a REST API for extracting reel data and generating intelligent content analysis.

## 🚀 Features

- **Modular Architecture**: Clean separation of concerns with dedicated services for scraping and AI analysis
- **Multiple Scraping Methods**: Support for both Instaloader and Selenium WebDriver
- **AI-Powered Analysis**: Integration with Mistral AI for content summarization, categorization, and sentiment analysis
- **Embeddings Support**: Generate vector embeddings for content similarity analysis
- **Production Ready**: Docker support, health checks, metrics, and comprehensive error handling
- **Open Source Friendly**: MIT licensed with comprehensive documentation

## 📋 API Endpoints

### Health Check
```
GET /health
```
Returns service health status and component availability.

### Analyze Reels
```
POST /api/analyze
```
Main endpoint for scraping and analyzing Instagram reels.

**Request Body:**
```json
{
  "target": "@username",           // Instagram URL, profile, or hashtag
  "max_reels": 10,                // Maximum reels to analyze (default: 10)
  "use_login": true,              // Use Instagram login (default: true)
  "scraping_method": "instaloader", // "instaloader" or "selenium"
  "include_comments": true,       // Include comment analysis
  "include_analysis": true        // Include AI analysis
}
```

### Service Metrics
```
GET /api/metrics
```
Returns service performance metrics and usage statistics.

### Configuration
```
GET /api/config
```
Returns current service configuration (sanitized).

## 🛠️ Quick Start

### Prerequisites
- Python 3.8+
- Mistral AI API key (get from [Mistral AI](https://mistral.ai/))
- Docker (optional)

### Installation

1. **Clone the repository:**
```bash
git clone https://github.com/yourusername/instagram-reels-microservice.git
cd instagram-reels-microservice
```

2. **Set up environment:**
```bash
cp .env.example .env
# Edit .env with your configuration
```

3. **Install dependencies:**
```bash
pip install -r requirements.txt
```

4. **Run the service:**
```bash
python main.py
```

### Docker Deployment

1. **Build and run with Docker:**
```bash
docker build -t instagram-reels-microservice .
docker run -p 5001:5001 --env-file .env instagram-reels-microservice
```

2. **Or use docker-compose:**
```bash
docker-compose up -d
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

### Python Client
```python
import requests
import json

# Configure API endpoint
API_URL = "http://localhost:5001"

def analyze_profile(username, max_reels=5):
    """Analyze reels from an Instagram profile"""
    
    payload = {
        "target": f"@{username}",
        "max_reels": max_reels,
        "use_login": True,
        "scraping_method": "instaloader",
        "include_analysis": True
    }
    
    response = requests.post(f"{API_URL}/api/analyze", json=payload)
    
    if response.status_code == 200:
        data = response.json()
        print(f"Analyzed {data['count']} reels from @{username}")
        
        for reel in data['results']:
            print(f"\nReel: {reel['reel_id']}")
            print(f"Views: {reel['views']:,}")
            print(f"Likes: {reel['likes']:,}")
            
            if reel['analysis']:
                print(f"Category: {', '.join(reel['analysis']['category'])}")
                print(f"Summary: {reel['analysis']['summary']}")
    else:
        print(f"Error: {response.json()}")

# Analyze a profile
analyze_profile("natgeo", max_reels=3)
```

### cURL Example
```bash
curl -X POST http://localhost:5001/api/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "target": "#travel",
    "max_reels": 5,
    "scraping_method": "instaloader"
  }'
```

### JavaScript/Node.js Client
```javascript
const axios = require('axios');

async function analyzeReels(target, maxReels = 10) {
    try {
        const response = await axios.post('http://localhost:5001/api/analyze', {
            target: target,
            max_reels: maxReels,
            include_analysis: true
        });
        
        console.log(`Analyzed ${response.data.count} reels`);
        return response.data.results;
    } catch (error) {
        console.error('Analysis failed:', error.response?.data || error.message);
        throw error;
    }
}

// Usage
analyzeReels('@instagram', 5)
    .then(results => console.log('Analysis complete:', results))
    .catch(err => console.error('Failed:', err));
```

## 🐳 Docker Deployment Options

### Basic Deployment
```bash
docker run -d \
  --name instagram-reels-microservice \
  -p 5001:5001 \
  -e MISTRAL_API_KEY=your_api_key \
  -e INSTAGRAM_USERNAME=your_username \
  -e INSTAGRAM_PASSWORD=your_password \
  instagram-reels-microservice
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
  name: instagram-reels-microservice
spec:
  replicas: 3
  selector:
    matchLabels:
      app: instagram-reels-microservice
  template:
    metadata:
      labels:
        app: instagram-reels-microservice
    spec:
      containers:
      - name: instagram-reels-microservice
        image: instagram-reels-microservice:latest
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
```

## 📈 Monitoring and Health Checks

### Health Check Response
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

### Metrics Response
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

## 🔒 Security Considerations

- **API Keys**: Store Mistral API keys securely using environment variables or secret management systems
- **Instagram Credentials**: Use dedicated Instagram accounts for scraping, not personal accounts
- **Rate Limiting**: Implement rate limiting in production deployments
- **CORS**: Configure CORS appropriately for your deployment environment
- **Input Validation**: All inputs are validated and sanitized
- **Error Handling**: Sensitive information is not exposed in error messages

## 🐛 Error Handling

The service provides detailed error responses:

```json
{
  "error": "Configuration validation failed: MISTRAL_API_KEY is required"
}
```

Common error scenarios:
- Missing API keys
- Invalid Instagram credentials
- Rate limiting from Instagram
- Network connectivity issues
- Invalid request parameters

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guidelines](CONTRIBUTING.md) for details.

### Development Setup

1. **Fork and clone the repository**
2. **Create a virtual environment:**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install development dependencies:**
```bash
pip install -r requirements.txt
pip install -e .[dev]
```

4. **Run tests:**
```bash
pytest tests/ -v
```

5. **Run linting:**
```bash
black src/
flake8 src/
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [Mistral AI](https://mistral.ai/) for providing the AI analysis capabilities
- [Instaloader](https://instaloader.github.io/) for Instagram data extraction
- [Sentence Transformers](https://www.sbert.net/) for embeddings generation
- The open-source community for continuous improvements

## 📞 Support

- 📧 Email: contact@example.com
- 🐛 Issues: [GitHub Issues](https://github.com/yourusername/instagram-reels-microservice/issues)
- 💬 Discussions: [GitHub Discussions](https://github.com/yourusername/instagram-reels-microservice/discussions)

---

**⭐ Star this repository if you find it useful!**