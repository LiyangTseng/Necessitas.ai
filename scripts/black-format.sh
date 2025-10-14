#!/bin/bash
# Comprehensive Black formatting script

set -e

echo "🖤 Running Black code formatting..."

# Format all Python files
echo "Formatting Python files..."
black src/ tests/ scripts/ --line-length=88 --extend-ignore=E203,W503

# Format Jupyter notebooks if any exist
if find . -name "*.ipynb" -not -path "./.git/*" -not -path "./node_modules/*" | grep -q .; then
    echo "Formatting Jupyter notebooks..."
    black --line-length=88 *.ipynb
fi

# Run isort to organize imports
echo "Organizing imports with isort..."
isort src/ tests/ scripts/ --profile black

# Check for any remaining formatting issues
echo "Checking for formatting issues..."
black --check src/ tests/ scripts/ --line-length=88

echo "✅ Black formatting completed successfully!"
