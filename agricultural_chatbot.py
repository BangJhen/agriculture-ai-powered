"""
Agricultural Decision Support System - Complete Single File Version
A simple input-output tool for crop and environmental recommendations.
Powered by ML-based crop prediction and AI-generated environmental suggestions.
All functionality integrated into one file for simplicity.
"""

import streamlit as st
import os
import pandas as pd
import numpy as np
import pickle
from datetime import datetime
from openai import OpenAI
from dotenv import load_dotenv
from typing import Dict, List, Tuple, Any
from qdrant_client import QdrantClient
from qdrant_client.http import models
# Load environment variables
load_dotenv()
client = QdrantClient(host="localhost", port=6333)
# ==================== ML CROP PREDICTOR CLASS ====================

class AICropPredictor:
    """AI-powered crop predictor with environmental improvement suggestions."""
    
    def __init__(self, model_path: str = "data"):
        """Initialize the crop predictor with trained models and data."""
        self.model_path = model_path
        self.model = None
        self.label_encoder = None
        self.scaler = None
        self.X_train = None
        self.X_test = None
        self.y_train = None
        self.y_test = None
        self.feature_columns = ['N', 'P', 'K', 'temperature', 'humidity', 'ph', 'rainfall']
        
        self.load_models()
    
    def load_models(self):
        """Load the trained models and reference data."""
        try:
            # Load the trained Random Forest model
            with open(os.path.join(self.model_path, 'best_model_random_forest.pkl'), 'rb') as f:
                self.model = pickle.load(f)
            
            # Load the label encoder
            with open(os.path.join(self.model_path, 'label_encoder.pkl'), 'rb') as f:
                self.label_encoder = pickle.load(f)
            
            # Load the scaler
            with open(os.path.join(self.model_path, 'scaler.pkl'), 'rb') as f:
                self.scaler = pickle.load(f)
            
            # Load training and test data for reference
            self.X_train = pd.read_csv(os.path.join(self.model_path, 'X_train.csv'))
            self.X_test = pd.read_csv(os.path.join(self.model_path, 'X_test.csv'))
            
            # Load training and test labels for analysis
            self.y_train = pd.read_csv(os.path.join(self.model_path, 'y_train.csv'))
            self.y_test = pd.read_csv(os.path.join(self.model_path, 'y_test.csv'))
            
            return True
            
        except Exception as e:
            st.error(f"Error loading models: {str(e)}")
            return False
    
    def engineer_features(self, input_data: Dict[str, float]) -> pd.DataFrame:
        """Engineer features exactly as done during training."""
        # Create base dataframe
        df = pd.DataFrame([input_data])
        
        # Feature engineering (matching training process)
        df['NPK_sum'] = df['N'] + df['P'] + df['K']
        
        # Ratios (with small epsilon to avoid division by zero)
        epsilon = 1e-8
        df['NP_ratio'] = df['N'] / (df['P'] + epsilon)
        df['NK_ratio'] = df['N'] / (df['K'] + epsilon)
        df['PK_ratio'] = df['P'] / (df['K'] + epsilon)
        
        # Interactions
        df['temp_humidity_interaction'] = df['temperature'] * df['humidity']
        df['rainfall_humidity_ratio'] = df['rainfall'] / (df['humidity'] + epsilon)
        
        # pH acidity level (categorical to numerical)
        def ph_acidity_level(ph):
            if ph < 6.0:
                return -1  # Acidic
            elif ph > 7.0:
                return 1   # Alkaline
            else:
                return 0   # Neutral
        
        df['ph_acidity_level'] = df['ph'].apply(ph_acidity_level)
        
        return df
    
    def preprocess_input(self, input_data: Dict[str, float]) -> np.ndarray:
        """Preprocess user input exactly as done during training."""
        # Engineer features
        df_engineered = self.engineer_features(input_data)
        
        # Ensure column order matches training data
        feature_order = self.X_train.columns.tolist()
        df_engineered = df_engineered[feature_order]
        
        # Scale the features
        scaled_features = self.scaler.transform(df_engineered)
        
        return scaled_features
    
    def evaluate_crop_suitability(self, input_data: Dict[str, float], selected_crop: str) -> Tuple[str, float]:
        """Evaluate the suitability of selected crop based on environmental conditions."""
        if not self.model:
            return selected_crop, 0.0
        
        try:
            # Preprocess input
            processed_input = self.preprocess_input(input_data)
            
            # Make prediction probabilities for all classes
            prediction_proba = self.model.predict_proba(processed_input)[0]
            
            # Get class names
            class_names = self.label_encoder.classes_
            probabilities = dict(zip(class_names, prediction_proba))
            
            # Find probability for selected crop
            if selected_crop in probabilities:
                confidence = probabilities[selected_crop]
            else:
                # If crop not found in model, give low confidence
                confidence = 0.1
            
            return selected_crop, confidence
            
        except Exception as e:
            st.error(f"Error mengevaluasi kesesuaian tanaman: {str(e)}")
            return selected_crop, 0.0

