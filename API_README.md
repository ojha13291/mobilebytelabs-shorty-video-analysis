# Instagram Reel Analyzer REST API

This REST API provides endpoints to analyze Instagram Reels using AI. It's designed to be used with Kotlin Multiplatform (KMP) applications but can be used with any client that can make HTTP requests.

## Getting Started

### Prerequisites

- Python 3.8+
- Required Python packages (install using `pip install -r requirements.txt`)

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
  "status": "ok",
  "version": "1.0.0",
  "timestamp": "2023-11-15T12:34:56.789012"
}
```

### Analyze Reels

```
POST /api/analyze
```

Analyzes Instagram reels from a profile, hashtag, or direct URL.

**Request Body:**

```json
{
  "target": "@username",  // Instagram URL, profile name, or hashtag
  "max_reels": 10,       // Maximum number of reels to analyze (default: 10)
  "use_login": true,     // Whether to use Instagram login (default: true)
  "scraping_method": "instaloader"  // "instaloader" or "selenium" (default: "instaloader")
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
      "Reel_link": "https://instagram.fxyz.com/v/t50.12345-16/123456_789012345678901_1234567890123456789_n.mp4",
      "caption": "This is a sample reel caption #trending",
      "creator": {
        "username": "username",
        "profile": "https://www.instagram.com/username/"
      },
      "ai_summary": "A funny video showing a cat playing with a toy.",
      "category": ["Comedy", "Animals"],
      "likes": 1234,
      "views": 5678,
      "sentiment": "Positive",
      "top_comment_summary": "Users find the video hilarious and are sharing similar experiences.",
      "embeddings": [0.123, 0.456, 0.789],
      "top_comments": [
        {
          "user": "commenter1",
          "comment": "This is so funny! 😂",
          "timestamp": "2023-11-10T15:30:45.123456"
        }
      ]
    }
  ]
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
- 400: Bad request (missing parameters)
- 500: Server error

Error responses include an error message:

```json
{
  "error": "Error message details"
}
```

## Security Considerations

- The API currently doesn't implement authentication. For production use, add proper authentication.
- Instagram credentials are stored directly in the code. For production, use environment variables or a secure configuration system.
- CORS is enabled for all origins, which may need to be restricted in production.

## License

This project is licensed under the MIT License.