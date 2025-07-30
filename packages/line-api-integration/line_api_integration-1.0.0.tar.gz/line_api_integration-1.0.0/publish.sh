#!/bin/bash
set -e

# Load environment variables from .env file
if [ -f .env ]; then
    echo "Loading environment variables from .env..."
    export $(grep -v '^#' .env | xargs)
fi

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🚀 LINE API Integration Library - Publishing Script${NC}"
echo "=================================================="set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${GREEN}🚀 LINE API Integration Library - Publishing Script${NC}"
echo "======================================================="

# Check if we're in the right directory
if [ ! -f "pyproject.toml" ]; then
    echo -e "${RED}❌ pyproject.toml not found. Please run this script from the project root.${NC}"
    exit 1
fi

# Check if we're on the release branch
current_branch=$(git branch --show-current)
if [[ ! "$current_branch" =~ ^release/ ]]; then
    echo -e "${YELLOW}⚠️  You're not on a release branch. Current branch: $current_branch${NC}"
    read -p "Continue anyway? (y/N): " confirm
    if [[ ! $confirm =~ ^[Yy]$ ]]; then
        echo -e "${YELLOW}Publishing cancelled.${NC}"
        exit 1
    fi
fi

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check required tools
echo -e "${GREEN}🔍 Checking prerequisites...${NC}"

if ! command_exists python; then
    echo -e "${RED}❌ Python not found${NC}"
    exit 1
fi

if ! command_exists uv; then
    echo -e "${YELLOW}⚠️  UV not found. Installing...${NC}"
    curl -LsSf https://astral.sh/uv/install.sh | sh
    source $HOME/.cargo/env
    if ! command_exists uv; then
        echo -e "${RED}❌ Failed to install UV${NC}"
        exit 1
    fi
fi

# Check if virtual environment exists and activate
if [ ! -d ".venv" ]; then
    echo -e "${GREEN}🔧 Creating virtual environment with uv...${NC}"
    uv venv
fi

echo -e "${GREEN}🔧 Activating virtual environment...${NC}"
source .venv/bin/activate

# Install dependencies
echo -e "${GREEN}📦 Installing dependencies with uv...${NC}"
uv sync --dev

# Install build tools
echo -e "${GREEN}📦 Installing build tools...${NC}"
uv pip install --upgrade build twine

# Run linting and type checking
echo -e "${GREEN}🔍 Running code quality checks...${NC}"
echo "Running ruff..."
uv run ruff check line_api/
if [ $? -ne 0 ]; then
    echo -e "${YELLOW}⚠️  Ruff found linting issues. Continue anyway? (y/N)${NC}"
    read -p ": " lint_confirm
    if [[ ! $lint_confirm =~ ^[Yy]$ ]]; then
        echo -e "${RED}❌ Linting failed! Aborting publish.${NC}"
        exit 1
    fi
fi

echo "Running mypy..."
uv run mypy line_api/
if [ $? -ne 0 ]; then
    echo -e "${YELLOW}⚠️  MyPy found type issues. Continue anyway? (y/N)${NC}"
    read -p ": " confirm
    if [[ ! $confirm =~ ^[Yy]$ ]]; then
        echo -e "${RED}❌ Type checking failed! Aborting publish.${NC}"
        exit 1
    fi
fi

# Run tests
echo -e "${GREEN}🧪 Running tests...${NC}"
uv run pytest tests/ -v --cov=line_api --cov-report=term-missing
if [ $? -ne 0 ]; then
    echo -e "${RED}❌ Tests failed! Aborting publish.${NC}"
    exit 1
fi

# Check if everything is committed
if [ -n "$(git status --porcelain)" ]; then
    echo -e "${YELLOW}⚠️  You have uncommitted changes:${NC}"
    git status --short
    read -p "Commit changes before publishing? (y/N): " commit_confirm
    if [[ $commit_confirm =~ ^[Yy]$ ]]; then
        read -p "Enter commit message: " commit_msg
        git add .
        git commit -m "$commit_msg"
    else
        echo -e "${YELLOW}⚠️  Publishing with uncommitted changes. This is not recommended.${NC}"
    fi
fi

# Clean previous builds
echo -e "${GREEN}🧹 Cleaning previous builds...${NC}"
rm -rf dist/ build/ *.egg-info/

# Build the package
echo -e "${GREEN}🔨 Building package...${NC}"
python -m build

# Check if dist directory was created and has files
if [ ! -d "dist" ] || [ -z "$(ls -A dist)" ]; then
    echo -e "${RED}❌ Build failed! No distribution files found.${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Package built successfully!${NC}"
echo "Distribution files created:"
ls -la dist/

