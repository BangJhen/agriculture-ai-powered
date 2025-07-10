# TaniCerdas Nusantara

**AI-Powered Crop Recommendations with Advanced LLM Integration**

A complete agricultural decision support system with ML-based crop prediction and AI environmental optimization using OpenRouter. Features SHAP explainability for low-confidence predictions and fully localized Indonesian interface.

## Fitur Unggulan
 - **Prediksi Tanaman ML**: Model Random Forest menganalisis N-P-K, iklim, pH
 - **AI Optimization**: Strategi pemupukan via LLM (Ollama / OpenRouter)
 - **SHAP Explainability**: Understand which factors limit crop suitability
 - **Modular Architecture**: Clean, maintainable code structure in `src/` directory
 - **Single File Option**: Complete functionality in `agricultural_chatbot.py`
 - **Indonesian Interface**: Fully localized UI and prompts
 - **Scientific Approach**: Evidence-based advice with confidence scoring
 - **Persistent History**: MongoDB Atlas integration for interaction history storage
 - **Location Integration**: GPS, interactive maps, and location search
 - **Easy Launcher**: Enhanced bash script for simple deployment

## Cara Cepat Menjalankan

### 1. Clone and Setup
```bash
git clone <repository-url>
cd agricultural-decision-support
chmod +x launch.sh
```

### 2. Launch the Application
**🎉 Super Easy Launch** - Use the enhanced launcher script:

```bash
# Interactive menu (recommended for first time)
./launch.sh

# Or direct launch options:
./launch.sh --modular     # Launch modular version (recommended)
./launch.sh --single      # Launch single-file version
./launch.sh --help        # Show all options
```

The launcher will automatically:
- ✅ Check system requirements
- 📦 Install dependencies if needed
- 🔍 Verify data files and environment
- 🚀 Launch the application

### 3. Optional: OpenRouter API Setup
For enhanced AI features, create a `.env` file:
```bash
# .env (optional)
OPENROUTER_API_KEY=your-openrouter-api-key-here
```

**Note**: The app works fully without OpenRouter - it will use fallback options for AI features.

### 4. Knowledge Base (Qdrant) – Manual Setup

Platform ini mendukung knowledge base berbasis **Qdrant** untuk pencarian semantik dokumen agrikultura. Di bawah ini panduan *manual* (tanpa skrip otomatis) untuk menyiapkan Qdrant:

```bash
# 1. Pastikan Docker terpasang
#    Unduh: https://docs.docker.com/get-docker/

# 2. Jalankan Qdrant
docker run -d --name qdrant-tanicerdas \
  -p 6333:6333 -p 6334:6334 \
  -v $(pwd)/qdrant_data:/qdrant/storage \
  qdrant/qdrant:latest

# 3. Instal dependensi Python
pip install sentence-transformers qdrant-client torch transformers

# 4. Jalankan aplikasi
streamlit run src/main.py

# Aplikasi akan otomatis mendeteksi Qdrant di http://localhost:6333 dan mengaktifkan fitur knowledge base.
```

Jika Qdrant tidak aktif, aplikasi tetap berjalan (fallback) dengan pesan "⚠️ Knowledge base tidak tersedia".

### 5. Konfigurasi MongoDB (Otomatis)

**🎉 READY TO USE**: The application comes with a pre-configured MongoDB Atlas database!
- **Database**: `munawir_datathon2025`  
- **Collection**: `interaction_history`
- **No setup required** - interaction history will be automatically saved and persistent across sessions

**🔧 Custom MongoDB (Optional)**: If you want to use your own MongoDB Atlas database:

1. Create a `.env` file in the project root:
```bash
# .env
MONGODB_CONNECTION_STRING=mongodb+srv://yourusername:yourpassword@yourcluster.mongodb.net/?retryWrites=true&w=majority
MONGODB_DATABASE=your_database_name
MONGODB_COLLECTION=your_collection_name
```

2. Replace with your actual MongoDB Atlas credentials
3. Restart the application

That's it! Your agricultural decision support system with persistent interaction history is ready.

### 4. Alternative Manual Launch
If you prefer to run manually without the launcher:

```bash
# Install dependencies
pip install -r requirements.txt

# Launch modular version (recommended)
streamlit run src/main.py

# OR launch single-file version
streamlit run agricultural_chatbot.py
```

## Struktur Direktori

```
📦 agricultural-decision-support/
├── 🚀 launch.sh                      # ⭐ ENHANCED LAUNCHER SCRIPT
├── 🔥 agricultural_chatbot.py        # Complete single-file application (with knowledge base)
├── 🏗️ src/                           # Modular application (recommended)
│   ├── main.py                      # Main entry point
│   ├── components/                  # UI components
│   ├── core/                        # ML prediction engine
│   ├── services/                    # Database, location, mapping
│   ├── utils/                       # Configuration and helpers
│   └── data/                        # ML model files
├── 📊 data/                          # Legacy ML model files
│   ├── best_model_random_forest.pkl
│   ├── label_encoder.pkl
│   ├── scaler.pkl
│   └── training data files...
├── 📄 requirements.txt               # Python dependencies (incl. knowledge base)
├── 📖 README.md                     # This documentation
├── 🔧 TECHNICAL_INTEGRATION_SUMMARY.md # Technical details
└── 📚 qdrant_data/                   # Knowledge base storage (auto-created)
```

## Cara Kerja Singkat

