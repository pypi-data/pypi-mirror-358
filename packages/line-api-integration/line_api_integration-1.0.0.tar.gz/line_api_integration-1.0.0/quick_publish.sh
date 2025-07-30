#!/bin/bash
set -e

# Load environment variables from .env file
if [ -f .env ]; then
    echo "Loading environment variables from .env..."
    export $(grep -v '^#' .env | xargs)
fi

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🚀 Quick LINE API Publishing${NC}"
echo "=============================="

# Activate virtual environment
source .venv/bin/activate

# Clean previous builds
echo -e "${GREEN}🧹 Cleaning previous builds...${NC}"
rm -rf dist/ build/ *.egg-info/

# Build the package
echo -e "${GREEN}🔨 Building package...${NC}"
python -m build

# Check package contents
echo -e "${GREEN}🔍 Checking package contents...${NC}"
python -m twine check dist/*

# Get package info
package_version=$(python -c "import tomllib; print(tomllib.load(open('pyproject.toml', 'rb'))['project']['version'])")
package_name=$(python -c "import tomllib; print(tomllib.load(open('pyproject.toml', 'rb'))['project']['name'])")
echo -e "${BLUE}📦 Package: ${package_name} v${package_version}${NC}"

# Upload to Test PyPI first
echo -e "${GREEN}📤 Uploading to Test PyPI...${NC}"
if [ -n "$PYPI_TOKEN" ]; then
    echo "Using PYPI_TOKEN from .env file..."
    python -m twine upload --repository testpypi dist/* --username __token__ --password "$PYPI_TOKEN"
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✅ Successfully uploaded to Test PyPI!${NC}"
        echo "Check your package at: https://test.pypi.org/project/${package_name}/"
        echo ""
        echo "To test installation:"
        echo "pip install --index-url https://test.pypi.org/simple/ ${package_name}"
        
        echo ""
        echo -e "${YELLOW}Do you want to upload to Production PyPI too? (y/N)${NC}"
        read -p ": " confirm
        if [[ $confirm =~ ^[Yy]$ ]]; then
            echo -e "${GREEN}📤 Uploading to Production PyPI...${NC}"
            python -m twine upload dist/* --username __token__ --password "$PYPI_TOKEN"
            if [ $? -eq 0 ]; then
                echo -e "${GREEN}✅ Successfully uploaded to Production PyPI!${NC}"
                echo "Your package is now available at: https://pypi.org/project/${package_name}/"
                echo ""
                echo "Users can install it with:"
                echo "pip install ${package_name}"
            fi
        fi
    fi
else
    echo "PYPI_TOKEN not found in .env file!"
    exit 1
fi

echo -e "${GREEN}🎉 Done!${NC}"