# Get package version from pyproject.toml
package_version=$(python -c "import tomllib; print(tomllib.load(open('pyproject.toml', 'rb'))['project']['version'])")
package_name=$(python -c "import tomllib; print(tomllib.load(open('pyproject.toml', 'rb'))['project']['name'])")

echo -e "${BLUE}📦 Package: ${package_name} v${package_version}${NC}"

# Check package contents
echo -e "${GREEN}🔍 Checking package contents...${NC}"
python -m twine check dist/*
if [ $? -ne 0 ]; then
    echo -e "${RED}❌ Package validation failed!${NC}"
    exit 1
fi

# Ask user what to do next
echo ""
echo -e "${YELLOW}📤 What would you like to do next?${NC}"
echo "1) Upload to Test PyPI (recommended for first release)"
echo "2) Upload to PyPI (production)"
echo "3) Create GitHub release tag"
echo "4) Exit without publishing"
read -p "Choose option (1-4): " choice

case $choice in
    1)
        echo -e "${GREEN}📤 Uploading to Test PyPI...${NC}"
        if [ -n "$PYPI_TOKEN" ]; then
            echo "Using PYPI_TOKEN from .env file..."
            python -m twine upload --repository testpypi dist/* --username __token__ --password "$PYPI_TOKEN"
        else
            echo "You will need your Test PyPI API token."
            echo "Create one at: https://test.pypi.org/manage/account/token/"
            python -m twine upload --repository testpypi dist/*
        fi
        if [ $? -eq 0 ]; then
            echo -e "${GREEN}✅ Successfully uploaded to Test PyPI!${NC}"
            echo "Check your package at: https://test.pypi.org/project/${package_name}/"
            echo ""
            echo "To test installation:"
            echo "pip install --index-url https://test.pypi.org/simple/ ${package_name}"
        fi
        ;;
    2)
        echo -e "${GREEN}📤 Uploading to PyPI...${NC}"
        if [ -n "$PYPI_TOKEN" ]; then
            echo "Using PYPI_TOKEN from .env file..."
            echo -e "${YELLOW}⚠️  This will make your package publicly available!${NC}"
            read -p "Are you sure you want to publish v${package_version} to PyPI? (y/N): " confirm
            if [[ $confirm =~ ^[Yy]$ ]]; then
                python -m twine upload dist/* --username __token__ --password "$PYPI_TOKEN"
                if [ $? -eq 0 ]; then
                echo -e "${GREEN}✅ Successfully uploaded to PyPI!${NC}"
                echo "Your package is now available at: https://pypi.org/project/${package_name}/"
                echo ""
                echo "Users can install it with:"
                echo "pip install ${package_name}"

            fi
        else
            echo "You will need your PyPI API token."
            echo "Create one at: https://pypi.org/manage/account/token/"
            echo -e "${YELLOW}⚠️  This will make your package publicly available!${NC}"
            read -p "Are you sure you want to publish v${package_version} to PyPI? (y/N): " confirm
            if [[ $confirm =~ ^[Yy]$ ]]; then
                python -m twine upload dist/*
                if [ $? -eq 0 ]; then
                    echo -e "${GREEN}✅ Successfully uploaded to PyPI!${NC}"
                    echo "Your package is now available at: https://pypi.org/project/${package_name}/"
                    echo ""
                    echo "Users can install it with:"
                    echo "pip install ${package_name}"

                    # Ask about creating a git tag
                    echo ""
                    read -p "Create a git tag for this release? (y/N): " tag_confirm
                    if [[ $tag_confirm =~ ^[Yy]$ ]]; then
                        git tag -a "v${package_version}" -m "Release v${package_version}"
                        echo -e "${GREEN}✅ Created git tag v${package_version}${NC}"
                        echo "Push to remote with: git push origin v${package_version}"
                    fi
                fi
            else
                echo -e "${YELLOW}Upload cancelled.${NC}"
            fi
        fi
        ;;
    3)
        echo -e "${GREEN}🏷️  Creating GitHub release tag...${NC}"
        git tag -a "v${package_version}" -m "Release v${package_version}"
        echo -e "${GREEN}✅ Created git tag v${package_version}${NC}"
        echo "Push to remote with: git push origin v${package_version}"
        echo "Then create a GitHub release at: https://github.com/yourusername/${package_name}/releases/new"
        ;;
    4)
        echo -e "${GREEN}👋 Exiting without publishing.${NC}"
        echo "Your package is built and ready in the dist/ directory."
        ;;
    *)
        echo -e "${RED}❌ Invalid option.${NC}"
        exit 1
        ;;
esac

echo ""
echo -e "${GREEN}🎉 Done!${NC}"
echo ""
echo -e "${BLUE}📝 Next steps:${NC}"
echo "• Update CHANGELOG.md with release notes"
echo "• Update README.md if needed"
echo "• Consider updating version number for next development cycle"
echo "• Push your release branch and create a pull request"
