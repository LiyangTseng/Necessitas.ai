#!/bin/bash
# Comprehensive linting and code quality check script

set -e

echo "🔍 Running comprehensive code quality checks..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}✅ $1${NC}"
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

# 1. Check for trailing whitespace
echo "🔍 Checking for trailing whitespace..."
if command -v grep &> /dev/null; then
    # Find files with trailing whitespace
    TRAILING_WHITESPACE=$(find . -type f \( -name "*.py" -o -name "*.js" -o -name "*.ts" -o -name "*.jsx" -o -name "*.tsx" -o -name "*.md" -o -name "*.yml" -o -name "*.yaml" \) -exec grep -l '[[:space:]]$' {} \; 2>/dev/null || true)

    if [ -n "$TRAILING_WHITESPACE" ]; then
        print_error "Found trailing whitespace in the following files:"
        echo "$TRAILING_WHITESPACE"
        echo ""
        echo "To fix trailing whitespace, run:"
        echo "  find . -type f \( -name '*.py' -o -name '*.js' -o -name '*.ts' -o -name '*.jsx' -o -name '*.tsx' -o -name '*.md' -o -name '*.yml' -o -name '*.yaml' \) -exec sed -i 's/[[:space:]]*$//' {} \;"
        exit 1
    else
        print_status "No trailing whitespace found"
    fi
else
    print_warning "grep not found, skipping trailing whitespace check"
fi

# 2. Python linting
echo "🐍 Running Python linting..."
if command -v python &> /dev/null; then
    # Install dependencies if needed
    if [ ! -d "venv" ]; then
        print_warning "Creating virtual environment..."
        python -m venv venv
    fi

    source venv/bin/activate
    pip install -q -r requirements.txt

    # Run flake8
    if command -v flake8 &> /dev/null; then
        echo "Running flake8..."
        flake8 src/ tests/ --max-line-length=88 --extend-ignore=E203,W503 || {
            print_error "Flake8 found issues"
            exit 1
        }
        print_status "Flake8 passed"
    else
        print_warning "flake8 not found, skipping Python linting"
    fi

    # Run black
    if command -v black &> /dev/null; then
        echo "Running black..."
        black --check src/ tests/ --line-length=88 || {
            print_error "Black found formatting issues"
            echo "To fix, run: black src/ tests/ --line-length=88"
            exit 1
        }
        print_status "Black passed"
    else
        print_warning "black not found, skipping Black formatting check"
    fi

    # Run mypy
    if command -v mypy &> /dev/null; then
        echo "Running mypy..."
        mypy src/ --ignore-missing-imports || {
            print_error "MyPy found type issues"
            exit 1
        }
        print_status "MyPy passed"
    else
        print_warning "mypy not found, skipping type checking"
    fi

    deactivate
else
    print_warning "Python not found, skipping Python linting"
fi

# 3. JavaScript/TypeScript linting
echo "🟨 Running JavaScript/TypeScript linting..."
if [ -d "frontend" ]; then
    cd frontend

    if [ -f "package.json" ]; then
        # Install dependencies if needed
        if [ ! -d "node_modules" ]; then
            print_warning "Installing frontend dependencies..."
            npm install
        fi

        # Run ESLint
        if npm list eslint &> /dev/null; then
            echo "Running ESLint..."
            npm run lint || {
                print_error "ESLint found issues"
                exit 1
            }
            print_status "ESLint passed"
        else
            print_warning "ESLint not found, skipping JavaScript linting"
        fi

        # Run Prettier
        if npm list prettier &> /dev/null; then
            echo "Running Prettier..."
            npm run format:check || {
                print_error "Prettier found formatting issues"
                echo "To fix, run: npm run format"
                exit 1
            }
            print_status "Prettier passed"
        else
            print_warning "Prettier not found, skipping formatting check"
        fi
    else
        print_warning "No package.json found in frontend directory"
    fi

    cd ..
else
    print_warning "Frontend directory not found, skipping JavaScript linting"
fi

# 4. YAML linting
echo "📄 Running YAML linting..."
if command -v yamllint &> /dev/null; then
    yamllint . || {
        print_error "Yamllint found issues"
        exit 1
    }
    print_status "Yamllint passed"
else
    print_warning "yamllint not found, skipping YAML linting"
fi

# 5. Check for large files
echo "📦 Checking for large files..."
LARGE_FILES=$(find . -type f -size +1M -not -path "./.git/*" -not -path "./node_modules/*" -not -path "./venv/*" -not -path "./.venv/*" 2>/dev/null || true)
if [ -n "$LARGE_FILES" ]; then
    print_warning "Found large files (>1MB):"
    echo "$LARGE_FILES"
    echo "Consider adding them to .gitignore or using Git LFS"
else
    print_status "No large files found"
fi

# 6. Check for secrets
echo "🔐 Checking for potential secrets..."
SECRET_PATTERNS=(
    "password\s*=\s*['\"][^'\"]+['\"]"
    "api_key\s*=\s*['\"][^'\"]+['\"]"
    "secret\s*=\s*['\"][^'\"]+['\"]"
    "token\s*=\s*['\"][^'\"]+['\"]"
    "aws_access_key"
    "aws_secret_key"
    "private_key"
)

SECRETS_FOUND=false
for pattern in "${SECRET_PATTERNS[@]}"; do
    if grep -r -i -E "$pattern" . --exclude-dir=.git --exclude-dir=node_modules --exclude-dir=venv --exclude-dir=.venv --exclude="*.pyc" --exclude="*.log" 2>/dev/null; then
        SECRETS_FOUND=true
    fi
done

if [ "$SECRETS_FOUND" = true ]; then
    print_warning "Potential secrets found in code. Please review and remove if necessary."
else
    print_status "No obvious secrets found"
fi

# 7. Check for TODO/FIXME comments
echo "📝 Checking for TODO/FIXME comments..."
TODO_COUNT=$(grep -r -i "TODO\|FIXME\|HACK\|XXX" . --exclude-dir=.git --exclude-dir=node_modules --exclude-dir=venv --exclude-dir=.venv --exclude="*.pyc" --exclude="*.log" 2>/dev/null | wc -l || echo "0")
if [ "$TODO_COUNT" -gt 0 ]; then
    print_warning "Found $TODO_COUNT TODO/FIXME comments. Consider addressing them before production."
else
    print_status "No TODO/FIXME comments found"
fi

print_status "All code quality checks completed successfully! 🎉"
