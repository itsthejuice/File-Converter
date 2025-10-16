#!/bin/bash
# Development environment setup script

set -e

echo "=== File Converter Development Setup ==="
echo

# Check Python version
echo "Checking Python version..."
python_version=$(python3 --version 2>&1 | grep -oP '\d+\.\d+' | head -1)
required_version="3.10"

if [[ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" != "$required_version" ]]; then
    echo "❌ Error: Python 3.10+ required (found $python_version)"
    exit 1
fi
echo "✓ Python $python_version"

# Create virtual environment
if [ ! -d "venv" ]; then
    echo
    echo "Creating virtual environment..."
    python3 -m venv venv
    echo "✓ Virtual environment created"
else
    echo "✓ Virtual environment exists"
fi

# Activate virtual environment
echo
echo "Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo
echo "Upgrading pip..."
pip install --upgrade pip > /dev/null

# Install requirements
echo
echo "Installing Python dependencies..."
pip install -r requirements.txt

echo "✓ Dependencies installed"

# Check for system tools
echo
echo "Checking system tools..."

check_tool() {
    if command -v "$1" &> /dev/null; then
        version=$($1 -version 2>&1 | head -1 || echo "unknown")
        echo "  ✓ $1: $version"
        return 0
    else
        echo "  ✗ $1: not found"
        return 1
    fi
}

ffmpeg_ok=true
if ! check_tool ffmpeg; then
    ffmpeg_ok=false
fi

# Provide installation hints
if [ "$ffmpeg_ok" = false ]; then
    echo
    echo "⚠ Missing system tools. Install with:"
    echo
    
    if [ -f /etc/debian_version ]; then
        echo "  sudo apt update"
        echo "  sudo apt install ffmpeg"
    elif [ -f /etc/redhat-release ]; then
        echo "  sudo dnf install ffmpeg"
    elif [ "$(uname)" = "Darwin" ]; then
        echo "  brew install ffmpeg"
    else
        echo "  Install ffmpeg for your system"
    fi
    echo
fi

echo
echo "=== Setup Complete ==="
echo
echo "To activate the virtual environment:"
echo "  source venv/bin/activate"
echo
echo "To run the GUI:"
echo "  ./scripts/run_gui.sh"
echo
echo "To run the CLI:"
echo "  ./scripts/run_cli.sh plan input.mp4 --to audio/mp3"
echo