# ==================== OPENAI CLIENT INITIALIZATION ====================

def initialize_openai_client():
    """Initialize OpenAI client with OpenRouter"""
    api_key = os.getenv('OPENROUTER_API_KEY')
    
    if not api_key:
        st.error("🔑 **Error**: OpenRouter API key not found!")
        st.info("""
        **Setup Required:**
        1. Copy `.env.example` to `.env`  
        2. Add your OpenRouter API key to `.env`
        3. Get your API key from: https://openrouter.ai/keys
        
        **Example .env file:**
        ```
        OPENROUTER_API_KEY=sk-or-v1-your-actual-api-key-here
        ```
        """)
        st.stop()
    
    return OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=api_key
    )

# ==================== DECISION SUPPORT SYSTEM ====================

class DecisionSupportSystem:
    """Main class for agricultural decision support functionality"""
    
    def __init__(self):
        self.client = initialize_openai_client()
        self.ai_predictor = None
        self.ai_predictor_loaded = False
        self.ai_predictor_error = None
    
    def get_ai_predictor(self):
        """Lazy load the AI predictor when first needed"""
        if not self.ai_predictor_loaded:
            try:
                st.info("🤖 Initializing ML models for the first time...")
                with st.spinner("Loading ML models (this may take a moment)..."):
                    self.ai_predictor = AICropPredictor()
                st.success("✅ ML models loaded successfully")
                self.ai_predictor_loaded = True
            except Exception as e:
                self.ai_predictor_error = str(e)
                st.warning(f"⚠️ Could not load ML models: {str(e)}")
                st.info("Application will continue with AI-only recommendations")
                self.ai_predictor = None
                self.ai_predictor_loaded = True
        
        return self.ai_predictor
    
    def create_query(self, SC, MLC) :
        """Create a query for the knowledge base"""
        prompt = f"Sekarang saya memiliki db knowledge base yang berisi informasi tentang pertanian di Indonesia. Saya ingin mencari informasi terkait dengan pertanian, tanaman, dan lingkungan. Berikut adalah pertanyaan saya:\n\n{SC}\n\nSaya juga ingin mempertimbangkan hasil evaluasi ML berikut:\n\n{MLC}\n\n berikan saya query ke qdrant yang relevan untuk menapatkan informasi yang relevan dalam bahasa inggris."
        response = self.client.chat.completions.create(
                model="anthropic/claude-3.5-sonnet",
                messages=[
                    {"role": "system", "content": "You are an expert Indonesian agricultural advisor focused on environmental optimization and sustainable farming practices."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=2000
            )
        return response.choices[0].message.content.strip()
        
    def query_knowledge_base(self, query_text, top_k=3):
        # Buat embedding dari query
        query_vector = self.embedding_model.encode(query_text).tolist()
        # Query ke Qdrant
        results = self.qdrant_client.search(
            collection_name="pdf_knowledge",
            query_vector=query_vector,
            limit=top_k
        )
        # Ambil hasil payload (teks knowledge)
        knowledge_chunks = [hit.payload.get("text", "") for hit in results]
        return knowledge_chunks
    
    def generate_environmental_advice(self, sensor_data, ml_evaluation=None):
        """Generate AI-powered environmental optimization advice"""
        
        # Prepare sensor data context
        sensor_context = ""
        if sensor_data:
            sensor_context = f"""
            **Kondisi Lingkungan Saat Ini:**
            - Nitrogen: {sensor_data.get('N', 'N/A')} kg/ha
            - Fosfor: {sensor_data.get('P', 'N/A')} kg/ha  
            - Kalium: {sensor_data.get('K', 'N/A')} kg/ha
            - Suhu: {sensor_data.get('temperature', 'N/A')}°C
            - Kelembaban: {sensor_data.get('humidity', 'N/A')}%
            - pH: {sensor_data.get('ph', 'N/A')}
            - Curah Hujan: {sensor_data.get('rainfall', 'N/A')} mm
            - Lokasi: {sensor_data.get('location', 'Indonesia')}
            """
        
        # Prepare ML evaluation context
        ml_context = ""
        if ml_evaluation:
            # Handle tuple format returned by evaluator: (crop_name, confidence)
            if isinstance(ml_evaluation, (tuple, list)) and len(ml_evaluation) >= 2:
                selected_crop = ml_evaluation[0] if ml_evaluation[0] else 'N/A'
                confidence = ml_evaluation[1] if ml_evaluation[1] else 0
                
                ml_context = f"""
                **Evaluasi Tanaman Berbasis ML:**
                - Tanaman yang Dipilih: {selected_crop}
                - Tingkat Kesesuaian: {confidence*100:.1f}%
                """
            else:
                # Fallback for unexpected format
                ml_context = f"""
                **Evaluasi Tanaman Berbasis ML:**
                - Hasil: {str(ml_evaluation)}
                """
            query_text = self.create_query(ml_context, sensor_context)
            knowledge_chunks = self.query_knowledge_base(query_text, top_k=3)
            knowledge_context = "\n\n".join([f"Referensi {i+1}: {chunk}" for i, chunk in enumerate(knowledge_chunks) if chunk])
        prompt = f"""
        You are an AI Indonesian agricultural advisor specializing in environmental optimization and crop decision support.
        
        {sensor_context}
        {ml_context}
        ### 📚 Referensi Pengetahuan Terkait:
        {knowledge_context}
        Provide a comprehensive environmental optimization recommendation in Indonesian for new farmers in Indonesia, considering the following factors:
        - The tropical climate conditions of Indonesia
        - Traditional agricultural practices in Indonesia
        - Availability of local resources
        - Agricultural challenges specific to Indonesia (such as wet/dry seasons, local pests, etc.)
        Structure the recommendation as follows:
        
        ## 🌱 Soil Health Optimization
        - Recommendations for balanced soil nutrient management
        - Strategies for adjusting soil pH according to Indonesia's tropical climate
        - Enhancing organic matter using locally available compost
        - Improving soil structure to withstand the rainy season
        
        ## 💧 Water Management
        - Optimizing irrigation efficiency for tropical conditions
        - Drainage considerations during the rainy season
        - Moisture retention strategies for the dry season
        - Water quality recommendations based on Indonesian conditions
        
        ## 🌡️ Climate Adaptation
        -Temperature management for tropical farming
        -Strategies to control high humidity levels
        -Protection against extreme weather (heavy rain, strong winds)
        -Seasonal preparation (wet and dry seasons)
        
        ## 🔧 Implementation Guide
        - Priority actions (immediate, short-term, long-term)
        - Resource requirements and cost estimates in Indonesian Rupiah
        - Realistic timelines for Indonesian farmers
        - Monitoring parameters to measure success
        
        ## 🌾 Indonesia-Specific Recommendations
        - Suitable companion plants for Indonesia’s climate
        - Appropriate organic farming techniques
        - Utilization of local fertilizers (compost, manure)
        - Environmentally friendly pest control strategies
        
        Provide practical, specific, and actionable recommendations. Focus on measurable improvements that align with Indonesia's agricultural conditions.             
        """
        
        try:
            response = self.client.chat.completions.create(
                model="anthropic/claude-3.5-sonnet",
                messages=[
                    {"role": "system", "content": "You are an expert Indonesian agricultural advisor focused on environmental optimization and sustainable farming practices."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=2000
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            error_msg = f"❌ Error generating environmental advice: {str(e)}"
            st.error(error_msg)
            
            # Provide fallback basic advice
            fallback_advice = f"""
            ## ⚠️ Basic Environmental Analysis
            
            Berdasarkan data input Anda:
            - **Kadar Nitrogen**: {sensor_data.get('N', 'N/A')} kg/ha
            - **Kadar Fosfor**: {sensor_data.get('P', 'N/A')} kg/ha
            - **Kadar Kalium**: {sensor_data.get('K', 'N/A')} kg/ha
            - **pH Tanah**: {sensor_data.get('ph', 'N/A')}
            - **Suhu**: {sensor_data.get('temperature', 'N/A')}°C
            - **Kelembaban**: {sensor_data.get('humidity', 'N/A')}%
            - **Curah Hujan**: {sensor_data.get('rainfall', 'N/A')} mm
            
            ### 🔧 Rekomendasi Umum:
            - Pantau kadar nutrisi tanah secara berkala
            - Pertahankan rentang pH optimal (6.0-7.0 untuk sebagian besar tanaman)
            - Pastikan drainase dan irigasi yang memadai
            - Pertimbangkan kondisi iklim untuk pemilihan tanaman
            
            *Catatan: Analisis bertenaga AI sementara tidak tersedia. Silakan periksa konfigurasi API Anda.*
            """
            
            return fallback_advice

# ==================== STREAMLIT UI FUNCTIONS ====================

def display_sensor_input_form():
    """Display sensor data input form"""
    st.markdown("### 📊 Input Data Sensor Lingkungan")
    st.markdown("*Masukkan kondisi lingkungan lahan Anda untuk mendapatkan rekomendasi yang dipersonalisasi*")
    
    with st.form("sensor_data_form"):
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("**Nutrisi Tanah (kg/ha)**")
            nitrogen = st.number_input("Nitrogen (N)", min_value=0.0, max_value=300.0, value=50.0, step=1.0, help="Kandungan nitrogen dalam tanah (kg/ha)")
            phosphorus = st.number_input("Fosfor (P)", min_value=0.0, max_value=150.0, value=25.0, step=1.0, help="Fosfor tersedia dalam tanah (kg/ha)")
            potassium = st.number_input("Kalium (K)", min_value=0.0, max_value=300.0, value=100.0, step=1.0, help="Kalium dapat ditukar dalam tanah (kg/ha)")
        
        with col2:
            st.markdown("**Kondisi Iklim**")
            temperature = st.number_input("Suhu (°C)", min_value=-10.0, max_value=50.0, value=28.0, step=0.1, help="Suhu rata-rata")
            humidity = st.number_input("Kelembaban (%)", min_value=0.0, max_value=100.0, value=75.0, step=1.0, help="Persentase kelembaban relatif")
            rainfall = st.number_input("Curah Hujan (mm)", min_value=0.0, max_value=3000.0, value=1500.0, step=10.0, help="Curah hujan tahunan dalam mm")
        
        with col3:
            st.markdown("**Kondisi Tanah**")
            ph = st.number_input("Tingkat pH", min_value=3.0, max_value=10.0, value=6.5, step=0.1, help="Tingkat pH tanah")
            
            # Additional context
            st.markdown("**Opsional**")
            field_size = st.number_input("Ukuran Lahan (hektar)", min_value=0.1, max_value=1000.0, value=1.0, step=0.1, help="Ukuran lahan pertanian")
            location = st.text_input("Lokasi/Daerah", value="Jawa Barat, Indonesia", help="Lokasi umum untuk pertimbangan regional")
        
        # Crop selection section below the 3 columns
        st.markdown("---")
        col4, col5 = st.columns(2)
        
        with col4:
            st.markdown("**Pilihan Tanaman (Wajib)**")
            crop_options = [
                "Rice", "Maize", "Chickpea", "Kidney Beans", "Pigeon Peas", 
                "Moth Beans", "Mung Bean", "Black Gram", "Lentil", "Pomegranate", 
                "Banana", "Mango", "Watermelon", "Muskmelon", 
                "Orange", "Papaya", "Cotton", "Jute", "Coffee"
            ]
            selected_crop = st.selectbox("Pilih Tanaman", crop_options, help="Pilih tanaman yang ingin Anda tanam")
        
        with col5:
            # Empty column for spacing
            st.markdown("")
        
        # Submit button
        submitted = st.form_submit_button("🔍 Dapatkan Rekomendasi Tanaman & Lingkungan", type="primary")
        
        if submitted:
            # Prepare sensor data
            sensor_data = {
                'N': nitrogen,
                'P': phosphorus,
                'K': potassium,
                'temperature': temperature,
                'humidity': humidity,
                'ph': ph,
                'rainfall': rainfall,
                'field_size': field_size,
                'location': location,
                'selected_crop': selected_crop
            }
            
            return sensor_data
    
    return None

def display_results(sensor_data, decision_system):
    """Display ML crop evaluation and AI environmental recommendations"""
    
    st.markdown("---")
    st.markdown("## 📈 Hasil Analisis")
    
    # ML Crop Evaluation Section
    ml_evaluation = None
    ai_predictor = decision_system.get_ai_predictor()
    
    if ai_predictor:
        st.markdown("### 🤖 Evaluasi Kesesuaian Tanaman")
        
        with st.spinner("Mengevaluasi kesesuaian tanaman dengan kondisi lingkungan"):
            try:
                # Get ML evaluation - returns tuple (crop_name, confidence)
                selected_crop = sensor_data.get('selected_crop', 'Unknown')
                crop_name, confidence = ai_predictor.evaluate_crop_suitability(sensor_data, selected_crop)
                
                # Display evaluation results
                col1, col2 = st.columns(2)
                
                with col1:
                    st.success(f"**Tanaman yang Dipilih:** {crop_name}")
                
                with col2:
                    # Determine color based on suitability level
                    if confidence >= 0.7:
                        st.success(f"**Tingkat Kesesuaian:** {confidence*100:.1f}% - Sangat Cocok")
                    elif confidence >= 0.5:
                        st.warning(f"**Tingkat Kesesuaian:** {confidence*100:.1f}% - Cukup Cocok")
                    else:
                        st.error(f"**Tingkat Kesesuaian:** {confidence*100:.1f}% - Kurang Cocok")
                
                ml_evaluation = (crop_name, confidence)
                
            except Exception as e:
                st.error(f"❌ ML prediction error: {str(e)}")
                st.info("Continuing with AI-only analysis...")
    else:
        if decision_system.ai_predictor_error:
            st.warning(f"⚠️ Evaluasi tanaman ML tidak tersedia: {decision_system.ai_predictor_error}")
        st.info("📊 Melanjutkan dengan analisis lingkungan AI saja...")
    
    # AI Environmental Recommendations Section  
    st.markdown("### 🧠 Optimisasi Lingkungan AI")
    
    with st.spinner("Menghasilkan rekomendasi lingkungan yang dipersonalisasi..."):
        environmental_advice = decision_system.generate_environmental_advice(sensor_data, ml_evaluation)
        st.markdown(environmental_advice)
    
    # Summary Section
    st.markdown("### 📋 Ringkasan Cepat")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Ukuran Lahan", f"{sensor_data.get('field_size', 'N/A')} ha")
        st.metric("pH Tanah", f"{sensor_data.get('ph', 'N/A')}")
    
    with col2:
        st.metric("Suhu", f"{sensor_data.get('temperature', 'N/A')}°C")
        st.metric("Curah Hujan", f"{sensor_data.get('rainfall', 'N/A')} mm")
    
    with col3:
        if ml_evaluation and len(ml_evaluation) >= 2:
            # Handle tuple format (crop_name, confidence)
            confidence = ml_evaluation[1] * 100  # Convert to percentage
            st.metric("Tingkat Kesesuaian", f"{confidence:.1f}%")
        st.metric("Tanggal Analisis", datetime.now().strftime("%Y-%m-%d"))

# ==================== MAIN APPLICATION ====================

def main():
    """Main application function"""
    
    st.set_page_config(
        page_title="Sistem Pendukung Keputusan Pertanian",
        page_icon="🌾",
        layout="wide",
        initial_sidebar_state="collapsed"
    )
    
    # Header
    st.title("🌾 Sistem Pendukung Keputusan Pertanian Indonesia")
    st.markdown("*Dapatkan rekomendasi tanaman instan dan saran optimisasi lingkungan berdasarkan kondisi lahan Anda*")
    
    # Deskripsi
    with st.expander("ℹ️ Cara Kerja Sistem Ini", expanded=False):
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**🤖 Komponen Machine Learning:**")
            st.markdown("• Model Random Forest yang dilatih pada dataset pertanian")
            st.markdown("• Menganalisis nutrisi tanah, iklim, dan kondisi pH")
            st.markdown("• Memberikan rekomendasi tanaman dengan skor kepercayaan")
            st.markdown("• Menyarankan pilihan tanaman alternatif")
        
        with col2:
            st.markdown("**🧠 Komponen Konsultasi dengan AI:**")
            st.markdown("• Model bahasa besar untuk analisis lingkungan")
            st.markdown("• Menghasilkan strategi optimisasi yang dipersonalisasi")
            st.markdown("• Memberikan panduan implementasi yang dapat ditindaklanjuti")
            st.markdown("• Menawarkan metrik pemantauan dan keberhasilan")
    
    # Initialize decision support system
    decision_system = DecisionSupportSystem()
    
    # Main input form
    sensor_data = display_sensor_input_form()
    
    # Display results if data is submitted
    if sensor_data:
        display_results(sensor_data, decision_system)
        
        # Action buttons
        st.markdown("---")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("🔄 Analisis Kondisi Berbeda", type="secondary"):
                st.rerun()
        
        with col2:
            if st.button("📊 Ekspor Hasil", type="secondary"):
                st.info("Fitur ekspor akan segera hadir!")
        
        with col3:
            if st.button("📖 Lihat Panduan Detail", type="secondary"):
                st.info("Panduan implementasi detail akan segera hadir!")
    
    # Footer
    st.markdown("---")
    st.markdown("### 💡 Fitur Sistem")
    
    feature_col1, feature_col2, feature_col3 = st.columns(3)
    
    with feature_col1:
        st.markdown("**🎯 Precision Agriculture**")
        st.markdown("• ML-powered crop selection")
        st.markdown("• Environmental condition analysis")
        st.markdown("• Data-driven recommendations")
    
    with feature_col2:
        st.markdown("**⚡ Instant Results**")
        st.markdown("• Real-time processing")
        st.markdown("• No account required")
        st.markdown("• Simple input interface")
    
    with feature_col3:
        st.markdown("**🔬 Scientific Approach**")
        st.markdown("• Evidence-based advice")
        st.markdown("• Confidence scoring")
        st.markdown("• Multiple alternatives")

if __name__ == "__main__":
    main()
