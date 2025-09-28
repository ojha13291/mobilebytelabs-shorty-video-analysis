# Contributing to Multi-Platform Video Data Fetcher

Thank you for your interest in contributing to this project! This document provides guidelines and information for contributors.

## 🎯 Project Overview

This is a multi-platform video data fetcher that extracts metadata from YouTube, Instagram, TikTok, and Twitter. The project consists of:

- **Core API**: Flask-based REST API (`api.py`)
- **Video Data Fetcher**: Modular fetcher system (`video_data_fetcher/`)
- **Platform Resolvers**: Platform detection and URL handling (`resolver/`)
- **Scrapers**: Platform-specific scraping logic (`scrapers/`)
- **Comprehensive Testing**: Unit tests with proper mocking (`tests/`)

## 🚀 Getting Started

### Prerequisites
- Python 3.8 or higher
- pip package manager
- Git

### Development Setup
```bash
# Clone the repository
git clone https://github.com/yourusername/multi-platform-video-fetcher.git
cd multi-platform-video-fetcher

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install development dependencies
pip install pytest pytest-cov black flake8 mypy

# Copy environment configuration
cp .env.example .env

# Run tests to verify setup
python -m pytest tests/ -v
```

## 📝 Contribution Guidelines

### Types of Contributions
- **Bug fixes**: Fix broken functionality or errors
- **Feature additions**: Add new platforms or capabilities
- **Documentation**: Improve README, API docs, or code comments
- **Testing**: Add or improve test coverage
- **Performance**: Optimize existing code
- **Security**: Fix security vulnerabilities or improve security practices

### Before You Start
1. **Check existing issues**: Look for open issues that match your contribution
2. **Create an issue**: If your contribution doesn't have an issue, create one first
3. **Discuss**: For major changes, discuss your approach in the issue before starting
4. **Fork the repository**: Create your own fork to work on

### Development Workflow

1. **Create a feature branch**
   ```bash
   git checkout -b feature/add-tiktok-support
   # or
   git checkout -b fix/youtube-scraper-issue
   ```

2. **Make your changes**
   - Follow the coding standards (see below)
   - Write or update tests for your changes
   - Update documentation as needed

3. **Test your changes**
   ```bash
   # Run all tests
   python -m pytest tests/ -v
   
   # Run with coverage
   python -m pytest tests/ --cov=video_data_fetcher --cov-report=html
   
   # Check code style
   flake8 video_data_fetcher/ tests/
   
   # Format code
   black video_data_fetcher/ tests/
   
   # Type checking (if applicable)
   mypy video_data_fetcher/
   ```

4. **Commit your changes**
   ```bash
   git add .
   git commit -m "feat: add TikTok platform support

   - Add TikTok scraper implementation
   - Add TikTok-specific URL patterns
   - Add comprehensive unit tests
   - Update documentation

   Closes #123"
   ```

5. **Push and create pull request**
   ```bash
   git push origin feature/add-tiktok-support
   ```
   Then create a pull request on GitHub.

## 🎨 Coding Standards

