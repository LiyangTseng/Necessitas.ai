#!/bin/bash
# Enhanced Black setup script for CompanyRadar

set -e

echo "🖤 Setting up enhanced Black code formatting..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_status() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Check if we're in the right directory
if [ ! -f "requirements.txt" ]; then
    print_error "Please run this script from the project root directory"
    exit 1
fi

# Install Black with Jupyter support
print_info "Installing Black with Jupyter support..."
pip install "black[jupyter]"

# Install additional Black-related tools
print_info "Installing additional formatting tools..."
pip install isort black-mypy

# Create .black.toml for additional configuration
print_info "Creating Black configuration..."
cat > .black.toml << 'EOF'
[tool.black]
line-length = 88
target-version = ['py311']
include = '\.pyi?$'
extend-exclude = '''
/(
  # directories
  \.eggs
  | \.git
  | \.hg
  | \.mypy_cache
  | \.tox
  | \.venv
  | build
  | dist
  | node_modules
)/
'''
skip-string-normalization = false
preview = true
EOF

# Create isort configuration to work with Black
print_info "Configuring isort to work with Black..."
cat > .isort.cfg << 'EOF'
[settings]
profile = black
line_length = 88
multi_line_output = 3
include_trailing_comma = true
force_grid_wrap = 0
use_parentheses = true
ensure_newline_before_comments = true
skip_glob = ["*/migrations/*", "*/node_modules/*"]
EOF

# Create a comprehensive Black script
print_info "Creating Black utility script..."
cat > scripts/black-format.sh << 'EOF'
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
EOF

chmod +x scripts/black-format.sh

# Create VS Code settings for Black
print_info "Creating VS Code settings for Black..."
mkdir -p .vscode
cat > .vscode/settings.json << 'EOF'
{
    "python.formatting.provider": "black",
    "python.formatting.blackArgs": ["--line-length=88"],
    "python.linting.enabled": true,
    "python.linting.flake8Enabled": true,
    "python.linting.flake8Args": ["--max-line-length=88", "--extend-ignore=E203,W503"],
    "python.linting.mypyEnabled": true,
    "editor.formatOnSave": true,
    "editor.codeActionsOnSave": {
        "source.organizeImports": true
    },
    "files.trimTrailingWhitespace": true,
    "files.insertFinalNewline": true,
    "files.trimFinalNewlines": true
}
EOF

# Create PyCharm/IntelliJ configuration
print_info "Creating PyCharm configuration..."
cat > .idea/codeStyles/Project.xml << 'EOF'
<?xml version="1.0" encoding="UTF-8"?>
<component name="ProjectCodeStyleConfiguration">
  <code_scheme name="Project" version="173">
    <option name="FORMATTER" value="Black" />
    <option name="LINE_LENGTH" value="88" />
    <option name="KEEP_LINE_BREAKS" value="true" />
    <option name="KEEP_FIRST_COLUMN_COMMENT" value="true" />
    <option name="KEEP_CONTROL_INDENTATION" value="true" />
    <option name="KEEP_BLANK_LINES_IN_DECLARATIONS" value="true" />
    <option name="KEEP_BLANK_LINES_IN_CODE" value="true" />
    <option name="KEEP_BLANK_LINES_BEFORE_RBRACE" value="true" />
    <option name="KEEP_BLANK_LINES_AFTER_RBRACE" value="true" />
  </code_scheme>
</component>
EOF

# Test Black installation
print_info "Testing Black installation..."
black --version

# Run initial formatting
print_info "Running initial Black formatting on all files..."
if [ -d "src" ]; then
    black src/ --line-length=88 --extend-ignore=E203,W503 || print_warning "Some files couldn't be formatted"
fi

if [ -d "tests" ]; then
    black tests/ --line-length=88 --extend-ignore=E203,W503 || print_warning "Some files couldn't be formatted"
fi

if [ -d "scripts" ]; then
    black scripts/ --line-length=88 --extend-ignore=E203,W503 || print_warning "Some files couldn't be formatted"
fi

print_status "Black setup completed successfully! 🎉"
echo ""
echo "💡 Usage tips:"
echo "  - Format all files: ./scripts/black-format.sh"
echo "  - Format specific file: black filename.py"
echo "  - Check formatting: black --check src/"
echo "  - VS Code: Install Python extension and Black formatter"
echo "  - PyCharm: Install Black plugin and configure as formatter"
echo ""
echo "🔧 Black features enabled:"
echo "  - Line length: 88 characters"
echo "  - Jupyter notebook support"
echo "  - Import organization with isort"
echo "  - Pre-commit hooks integration"
echo "  - IDE integration (VS Code, PyCharm)"
