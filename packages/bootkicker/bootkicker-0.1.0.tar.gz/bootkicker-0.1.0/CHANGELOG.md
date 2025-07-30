# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2025-06-29

### Added
- Initial release of Bootkicker CLI tool
- Project specification review using multiple LLM models
- Support for OpenRouter API integration
- Parallel model execution with retry logic
- Configuration via YAML files
- Progress tracking with tqdm
- Graceful error handling and fallback mechanisms
- Markdown file processing and merging
- CLI interface with proper argument handling

### Features
- Read configuration from `.review.conf.yml`
- Process multiple markdown files in alphabetical order
- Call multiple LLM models in parallel
- Aggregate and summarize model responses
- Environment variable support for API keys
- Comprehensive error handling and logging
