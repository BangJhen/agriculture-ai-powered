"""
ML Predictor Core Module for Agricultural Decision Support System
Contains AI Crop Predictor class and related ML functionality.
"""

import os
import pickle
import pandas as pd
import numpy as np
from typing import Dict, Tuple, Any, Optional, List

# Import config and utilities
from ..utils.config import ML_CONFIG, CROP_MAPPING, SENSOR_PARAMS
from ..utils.helpers import safe_float, handle_error, format_confidence_score

# Optional SHAP import
try:
    import shap
    SHAP_AVAILABLE = True
except ImportError:
    SHAP_AVAILABLE = False

# ==================== AI CROP PREDICTOR CLASS ====================

class AICropPredictor:
    """AI-powered crop prediction system with SHAP explainability."""
    
    def __init__(self, model_path: str = None):
        """Initialize the AI Crop Predictor"""
        self.model_path = model_path or ML_CONFIG['model_path']
        self.model = None
        self.label_encoder = None
        self.scaler = None
        self.explainer = None
        self.training_data = None
        
        # Load models on initialization
        self.load_models()
        if SHAP_AVAILABLE:
            self.initialize_explainer()
    
    def load_models(self):
        """Load the trained models"""
        try:
            model_files = ML_CONFIG['models']
            
            # Load Random Forest model
            model_file = os.path.join(self.model_path, model_files['random_forest'])
            with open(model_file, 'rb') as f:
                self.model = pickle.load(f)
            
            # Load Label Encoder
            encoder_file = os.path.join(self.model_path, model_files['label_encoder'])
            with open(encoder_file, 'rb') as f:
                self.label_encoder = pickle.load(f)
            
            # Load Scaler
            scaler_file = os.path.join(self.model_path, model_files['scaler'])
            with open(scaler_file, 'rb') as f:
                self.scaler = pickle.load(f)
            
            print("✅ ML models loaded successfully")
            return True
            
        except FileNotFoundError as e:
            handle_error('model_loading_failed', f"Model file not found: {str(e)}")
            return False
        except Exception as e:
            handle_error('model_loading_failed', f"Error loading models: {str(e)}")
            return False
    
    def initialize_explainer(self):
        """Initialize SHAP explainer for model interpretability"""
        if not SHAP_AVAILABLE or not self.model:
            return
            
        try:
            # Load training data for background
            training_files = ML_CONFIG['training_data']
            X_train_file = os.path.join(self.model_path, training_files['X_train'])
            
            if os.path.exists(X_train_file):
                X_train = pd.read_csv(X_train_file)
                
                # Create SHAP explainer with background data
                self.explainer = shap.TreeExplainer(self.model, X_train.sample(min(100, len(X_train))))
                print("✅ SHAP explainer initialized")
            else:
                print("⚠️ Training data not found for SHAP explainer")
                
        except Exception as e:
            print(f"⚠️ Error initializing SHAP explainer: {str(e)}")
    
    def get_feature_explanation(self, input_data: Dict[str, float], selected_crop: str, confidence: float) -> str:
        """Generate feature importance explanation using SHAP"""
        
        if not SHAP_AVAILABLE or not self.explainer:
            return self._generate_simple_explanation(input_data, selected_crop, confidence)
        
        try:
            # Prepare data for SHAP
            engineered_data = self.engineer_features(input_data)
            scaled_data = self.scaler.transform(engineered_data)
            
            # Get SHAP values
            shap_values = self.explainer.shap_values(scaled_data)
            
            # Extract feature importance
            if hasattr(shap_values, '__len__') and len(shap_values) > 1:
                # Multi-class classification
                shap_values = shap_values[0]  # Take first class
            
            feature_importance = dict(zip(engineered_data.columns, shap_values[0]))
            
            # Generate explanation
            return self._generate_shap_explanation(feature_importance, input_data, selected_crop, confidence)
            
        except Exception as e:
            print(f"⚠️ Error generating SHAP explanation: {str(e)}")
            return self._generate_simple_explanation(input_data, selected_crop, confidence)
    
    def _generate_simple_explanation(self, input_data: Dict[str, float], selected_crop: str, confidence: float) -> str:
        """Generate simple explanation without SHAP"""
        
        explanations = []
        
        # Analyze each parameter
        for param, value in input_data.items():
            if param in SENSOR_PARAMS:
                param_config = SENSOR_PARAMS[param]
                param_range = param_config['max'] - param_config['min']
                
                # Calculate relative position (0-1)
                relative_pos = (value - param_config['min']) / param_range
                
                if relative_pos < 0.3:
                    level = "rendah"
                elif relative_pos > 0.7:
                    level = "tinggi"
                else:
                    level = "sedang"
                
                explanations.append(f"• {param.title()}: {value} {param_config['unit']} ({level})")
        
        confidence_text = format_confidence_score(confidence)
        
        explanation = f"""
📊 **Analisis Kondisi Lahan untuk {selected_crop.title()}:**

{chr(10).join(explanations)}

🎯 **Tingkat Keyakinan:** {confidence_text}

💡 **Kesimpulan:** Berdasarkan kondisi sensor saat ini, tingkat kesesuaian untuk tanaman {selected_crop} adalah {confidence:.1%}.
        """
        
        return explanation.strip()
    
    def _generate_shap_explanation(self, feature_importance: Dict[str, float], input_data: Dict[str, float], 
                                  selected_crop: str, confidence: float) -> str:
        """Generate explanation using SHAP feature importance"""
        
        # Sort features by absolute importance
        sorted_features = sorted(feature_importance.items(), key=lambda x: abs(x[1]), reverse=True)
        
        explanations = []
        
        for feature, importance in sorted_features[:5]:  # Top 5 features
            # Map engineered feature back to original parameter
            original_param = self._map_feature_to_param(feature)
            
            if original_param in input_data:
                value = input_data[original_param]
                impact = "mendukung" if importance > 0 else "menghambat"
                strength = "sangat" if abs(importance) > 0.1 else "cukup"
                
                unit = SENSOR_PARAMS.get(original_param, {}).get('unit', '')
                explanations.append(f"• {original_param.title()}: {value} {unit} - {strength} {impact}")
        
        confidence_text = format_confidence_score(confidence)
        
        explanation = f"""
🧠 **Analisis AI untuk {selected_crop.title()}:**

**Faktor-faktor Utama:**
{chr(10).join(explanations)}

🎯 **Tingkat Keyakinan:** {confidence_text}

💡 **Rekomendasi:** Model AI mendeteksi tingkat kesesuaian {confidence:.1%} berdasarkan pola dari data training.
        """
        
        return explanation.strip()
    
    def _map_feature_to_param(self, feature_name: str) -> str:
        """Map engineered feature back to original parameter"""
        
        # Simple mapping for basic features
        param_mapping = {
            'N': 'nitrogen',
            'P': 'phosphorus', 
            'K': 'potassium',
            'temperature': 'temperature',
            'humidity': 'humidity',
            'ph': 'ph',
            'rainfall': 'rainfall'
        }
        
        # Check for direct match
        if feature_name in param_mapping:
            return param_mapping[feature_name]
        
        # Check for partial match (for engineered features)
        for orig_name, param in param_mapping.items():
            if orig_name.lower() in feature_name.lower():
                return param
        
        return feature_name  # Return as is if no mapping found
    
    def engineer_features(self, input_data: Dict[str, float]) -> pd.DataFrame:
        """Engineer features from input data - matches original model training from EDA.ipynb"""
        
        # Extract base features (original scale)
        N = safe_float(input_data.get('nitrogen', 0))
        P = safe_float(input_data.get('phosphorus', 0))
        K = safe_float(input_data.get('potassium', 0))
        temperature = safe_float(input_data.get('temperature', 0))
        humidity = safe_float(input_data.get('humidity', 0))
        ph = safe_float(input_data.get('ph', 0))
        rainfall = safe_float(input_data.get('rainfall', 0))
        
        # Create features in exact order from EDA.ipynb
        # Base features first
        features = {
            'N': N,
            'P': P,
            'K': K,
            'temperature': temperature,
            'humidity': humidity,
            'ph': ph,
            'rainfall': rainfall
        }
        
        # Engineered features (using exact logic from notebook)
        features['NPK_sum'] = N + P + K
        features['NP_ratio'] = N / (P + 1e-6)  # Avoid division by zero as in notebook
        features['NK_ratio'] = N / (K + 1e-6)
        features['PK_ratio'] = P / (K + 1e-6)
        features['temp_humidity_interaction'] = temperature * humidity
        features['rainfall_humidity_ratio'] = rainfall / (humidity + 1e-6)
        
        # pH categorization (exact logic from notebook)
        if ph < 6.5:
            features['ph_acidity_level'] = 1  # acidic
        elif ph > 7.5:
            features['ph_acidity_level'] = 3  # alkaline
        else:
            features['ph_acidity_level'] = 2  # neutral
        
        return pd.DataFrame([features])
    
    def preprocess_input(self, input_data: Dict[str, float]) -> np.ndarray:
        """Preprocess input data for prediction"""
        
        if not self.scaler:
            raise ValueError("Scaler not loaded")
        
        # Engineer features
        engineered_data = self.engineer_features(input_data)
        
        # Scale the data
        scaled_data = self.scaler.transform(engineered_data)
        
        return scaled_data
    
    def evaluate_crop_suitability(self, input_data: Dict[str, float], selected_crop: str) -> Tuple[str, float, str]:
        """Evaluate crop suitability and return prediction, confidence, and explanation"""
        
        if not self.model or not self.label_encoder:
            return "Error", 0.0, "Model tidak tersedia"
        
        try:
            # Preprocess input
            scaled_data = self.preprocess_input(input_data)
            
            # Get prediction probabilities
            probabilities = self.model.predict_proba(scaled_data)[0]
            
            # Get crop index
            crop_classes = self.label_encoder.classes_
            
            if selected_crop not in crop_classes:
                return "Error", 0.0, f"Tanaman '{selected_crop}' tidak dikenali oleh model"
            
            crop_index = list(crop_classes).index(selected_crop)
            confidence = probabilities[crop_index]
            
            # Determine recommendation
            threshold_high = ML_CONFIG['confidence_threshold']
            threshold_low = ML_CONFIG['low_confidence_threshold']
            
            if confidence >= threshold_high:
                recommendation = "Sangat Cocok"
            elif confidence >= threshold_low:
                recommendation = "Cukup Cocok"
            else:
                recommendation = "Kurang Cocok"
            
            # Generate explanation
            explanation = self.get_feature_explanation(input_data, selected_crop, confidence)
            
            return recommendation, confidence, explanation
            
        except Exception as e:
            error_msg = f"Error dalam evaluasi: {str(e)}"
            handle_error('evaluation_failed', error_msg)
            return "Error", 0.0, error_msg
    
    def get_top_crop_recommendations(self, input_data: Dict[str, float], top_k: int = 5) -> List[Tuple[str, float]]:
        """Get top crop recommendations based on input conditions"""
        
        if not self.model or not self.label_encoder:
            return []
        
        try:
            # Preprocess input
            scaled_data = self.preprocess_input(input_data)
            
            # Get prediction probabilities
            probabilities = self.model.predict_proba(scaled_data)[0]
            
            # Get crop classes
            crop_classes = self.label_encoder.classes_
            
            # Create recommendations
            recommendations = [(crop, prob) for crop, prob in zip(crop_classes, probabilities)]
            
            # Sort by probability and return top K
            recommendations.sort(key=lambda x: x[1], reverse=True)
            
            return recommendations[:top_k]
            
        except Exception as e:
            handle_error('recommendation_failed', f"Error getting recommendations: {str(e)}")
            return []
    
    def is_model_loaded(self) -> bool:
        """Check if models are loaded successfully"""
        return all([self.model, self.label_encoder, self.scaler])
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get information about loaded models"""
        
        info = {
            'model_loaded': self.is_model_loaded(),
            'shap_available': SHAP_AVAILABLE and self.explainer is not None,
            'model_type': type(self.model).__name__ if self.model else None,
            'feature_count': len(self.scaler.feature_names_in_) if self.scaler and hasattr(self.scaler, 'feature_names_in_') else None,
            'crop_classes': list(self.label_encoder.classes_) if self.label_encoder else None
        }
        
        return info 