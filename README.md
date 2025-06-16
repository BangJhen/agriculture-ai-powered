# 🌾 Indonesian Agricultural Chatbot

**AI-powered sustainable agriculture assistant for Indonesian farmers and agricultural professionals.**

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://python.org)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.28+-red.svg)](https://streamlit.io)
[![OpenAI](https://img.shields.io/badge/OpenAI-API-green.svg)](https://openai.com)

## 🚀 Quick Start

```bash
# 1. Clone and install
git clone <your-repo-url>
cd prototype-model
pip install -r requirements.txt

# 2. Setup API key
cp .env.example .env
# Edit .env and add your OpenRouter API key

# 3. Run the app
./launch.sh
```

**That's it!** The app will open at `http://localhost:8501` 🎉

## ✨ Features

- 🧑‍💼 **7 Professional Roles** - Tailored for different agricultural specialists
- 📊 **20+ Field Parameters** - Soil, water, and climate analysis
- 🌱 **Indonesian Agriculture Focus** - Local crops, techniques, and climate patterns
- 🔧 **Structured AI Responses** - Forecasting, suggestions, and problem-solving
- 🔐 **Secure API Management** - Environment-based configuration

## 🏗️ Project Structure

```
📦 indonesian-agricultural-chatbot
├── 🔥 agricultural_chatbot.py     # Main application
├── 📄 requirements.txt            # Dependencies
├── 🔧 launch.sh                   # Quick launcher
├── 📋 .env.example               # API key template
│
├── 📚 docs/                      # User guides
├── 🔧 scripts/                   # Utility scripts
└── 📖 Additional guides...       # Setup & development docs
```

## 🔐 API Key Setup

This app requires an OpenRouter API key. The launch script will guide you through setup:

1. Get your API key from [OpenRouter](https://openrouter.ai/keys)
2. Copy `.env.example` to `.env`
3. Add your key to the `.env` file

**Need help?** See [API_SETUP.md](API_SETUP.md) for detailed instructions.

## 📖 Documentation

| Guide | Description |
|-------|-------------|
| [API_SETUP.md](API_SETUP.md) | Complete API key configuration guide |
| [CONTRIBUTING.md](CONTRIBUTING.md) | Quick start guide for new contributors |
| [DEVELOPER_GUIDE.md](DEVELOPER_GUIDE.md) | Development workflow and best practices |
| [docs/README.md](docs/README.md) | Detailed user documentation |
| [docs/DOKUMENTASI_INDONESIA.md](docs/DOKUMENTASI_INDONESIA.md) | Technical docs (Indonesian) |

## 🌍 Indonesian Agriculture Focus

Designed specifically for Indonesian agricultural conditions:

- **Crops**: Padi, jagung, cabai, kelapa sawit, kakao, kopi
- **Techniques**: Tumpangsari, jajar legowo, integrated farming
- **Conservation**: Terasering, embung, agroforestry, SRI
- **Climate**: Monsoon patterns, tropical adaptation

## 🤝 Contributing

**Want to help improve Indonesian agriculture?** We'd love your contribution!

```bash
# Quick contributor setup
git clone <your-fork>
cd prototype-model
pip install -r requirements.txt
cp .env.example .env  # Add your API key
./launch.sh  # Test the application
```

**New to the project?** See [CONTRIBUTING.md](CONTRIBUTING.md) for a quick start guide.

**Detailed workflow?** Check [DEVELOPER_GUIDE.md](DEVELOPER_GUIDE.md) for comprehensive instructions.
