# Contributing to Video Sentiment Analysis API

We love your input! We want to make contributing to this project as easy and transparent as possible, whether it's:

- Reporting a bug
- Discussing the current state of the code
- Submitting a fix
- Proposing new features
- Adding platform support
- Becoming a maintainer

## Development Process

We use GitHub to host code, to track issues and feature requests, as well as accept pull requests.

1. Fork the repo and create your branch from `main`.
2. If you've added code that should be tested, add tests.
3. If you've changed APIs, update the documentation.
4. Ensure the test suite passes.
5. Make sure your code lints.
6. Issue that pull request!

## Pull Request Process

1. Update the README.md with details of changes to the interface, if applicable.
2. Update the API_README.md with details of API changes, if applicable.
3. The PR will be merged once you have the sign-off of at least one maintainer.

## Any contributions you make will be under the MIT Software License

In short, when you submit code changes, your submissions are understood to be under the same [MIT License](LICENSE) that covers the project. Feel free to contact the maintainers if that's a concern.

## Report bugs using GitHub's [issue trackers](https://github.com/your-username/mobilebytelabs-video-sentiment-analysis/issues)

We use GitHub issues to track public bugs. Report a bug by [opening a new issue](https://github.com/your-username/mobilebytelabs-video-sentiment-analysis/issues/new/choose); it's that easy!

**Great Bug Reports** tend to have:

- A quick summary and/or background
- Steps to reproduce
  - Be specific!
  - Give sample code if you can
- What you expected would happen
- What actually happens
- Notes (possibly including why you think this might be happening, or stuff you tried that didn't work)

## Platform Support Guidelines

When adding support for new social media platforms:

1. **Update the platform resolver** in `platform_resolver.py`
2. **Add comprehensive tests** in `test_platform_resolver.py`
3. **Update API documentation** in `API_README.md`
4. **Test with real URLs** from the platform
5. **Consider rate limiting** and terms of service
6. **Document any special requirements**

## Testing

- Run unit tests: `python -m pytest test_platform_resolver.py -v`
- Test API imports: `python -c "from api import app; print('API imports successfully')"`
- Test with sample URLs from different platforms
- Verify error handling for malformed URLs

## Code Style

- We follow PEP 8 for Python code
- Use meaningful variable and function names
- Add docstrings to functions and classes
- Comment complex logic
- Keep functions focused and modular

## License

By contributing, you agree that your contributions will be licensed under its MIT License.