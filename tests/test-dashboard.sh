#!/bin/bash

# SVCS Web Dashboard Test Runner
# This script starts a simple HTTP server to test the modular dashboard

echo "🚀 Starting SVCS Web Dashboard Test Server..."
echo "📁 Serving from: $(pwd)/web-app"

# Check if we're in the right directory
if [ ! -d "web-app" ]; then
    echo "❌ Error: web-app directory not found"
    echo "Please run this script from the SVCS root directory"
    exit 1
fi

# Find available port
PORT=8080
while lsof -Pi :$PORT -sTCP:LISTEN -t >/dev/null ; do
    PORT=$((PORT + 1))
done

echo "🌐 Starting server on port $PORT..."
echo "📄 Dashboard URL: http://localhost:$PORT"
echo "⏹️  Press Ctrl+C to stop the server"
echo ""

# Start HTTP server
cd web-app
if command -v python3 &> /dev/null; then
    python3 -m http.server $PORT
elif command -v python &> /dev/null; then
    python -m http.server $PORT
elif command -v node &> /dev/null; then
    npx http-server -p $PORT
else
    echo "❌ Error: No HTTP server available"
    echo "Please install Python 3 or Node.js to run the test server"
    exit 1
fi
