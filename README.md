# 🌾 Agricultural Decision Support System - Local AI Version

**AI-Powered Crop Recommendations with Local LLM Integration**

A complete agricultural decision support system with ML-based crop prediction and local AI environmental optimization using Ollama. Features SHAP explainability for low-confidence predictions and fully localized Indonesian interface.

## ✨ Features

- **🤖 ML Crop Prediction**: Random Forest model analyzes soil nutrients, climate, and pH
- **🧠 Local AI Optimization**: Personalized strategies using local Ollama + Gemma models
- **🔍 SHAP Explainability**: Understand which factors limit crop suitability
- **⚡ Single File**: Everything integrated in `agricultural_chatbot.py`
- **🇮🇩 Indonesian Interface**: Fully localized UI and prompts
- **🔒 Privacy-First**: No external API calls - all processing local
- **📊 Scientific Approach**: Evidence-based advice with confidence scoring
- **💾 Persistent History**: MongoDB Atlas integration for interaction history storage

## 🚀 Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Setup Ollama
```bash
# Install Ollama
curl -fsSL https://ollama.com/install.sh | sh

# Start Ollama server
ollama serve

# Download Gemma model (choose based on your system)
ollama pull gemma2:9b  # For 16GB+ RAM (recommended)
# OR
ollama pull gemma:7b   # For 8-16GB RAM
# OR  
ollama pull gemma:2b   # For 4-8GB RAM
```

### 3. MongoDB Configuration (Automatic)

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

### 4. Verify Setup
```bash
python test_ollama.py
```

### 5. Run the Application
```bash
streamlit run agricultural_chatbot.py
```

That's it! Your agricultural decision support system with persistent interaction history is ready.

## 📁 File Structure

```
📦 agricultural-decision-support/
├── 🔥 agricultural_chatbot.py        # ⭐ COMPLETE APPLICATION
├── 📊 data/                          # ML model files (required)
│   ├── best_model_random_forest.pkl
│   ├── label_encoder.pkl
│   ├── scaler.pkl
│   ├── X_train.csv
│   └── y_train.csv
├── 🧪 test_ollama.py                # Ollama integration test
├── 📋 OLLAMA_SETUP.md               # Detailed Ollama setup guide
├── 📄 requirements.txt               # Dependencies (no OpenAI!)
└── 📖 README.md                     # This file
```

## 💡 How It Works

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
2. **DecisionSupportSystem Class**: Local AI advice generation via Ollama
3. **Streamlit UI Functions**: Fully localized Indonesian interface
4. **Ollama Integration**: Local LLM processing with Gemma models

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

## 🎯 Key Advantages of Local AI Integration

### Privacy & Security
- **No external API calls** - all processing happens locally
- **Data stays private** - sensor data never leaves your system
- **No API keys needed** - eliminate security concerns
- **Offline capable** - works without internet after setup

### Performance & Reliability
- **No API rate limits** - unlimited usage
- **Consistent performance** - not dependent on external service status
- **Lower latency** - no network round trips
- **Cost effective** - no ongoing API fees

### Customization
- **Model choice** - select Gemma model based on your hardware
- **Fine-tuning capable** - can adapt models for specific needs
- **Full control** - modify prompts and behavior as needed
- **Language optimization** - better Indonesian language support

## 🚀 Usage Examples

### Basic Usage
```bash
# Start Ollama server
ollama serve &

# Run the application
streamlit run agricultural_chatbot.py
```

### Test Ollama Integration
```bash
# Verify everything works
python test_ollama.py
```

### Development Mode
```python
# Test ML components individually
python -c "
from agricultural_chatbot import AICropPredictor
predictor = AICropPredictor()
result = predictor.evaluate_crop_suitability(
    {'N': 50, 'P': 25, 'K': 100, 'temperature': 25, 'humidity': 65, 'ph': 6.5, 'rainfall': 800}, 
    'rice'
)
print(result)
"
```

### Production Deployment
```bash
# Deploy with specific port
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
pip install streamlit ollama pymongo pandas numpy scikit-learn shap
```

**Ollama connection errors:**
```bash
# Check if Ollama is running
curl http://localhost:11434/api/tags

# Start Ollama if not running
ollama serve

# Check available models
ollama list
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

You now have a complete agricultural decision support system in a single file!

- ✅ **One file to rule them all**: `agricultural_chatbot.py`
- ✅ **Simple setup**: Just install dependencies and add API key
- ✅ **Full functionality**: ML prediction + AI optimization + Beautiful UI  
- ✅ **Production ready**: Error handling, lazy loading, user feedback
- ✅ **Easy to maintain**: Single file, clear structure, well documented

---

**Ready to revolutionize agriculture with AI? Just run:**
```bash
streamlit run agricultural_chatbot.py
```
