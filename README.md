# 🌾 Agricultural Decision Support System - Single File Version

**AI-Powered Crop Recommendations and Environmental Optimization**

A complete agricultural decision support system integrated into a single Python file. Simply input your environmental sensor data and get instant ML-powered crop recommendations with AI-generated environmental optimization advice.

## ✨ Features

- **🤖 ML Crop Prediction**: Random Forest model analyzes soil nutrients, climate, and pH
- **🧠 AI Environmental Optimization**: Personalized improvement strategies from advanced LLM
- **⚡ Single File**: Everything in one `agricultural_chatbot.py` file - no complex imports
- **📊 Simple Interface**: Input sensor data → get immediate recommendations
- **🎯 Scientific Approach**: Evidence-based advice with confidence scoring

## 🚀 Quick Start

### 1. Requirements
```bash
pip install streamlit openai python-dotenv pandas numpy scikit-learn
```

### 2. Setup API Key
```bash
# Create .env file with your OpenRouter API key
echo "OPENROUTER_API_KEY=sk-or-v1-your-actual-api-key-here" > .env
```
Get your API key from: https://openrouter.ai/keys

### 3. Run the Application
```bash
streamlit run agricultural_chatbot.py
```

That's it! Your agricultural decision support system is ready to use.

## 📁 File Structure (Simplified)

```
📦 agricultural-decision-support/
├── 🔥 agricultural_chatbot.py        # ⭐ COMPLETE APPLICATION (single file)
├── 📊 data/                          # ML model files (required)
│   ├── best_model_random_forest.pkl
│   ├── label_encoder.pkl
│   ├── scaler.pkl
│   ├── X_train.csv
│   └── y_train.csv
├── 📄 requirements.txt               # Dependencies
├── 📋 .env                          # Your API key
└── 📖 README.md                     # This file
```

## 💡 How It Works

### Input Your Field Data
```
Soil Nutrients: N, P, K (kg/ha)
Climate: Temperature, Humidity, Rainfall  
Soil: pH level, field size, location
```

### Get Instant Analysis
```
🤖 ML Prediction: Best crop with 92.3% confidence
🔄 Alternatives: Top 3 alternative crops
🧠 AI Advice: Specific environmental optimization strategies
📊 Summary: Quick metrics and implementation guidance
```

### Example Results
```
Input: N=85, P=50, K=45, temp=24°C, humidity=82%, pH=6.5, rainfall=220mm

ML Prediction: Rice (92.3% confidence)
Alternatives: Corn (78%), Sugarcane (65%), Cotton (52%)

AI Environmental Recommendations:
✅ Soil pH optimal for rice cultivation
⚠️ Consider increasing phosphorus levels for higher yields  
💧 Current rainfall suitable, prepare drainage for monsoon season
🌡️ Temperature range ideal for rice growth cycle
```

## 🔧 Technical Details

### Integrated Components
1. **AICropPredictor Class**: Complete ML pipeline with feature engineering
2. **DecisionSupportSystem Class**: AI advice generation and system management  
3. **Streamlit UI Functions**: User interface and result display
4. **OpenAI Integration**: Environmental optimization advice generation

### ML Model Pipeline
```python
# Feature Engineering
NPK_sum, nutrient ratios, climate interactions, pH categories

# Preprocessing  
Scaling, feature alignment, data validation

# Prediction
Random Forest → crop name, confidence, probabilities

# Post-processing
Alternative ranking, confidence conversion, result formatting
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

## 🎯 Key Advantages of Single File

### Simplicity
- **No complex imports** - everything in one file
- **Easy deployment** - just copy one file  
- **Simple maintenance** - single point of update
- **Clear organization** - well-structured with section comments

### Functionality
- **Complete ML pipeline** - feature engineering, prediction, post-processing
- **Full AI integration** - environmental optimization with LLM
- **Robust error handling** - graceful degradation when components fail
- **Production ready** - lazy loading, input validation, user feedback

### Development
- **Self-contained** - no dependency on external modules
- **Portable** - works anywhere with Python + dependencies
- **Debuggable** - all code visible in one file
- **Extensible** - easy to modify and enhance

## 🚀 Usage Examples

### Basic Usage
```bash
# Just run the single file
streamlit run agricultural_chatbot.py
```

### Development Mode
```python
# Test components individually
python -c "
from agricultural_chatbot import AICropPredictor
predictor = AICropPredictor()
result = predictor.predict_crop({'N': 50, 'P': 25, 'K': 100, 'temperature': 25, 'humidity': 65, 'ph': 6.5, 'rainfall': 800})
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
pip install streamlit openai python-dotenv pandas numpy scikit-learn
```

**API key errors:**
```bash
# Check .env file
cat .env
# Should show: OPENROUTER_API_KEY=sk-or-v1-...
```

**ML model errors:**
```bash
# Check if data directory exists
ls -la data/
# Should show: *.pkl and *.csv files
```

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
