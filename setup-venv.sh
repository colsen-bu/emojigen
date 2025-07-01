#!/bin/bash
# Virtual Environment Setup Script for Discord Emoji Bot
# This script sets up a clean Python virtual environment for development

set -e  # Exit on any error

PROJECT_NAME="emoji_gen_bot"
VENV_DIR="venv"
PYTHON_VERSION="python3"

echo "🐍 Setting up Python Virtual Environment for $PROJECT_NAME"
echo "=================================================="

# Check if Python 3 is available
if ! command -v $PYTHON_VERSION &> /dev/null; then
    echo "❌ Python 3 is not installed or not in PATH"
    echo "Please install Python 3.8 or later"
    exit 1
fi

# Display Python version
PYTHON_VER=$($PYTHON_VERSION --version)
echo "✅ Found $PYTHON_VER"

# Remove existing virtual environment if it exists
if [ -d "$VENV_DIR" ]; then
    echo "🗑️  Removing existing virtual environment..."
    rm -rf "$VENV_DIR"
fi

# Create new virtual environment
echo "🏗️  Creating new virtual environment..."
$PYTHON_VERSION -m venv "$VENV_DIR"

# Activate virtual environment
echo "⚡ Activating virtual environment..."
source "$VENV_DIR/bin/activate"

# Upgrade pip to latest version
echo "📦 Upgrading pip..."
pip install --upgrade pip

# Install production dependencies
echo "📦 Installing production dependencies..."
pip install -r requirements.txt

# Install development dependencies
echo "🛠️  Installing development dependencies..."
pip install -r requirements-dev.txt

echo ""
echo "✅ Virtual environment setup complete!"
echo ""
echo "🎯 To activate the virtual environment, run:"
echo "   source venv/bin/activate"
echo ""
echo "🎯 To deactivate, run:"
echo "   deactivate"
echo ""
echo "🎯 To run the bot in the virtual environment:"
echo "   source venv/bin/activate && python discord_emoji.py"
echo ""
echo "🎯 Or use the Makefile commands which automatically handle the virtual environment:"
echo "   make venv-install    # Setup virtual environment"
echo "   make venv-dev        # Run bot in development mode"
echo "   make venv-test       # Run tests in virtual environment"
echo "   make venv-lint       # Run linting in virtual environment"
echo ""
