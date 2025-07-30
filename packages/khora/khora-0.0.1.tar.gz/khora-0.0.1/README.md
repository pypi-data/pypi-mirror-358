# Khora

Ad-hoc Dagster pipelines for data fetching using AI/LLM prompts and agentic AI.

## Overview

Khora is a Python package that enables the creation of dynamic data pipelines using Dagster, powered by AI agents built with LangGraph and LangChain. It can fetch data from various sources including:

- APIs (REST endpoints with full HTTP method support)
- Websites (advanced web scraping using Playwright - handles JavaScript, takes screenshots, executes custom scripts)
- Google Docs/Sheets (with service account authentication)

## Features

- 🤖 AI-powered data fetching using natural language prompts
- 🔄 Dynamic pipeline generation based on descriptions
- 🛠️ Support for multiple data sources:
  - APIs (REST endpoints)
  - Web scraping with Playwright (handles JavaScript-rendered content)
  - Google Docs and Sheets
- 🎭 Advanced web scraping capabilities:
  - JavaScript execution
  - Screenshot capture
  - Custom selectors
  - Wait conditions
- 📊 Integration with Dagster for orchestration
- 🐳 Docker support for easy deployment
- ✅ Comprehensive test coverage

## Installation

### Using uv (recommended)

```bash
uv pip install khora
```

### Using pip

```bash
pip install khora
```

### Development Installation

```bash
git clone https://github.com/yourusername/khora.git
cd khora
uv pip install -e ".[dev]"
```

## Configuration

1. Copy the environment template:
```bash
cp .env.example .env
```

2. Edit `.env` and add your credentials:
- `OPENAI_API_KEY`: Your OpenAI API key
- `GOOGLE_CREDENTIALS_PATH`: Path to Google service account credentials (for Google Docs/Sheets)

## Usage

### Basic Example

```python
from khora.agents import DataFetcherAgent, PipelineBuilderAgent
from khora.utils.data_models import DataRequest, DataSourceType

# Initialize agents
fetcher = DataFetcherAgent(openai_api_key="your-key")
builder = PipelineBuilderAgent(openai_api_key="your-key")

# Create a data request
request = DataRequest(
    source_type=DataSourceType.API,
    prompt="Fetch current weather data for San Francisco",
    source_config={
        "url": "https://api.weather.com/v1/current"
    }
)

# Fetch data
response = await fetcher.fetch_data(request)
print(response.data)
```

### Creating Dynamic Pipelines

```python
# Describe your pipeline in natural language
description = """
Create a pipeline that:
1. Fetches cryptocurrency prices from CoinGecko API
2. Scrapes latest crypto news from CoinDesk
3. Reads analysis from a Google Sheet
"""

# Generate pipeline configuration
config = builder.analyze_pipeline_request(description)

# Build and execute the pipeline
pipeline = builder.build_pipeline(config)
```

### Running Dagster UI

```bash
dagster dev -f src/khora/pipelines/definitions.py
```

Then navigate to http://localhost:3000 to see the Dagster UI.

## Docker Usage

### Build the image

```bash
docker build -t khora:latest .
```

### Run the container

```bash
docker run -p 3000:3000 \
  -e OPENAI_API_KEY=your-key \
  -v $(pwd)/.env:/app/.env \
  khora:latest
```

## Testing

Run the test suite:

```bash
pytest tests/
```

With coverage:

```bash
pytest tests/ --cov=khora --cov-report=html
```

## Requirements

- Python 3.12 (required)
- Playwright browsers (automatically installed during setup)

## CI/CD

The project uses GitHub Actions for CI/CD with two main workflows:

### Main CI Workflow (`ci.yml`)
1. Runs tests on Python 3.12
2. Checks code formatting with Black and Ruff
3. Performs type checking with mypy
4. Builds and tests the Docker image
5. Uploads coverage reports to Codecov

### Publish Workflow (`publish.yml`)
**Automatically publishes to PyPI** when version tags are pushed:
- Triggered by pushing tags matching `v*` pattern (e.g., `v0.0.2`)
- Runs full test suite and quality checks
- Builds and publishes package to PyPI
- Uses `PYPI_API_TOKEN` secret for authentication

## Project Structure

```
khora/
├── src/khora/
│   ├── agents/         # AI agents for data fetching and pipeline building
│   ├── pipelines/      # Dagster pipeline definitions
│   ├── tools/          # Tools for different data sources
│   └── utils/          # Utilities and data models
├── tests/              # Test suite
├── .github/workflows/  # CI/CD configuration
├── Dockerfile          # Container definition
└── pyproject.toml      # Project configuration
```

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Make your changes and add tests
4. Run tests and linting: `pytest && black . && ruff check .`
5. Commit your changes: `git commit -m "Add feature"`
6. Push to your fork: `git push origin feature-name`
7. Create a pull request

## License

MIT License - see LICENSE file for details.

## Support

For issues and questions:
- Open an issue on GitHub
- Check the documentation
- Review existing discussions

## Roadmap

- [ ] Add support for more data sources (databases, S3, etc.)
- [ ] Implement data transformation capabilities
- [ ] Add scheduling and monitoring features
- [ ] Create a web UI for pipeline management
- [ ] Support for more LLM providers

## Releasing

### Quick Release (Recommended)

Use the automated release script:

```bash
# Create and push a patch release (0.0.1 -> 0.0.2)
python scripts/create_release.py patch --push

# Create a minor release (0.0.1 -> 0.1.0)
python scripts/create_release.py minor

# Create a major release (0.0.1 -> 1.0.0)
python scripts/create_release.py major

# Preview what would happen
python scripts/create_release.py patch --dry-run
```

### Step-by-Step Release

1. **Bump version**:
   ```bash
   python scripts/bump_version.py patch
   ```

2. **Create git tag and push**:
   ```bash
   git add .
   git commit -m "Bump version to 0.0.2"
   git tag v0.0.2
   git push origin main --tags
   ```

3. **Automatic publishing**: The publish workflow will automatically:
   - Run all tests and quality checks
   - Build the package
   - Publish to PyPI

### Setup PyPI Token

To enable publishing, add your PyPI API token as a GitHub secret:
1. Create an API token on [PyPI](https://pypi.org/manage/account/token/)
2. Add it as `PYPI_API_TOKEN` in your repository secrets

## Version

Current version: 0.0.1
