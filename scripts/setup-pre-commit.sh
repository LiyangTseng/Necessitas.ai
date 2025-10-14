#!/bin/bash
# Setup script for pre-commit hooks

echo "🔧 Setting up pre-commit hooks for CompanyRadar..."

# Install pre-commit if not already installed
if ! command -v pre-commit &> /dev/null; then
    echo "📦 Installing pre-commit..."
    pip install pre-commit
fi

# Install the pre-commit hooks
echo "🔗 Installing pre-commit hooks..."
pre-commit install

# Run pre-commit on all files to fix existing issues
echo "🧹 Running pre-commit on all files to fix existing issues..."
pre-commit run --all-files

echo "✅ Pre-commit hooks setup complete!"
echo ""
echo "💡 Tips:"
echo "  - Pre-commit will automatically run before each commit"
echo "  - To run manually: pre-commit run --all-files"
echo "  - To skip hooks: git commit --no-verify"
echo "  - To update hooks: pre-commit autoupdate"
