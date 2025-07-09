"""
Configuration module for Agricultural Decision Support System
Contains all application settings, environment variables, and global configurations.
"""

import os
import warnings
from dotenv import load_dotenv

# ==================== ENVIRONMENT & BASIC SETUP ====================

# Load environment variables
load_dotenv()

# Suppress warnings
warnings.filterwarnings('ignore')

# ==================== FEATURE FLAGS ====================

# Disable sentence transformers temporarily to fix PyTorch import error
SENTENCE_TRANSFORMERS_AVAILABLE = False

# Library availability flags (will be set by utils/helpers.py)
SHAP_AVAILABLE = False
FOLIUM_AVAILABLE = False
STREAMLIT_FOLIUM_AVAILABLE = False
GEOPY_AVAILABLE = False

# ==================== MONGODB CONFIGURATION ====================

# MongoDB Atlas connection settings
MONGODB_CONFIG = {
    'connection_string': os.getenv(
        'MONGODB_CONNECTION_STRING',
        'mongodb+srv://munawir:munawir123@cluster0.u02m0.mongodb.net/?retryWrites=true&w=majority'
    ),
    'database': os.getenv('MONGODB_DATABASE', 'munawir_datathon2025'),
    'collection': os.getenv('MONGODB_COLLECTION', 'interaction_history'),
    'user_session': 'agricultural_global_session'
}

# ==================== MAP CONFIGURATION ====================

MAP_CONFIG = {
    'default_center': [-2.5, 118.0],  # Indonesia center
    'default_zoom': 5,
    'pin_color': 'red',
    'circle_radius': 1000,  # 1km radius
    'map_width': 700,
    'map_height': 400
}

# ==================== GPS CONFIGURATION ====================

GPS_CONFIG = {
    'timeout': 10000,  # 10 seconds
    'maximum_age': 60000,  # 1 minute
    'enable_high_accuracy': True,
    'accuracy_excellent': 10,  # <10m = excellent
    'accuracy_good': 50,       # 10-50m = good
    'accuracy_fair': 100       # >50m = fair
}

# ==================== LLM CONFIGURATION ====================

LLM_CONFIG = {
    'ollama': {
        'base_url': 'http://localhost:11434',
        'default_model': 'llama3.2:1b',
        'timeout': 30
    },
    'openrouter': {
        'base_url': 'https://openrouter.ai/api/v1',
        'api_key': os.getenv('OPENROUTER_API_KEY', 'sk-or-v1-d6c4ab9f3f5f27e45c9c5dfa2d8e9e4e5f4e3c2a9b8d7e6f5a4b3c2d1e9f8a7b6'),
        'default_model': 'mistralai/mistral-tiny',
        'timeout': 60
    },
    'temperature': 0.7,
    'max_tokens': 2000
}

# ==================== ML MODEL CONFIGURATION ====================

ML_CONFIG = {
    'model_path': 'src/data',
    'models': {
        'random_forest': 'best_model_random_forest.pkl',
        'label_encoder': 'label_encoder.pkl',
        'scaler': 'scaler.pkl'
    },
    'training_data': {
        'X_train': 'X_train.csv',
        'X_test': 'X_test.csv', 
        'y_train': 'y_train.csv',
        'y_test': 'y_test.csv'
    },
    'confidence_threshold': 0.7,
    'low_confidence_threshold': 0.6
}

# ==================== UI CONFIGURATION ====================

UI_CONFIG = {
    'page_title': 'Agricultural Decision Support System',
    'page_icon': '🌾',
    'layout': 'wide',
    'sidebar_title': '📋 Agricultural Tools',
    'max_interactions_display': 10
}

# ==================== CROP MAPPING ====================

CROP_MAPPING = {
    "🌾 Padi (Rice)": "rice",
    "🌽 Jagung (Maize)": "maize", 
    "🫘 Kedelai (Soybean)": "chickpea",
    "🥔 Kentang (Potato)": "kidneybeans",
    "🍌 Pisang (Banana)": "banana",
    "🥭 Mangga (Mango)": "mango",
    "🥥 Kelapa (Coconut)": "coconut",
    "☕ Kopi (Coffee)": "coffee",
    "🧄 Bawang (Onion)": "mothbeans",
    "🌶️ Cabai (Chili)": "pomegranate",
    "🍎 Apel (Apple)": "apple",
    "🍇 Anggur (Grapes)": "grapes",
    "🍊 Jeruk (Orange)": "orange",
    "🫛 Kacang Hijau (Mung Bean)": "mungbean",
    "🌻 Bunga Matahari (Sunflower)": "cotton",
    "🌱 Jute": "jute",
    "🌿 Lentil": "lentil",
    "🫘 Kacang Merah (Kidney Bean)": "kidneybeans",
    "🌾 Blackgram": "blackgram",
    "🌾 Mothbeans": "mothbeans"
}

# ==================== SENSOR PARAMETERS ====================

SENSOR_PARAMS = {
    'nitrogen': {'min': 0.0, 'max': 140.0, 'default': 50.0, 'unit': 'kg/ha'},
    'phosphorus': {'min': 5.0, 'max': 145.0, 'default': 53.0, 'unit': 'kg/ha'},
    'potassium': {'min': 5.0, 'max': 205.0, 'default': 48.0, 'unit': 'kg/ha'},
    'temperature': {'min': 8.8, 'max': 43.7, 'default': 25.0, 'unit': '°C'},
    'humidity': {'min': 14.3, 'max': 99.9, 'default': 71.0, 'unit': '%'},
    'ph': {'min': 3.5, 'max': 9.9, 'default': 6.5, 'unit': ''},
    'rainfall': {'min': 20.2, 'max': 298.6, 'default': 103.0, 'unit': 'mm'}
}

# ==================== ERROR MESSAGES ====================

ERROR_MESSAGES = {
    'mongodb_connection': '❌ Tidak dapat terhubung ke MongoDB',
    'location_not_found': '❌ Lokasi tidak ditemukan',
    'gps_not_supported': '❌ GPS tidak didukung browser ini',
    'gps_permission_denied': '❌ Akses GPS ditolak',
    'gps_timeout': '❌ Timeout GPS - Coba lagi di area terbuka',
    'llm_connection_failed': '❌ Koneksi LLM gagal',
    'model_loading_failed': '❌ Gagal memuat model ML'
}

# ==================== SUCCESS MESSAGES ====================

SUCCESS_MESSAGES = {
    'mongodb_connected': '✅ MongoDB Atlas connection established successfully',
    'location_found': '✅ Lokasi berhasil ditemukan',
    'gps_success': '✅ GPS berhasil dideteksi',
    'model_loaded': '✅ Model ML berhasil dimuat',
    'data_saved': '✅ Data berhasil disimpan'
} 