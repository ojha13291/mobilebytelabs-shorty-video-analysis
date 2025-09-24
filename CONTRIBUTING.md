# Contributing to Instagram Reels Microservice

Thank you for your interest in contributing to the Instagram Reels Microservice! We welcome contributions from the community and are pleased to have you join us.

## 🚀 Getting Started

### Prerequisites
- Python 3.8 or higher
- Git
- Docker (optional, for containerized development)

### Development Environment Setup

1. **Fork the repository** on GitHub
2. **Clone your fork locally:**
```bash
git clone https://github.com/yourusername/instagram-reels-microservice.git
cd instagram-reels-microservice
```

3. **Create a virtual environment:**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

4. **Install development dependencies:**
```bash
pip install -r requirements.txt
pip install -e .[dev]
```

5. **Set up your environment file:**
```bash
cp .env.example .env
# Edit .env with your configuration
```

6. **Run the service locally:**
```bash
python main.py
```

## 📋 Types of Contributions

We welcome several types of contributions:

- 🐛 **Bug Reports**: Report issues you encounter
- 💡 **Feature Requests**: Suggest new features or improvements
- 🔧 **Code Contributions**: Submit pull requests with improvements
- 📖 **Documentation**: Improve our documentation and examples
- 🧪 **Testing**: Help improve test coverage
- 🎨 **UI/UX**: Improve user experience and interfaces
- 🌍 **Translations**: Help translate documentation

## 🐛 Bug Reports

When reporting bugs, please include:

- **Clear description** of the issue
- **Steps to reproduce** the problem
- **Expected behavior** vs actual behavior
- **Environment details** (OS, Python version, dependencies)
- **Error logs** or screenshots
- **API request/response** examples (if applicable)

### Bug Report Template
```markdown
**Bug Description:**
A clear description of what the bug is.

**Steps to Reproduce:**
1. Go to '...'
2. Click on '...'
3. See error

**Expected Behavior:**
What should have happened.

**Actual Behavior:**
What actually happened.

**Environment:**
- OS: [e.g., macOS 14.0, Ubuntu 22.04]
- Python Version: [e.g., 3.11.0]
- Service Version: [e.g., 1.0.0]
- Browser: [if applicable]

**Additional Context:**
Add any other context about the problem here.
```

## 💡 Feature Requests

For feature requests, please:

- **Check existing issues** to avoid duplicates
- **Describe the feature** and its use case
- **Explain why** this feature would be beneficial
- **Provide examples** of how it would work
- **Consider implementation** complexity and impact

## 🔧 Code Contributions

### Code Style Guidelines

We follow PEP 8 style guidelines with some additional rules:

- **Line length**: Maximum 100 characters
- **Imports**: Grouped as standard library, third-party, local imports
- **Docstrings**: Use Google style docstrings for functions and classes
- **Type hints**: Use type hints for all function parameters and return values
- **Variable naming**: Use descriptive names, snake_case for functions/variables
- **Constants**: Use UPPER_CASE for constants

#### Example Code Style
```python
from typing import List, Optional, Dict, Any
import logging
from datetime import datetime

from flask import Flask, jsonify, request

from instagram_reels_microservice.models import ReelData
from instagram_reels_microservice.config import ConfigManager

logger = logging.getLogger(__name__)

class InstagramScraper:
    """Instagram scraping service with multiple methods."""
    
    def __init__(self, config: ConfigManager) -> None:
        """Initialize the scraper with configuration.
        
        Args:
            config: Configuration manager instance.
        """
        self.config = config
        self.session = None
    
    def scrape_reels(self, target: str, max_reels: int = 10) -> List[ReelData]:
        """Scrape reels from Instagram target.
        
        Args:
            target: Instagram profile, hashtag, or URL.
            max_reels: Maximum number of reels to scrape.
            
        Returns:
            List of ReelData objects.
            
        Raises:
            ScrapingError: If scraping fails.
        """
        # Implementation here
        pass
```

### Testing Guidelines

- **Write tests** for all new functionality
- **Maintain coverage** above 80%
- **Use pytest** for testing framework
- **Mock external services** (Instagram, Mistral AI)
- **Test edge cases** and error conditions
- **Use fixtures** for common test data

