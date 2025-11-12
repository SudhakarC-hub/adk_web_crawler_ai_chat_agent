#!/bin/bash
# Quick Start Script for ADK Web Crawler Chatbot

echo "🚀 Starting ADK Web Crawler Chatbot Setup..."
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.9+ first."
    exit 1
fi

# Check Python version
PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
echo "✅ Python version: $PYTHON_VERSION"
echo ""

# Check if Ollama is installed
if ! command -v ollama &> /dev/null; then
    echo "❌ Ollama is not installed."
    echo "📥 Install from: https://ollama.ai"
    exit 1
fi

echo "✅ Ollama is installed"
echo ""

# Check if mistral model is available
echo "🔍 Checking for Mistral model..."
if ollama list | grep -q "mistral"; then
    echo "✅ Mistral model is available"
else
    echo "📥 Pulling Mistral model..."
    ollama pull mistral
fi
echo ""

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
    echo "✅ Virtual environment created"
else
    echo "✅ Virtual environment already exists"
fi
echo ""

# Activate virtual environment
echo "🔌 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📚 Installing dependencies..."
pip install -q --upgrade pip
pip install -q -r ADK_VERSION_requirements.txt
echo "✅ Dependencies installed"
echo ""

# Set environment variable
export OLLAMA_API_BASE=http://localhost:11434
echo "✅ Environment variable set: OLLAMA_API_BASE=$OLLAMA_API_BASE"
echo ""

# Start Ollama in background if not running
if ! pgrep -x "ollama" > /dev/null; then
    echo "🦙 Starting Ollama server..."
    ollama serve &
    sleep 2
    echo "✅ Ollama server started"
else
    echo "✅ Ollama server is already running"
fi
echo ""

# Start HTTP server for test page in background
echo "🌐 Starting HTTP server for test page..."
python3 -m http.server 8000 > /dev/null 2>&1 &
HTTP_PID=$!
echo "✅ Test page available at: http://localhost:8000/cats_guide.html"
echo ""

echo "✨ Setup complete!"
echo ""
echo "🎮 To start the Streamlit app, run:"
echo "   streamlit run adk_app.py --server.port 8503"
echo ""
echo "🧪 Test URL: http://localhost:8000/cats_guide.html"
echo ""
echo "🛑 To stop servers:"
echo "   pkill -f 'python -m http.server'"
echo "   pkill ollama"
echo ""
