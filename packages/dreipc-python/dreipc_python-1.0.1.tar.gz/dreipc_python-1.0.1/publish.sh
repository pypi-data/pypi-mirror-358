#!/bin/bash
set -e

echo "🚀 Publishing dreipc-python to PyPI"
echo "===================================="

# Clean previous builds
echo "🧹 Cleaning previous builds..."
rm -rf dist/ build/

# Build package
echo "📦 Building package..."
python -m build

# Check package
echo "🔍 Checking package..."
python -m twine check dist/*

# Upload to TestPyPI first
echo "🧪 Uploading to TestPyPI..."
python -m twine upload --repository testpypi dist/* --verbose

echo "✅ Published to TestPyPI!"
echo "Test with: pip install --index-url https://test.pypi.org/simple/ dreipc-python"
echo ""
echo "If everything works, publish to PyPI with:"
echo "python -m twine upload dist/*"