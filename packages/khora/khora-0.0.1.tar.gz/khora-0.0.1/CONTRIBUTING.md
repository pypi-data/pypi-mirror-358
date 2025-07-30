# Contributing to Khora

Thank you for your interest in contributing to Khora! This guide will help you get started.

## Development Setup

1. **Clone the repository**:
   ```bash
   git clone https://github.com/yourusername/khora.git
   cd khora
   ```

2. **Run the setup script**:
   ```bash
   ./setup.sh
   ```

3. **Activate the virtual environment**:
   ```bash
   source .venv/bin/activate
   ```

## Development Workflow

1. **Create a feature branch**:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes**:
   - Write code following the project style
   - Add tests for new functionality
   - Update documentation as needed

3. **Run tests and checks**:
   ```bash
   # Run tests
   pytest tests/

   # Format code
   black src tests
   ruff format src tests

   # Check linting
   ruff check src tests

   # Type checking
   mypy src
   ```

4. **Commit and push**:
   ```bash
   git add .
   git commit -m "Add your feature description"
   git push origin feature/your-feature-name
   ```

5. **Create a Pull Request**:
   - Open a PR against the `main` branch
   - Provide a clear description of your changes
   - Wait for review and CI checks to pass

## Code Style

- Use Black for code formatting (line length: 88)
- Follow Ruff linting rules
- Use type hints where appropriate
- Write docstrings for functions and classes
- Keep functions focused and concise

## Testing

- Write unit tests for new functionality
- Place tests in the appropriate `tests/` subdirectory
- Use descriptive test names
- Mock external dependencies
- Aim for good test coverage

## Releasing (Maintainers Only)

### PyPI Setup for Publishing

The project uses PyPI API tokens for publishing. To set this up:

1. **Create PyPI API Token**:
   - Go to [PyPI account settings](https://pypi.org/manage/account/token/)
   - Create a new API token with upload permissions
   - Copy the token (starts with `pypi-`)

2. **Add GitHub Secret**:
   - Go to repository Settings > Secrets and variables > Actions
   - Create a new secret named `PYPI_API_TOKEN`
   - Paste your PyPI API token as the value

### Creating a Release

Use the automated release script:

```bash
# Create complete release with tests and git operations
python scripts/create_release.py patch

# Or with automatic push
python scripts/create_release.py patch --push

# Preview changes first
python scripts/create_release.py minor --dry-run
```

The publish workflow will automatically:
1. Trigger when you push a version tag (e.g., `v0.0.2`)
2. Run all tests and quality checks
3. Build the package
4. Publish to PyPI if all checks pass

### Version Numbering

Follow [Semantic Versioning](https://semver.org/):
- **MAJOR**: Breaking changes
- **MINOR**: New features (backwards compatible)
- **PATCH**: Bug fixes (backwards compatible)

## Project Structure

```
khora/
├── src/khora/              # Main package
│   ├── agents/             # AI agents
│   ├── pipelines/          # Dagster pipelines
│   ├── tools/              # Data source tools
│   └── utils/              # Utilities
├── tests/                  # Test suite
│   ├── unit/               # Unit tests
│   └── integration/        # Integration tests
├── scripts/                # Development scripts
├── examples/               # Usage examples
└── .github/workflows/      # CI/CD
```

## Adding New Data Sources

To add a new data source:

1. **Create a tool** in `src/khora/tools/`:
   - Inherit from `BaseTool`
   - Implement `_run()` and `_arun()` methods
   - Add proper error handling

2. **Add to enum** in `src/khora/utils/data_models.py`:
   - Add new source type to `DataSourceType`

3. **Update agent** in `src/khora/agents/data_fetcher.py`:
   - Add tool to the `tools` dictionary

4. **Write tests**:
   - Add unit tests in `tests/unit/test_tools.py`
   - Mock external dependencies

5. **Add examples**:
   - Create usage examples in `examples/`

## Getting Help

- Open an issue for bugs or feature requests
- Join discussions for questions
- Check existing issues before creating new ones

Thank you for contributing! 🚀