### Input Your Field Data
```
Soil Nutrients: N, P, K (kg/ha)
Climate: Temperature, Humidity, Rainfall  
Soil: pH level, field size, location
Selected Crop: Choose from available options
```

### Get Instant Analysis
```
🤖 ML Evaluation: Crop suitability with confidence score
� SHAP Explanation: Why confidence is low (if applicable)
🧠 Local AI Advice: Specific environmental optimization strategies
📊 Summary: Quick metrics and implementation guidance
```

### Example Results
```
Input: N=85, P=50, K=45, temp=24°C, humidity=82%, pH=6.5, rainfall=220mm
Selected Crop: Rice

ML Evaluation: Rice (92.3% suitability)
SHAP Analysis: ✅ No limiting factors identified

Local AI Environmental Recommendations:
✅ Soil pH optimal for rice cultivation
⚠️ Consider increasing phosphorus levels for higher yields  
💧 Current rainfall suitable, prepare drainage for monsoon season
🌡️ Temperature range ideal for rice growth cycle
```

## 🔧 Technical Details

### Integrated Components
1. **AICropPredictor Class**: Complete ML pipeline with SHAP explainability
2. **DecisionSupportSystem Class**: AI advice generation via OpenRouter
3. **Streamlit UI Functions**: Fully localized Indonesian interface  
4. **Location Integration**: GPS, interactive maps, and geocoding services
5. **Database Integration**: MongoDB Atlas for persistent storage

### ML Model Pipeline
```python
# Feature Engineering
NPK_sum, nutrient ratios, climate interactions, pH categories

# Preprocessing  
Scaling, feature alignment, data validation

# Prediction
Random Forest → crop suitability, confidence, probabilities

# SHAP Analysis (for low confidence)
TreeExplainer → feature importance, limiting factors

# Post-processing
Confidence scoring, explanation generation, result formatting
```

### AI Advisory System
```python
# Context Preparation
Sensor data + ML prediction + optimal ranges

# LLM Generation
OpenRouter API → Environmental optimization strategies

# Output Processing  
Structured recommendations with implementation guidance
```

## 🎯 Key Advantages

### Smart Architecture
- **Modular design** - clean separation of concerns
- **Dual deployment options** - modular or single-file versions
- **Enhanced launcher** - automated setup and dependency management
- **Location-aware** - GPS and interactive map integration

### Reliability & Performance
- **Fallback systems** - OpenRouter with local alternatives
- **Persistent storage** - MongoDB Atlas for interaction history
- **Error handling** - comprehensive validation and recovery
- **User experience** - intuitive interface with helpful guidance

### Deployment & Maintenance
- **Easy setup** - automated launcher handles dependencies
- **Flexible configuration** - optional API keys and custom settings
- **Production ready** - robust error handling and logging
- **Indonesian localization** - full language support

## 🚀 Usage Examples

### Basic Usage
```bash
# Quick start with launcher (recommended)
./launch.sh

# Or launch specific version directly
./launch.sh --modular     # Recommended: latest modular version
./launch.sh --single      # Stable: single-file version
```

### Development Mode
```bash
# Manual launch for development
streamlit run src/main.py    # Modular version
streamlit run agricultural_chatbot.py  # Single-file version

# Custom port
streamlit run src/main.py --server.port 8502
```

### Production Deployment
```bash
# Production with enhanced launcher
./launch.sh --modular

# Manual production deployment
streamlit run src/main.py --server.port 8501 --server.headless true

# Or single-file version
streamlit run agricultural_chatbot.py --server.port 8501 --server.headless true
```

## 📊 System Requirements

### Minimum
- Python 3.8+
- 2GB RAM
- Internet connection (for AI features)

### Recommended  
- Python 3.9+
- 4GB RAM
- Stable internet connection

### Required Files
- `agricultural_chatbot.py` (main application)
- `data/` directory with ML model files
- `.env` file with API key

## 🔍 Troubleshooting

### Common Issues

**"Module not found" errors:**
```bash
# Use the enhanced launcher (recommended)
./launch.sh

# Or install manually
pip install -r requirements.txt
```

**Launcher issues:**
```bash
# Make sure script is executable
chmod +x launch.sh

# Check launcher help
./launch.sh --help

# Use manual installation if needed
pip install -r requirements.txt
```

**MongoDB connection issues:**
- **Default database works out of the box** - no configuration needed
- **For custom MongoDB**: Check your `.env` file configuration
- **Network issues**: Ensure internet connectivity for MongoDB Atlas
- **Credentials**: Verify your MongoDB Atlas username/password in connection string

**ML model errors:**
```bash
# Check if data directory exists
ls -la data/
# Should show: *.pkl and *.csv files
```

**Interaction history not persisting:**
- **Check console output** for MongoDB connection status
- **Default database**: Should connect automatically  
- **Custom database**: Verify `.env` configuration

## 🎉 Success!

You now have a complete agricultural decision support system with enhanced deployment!

- ✅ **Enhanced launcher**: `./launch.sh` handles everything automatically
- ✅ **Dual architecture**: Choose modular or single-file versions
- ✅ **Smart setup**: Automated dependency installation and verification
- ✅ **Full functionality**: ML prediction + AI optimization + Location integration + Beautiful UI  
- ✅ **Production ready**: Error handling, persistent storage, user feedback
- ✅ **Easy to maintain**: Clean modular structure, well documented

---

**Ready to revolutionize agriculture with AI? Just run:**
```bash
./launch.sh
```
