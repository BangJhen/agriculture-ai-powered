"""
Recommendation Engine for Agricultural Decision Support System
Combines ML predictions, LLM insights, and knowledge base search for comprehensive recommendations.
"""

import os
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
import json

# Import our services
from .llm_service import agricultural_llm
from .knowledge_base import knowledge_base
from ..core.ml_predictor import AICropPredictor
from ..utils.config import CROP_MAPPING, SENSOR_PARAMS
from ..utils.helpers import format_timestamp, safe_float

# ==================== RECOMMENDATION ENGINE ====================

class RecommendationEngine:
    """Comprehensive recommendation engine combining ML, LLM, and knowledge base"""
    
    def __init__(self):
        self.llm_service = agricultural_llm
        self.knowledge_base = knowledge_base
        self.ml_predictor = None
        self.ml_predictor_loaded = False
        
        # Initialize ML predictor lazily
        self._initialize_ml_predictor()
    
    def _initialize_ml_predictor(self):
        """Initialize ML predictor if not already loaded"""
        if not self.ml_predictor_loaded:
            try:
                self.ml_predictor = AICropPredictor()
                self.ml_predictor_loaded = True
                print("✅ ML Predictor initialized in recommendation engine")
            except Exception as e:
                print(f"⚠️ Could not initialize ML predictor: {e}")
                self.ml_predictor_loaded = True  # Set to True to prevent retries
    
    def generate_comprehensive_analysis(self, sensor_data: Dict[str, Any], 
                                       location_data: Dict[str, Any] = None,
                                       selected_crop: str = None) -> Dict[str, Any]:
        """Generate comprehensive analysis combining all available tools"""
        
        analysis = {
            "timestamp": datetime.now().isoformat(),
            "sensor_data": sensor_data,
            "location_data": location_data,
            "selected_crop": selected_crop,
            "ml_prediction": None,
            "llm_evaluation": None,
            "knowledge_base_insights": None,
            "final_recommendations": None,
            "confidence_score": 0.0,
            "warning_flags": [],
            "optimization_suggestions": []
        }
        
        # 1. ML Prediction
        if self.ml_predictor and selected_crop:
            try:
                ml_result = self.ml_predictor.evaluate_crop_suitability(
                    sensor_data, selected_crop
                )
                analysis["ml_prediction"] = {
                    "crop": ml_result[0],
                    "confidence": ml_result[1],
                    "explanation": ml_result[2]
                }
                analysis["confidence_score"] = ml_result[1]
            except Exception as e:
                print(f"⚠️ ML prediction error: {e}")
                analysis["warning_flags"].append("ML prediction not available")
        
        # 2. Knowledge Base Search
        if self.knowledge_base.is_available:
            try:
                # Search for relevant knowledge
                search_queries = self._generate_knowledge_search_queries(
                    sensor_data, location_data, selected_crop
                )
                
                knowledge_results = []
                for query in search_queries:
                    results = self.knowledge_base.search_knowledge(query, top_k=3)
                    knowledge_results.extend(results)
                
                # Remove duplicates and sort by similarity
                unique_results = {}
                for result in knowledge_results:
                    if result['id'] not in unique_results:
                        unique_results[result['id']] = result
                
                analysis["knowledge_base_insights"] = list(unique_results.values())[:5]
                
            except Exception as e:
                print(f"⚠️ Knowledge base search error: {e}")
                analysis["warning_flags"].append("Knowledge base search not available")
        
        # 3. LLM Evaluation
        if self.llm_service.llm_manager.is_available():
            try:
                llm_evaluation = self.llm_service.generate_crop_evaluation(
                    sensor_data, location_data, analysis["ml_prediction"]
                )
                analysis["llm_evaluation"] = llm_evaluation
                
            except Exception as e:
                print(f"⚠️ LLM evaluation error: {e}")
                analysis["warning_flags"].append("LLM evaluation not available")
        
        # 4. Generate Final Recommendations
        analysis["final_recommendations"] = self._generate_final_recommendations(analysis)
        
        # 5. Optimization Suggestions
        analysis["optimization_suggestions"] = self._generate_optimization_suggestions(
            sensor_data, selected_crop, analysis
        )
        
        # 6. Warning Flags
        analysis["warning_flags"].extend(
            self._check_warning_conditions(sensor_data, analysis)
        )
        
        return analysis
    
    def _generate_knowledge_search_queries(self, sensor_data: Dict[str, Any], 
                                         location_data: Dict[str, Any] = None,
                                         selected_crop: str = None) -> List[str]:
        """Generate search queries for knowledge base"""
        
        queries = []
        
        # Base crop query
        if selected_crop:
            queries.append(f"budidaya {selected_crop} Indonesia")
            queries.append(f"cara menanam {selected_crop}")
        
        # Condition-based queries
        temp = sensor_data.get('temperature', 25)
        humidity = sensor_data.get('humidity', 70)
        ph = sensor_data.get('ph', 6.5)
        
        if temp > 30:
            queries.append("pertanian suhu tinggi panas")
        elif temp < 20:
            queries.append("pertanian suhu dingin")
        
        if humidity > 80:
            queries.append("pertanian kelembaban tinggi")
        elif humidity < 50:
            queries.append("pertanian kelembaban rendah")
        
        if ph < 5.5:
            queries.append("tanah asam pengapuran")
        elif ph > 8.0:
            queries.append("tanah basa alkalin")
        
        # Location-based queries
        if location_data and location_data.get('address'):
            location = location_data['address']
            queries.append(f"pertanian {location}")
        
        # Nutrient queries
        nitrogen = sensor_data.get('nitrogen', 50)
        phosphorus = sensor_data.get('phosphorus', 50)
        potassium = sensor_data.get('potassium', 50)
        
        if nitrogen < 30:
            queries.append("kekurangan nitrogen pupuk")
        if phosphorus < 20:
            queries.append("kekurangan fosfor pupuk")
        if potassium < 30:
            queries.append("kekurangan kalium pupuk")
        
        return queries[:5]  # Limit to 5 queries
    
    def _generate_final_recommendations(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Generate final recommendations based on all analysis"""
        
        recommendations = {
            "primary_actions": [],
            "secondary_actions": [],
            "immediate_concerns": [],
            "long_term_planning": [],
            "resource_requirements": {}
        }
        
        sensor_data = analysis["sensor_data"]
        ml_prediction = analysis.get("ml_prediction")
        knowledge_insights = analysis.get("knowledge_base_insights", [])
        
        # Primary actions based on ML prediction
        if ml_prediction:
            confidence = ml_prediction["confidence"]
            if confidence > 0.7:
                recommendations["primary_actions"].append(
                    f"✅ Kondisi sangat cocok untuk {ml_prediction['crop']} (confidence: {confidence:.1%})"
                )
            elif confidence > 0.5:
                recommendations["primary_actions"].append(
                    f"⚠️ Kondisi cukup cocok untuk {ml_prediction['crop']} dengan optimasi (confidence: {confidence:.1%})"
                )
            else:
                recommendations["primary_actions"].append(
                    f"❌ Kondisi kurang cocok untuk {ml_prediction['crop']} (confidence: {confidence:.1%})"
                )
        
        # Nutrient management
        n_level = sensor_data.get('nitrogen', 50)
        p_level = sensor_data.get('phosphorus', 50)
        k_level = sensor_data.get('potassium', 50)
        
        if n_level < 40:
            recommendations["immediate_concerns"].append(
                f"🧪 Nitrogen rendah ({n_level} kg/ha) - Aplikasi pupuk urea atau organik"
            )
        if p_level < 30:
            recommendations["immediate_concerns"].append(
                f"🧪 Fosfor rendah ({p_level} kg/ha) - Aplikasi pupuk TSP atau DAP"
            )
        if k_level < 30:
            recommendations["immediate_concerns"].append(
                f"🧪 Kalium rendah ({k_level} kg/ha) - Aplikasi pupuk KCl atau organik"
            )
        
        # pH management
        ph_level = sensor_data.get('ph', 6.5)
        if ph_level < 5.5:
            recommendations["immediate_concerns"].append(
                f"⚗️ pH terlalu asam ({ph_level}) - Aplikasi kapur pertanian"
            )
        elif ph_level > 8.0:
            recommendations["immediate_concerns"].append(
                f"⚗️ pH terlalu basa ({ph_level}) - Aplikasi bahan organik dan sulfur"
            )
        
        # Water management
        rainfall = sensor_data.get('rainfall', 100)
        if rainfall < 50:
            recommendations["immediate_concerns"].append(
                f"💧 Curah hujan rendah ({rainfall} mm) - Siapkan sistem irigasi"
            )
        elif rainfall > 250:
            recommendations["immediate_concerns"].append(
                f"🌧️ Curah hujan tinggi ({rainfall} mm) - Siapkan sistem drainase"
            )
        
        # Knowledge base insights
        if knowledge_insights:
            for insight in knowledge_insights[:3]:
                if insight['similarity_score'] > 0.8:
                    recommendations["secondary_actions"].append(
                        f"📚 {insight['category'].replace('_', ' ').title()}: {insight['content'][:100]}..."
                    )
        
        # Resource requirements
        land_area = sensor_data.get('land_area', 1.0)
        recommendations["resource_requirements"] = {
            "luas_lahan": f"{land_area} ha",
            "estimasi_biaya_pupuk": f"Rp {self._estimate_fertilizer_cost(sensor_data, land_area):,.0f}",
            "waktu_implementasi": "2-4 minggu",
            "tenaga_kerja": "2-3 orang" if land_area > 2 else "1-2 orang"
        }
        
        return recommendations
    
    def _generate_optimization_suggestions(self, sensor_data: Dict[str, Any], 
                                         selected_crop: str = None,
                                         analysis: Dict[str, Any] = None) -> List[str]:
        """Generate optimization suggestions"""
        
        suggestions = []
        
        # Soil optimization
        ph_level = sensor_data.get('ph', 6.5)
        if ph_level < 6.0 or ph_level > 7.5:
            suggestions.append("🌱 Optimasi pH tanah untuk meningkatkan penyerapan nutrisi")
        
        # Nutrient optimization
        n_level = sensor_data.get('nitrogen', 50)
        p_level = sensor_data.get('phosphorus', 50)
        k_level = sensor_data.get('potassium', 50)
        
        if n_level < 60:
            suggestions.append("🧪 Tingkatkan nitrogen untuk pertumbuhan vegetatif optimal")
        if p_level < 40:
            suggestions.append("🧪 Tingkatkan fosfor untuk perkembangan akar yang baik")
        if k_level < 50:
            suggestions.append("🧪 Tingkatkan kalium untuk ketahanan terhadap penyakit")
        
        # Climate optimization
        temp = sensor_data.get('temperature', 25)
        humidity = sensor_data.get('humidity', 70)
        
        if temp > 32:
            suggestions.append("🌡️ Gunakan mulsa atau naungan untuk mengurangi suhu tanah")
        if humidity > 85:
            suggestions.append("💨 Perbaiki ventilasi untuk mengurangi kelembaban berlebih")
        
        # Water optimization
        rainfall = sensor_data.get('rainfall', 100)
        if rainfall < 80:
            suggestions.append("💧 Implementasi sistem irigasi tetes untuk efisiensi air")
        
        # Crop-specific optimization
        if selected_crop:
            if selected_crop == 'rice':
                suggestions.append("🌾 Aplikasi pupuk organik untuk meningkatkan struktur tanah")
            elif selected_crop == 'corn':
                suggestions.append("🌽 Pertimbangkan penanaman sisipan untuk diversifikasi")
            elif selected_crop == 'banana':
                suggestions.append("🍌 Pastikan drainase yang baik untuk mencegah busuk akar")
        
        return suggestions
    
    def _check_warning_conditions(self, sensor_data: Dict[str, Any], 
                                 analysis: Dict[str, Any]) -> List[str]:
        """Check for warning conditions"""
        
        warnings = []
        
        # Critical pH levels
        ph_level = sensor_data.get('ph', 6.5)
        if ph_level < 4.5:
            warnings.append("KRITIS: pH tanah terlalu asam - dapat meracuni tanaman")
        elif ph_level > 9.0:
            warnings.append("KRITIS: pH tanah terlalu basa - nutrisi tidak tersedia")
        
        # Extreme temperatures
        temp = sensor_data.get('temperature', 25)
        if temp > 40:
            warnings.append("KRITIS: Suhu terlalu tinggi - risiko heat stress")
        elif temp < 10:
            warnings.append("KRITIS: Suhu terlalu rendah - pertumbuhan terhambat")
        
        # Nutrient deficiency
        n_level = sensor_data.get('nitrogen', 50)
        if n_level < 10:
            warnings.append("KRITIS: Kekurangan nitrogen parah - tanaman akan kuning")
        
        # Excessive rainfall
        rainfall = sensor_data.get('rainfall', 100)
        if rainfall > 300:
            warnings.append("PERINGATAN: Curah hujan berlebih - risiko banjir dan penyakit")
        
        # Low confidence prediction
        if analysis.get("ml_prediction") and analysis["ml_prediction"]["confidence"] < 0.3:
            warnings.append("PERINGATAN: Prediksi ML confidence rendah - pertimbangkan tanaman alternatif")
        
        return warnings
    
    def _estimate_fertilizer_cost(self, sensor_data: Dict[str, Any], land_area: float) -> float:
        """Estimate fertilizer cost based on nutrient needs"""
        
        # Base prices per kg (in Rupiah)
        prices = {
            'urea': 2500,  # Nitrogen
            'tsp': 3000,   # Phosphorus
            'kcl': 2800    # Potassium
        }
        
        # Calculate nutrient needs
        n_need = max(0, 60 - sensor_data.get('nitrogen', 50))
        p_need = max(0, 40 - sensor_data.get('phosphorus', 50))
        k_need = max(0, 50 - sensor_data.get('potassium', 50))
        
        # Calculate fertilizer amounts (simplified conversion)
        urea_kg = (n_need * 2.2) * land_area  # Urea is ~45% N
        tsp_kg = (p_need * 2.2) * land_area   # TSP is ~45% P2O5
        kcl_kg = (k_need * 1.7) * land_area   # KCl is ~60% K2O
        
        # Calculate total cost
        total_cost = (
            urea_kg * prices['urea'] +
            tsp_kg * prices['tsp'] +
            kcl_kg * prices['kcl']
        )
        
        return total_cost
    
    def generate_seasonal_recommendations(self, location_data: Dict[str, Any],
                                        current_month: int = None) -> Dict[str, Any]:
        """Generate seasonal recommendations"""
        
        if self.llm_service.llm_manager.is_available():
            try:
                seasonal_advice = self.llm_service.generate_seasonal_recommendations(
                    location_data, current_month
                )
                return {
                    "seasonal_advice": seasonal_advice,
                    "generated_at": datetime.now().isoformat(),
                    "location": location_data.get('address', 'Unknown')
                }
            except Exception as e:
                print(f"⚠️ Error generating seasonal recommendations: {e}")
        
        return {
            "seasonal_advice": "Rekomendasi musiman tidak tersedia saat ini",
            "generated_at": datetime.now().isoformat(),
            "location": location_data.get('address', 'Unknown')
        }
    
    def generate_location_specific_advice(self, location_data: Dict[str, Any],
                                        sensor_data: Dict[str, Any] = None) -> Dict[str, Any]:
        """Generate location-specific advice"""
        
        if self.llm_service.llm_manager.is_available():
            try:
                location_advice = self.llm_service.generate_location_specific_advice(
                    location_data, sensor_data
                )
                return {
                    "location_advice": location_advice,
                    "generated_at": datetime.now().isoformat(),
                    "location": location_data.get('address', 'Unknown')
                }
            except Exception as e:
                print(f"⚠️ Error generating location advice: {e}")
        
        return {
            "location_advice": "Saran lokasi tidak tersedia saat ini",
            "generated_at": datetime.now().isoformat(),
            "location": location_data.get('address', 'Unknown')
        }
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get comprehensive system status"""
        
        return {
            "ml_predictor": {
                "loaded": self.ml_predictor_loaded,
                "available": self.ml_predictor is not None
            },
            "llm_service": self.llm_service.get_service_status(),
            "knowledge_base": self.knowledge_base.get_status(),
            "last_check": datetime.now().isoformat()
        }

# ==================== GLOBAL INSTANCE ====================

# Global instance for easy access
recommendation_engine = RecommendationEngine() 