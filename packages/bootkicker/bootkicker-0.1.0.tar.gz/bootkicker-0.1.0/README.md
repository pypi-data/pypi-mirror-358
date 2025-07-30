# Bootkicker - Project Specification Review Tool

An AI-powered CLI tool that analyzes project specifications and provides intelligent improvement suggestions using multiple Large Language Models.

## Features

- 🤖 **Multi-Model Analysis**: Leverages multiple LLMs for comprehensive reviews
- ⚡ **Parallel Processing**: Calls multiple models simultaneously for faster results
- 🔄 **Robust Error Handling**: Automatic retries and graceful failure handling
- 📊 **Progress Tracking**: Real-time progress bars for long-running operations
- 📝 **Markdown Support**: Processes and merges multiple markdown specification files
- ⚙️ **Configurable**: YAML-based configuration for model selection and settings
- 🔑 **OpenRouter Integration**: Uses OpenRouter API for access to various LLM providers

## Installation

### From PyPI (Recommended)

```bash
pip install bootkicker
```

### From Source

```bash
git clone <repository-url>
cd bootkicker
pip install -e .
```

## Quick Start

1. **Set up your API key**:
   ```bash
   export OPENROUTER_API_KEY="your_api_key_here"
   ```

2. **Create a configuration file** (`.review.conf.yml`) in your project directory:
   ```yaml
   models:
     - "openai/gpt-4"
     - "anthropic/claude-3-sonnet"
     - "google/gemini-pro"
     - "meta-llama/llama-2-70b-chat"
   
   summarizer: "google/gemini-2.5-flash"
   ```

3. **Add your project specification** as markdown files in the same directory

4. **Run the review**:
   ```bash
   bootkicker /path/to/your/project/directory
   ```

## Configuration

### Configuration File Format

Create a `.review.conf.yml` file in your project directory:

```yaml
# Required: List of models to use for review
models:
  - "openai/gpt-4"
  - "anthropic/claude-3-sonnet"
  - "google/gemini-pro"
  - "deepseek/deepseek-chat"

# Optional: Model for final summarization (default: google/gemini-2.5-flash)
summarizer: "google/gemini-2.5-flash"
```

### Environment Variables

- `OPENROUTER_API_KEY`: Your OpenRouter API key (required)

### Supported File Types

- All `.md` (Markdown) files in the specified directory
- Files are processed in alphabetical order
- Content is merged with proper headers and separators

## Usage Examples

### Basic Usage
```bash
bootkicker ./my-project
```

### With Custom Directory
```bash
bootkicker /path/to/project/specs
```

### Example Output
```
# Project Review Results

Based on analysis from 4 model(s):

## Review 1

[Detailed feedback from first model...]

---

## Review 2

[Detailed feedback from second model...]

---

[Final summarized recommendations...]
```

## Algorithm Implementation

The tool implements a comprehensive review workflow:

### ✅ A1 - Configuration Reading
- Reads `.review.conf.yml` from specified directory
- Validates model list and configuration format
- Supports optional summarizer model configuration

### ✅ A2 - Markdown File Processing
- Discovers all `.md` files in alphabetical order
- Validates file existence and readability
- Fails gracefully if no markdown files found

### ✅ A3 - Content Merging
- Merges multiple markdown files with proper headers
- Preserves file structure and organization
- Handles empty files gracefully

### ✅ A4 - Multi-Model Analysis
- Uses OpenRouter API with environment-based authentication
- Executes model calls in parallel for efficiency
- Implements retry logic (2 retries per model)
- Reports failures to stderr while continuing with successful models
- Aggregates all successful responses into structured output

### ✅ A5 - Intelligent Summarization
- Uses dedicated summarizer model for final synthesis
- Organizes feedback by themes and priorities
- Provides actionable recommendations
- Falls back to aggregated review if summarization fails

## Error Handling

The tool provides comprehensive error handling:

- **Missing configuration**: Clear error with file path
- **Invalid YAML**: Detailed parsing error information
- **Missing API key**: Environment variable guidance
- **API failures**: Automatic retries with progress reporting
- **No markdown files**: Helpful error message
- **Network issues**: Graceful degradation and fallback

## Development

### Requirements

- Python 3.12+
- OpenRouter API key
- Dependencies: `openai`, `langchain`, `tqdm`, `pyyaml`, `aiohttp`

### Testing

Run with the provided test configuration:

```bash
export OPENROUTER_API_KEY="your_key"
bootkicker test
```

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Contributing

Contributions are welcome! Please feel free to submit issues and enhancement requests.

## Changelog

See [CHANGELOG.md](CHANGELOG.md) for version history and changes.
