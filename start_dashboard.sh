#!/bin/bash
"""
SVCS Web Dashboard Setup and Launch Script

This script installs the required dependencies and starts the SVCS web dashboard.
"""

set -e  # Exit on any error

echo "🧠 SVCS Interactive Dashboard Setup"
echo "===================================="
echo

# Check if we're in the right directory
if [ ! -f "svcs.py" ]; then
    echo "❌ Error: Please run this script from the SVCS root directory"
    echo "   (The directory containing svcs.py)"
    exit 1
fi

# Check if virtual environment exists
if [ ! -d ".svcs/venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv .svcs/venv
fi

echo "🔧 Installing Python dependencies..."

# Activate virtual environment and install dependencies
source .svcs/venv/bin/activate

# Install Flask and Flask-CORS for the web server
pip install Flask Flask-CORS

echo "✅ Dependencies installed successfully!"
echo

# Check if dashboard HTML exists
if [ ! -f "svcs_interactive_dashboard.html" ]; then
    echo "❌ Error: svcs_interactive_dashboard.html not found"
    echo "   Please ensure the dashboard file exists in the current directory"
    exit 1
fi

echo "🚀 Starting SVCS Interactive Dashboard..."
echo "   Dashboard will be available at: http://127.0.0.1:8080"
echo "   Press Ctrl+C to stop the server"
echo

# Start the web server
python3 svcs_web_server.py --host 127.0.0.1 --port 8080
