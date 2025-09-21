import io.ktor.client.*
import io.ktor.client.call.*
import io.ktor.client.engine.cio.*
import io.ktor.client.plugins.contentnegotiation.*
import io.ktor.client.request.*
import io.ktor.http.*
import io.ktor.serialization.kotlinx.json.*
import kotlinx.coroutines.*
import kotlinx.serialization.*
import kotlinx.serialization.json.*

/**
 * Example Kotlin Multiplatform client for Instagram Reel Analyzer API
 * 
 * Dependencies required in your KMP project:
 * - implementation("io.ktor:ktor-client-core:2.3.5")
 * - implementation("io.ktor:ktor-client-cio:2.3.5")
 * - implementation("io.ktor:ktor-client-content-negotiation:2.3.5")
 * - implementation("io.ktor:ktor-serialization-kotlinx-json:2.3.5")
 * - implementation("org.jetbrains.kotlinx:kotlinx-serialization-json:1.6.0")
 */

// Data models for API responses
@Serializable
data class Creator(
    val username: String = "",
    val profile: String = ""
)

@Serializable
data class Comment(
    val user: String = "",
    val comment: String = "",
    val timestamp: String = ""
)

@Serializable
data class ReelResult(
    val reel_id: String = "",
    val Reel_link: String = "",
    val caption: String = "",
    val creator: Creator = Creator(),
    val ai_summary: String = "",
    val category: List<String> = emptyList(),
    val likes: Int = 0,
    val views: Int = 0,
    val sentiment: String = "",
    val top_comment_summary: String = "",
    val embeddings: List<Double> = emptyList(),
    val top_comments: List<Comment> = emptyList()
)

@Serializable
data class ApiResponse(
    val status: String = "",
    val count: Int = 0,
    val results: List<ReelResult> = emptyList()
)

@Serializable
data class HealthResponse(
    val status: String = "",
    val version: String = "",
    val timestamp: String = ""
)

@Serializable
data class AnalyzeRequest(
    val target: String,
    val max_reels: Int = 10,
    val use_login: Boolean = true,
    val scraping_method: String = "instaloader"
)

class InstagramReelClient(private val baseUrl: String = "http://localhost:5001") {
    private val client = HttpClient(CIO) {
        install(ContentNegotiation) {
            json(Json {
                ignoreUnknownKeys = true
                prettyPrint = true
                isLenient = true
            })
        }
    }
    
    /**
     * Check if the API server is running
     */
    suspend fun checkHealth(): HealthResponse {
        return client.get("$baseUrl/api/health").body()
    }
    
    /**
     * Analyze Instagram reels from a profile, hashtag, or direct URL
     * 
     * @param target Instagram URL, profile name, or hashtag
     * @param maxReels Maximum number of reels to analyze
     * @param useLogin Whether to use Instagram login
     * @param scrapingMethod "instaloader" or "selenium"
     */
    suspend fun analyzeReels(
        target: String,
        maxReels: Int = 10,
        useLogin: Boolean = true,
        scrapingMethod: String = "instaloader"
    ): ApiResponse {
        val request = AnalyzeRequest(
            target = target,
            max_reels = maxReels,
            use_login = useLogin,
            scraping_method = scrapingMethod
        )
        
        return client.post("$baseUrl/api/analyze") {
            contentType(ContentType.Application.Json)
            setBody(request)
        }.body()
    }
    
    /**
     * Close the HTTP client when done
     */
    fun close() {
        client.close()
    }
}

/**
 * Example usage
 */
suspend fun main() {
    val client = InstagramReelClient()
    
    try {
        // Check if API is running
        val health = client.checkHealth()
        println("API Status: ${health.status}, Version: ${health.version}")
        
        // Analyze reels from a profile
        val response = client.analyzeReels(
            target = "@only_comedy_vid",
            maxReels = 5,
            useLogin = true,
            scrapingMethod = "instaloader"
        )
        
        println("Found ${response.count} reels")
        
        // Process results
        response.results.forEachIndexed { index, reel ->
            println("\nReel ${index + 1}: ${reel.reel_id}")
            println("Caption: ${reel.caption.take(100)}...")
            println("AI Summary: ${reel.ai_summary}")
            println("Categories: ${reel.category.joinToString(", ")}")
            println("Sentiment: ${reel.sentiment}")
            println("Likes: ${reel.likes}, Views: ${reel.views}")
            println("Creator: ${reel.creator.username}")
            
            println("\nTop Comments:")
            reel.top_comments.forEach { comment ->
                println("${comment.user}: ${comment.comment}")
            }
        }
    } catch (e: Exception) {
        println("Error: ${e.message}")
    } finally {
        client.close()
    }
}