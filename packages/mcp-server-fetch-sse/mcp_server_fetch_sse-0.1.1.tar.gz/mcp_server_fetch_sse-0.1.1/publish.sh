#!/bin/bash

# Publish script for mcp-server-fetch-sse
# This script helps build and publish the package to PyPI

set -e

echo "🚀 Publishing mcp-server-fetch-sse to PyPI..."

# Check if we're in the right directory
if [ ! -f "pyproject.toml" ]; then
    echo "❌ Error: pyproject.toml not found. Please run this script from the src/fetch directory."
    exit 1
fi

# Check if uv is installed
if ! command -v uv &> /dev/null; then
    echo "❌ Error: uv is not installed. Please install uv first: https://docs.astral.sh/uv/getting-started/installation/"
    exit 1
fi

# Clean previous builds
echo "🧹 Cleaning previous builds..."
rm -rf dist/ build/ *.egg-info/

# Install dependencies
echo "📦 Installing dependencies..."
uv sync --frozen --all-extras --dev

# Run type checking
echo "🔍 Running type checking..."
uv run --frozen pyright

# Build the package
echo "🔨 Building package..."
uv build

# Check what was built
echo "📋 Built packages:"
ls -la dist/

# Ask for confirmation before publishing
echo ""
echo "📤 Ready to publish to PyPI?"
echo "Package name: mcp-server-fetch-sse"
echo "Version: $(grep '^version = ' pyproject.toml | cut -d'"' -f2)"
echo ""
read -p "Do you want to continue? (y/N): " -n 1 -r
echo

if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "🚀 Publishing to PyPI..."
    uv publish
    
    echo "✅ Successfully published mcp-server-fetch-sse to PyPI!"
    echo ""
    echo "📋 Installation instructions:"
    echo "pip install mcp-server-fetch-sse"
    echo ""
    echo "🔧 Usage:"
    echo "mcp-server-fetch-sse"
    echo "mcp-server-fetch-http"
else
    echo "❌ Publishing cancelled."
    exit 1
fi 