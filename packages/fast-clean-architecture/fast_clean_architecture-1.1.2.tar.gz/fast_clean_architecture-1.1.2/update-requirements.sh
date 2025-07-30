#!/bin/bash
# update-requirements.sh
# Script to update requirements.txt files from Poetry dependencies

set -e

echo "🔄 Updating requirements.txt files from Poetry dependencies..."

# Check if Poetry is installed
if ! command -v poetry &> /dev/null; then
    echo "❌ Poetry is not installed. Please install Poetry first."
    echo "   Visit: https://python-poetry.org/docs/#installation"
    exit 1
fi

# Check if pyproject.toml exists
if [ ! -f "pyproject.toml" ]; then
    echo "❌ pyproject.toml not found. Are you in the project root directory?"
    exit 1
fi

# Update poetry.lock if needed
echo "📦 Updating Poetry lock file..."
poetry lock --no-update

# Export main requirements
echo "📝 Generating requirements.txt..."
poetry export -f requirements.txt --output requirements.txt

# Export dev requirements
echo "📝 Generating requirements-dev.txt..."
poetry export -f requirements.txt --output requirements-dev.txt --extras dev

echo "✅ Requirements files updated successfully!"
echo "   - requirements.txt (production dependencies)"
echo "   - requirements-dev.txt (development dependencies)"
echo ""
echo "💡 Tip: Add this script to your pre-commit hooks to keep requirements.txt in sync."