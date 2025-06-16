#!/bin/bash

# Indonesian Agricultural Chatbot Launcher
# This script starts the Streamlit application

echo "🌾 Starting Indonesian Agricultural Chatbot..."
echo "==========================================="

# Check if we're in the right directory
if [ ! -f "agricultural_chatbot.py" ]; then
    echo "❌ Error: agricultural_chatbot.py not found in current directory"
    echo "Please run this script from the project directory"
    exit 1
fi

# Check if Python is available
if ! command -v python &> /dev/null; then
    echo "❌ Error: Python is not installed or not in PATH"
    exit 1
fi

# Check if Streamlit is installed
if ! python -c "import streamlit" &> /dev/null; then
    echo "❌ Error: Streamlit is not installed"
    echo "Please install requirements: pip install -r requirements.txt"
    exit 1
fi

# Check if OpenAI is installed
if ! python -c "import openai" &> /dev/null; then
    echo "❌ Error: OpenAI package is not installed"
    echo "Please install requirements: pip install -r requirements.txt"
    exit 1
fi

# Check if python-dotenv is installed
if ! python -c "import dotenv" &> /dev/null; then
    echo "❌ Error: python-dotenv is not installed"
    echo "Please install requirements: pip install -r requirements.txt"
    exit 1
fi

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "⚠️  Warning: .env file not found"
    echo "🔧 Setting up API key configuration..."
    echo ""
    if [ -f ".env.example" ]; then
        cp .env.example .env
        echo "✅ Created .env file from template"
        echo "📝 Please edit .env and add your OpenRouter API key"
        echo "🔗 Get your API key from: https://openrouter.ai/keys"
        echo ""
        echo "Then run this script again to start the application."
        exit 1
    else
        echo "❌ Error: .env.example file not found"
        echo "Please check the API_SETUP.md file for manual setup instructions"
        exit 1
    fi
fi

# Check if API key is set in .env
if ! grep -q "OPENROUTER_API_KEY=sk-or-v1-" .env 2>/dev/null; then
    echo "⚠️  Warning: OpenRouter API key not configured"
    echo "📝 Please edit .env and add your actual API key"
    echo "🔗 Get your API key from: https://openrouter.ai/keys"
    echo ""
    echo "Example:"
    echo "OPENROUTER_API_KEY=sk-or-v1-your-actual-api-key-here"
    exit 1
fi

echo "✅ All dependencies are available"
echo "🚀 Launching chatbot application..."
echo ""
echo "The application will open in your default web browser"
echo "Default URL: http://localhost:8501"
echo ""
echo "To stop the application, press Ctrl+C in this terminal"
echo ""

# Start the Streamlit application
streamlit run agricultural_chatbot.py