#### Test Example
```python
import pytest
from unittest.mock import Mock, patch

from instagram_reels_microservice.services.analyzer import AIAnalyzer
from instagram_reels_microservice.models import ReelData

class TestAIAnalyzer:
    """Test cases for AI Analyzer service."""
    
    @pytest.fixture
    def analyzer(self):
        """Create analyzer instance for testing."""
        return AIAnalyzer(api_key="test_key")
    
    @patch('requests.post')
    def test_analyze_content_success(self, mock_post, analyzer):
        """Test successful content analysis."""
        # Arrange
        mock_response = Mock()
        mock_response.json.return_value = {
            'choices': [{'message': {'content': 'Test analysis'}}]
        }
        mock_post.return_value = mock_response
        
        reel_data = ReelData(
            reel_id="test123",
            caption="Test caption",
            # ... other fields
        )
        
        # Act
        result = analyzer.analyze_content(reel_data)
        
        # Assert
        assert result.summary == "Test analysis"
        mock_post.assert_called_once()
```

### Git Workflow

1. **Create a feature branch** from `main`:
```bash
git checkout -b feature/your-feature-name
```

2. **Make your changes** following our guidelines

3. **Write/update tests** for your changes

4. **Run the test suite**:
```bash
pytest tests/ -v
```

5. **Run linting**:
```bash
black src/ tests/
flake8 src/ tests/
mypy src/
```

6. **Commit your changes** with a clear commit message:
```bash
git commit -m "feat: add new scraping method for hashtags

- Implement hashtag scraping using Selenium
- Add comprehensive tests for new functionality
- Update documentation with usage examples

Closes #123"
```

7. **Push to your fork**:
```bash
git push origin feature/your-feature-name
```

8. **Create a Pull Request** on GitHub

### Commit Message Guidelines

