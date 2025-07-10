#!/bin/bash

# Agricultural Decision Support System - Enhanced Launcher
# Updated for OpenRouter integration and modular architecture

echo "🌾 Agricultural Decision Support System Launcher"
echo "=================================================="

# Function to display usage help
show_help() {
    echo ""
    echo "Usage: ./launch.sh [option]"
    echo ""
    echo "Options:"
    echo "  --modular, -m     Launch modular version (src/main.py)"
    echo "  --single, -s      Launch single-file version (agricultural_chatbot.py)"
    echo "  --help, -h        Show this help message"
    echo ""
    echo "Default: If no option specified, shows menu to choose version"
    echo ""
}

# Function to check system requirements
check_requirements() {
    echo "🔍 Checking system requirements..."
    
    # Check if we're in the right directory
    if [ ! -f "agricultural_chatbot.py" ] && [ ! -f "src/main.py" ]; then
        echo "❌ Error: Project files not found in current directory"
        echo "Please run this script from the project root directory"
        exit 1
    fi
    
    # Check Python installation
    if ! command -v python3 &> /dev/null && ! command -v python &> /dev/null; then
        echo "❌ Error: Python is not installed or not in PATH"
        echo "Please install Python 3.8+ from https://python.org"
        exit 1
    fi
    
    # Determine Python command
    if command -v python3 &> /dev/null; then
        PYTHON_CMD="python3"
    else
        PYTHON_CMD="python"
    fi
    
    echo "✅ Python found: $($PYTHON_CMD --version)"
    
    # Check pip installation
    if ! $PYTHON_CMD -m pip --version &> /dev/null; then
        echo "❌ Error: pip is not available"
        echo "Please install pip or use a Python environment with pip"
        exit 1
    fi
    
    echo "✅ pip is available"
    
    # Check and install requirements
    if [ -f "requirements.txt" ]; then
        echo "📦 Checking Python dependencies..."
        
        # Check if Streamlit is installed
        if ! $PYTHON_CMD -c "import streamlit" &> /dev/null; then
            echo "⚠️  Streamlit not found. Installing requirements..."
            $PYTHON_CMD -m pip install -r requirements.txt
            
            if [ $? -ne 0 ]; then
                echo "❌ Failed to install requirements"
                echo "Try manually: $PYTHON_CMD -m pip install -r requirements.txt"
                exit 1
            fi
        fi
        
        echo "✅ Dependencies are ready"
    else
        echo "⚠️  Warning: requirements.txt not found"
    fi
    
    # Check data directory
    if [ -d "data" ] || [ -d "src/data" ]; then
        echo "✅ Model data directory found"
    else
        echo "⚠️  Warning: Model data directory not found"
        echo "   Some ML features may be limited"
    fi
    
    # Check environment file
    if [ -f ".env" ]; then
        echo "✅ Environment configuration found"
    else
        echo "⚠️  Info: No .env file found"
        echo "   App will use default MongoDB. For custom config:"
        echo "   Create .env with: OPENROUTER_API_KEY=your-key-here"
    fi
}

# Function to launch modular version
launch_modular() {
    echo ""
    echo "🚀 Launching Modular Version (src/main.py)..."
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "📱 App will open at: http://localhost:8501"
    echo "🛑 Press Ctrl+C to stop the application"
    echo ""
    
    # Launch the modular application
    exec $PYTHON_CMD -m streamlit run src/main.py
}

# Function to launch single-file version
launch_single() {
    echo ""
    echo "🚀 Launching Single-File Version (agricultural_chatbot.py)..."
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "📱 App will open at: http://localhost:8501"
    echo "🛑 Press Ctrl+C to stop the application"
    echo ""
    
    # Launch the single-file application
    exec $PYTHON_CMD -m streamlit run agricultural_chatbot.py
}

# Function to show version selection menu
show_menu() {
    echo ""
    echo "📋 Select Application Version:"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "1) 🏗️  Modular Version (Recommended)"
    echo "   └─ File: src/main.py"
    echo "   └─ Features: Latest updates, better organization"
    echo ""
    echo "2) 📄 Single-File Version (Complete)"
    echo "   └─ File: agricultural_chatbot.py"
    echo "   └─ Features: All-in-one file, stable"
    echo ""
    echo "3) ❌ Exit"
    echo ""
    
    while true; do
        read -p "Choose option (1-3): " choice
        case $choice in
            1)
                launch_modular
                break
                ;;
            2)
                launch_single
                break
                ;;
            3)
                echo "👋 Goodbye!"
                exit 0
                ;;
            *)
                echo "❌ Invalid option. Please choose 1, 2, or 3."
                ;;
        esac
    done
}

# Main script logic
main() {
    # Parse command line arguments
    case "${1:-}" in
        --modular|-m)
            check_requirements
            launch_modular
            ;;
        --single|-s)
            check_requirements
            launch_single
            ;;
        --help|-h)
            show_help
            exit 0
            ;;
        "")
            check_requirements
            show_menu
            ;;
        *)
            echo "❌ Unknown option: $1"
            show_help
            exit 1
            ;;
    esac
}

# Run main function with all arguments
main "$@"
