#!/bin/bash

# Build and Install 3PC Python CLI Package
# This script helps you build and install the 3PC Python CLI package locally

set -e

echo "🚀 DreiPC Python CLI - Build and Install Script"
echo "==============================================="

# Check if we're in the right directory by looking for the package structure
if [ ! -f "pyproject.toml" ]; then
    echo "❌ Error: pyproject.toml not found"
    echo "   Make sure you're in the package root directory"
    exit 1
fi

# Check if the package directory exists (either dreipc_python or src/dreipc_python)
if [ ! -d "dreipc_python" ] && [ ! -d "src/dreipc_python" ]; then
    echo "❌ Error: Package directory not found"
    echo "   Expected to find 'dreipc_python/' directory"
    echo "   Current directory contents:"
    ls -la
    exit 1
fi

echo "✅ Found package structure"

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Error: Python 3 is not installed or not in PATH"
    exit 1
fi

# Check Python version
python_version=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
echo "✅ Python version: $python_version"

# Extract major and minor version numbers
major=$(echo $python_version | cut -d. -f1)
minor=$(echo $python_version | cut -d. -f2)

# Check if Python version is 3.8 or higher
if [ "$major" -lt 3 ] || ([ "$major" -eq 3 ] && [ "$minor" -lt 8 ]); then
    echo "❌ Error: Python 3.8+ is required, found $python_version"
    exit 1
fi

echo "✅ Python version $python_version is compatible"

# Check if pip is available
if ! command -v pip &> /dev/null && ! command -v pip3 &> /dev/null; then
    echo "❌ Error: pip is not installed or not in PATH"
    exit 1
fi

# Use pip3 if available, otherwise pip
PIP_CMD="pip"
if command -v pip3 &> /dev/null; then
    PIP_CMD="pip3"
fi

echo ""
echo "📦 Building the package..."

# Clean previous builds
rm -rf dist/ build/ *.egg-info/

# Install build tools if needed
echo "Installing build dependencies..."
$PIP_CMD install --upgrade build wheel

# Build the package
python3 -m build

echo "✅ Package built successfully!"

echo ""
echo "📥 Installing the package..."

# Install the package in development mode
$PIP_CMD install -e .

echo "✅ Package installed successfully!"

echo ""
echo "🧪 Testing the installation..."

# Test the installation - note the command name uses hyphens, not underscores
if command -v dreipc-python &> /dev/null; then
    echo "✅ dreipc-python command is available!"
    
    # Show version
    echo ""
    echo "📋 Package info:"
    dreipc-python --version
    
    echo ""
    echo "🎉 Installation successful!"
    echo ""
    echo "You can now use the dreipc-python command:"
    echo "  dreipc-python create my-awesome-api"
    echo "  dreipc-python create my-api --interactive"
    echo "  dreipc-python --help"
    
else
    echo "❌ Error: dreipc-python command not found in PATH"
    echo "   You may need to restart your terminal or add the installation directory to PATH"
    echo "   Try running: hash -r"
    exit 1
fi

echo ""
echo "📚 Next steps:"
echo "1. Create a new FastAPI project:"
echo "   dreipc-python create my-awesome-api"
echo ""
echo "2. Navigate to your project:"
echo "   cd my-awesome-api"
echo ""
echo "3. Install project dependencies:"
echo "   poetry install"
echo ""
echo "4. Run your FastAPI app:"
echo "   make run"
echo ""
echo "Happy coding! 🚀"