We follow [Conventional Commits](https://www.conventionalcommits.org/) specification:

- **feat**: New feature
- **fix**: Bug fix
- **docs**: Documentation changes
- **style**: Code style changes (formatting, etc.)
- **refactor**: Code refactoring
- **test**: Test additions or changes
- **chore**: Build process or auxiliary tool changes

Format: `type(scope): description`

Examples:
```
feat(scraper): add hashtag scraping support
fix(analyzer): resolve sentiment analysis error
docs(readme): update installation instructions
test(services): add unit tests for scraper service
```

## 📖 Documentation Contributions

### Documentation Structure

```
docs/
├── api/                    # API documentation
├── examples/              # Usage examples
├── deployment/             # Deployment guides
└── development/           # Development guides
```

### Documentation Guidelines

- **Use clear, concise language**
- **Include code examples** where appropriate
- **Update API docs** when endpoints change
- **Add examples** for new features
- **Keep documentation in sync** with code changes

### API Documentation

When adding new endpoints:

1. **Update OpenAPI specification** (if applicable)
2. **Document request/response formats**
3. **Include example requests**
4. **Document error responses**
5. **Update API README**

## 🧪 Testing

### Running Tests

```bash
# Run all tests
pytest tests/ -v

# Run specific test file
pytest tests/test_analyzer.py -v

# Run with coverage
pytest tests/ --cov=src/ --cov-report=html

# Run integration tests only
pytest tests/integration/ -v

# Run unit tests only
pytest tests/unit/ -v
```

### Test Categories

- **Unit Tests**: Test individual functions and classes
- **Integration Tests**: Test service interactions
- **API Tests**: Test REST API endpoints
- **Performance Tests**: Test performance and scalability

### Mocking External Services

When testing, always mock external dependencies:

```python
from unittest.mock import Mock, patch

@patch('instagram_reels_microservice.services.scraper.Instaloader')
def test_instagram_scraping(mock_instaloader):
    """Test Instagram scraping with mocked Instaloader."""
    # Configure mock
    mock_instance = Mock()
    mock_instaloader.return_value = mock_instance
    
    # Set up mock behavior
    mock_instance.get_posts.return_value = [
        Mock(shortcode="test123", caption="Test post")
    ]
    
    # Test implementation
    # ...
```

## 🐳 Docker Development

### Building Development Image

```bash
# Build development image
docker build -t instagram-reels-microservice:dev .

# Run with development configuration
docker run -p 5001:5001 \
  --env-file .env \
  -v $(pwd)/src:/app/src \
  instagram-reels-microservice:dev
```

### Docker Compose for Development

```bash
# Start development services
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up

# Run tests in container
docker-compose exec app pytest tests/ -v

# Access container shell
docker-compose exec app bash
```

## 🌍 Internationalization

When adding new features:

- **Use translatable strings** for user-facing messages
- **Avoid hardcoded text** in error messages
- **Support multiple languages** where appropriate
- **Consider cultural differences** in examples

## 🔒 Security

### Security Guidelines

- **Never commit sensitive data** (API keys, passwords)
- **Use environment variables** for configuration
- **Validate all inputs** thoroughly
- **Implement proper error handling** without exposing internals
- **Use secure communication** (HTTPS in production)
- **Keep dependencies updated** regularly

### Reporting Security Issues

**Do not** report security vulnerabilities through public GitHub issues.

Instead, please email security concerns to: security@example.com

Include:
- Description of the vulnerability
- Steps to reproduce
- Potential impact
- Suggested fix (if any)

## 📊 Performance

### Performance Guidelines

- **Profile your code** before optimizing
- **Use caching** where appropriate
- **Implement connection pooling** for external services
- **Optimize database queries** (if applicable)
- **Monitor resource usage** (CPU, memory, network)
- **Consider async operations** for I/O bound tasks

## 🏷️ Release Process

### Version Numbering

We follow [Semantic Versioning](https://semver.org/):

- **MAJOR**: Breaking changes
- **MINOR**: New features (backward compatible)
- **PATCH**: Bug fixes (backward compatible)

### Release Checklist

- [ ] All tests pass
- [ ] Documentation updated
- [ ] CHANGELOG.md updated
- [ ] Version bumped in setup.py
- [ ] Docker image built and tested
- [ ] Git tag created
- [ ] GitHub release created
- [ ] PyPI package published (if applicable)

## 🤝 Code Review Process

### Review Criteria

- **Code quality**: Follows our style guidelines
- **Functionality**: Works as intended
- **Tests**: Adequate test coverage
- **Documentation**: Updated and accurate
- **Performance**: No significant performance regressions
- **Security**: No security vulnerabilities introduced

### Review Guidelines

- **Be constructive** and helpful
- **Focus on the code**, not the person
- **Explain your reasoning** for suggestions
- **Approve** when ready, **request changes** when needed
- **Test the changes** locally when possible

## 📞 Getting Help

### Communication Channels

- **GitHub Issues**: Bug reports and feature requests
- **GitHub Discussions**: General questions and discussions
- **Email**: contact@example.com
- **Discord**: [Join our server](https://discord.gg/example)

### Getting Help

When asking for help:

1. **Search existing issues** first
2. **Provide context** about your problem
3. **Include relevant code** snippets
4. **Share error messages** and logs
5. **Describe what you've tried** already

## 🏆 Recognition

Contributors are recognized in:

- **CONTRIBUTORS.md** file
- **Release notes** for significant contributions
- **GitHub contributors** page
- **Special mentions** in community updates

## 📜 Code of Conduct

This project adheres to a Code of Conduct. By participating, you are expected to uphold this code:

### Our Standards

- **Be respectful** and inclusive
- **Welcome newcomers** and help them get started
- **Accept constructive criticism** gracefully
- **Focus on what's best** for the community
- **Show empathy** towards other community members

### Unacceptable Behavior

- **Harassment** of any kind
- **Discriminatory language** or behavior
- **Personal attacks** or trolling
- **Spam** or off-topic discussions
- **Sharing private information** without consent

## 📚 Additional Resources

- [Python Style Guide (PEP 8)](https://www.python.org/dev/peps/pep-0008/)
- [Google Python Style Guide](https://google.github.io/styleguide/pyguide.html)
- [Conventional Commits](https://www.conventionalcommits.org/)
- [Semantic Versioning](https://semver.org/)
- [Docker Best Practices](https://docs.docker.com/develop/dev-best-practices/)

## 📝 License

By contributing to this project, you agree that your contributions will be licensed under the MIT License.

---

**Thank you for contributing to Instagram Reels Microservice! 🎉**