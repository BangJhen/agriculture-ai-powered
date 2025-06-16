# 🌾 Indonesian Agricultural Chatbot

**AI## 🏗️ Project Structure

```
📦 indonesian-agricultural-chatbot
├── 🔥 agricultural_chatbot.py           # Main Streamlit application
├── 🗺️ west_java_crop_analysis.py       # Crop suitability analysis engine
├── 📄 requirements.txt                  # Dependencies
├── 🔧 launch.sh                         # Quick launcher
├── 📋 .env.example                     # API key template
│
├── 📊 data/                            # Analysis data files
│   ├── west_java_crop_analysis_report.json
│   ├── traditional_practices_risks.json
│   └── mapping_visualization_guide.json
│
├── 📚 docs/                            # User guides
├── 🔧 scripts/                         # Utility scripts
└── 📖 Additional setup guides...       # API & development docs
```e agriculture assistant for Indonesian farmers and agricultural professionals.**

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

### Core Chatbot
- 🧑‍💼 **7 Professional Roles** - Tailored for different agricultural specialists
- 📊 **20+ Field Parameters** - Soil, water, and climate analysis
- 🌱 **Indonesian Agriculture Focus** - Local crops, techniques, and climate patterns
- 🔧 **Structured AI Responses** - Forecasting, suggestions, and problem-solving
- 🔐 **Secure API Management** - Environment-based configuration

### 🗺️ West Java Crop Suitability Analysis (NEW!)
- **🌽 Corn & 🥔 Cassava Analysis** - Scientific suitability assessment
- **18 Regional Coverage** - All major districts/regencies in West Java
- **Multi-Factor Scoring** - Edaphic (soil), hydrologic (water), atmospheric (climate)
- **Traditional Practices** - Integration of local farming knowledge
- **Interactive Dashboard** - Compare regions and crops with detailed insights

## 🏗️ Project Structure

```
📦 indonesian-agricultural-chatbot
├── 🔥 agricultural_chatbot.py           # Main Streamlit application
├── �️ west_java_crop_analysis.py       # Crop suitability analysis engine
├── �📄 requirements.txt                  # Dependencies
├── 🔧 launch.sh                         # Quick launcher
├── 📋 .env.example                     # API key template
│
├── 📊 Data Files
│   ├── west_java_crop_analysis_report.json
│   ├── traditional_practices_risks.json
│   └── mapping_visualization_guide.json
│
├── 📚 docs/                            # User guides
├── 🔧 scripts/                         # Utility scripts
└── 📖 Additional setup guides...       # API & development docs
```

## 🔐 API Key Setup

This app requires an OpenRouter API key. The launch script will guide you through setup:

1. Get your API key from [OpenRouter](https://openrouter.ai/keys)
2. Copy `.env.example` to `.env`
3. Add your key to the `.env` file

**Need help?** See [API_SETUP.md](API_SETUP.md) for detailed instructions.

## �️ Using West Java Crop Analysis

### Quick Start
1. **Run the app**: `streamlit run agricultural_chatbot.py`
2. **Find the sidebar section**: "🗺️ Analisis Kesesuaian Tanaman Jawa Barat"
3. **Choose analysis type**: Dashboard, Corn, Cassava, or Comparison
4. **Select regions** and view detailed results

### Analysis Types
- **📊 Dashboard**: Overview of all 18 regions with rankings
- **🌽 Corn**: Detailed corn suitability analysis
- **🥔 Cassava**: Comprehensive cassava assessment  
- **📈 Comparison**: Side-by-side crop comparison

### Sample Results
**Top regions for corn**: Karawang (0.839), Cirebon (0.824), Subang (0.819)  
**Top regions for cassava**: Cirebon (0.900), Karawang (0.892), Indramayu (0.879)

## �📖 Documentation

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
