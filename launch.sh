#!/bin/bash

# Agricultural Decision Support System - Single File Launcher
# Simplified launcher for the consolidated application

echo "🌾 Starting Agricultural Decision Support System (Single File Version)..."
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

echo ""
echo "🚀 Launching Agricultural Decision Support System..."
echo "📱 Access the app at: http://localhost:8501"
echo "🛑 Press Ctrl+C to stop the application"
echo ""

# Start the application
exec streamlit run agricultural_chatbot.py