### Python Style Guide
- Follow [PEP 8](https://pep8.org/) style guidelines
- Use meaningful variable and function names
- Add docstrings to all functions and classes
- Keep functions small and focused (single responsibility)
- Use type hints where appropriate

### Code Structure
```python
def fetch_video_data(url: str) -> Dict[str, Any]:
    """
    Fetch video metadata from a given URL.
    
    Args:
        url: The video URL to fetch data from
        
    Returns:
        Dictionary containing video metadata
        
    Raises:
        ValueError: If URL is invalid or unsupported
        NetworkError: If request fails
    """
    # Implementation here
    pass
```

### Error Handling
- Use specific exception types
- Provide meaningful error messages
- Include context in error messages
- Log errors appropriately

```python
try:
    response = requests.get(url, timeout=30)
    response.raise_for_status()
except requests.Timeout:
    raise NetworkError(f"Request timed out for URL: {url}")
except requests.RequestException as e:
    raise NetworkError(f"Request failed for URL {url}: {str(e)}")
```

## 🧪 Testing Guidelines

### Test Structure
- Place tests in the `tests/` directory
- Name test files with `test_` prefix
- Use descriptive test function names
- Follow the Arrange-Act-Assert pattern

### Example Test
```python
def test_youtube_fetcher_success():
    """Test successful YouTube video data fetching."""
    # Arrange
    fetcher = YouTubeFetcher()
    url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
    
    # Act
    result = fetcher.fetch(url)
    
    # Assert
    assert result["success"] is True
    assert result["platform"] == "youtube"
    assert "title" in result
    assert "view_count" in result
```

### Mocking Best Practices
- Mock external HTTP requests
- Mock platform-specific APIs
- Use fixtures for common test data
- Test both success and failure scenarios

### Running Tests
```bash
# Run all tests
python -m pytest tests/ -v

# Run specific test file
python -m pytest tests/test_video_data_fetcher.py -v

# Run with coverage report
python -m pytest tests/ --cov=video_data_fetcher --cov-report=html

# Run tests in parallel (if pytest-xdist installed)
python -m pytest tests/ -n auto
```

## 📋 Pull Request Process

### Before Submitting
1. **Update documentation**: Update README, API docs, or code comments
2. **Add tests**: Ensure new functionality has tests
3. **Update changelog**: Add entry to CHANGELOG.md if applicable
4. **Check dependencies**: Update requirements.txt if needed
5. **Test thoroughly**: Run all tests and ensure they pass

### Pull Request Template
When creating a pull request, please include:

- **Description**: What does this PR do?
- **Type of change**: Bug fix, feature, documentation, etc.
- **Testing**: How did you test your changes?
- **Breaking changes**: Any breaking changes?
- **Screenshots**: If UI changes
- **Checklist**: Verify all items are completed

### Review Process
1. **Automated checks**: CI/CD will run tests and checks
2. **Code review**: Maintainers will review your code
3. **Feedback**: Address any feedback or requested changes
4. **Merge**: Once approved, your PR will be merged

## 🐛 Bug Reports

When reporting bugs, please include:

- **Bug description**: Clear description of the issue
- **Steps to reproduce**: How to reproduce the bug
- **Expected behavior**: What should happen
- **Actual behavior**: What actually happens
- **Environment**: OS, Python version, dependencies
- **Error messages**: Any error messages or logs
- **URLs tested**: Specific URLs that cause the issue

## 💡 Feature Requests

For new features, please provide:

- **Use case**: Why is this feature needed?
- **Proposed solution**: How should it work?
- **Alternatives**: Any alternative approaches?
- **Platform support**: Which platforms should be supported?
- **API changes**: Any API changes needed?
- **Breaking changes**: Will this break existing functionality?

## 🔧 Development Tips

### Debugging
```python
import logging

# Enable debug logging
logging.basicConfig(level=logging.DEBUG)

# Add debug logs to your code
logger = logging.getLogger(__name__)
logger.debug(f"Processing URL: {url}")
```

### Performance Testing
```bash
# Simple load testing with curl
for i in {1..10}; do
  curl -X POST http://localhost:5001/api/analyze \
    -H "Content-Type: application/json" \
    -d '{"target": "https://www.youtube.com/watch?v=dQw4w9WgXcQ"}' &
done
wait
```

### Environment Variables
Create a `.env` file for local development:
```bash
SERVICE_HOST=0.0.0.0
SERVICE_PORT=5001
DEBUG=true
MAX_REELS_DEFAULT=10
```

## 📚 Documentation

### Code Documentation
- Add docstrings to all public functions and classes
- Include parameter types and return types
- Provide usage examples for complex functions
- Keep documentation up to date with code changes

### API Documentation
- Update API_README.md when adding new endpoints
- Include request/response examples
- Document error codes and messages
- Keep examples current and working

## 🚨 Security

### Security Guidelines
- Never commit API keys or credentials
- Use environment variables for sensitive data
- Validate all user inputs
- Sanitize error messages (don't expose internal details)
- Keep dependencies updated
- Report security issues privately

### Security Reporting
If you discover a security vulnerability, please:
1. **Do not** create a public issue
2. Email the maintainers privately
3. Provide detailed information about the vulnerability
4. Allow time for the issue to be addressed before disclosure

## 📞 Getting Help

- **GitHub Issues**: For bug reports and feature requests
- **Discussions**: For questions and general discussion
- **Documentation**: Check README and API docs first
- **Examples**: Look at examples/ directory for usage patterns

## 🏆 Recognition

Contributors will be recognized in:
- CONTRIBUTORS.md file
- Release notes for significant contributions
- Project documentation

Thank you for contributing to make this project better!