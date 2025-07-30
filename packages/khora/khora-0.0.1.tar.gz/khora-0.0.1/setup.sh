#!/bin/bash

# Khora Project Setup Script

echo "🚀 Setting up Khora project..."
echo "================================"

# Check if uv is installed
if ! command -v uv &> /dev/null; then
    echo "📦 Installing uv package manager..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
    export PATH="$HOME/.cargo/bin:$PATH"
fi

# Create virtual environment and install dependencies
echo "🔧 Creating virtual environment and installing dependencies..."
uv venv
source .venv/bin/activate || source .venv/Scripts/activate

# Install the package in editable mode with dev dependencies
echo "📚 Installing Khora with development dependencies..."
uv pip install -e ".[dev]"

# Install Playwright browsers
echo "🌐 Installing Playwright browsers..."
playwright install chromium

# Copy environment template if .env doesn't exist
if [ ! -f .env ]; then
    echo "📋 Creating .env file from template..."
    cp env.example .env
    echo "⚠️  Please edit .env and add your API keys!"
fi

# Create necessary directories
echo "📁 Creating necessary directories..."
mkdir -p dagster_home
mkdir -p credentials

# Run initial tests
echo "🧪 Running tests..."
pytest tests/unit -v

echo ""
echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "1. Edit .env file and add your API keys:"
echo "   - OPENAI_API_KEY"
echo "   - GOOGLE_CREDENTIALS_PATH (optional)"
echo ""
echo "2. Activate the virtual environment:"
echo "   source .venv/bin/activate"
echo ""
echo "3. Run Dagster UI:"
echo "   dagster dev -f src/khora/pipelines/definitions.py"
echo ""
echo "4. Or use the CLI:"
echo "   python -m khora --help"
echo ""
echo "Happy data fetching! 🎉"
