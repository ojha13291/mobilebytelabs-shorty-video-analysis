# 🎥 Streamlit Video Sentiment Analyzer

A modern, feature-rich web interface for analyzing video content sentiment from multiple social media platforms including YouTube, Instagram, TikTok, Twitter, and more.

## ✨ Features

### 🚀 Core Functionality
- **Multi-Platform Support**: Analyze videos from YouTube, Instagram, TikTok, Twitter/X, Facebook, LinkedIn
- **AI-Powered Sentiment Analysis**: Advanced sentiment detection with confidence scores
- **Topic Extraction**: Identify key topics and themes in video content
- **Emotion Detection**: Detect emotions expressed in video descriptions and comments
- **Engagement Metrics**: Analyze likes, comments, shares, and views

### 📊 Advanced Analytics
- **Real-Time Dashboard**: Live metrics and analytics
- **Sentiment Trends**: Track sentiment changes over time
- **Platform Comparison**: Compare performance across platforms
- **Word Cloud Visualization**: Visual representation of frequent terms
- **Interactive Charts**: Beautiful Plotly visualizations

### 🛠️ Advanced Tools
- **Batch Processing**: Analyze multiple videos via CSV upload
- **Video Comparison**: Side-by-side comparison of two videos
- **Export & Reporting**: Generate comprehensive reports
- **Analysis History**: Track and revisit previous analyses
- **Custom Configuration**: Flexible analysis options

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Chrome/Chromium browser (for scraping)
- API server running (see setup below)

### Installation

1. **Clone and setup the project:**
```bash
git clone <repository-url>
cd mobilebytelabs-video-sentiment-analysis
```

2. **Install dependencies:**
```bash
pip install -r requirements.txt
```

3. **Start the API server:**
```bash
python api/app.py
```

4. **Launch the Streamlit app:**
```bash
# Option 1: Using the launch script
python run_streamlit.py

# Option 2: Direct Streamlit command
streamlit run streamlit_app.py
```

5. **Open your browser:**
Navigate to `http://localhost:8501`

## 📋 Usage Guide

### Single Video Analysis
1. Paste a video URL in the input field
2. Select platform (optional - auto-detection available)
3. Click "Analyze Video"
4. View comprehensive analysis results

### Batch Analysis
1. Go to "Batch Analysis" tab
2. Upload CSV file with URLs
3. Click "Analyze All URLs"
4. Download results as CSV

### Advanced Dashboard
1. Navigate to "Advanced Dashboard"
2. View real-time metrics and trends
3. Use comparison tools
4. Generate and export reports

## 🔧 Configuration

### Environment Variables
```bash
# API Configuration
API_BASE_URL=http://localhost:5001/api

# Streamlit Configuration
STREAMLIT_SERVER_PORT=8501
STREAMLIT_SERVER_ADDRESS=localhost
```

### Analysis Options
- Enable/disable sentiment analysis
- Configure confidence thresholds
- Customize visualization preferences
- Set platform-specific options

## 📊 Metrics Explained

### Sentiment Analysis
- **Score Range**: -1.0 (very negative) to +1.0 (very positive)
- **Confidence**: AI model's confidence in analysis (0-100%)
- **Categories**: Positive, Negative, Neutral

### Engagement Metrics
- **Platform-specific**: Varies by platform (likes, comments, shares)
- **Hashtag Analysis**: Frequency and relevance of hashtags
- **Content Quality**: Based on description and metadata

### Topic Extraction
- **Relevance Score**: How relevant topics are to content (0-100%)
- **Topic Categories**: Automatic categorization
- **Keyword Density**: Frequency of key terms

## 🛠️ Advanced Features

### Video Comparison Tool
- Side-by-side sentiment analysis
- Engagement metric comparison
- Content similarity analysis
- Performance benchmarking

### Export & Reporting
- **JSON Reports**: Complete analysis data
- **CSV Exports**: Tabular data for spreadsheets
- **Chart Exports**: High-quality visualizations
- **Summary Reports**: Executive summaries

### Real-Time Analytics
- Live processing metrics
- Success rate tracking
- Platform distribution
- Sentiment trend analysis

## 🔒 Privacy & Security

- **Local Processing**: All analysis performed locally or via secure API
- **No Data Storage**: Video content not stored permanently
- **Secure Connections**: HTTPS support for API communications
- **Privacy-First**: Minimal data collection approach

## 🐛 Troubleshooting

### Common Issues

**API Connection Failed**
```bash
# Ensure API server is running
python api/app.py

# Check API health
curl http://localhost:5001/api/health
```

**ChromeDriver Issues**
```bash
# Update WebDriver Manager
pip install --upgrade webdriver-manager

# Check Chrome installation
which google-chrome  # Linux/Mac
where chrome          # Windows
```

**Memory Issues with Large Batches**
- Reduce batch size in CSV files
- Process in smaller chunks
- Monitor system resources

### Performance Tips
- Use smaller video batches for faster processing
- Enable caching for repeated analyses
- Monitor API rate limits
- Use appropriate confidence thresholds

## 📈 Performance Optimization

### For Large-Scale Analysis
- Implement batch processing with delays
- Use parallel processing for multiple videos
- Monitor API rate limits
- Implement retry mechanisms

### Memory Management
- Process videos in chunks
- Clear analysis history regularly
- Use streaming for large datasets
- Monitor system resources

## 🔧 Development

### Adding New Features
1. Modify `streamlit_app.py` for UI changes
2. Update `dashboard_components.py` for analytics
3. Add new API endpoints if needed
4. Update requirements if new dependencies

### Custom Visualizations
- Extend Plotly charts in dashboard components
- Add new metrics and KPIs
- Create custom comparison tools
- Implement advanced filtering

## 📚 API Integration

The Streamlit app integrates with the Flask API backend:

### Endpoints Used
- `POST /api/analyze` - Analyze single video
- `POST /api/platform/detect` - Platform detection
- `GET /api/health` - Health check

### Custom API Integration
- Modify `VideoAnalyzerClient` class
- Update endpoint URLs in configuration
- Add custom authentication if needed
- Implement error handling

## 📱 Mobile Support

The interface is responsive and works on:
- Desktop browsers (Chrome, Firefox, Safari, Edge)
- Mobile browsers (iOS Safari, Chrome Mobile)
- Tablet devices
- Touch-friendly interface

## 🎯 Future Enhancements

### Planned Features
- **Real-time Processing**: Live video analysis
- **Advanced AI Models**: GPT-4, Claude integration
- **Social Media APIs**: Direct platform integration
- **Machine Learning**: Custom model training
- **Collaborative Features**: Team sharing and annotations

### Community Contributions
- Plugin system for custom analyzers
- Theme customization
- Multi-language support
- Advanced export formats

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📞 Support

For support and questions:
- Check the troubleshooting section
- Review API documentation
- Check GitHub issues
- Contact development team

---

**Happy Analyzing! 🎥✨**