#!/bin/bash

# Quick launcher script for the root directory
# This script calls the main launcher in the scripts directory

echo "🌾 Starting Indonesian Agricultural Chatbot..."

# Check if we're in the right directory
if [ ! -f "agricultural_chatbot.py" ]; then
    echo "❌ Error: Not in the correct directory"
    echo "Please run this from the project root directory"
    exit 1
fi

# Call the main launcher
exec ./scripts/launch_chatbot.sh
