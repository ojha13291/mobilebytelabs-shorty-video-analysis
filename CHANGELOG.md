# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Initial microservice architecture implementation
- Modular service structure with separate scraper and analyzer services
- REST API with health checks and metrics endpoints
- Docker support with multi-stage builds
- Comprehensive configuration management
- Error handling and logging
- Open source documentation (README, CONTRIBUTING, LICENSE)
- Environment-based configuration
- Support for both Instaloader and Selenium scraping methods
- AI-powered content analysis using Mistral AI
- Sentence transformer embeddings
- Comprehensive test suite
- Docker Compose setup with nginx reverse proxy
- MIT license for open source distribution

### Changed
- Restructured from monolithic Flask/Streamlit apps to modular microservice
- Consolidated functionality from separate `api.py` and `app.py` files
- Improved error handling and validation
- Enhanced logging and monitoring
- Better separation of concerns

### Removed
- Streamlit application (consolidated into API service)
- Redundant Flask application files
- Hardcoded configuration values

## [1.0.0] - 2024-01-15

### Added
- Initial release as Instagram Reels Analyzer
- Flask API for reel analysis
- Streamlit web interface
- Instagram scraping functionality
- AI analysis using Mistral AI
- Docker support
- Basic documentation

### Notes
- This was the initial version before microservice restructuring
- Contained both `api.py` and `app.py` with overlapping functionality
- Monolithic architecture with mixed concerns