# Instagram Reel Analyzer REST API

This REST API provides endpoints to analyze Instagram Reels using AI. It's designed to be used with Kotlin Multiplatform (KMP) applications but can be used with any client that can make HTTP requests.

## Getting Started

### Prerequisites

- Python 3.8+
- Required Python packages (install using `pip install -r requirements.txt`)
- Mistral AI API key (get from [Mistral AI](https://mistral.ai/))

### Running the API Server

```bash
python api.py
```

The server will start on `http://localhost:5001`.

## API Endpoints

### Health Check

```
GET /api/health
```

Returns the status of the API server.

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

### Analyze Reels

```
POST /api/analyze
```

Analyzes Instagram reels from a profile, hashtag, or direct URL.

### Service Metrics

```
GET /api/metrics
```

Returns service performance metrics and usage statistics.

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

```
GET /api/config
```

Returns current service configuration (sanitized).

**Response:**

```json
{
  "service_host": "0.0.0.0",
  "service_port": 5001,
  "max_reels_default": 10,
  "debug": false,
  "scraping_method": "instaloader"
}
```

**Request Body:**

```json
{
  "target": "@username",                    // Instagram URL, profile name, or hashtag
  "max_reels": 10,                         // Maximum number of reels to analyze (default: 10)
  "use_login": true,                       // Whether to use Instagram login (default: true)
  "scraping_method": "instaloader",        // "instaloader" or "selenium" (default: "instaloader")
  "include_analysis": true                 // Include AI analysis (default: true)
}
```

**Response:**

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
      "embeddings": [0.123, 0.456, 0.789]
    }
  ],
  "processing_time": 8.5,
  "errors": []
}
```

## Using with Kotlin Multiplatform

A sample KMP client is provided in `KMPClient.kt`. To use it in your KMP project:

1. Add the required dependencies to your `build.gradle.kts`:

```kotlin
dependencies {
    implementation("io.ktor:ktor-client-core:2.3.5")
    implementation("io.ktor:ktor-client-cio:2.3.5")
    implementation("io.ktor:ktor-client-content-negotiation:2.3.5")
    implementation("io.ktor:ktor-serialization-kotlinx-json:2.3.5")
    implementation("org.jetbrains.kotlinx:kotlinx-serialization-json:1.6.0")
}
```

2. Copy the data models and client class from `KMPClient.kt` to your project.

3. Use the client in your KMP code:

```kotlin
val client = InstagramReelClient("http://your-api-server:5001")

try {
    val response = client.analyzeReels(
        target = "@instagram_profile",
        maxReels = 5
    )
    
    // Process the results
    response.results.forEach { reel ->
        println("Reel: ${reel.reel_id}")
        println("Summary: ${reel.ai_summary}")
    }
} finally {
    client.close()
}
```

## Error Handling

The API returns appropriate HTTP status codes:

- 200: Success
- 400: Bad request (missing parameters, validation errors)
- 500: Server error

Error responses include detailed error messages:

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

## Security Considerations

- **API Keys**: Store Mistral API keys securely using environment variables or secret management systems
- **Instagram Credentials**: Use dedicated Instagram accounts for scraping, not personal accounts
- **Rate Limiting**: Implement rate limiting in production deployments
- **CORS**: Configure CORS appropriately for your deployment environment
- **Input Validation**: All inputs are validated and sanitized
- **Error Handling**: Sensitive information is not exposed in error messages

## License

This project is licensed under the MIT License.