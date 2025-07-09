#!/bin/bash

# Agricultural Decision Support System - Local AI Launcher
# Launches the application with Ollama integration

echo "🌾 Starting Agricultural Decision Support System (Local AI Version)..."
echo "=================================================================="

# Check if we're in the right directory
if [ ! -f "agricultural_chatbot.py" ]; then
    echo "❌ Error: agricultural_chatbot.py not found in current directory"
    echo "Please run this from the project directory"
    exit 1
fi

echo "✅ Found agricultural_chatbot.py"

# Check if Python is available
if ! command -v python &> /dev/null; then
    echo "❌ Error: Python is not installed or not in PATH"
    exit 1
fi

echo "✅ Python is available"

# Check if Streamlit is installed
if ! python -c "import streamlit" &> /dev/null; then
    echo "❌ Error: Streamlit is not installed"
    echo "Please install requirements: pip install -r requirements.txt"
    exit 1
fi

echo "✅ Streamlit is installed"

# Check if required data directory exists
if [ ! -d "data" ]; then
    echo "⚠️  Warning: data directory not found"
    echo "ML features will be limited without model files"
else
    echo "✅ Data directory found"
fi

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "⚠️  Warning: .env file not found"
    echo "AI features will be limited without API key"
    echo "Create .env file with: OPENROUTER_API_KEY=your-key-here"
else
    echo "✅ Environment file found"
fi

# Check if Ollama is installed
if ! command -v ollama &> /dev/null; then
    echo "❌ Error: Ollama is not installed"
    echo "Please install Ollama: curl -fsSL https://ollama.com/install.sh | sh"
    exit 1
fi

echo "✅ Ollama is installed"

# Check if Ollama server is running
if ! curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
    echo "🔄 Ollama server not running, starting it..."
    
    # Start Ollama server in background
    ollama serve > /dev/null 2>&1 &
    OLLAMA_PID=$!
    
    # Wait for server to start
    echo "⏳ Waiting for Ollama server to start..."
    for i in {1..30}; do
        if curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
            echo "✅ Ollama server is running"
            break
        fi
        sleep 1
        echo -n "."
    done
    
    if ! curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
        echo "❌ Failed to start Ollama server"
        exit 1
    fi
else
    echo "✅ Ollama server is already running"
fi

# Check for Gemma models
echo "🔍 Checking for Gemma models..."
if ! ollama list | grep -q gemma; then
    echo "⚠️  No Gemma models found"
    echo "Please install a Gemma model:"
    echo "  For 16GB+ RAM: ollama pull gemma2:9b"
    echo "  For 8-16GB RAM: ollama pull gemma:7b" 
    echo "  For 4-8GB RAM: ollama pull gemma:2b"
    read -p "Continue without Gemma model? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
else
    GEMMA_MODEL=$(ollama list | grep gemma | head -1 | awk '{print $1}')
    echo "✅ Found Gemma model: $GEMMA_MODEL"
fi

echo ""
echo "🚀 Launching Agricultural Decision Support System..."
echo "📱 Access the app at: http://localhost:8501"
echo "🛑 Press Ctrl+C to stop the application"
echo ""

# Start the application
exec streamlit run agricultural_chatbot.py
