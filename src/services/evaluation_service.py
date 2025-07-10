"""
Evaluation Service for Agricultural Decision Support System
Provides comprehensive crop suitability analysis with ML and LLM integration.
"""

import os
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
import json

# Import services
from .llm_service import agricultural_llm
from .knowledge_base import knowledge_base
from .location_context import location_context_service
from ..core.ml_predictor import AICropPredictor
from ..utils.config import CROP_MAPPING, SENSOR_PARAMS
from ..utils.helpers import safe_float, format_timestamp

# ==================== EVALUATION SERVICE ====================

class EvaluationService:
    """Comprehensive evaluation service for crop suitability analysis"""
    
    def __init__(self):
        self.llm_service = agricultural_llm
        self.knowledge_base = knowledge_base
        self.location_service = location_context_service
        self.ml_predictor = None
        self.ml_predictor_loaded = False
        
        # Initialize ML predictor
        self._initialize_ml_predictor()
    
    def _initialize_ml_predictor(self):
        """Initialize ML predictor if not already loaded"""
        if not self.ml_predictor_loaded:
            try:
                self.ml_predictor = AICropPredictor()
                self.ml_predictor_loaded = True
                print("✅ ML Predictor initialized in evaluation service")
            except Exception as e:
                print(f"⚠️ Could not initialize ML predictor: {e}")
                self.ml_predictor_loaded = True
    
    def comprehensive_crop_evaluation(self, sensor_data: Dict[str, Any], 
                                     location_data: Dict[str, Any] = None,
                                     selected_crop: str = None) -> Dict[str, Any]:
        """Perform comprehensive crop evaluation using all available tools"""
        
        evaluation = {
            "timestamp": datetime.now().isoformat(),
            "sensor_data": sensor_data,
            "location_data": location_data,
            "selected_crop": selected_crop,
            "ml_analysis": None,
            "llm_analysis": None,
            "knowledge_base_insights": None,
            "location_context": None,
            "suitability_score": 0.0,
            "confidence_level": "low",
            "recommendations": {},
            "risk_assessment": {},
            "optimization_plan": {},
            "alternative_crops": []
        }
        
        # 1. ML Analysis
        evaluation["ml_analysis"] = self._perform_ml_analysis(sensor_data, selected_crop)
        
        # 2. Location Context Analysis
        if location_data:
            evaluation["location_context"] = self.location_service.determine_location_context(location_data)
        
        # 3. Knowledge Base Search
        evaluation["knowledge_base_insights"] = self._search_knowledge_base(
            sensor_data, location_data, selected_crop
        )
        
        # 4. LLM Analysis
        evaluation["llm_analysis"] = self._perform_llm_analysis(
            sensor_data, location_data, selected_crop, evaluation
        )
        
        # 5. Calculate Overall Suitability Score
        evaluation["suitability_score"] = self._calculate_suitability_score(evaluation)
        evaluation["confidence_level"] = self._determine_confidence_level(evaluation)
        
        # 6. Generate Recommendations
        evaluation["recommendations"] = self._generate_recommendations(evaluation)
        
        # 7. Risk Assessment
        evaluation["risk_assessment"] = self._assess_risks(evaluation)
        
        # 8. Optimization Plan
        evaluation["optimization_plan"] = self._create_optimization_plan(evaluation)
        
        # 9. Alternative Crops
        evaluation["alternative_crops"] = self._suggest_alternative_crops(evaluation)
        
        return evaluation
    
    def _perform_ml_analysis(self, sensor_data: Dict[str, Any], selected_crop: str) -> Dict[str, Any]:
        """Perform ML analysis for crop suitability"""
        
        ml_analysis = {
            "available": False,
            "crop_prediction": None,
            "confidence": 0.0,
            "feature_importance": {},
            "explanation": ""
        }
        
        if self.ml_predictor and selected_crop:
            try:
                # Get crop prediction
                ml_result = self.ml_predictor.evaluate_crop_suitability(
                    sensor_data, selected_crop
                )
                
                ml_analysis["available"] = True
                ml_analysis["crop_prediction"] = ml_result[0]
                ml_analysis["confidence"] = ml_result[1]
                ml_analysis["explanation"] = ml_result[2]
                
                # Get top crop recommendations for comparison
                if hasattr(self.ml_predictor, 'get_top_crop_recommendations'):
                    top_crops = self.ml_predictor.get_top_crop_recommendations(sensor_data, 5)
                    ml_analysis["top_recommendations"] = top_crops
                
                print(f"✅ ML Analysis completed for {selected_crop}")
                
            except Exception as e:
                print(f"⚠️ ML Analysis error: {e}")
                ml_analysis["explanation"] = f"Error in ML analysis: {str(e)}"
        
        return ml_analysis
    
    def _search_knowledge_base(self, sensor_data: Dict[str, Any], 
                              location_data: Dict[str, Any] = None,
                              selected_crop: str = None) -> List[Dict[str, Any]]:
        """Search knowledge base for relevant information"""
        
        if not self.knowledge_base.is_available:
            return []
        
        try:
            # Generate search queries
            queries = []
            
            # Crop-specific queries
            if selected_crop:
                queries.extend([
                    f"budidaya {selected_crop}",
                    f"syarat tumbuh {selected_crop}",
                    f"masalah {selected_crop}"
                ])
            
            # Condition-based queries
            ph = sensor_data.get('ph', 6.5)
            temp = sensor_data.get('temperature', 25)
            
            if ph < 5.5:
                queries.append("tanah asam masalah")
            elif ph > 8.0:
                queries.append("tanah alkalin basa")
            
            if temp > 35:
                queries.append("suhu tinggi panas")
            elif temp < 15:
                queries.append("suhu rendah dingin")
            
            # Search knowledge base
            all_results = []
            for query in queries:
                results = self.knowledge_base.search_knowledge(query, top_k=3)
                all_results.extend(results)
            
            # Remove duplicates and sort by relevance
            unique_results = {}
            for result in all_results:
                if result['id'] not in unique_results:
                    unique_results[result['id']] = result
            
            return sorted(unique_results.values(), 
                         key=lambda x: x['similarity_score'], reverse=True)[:5]
            
        except Exception as e:
            print(f"⚠️ Knowledge base search error: {e}")
            return []
    
    def _perform_llm_analysis(self, sensor_data: Dict[str, Any], 
                             location_data: Dict[str, Any] = None,
                             selected_crop: str = None,
                             evaluation: Dict[str, Any] = None) -> str:
        """Perform LLM analysis for comprehensive evaluation"""
        
        if not self.llm_service.llm_manager.is_available():
            return "⚠️ LLM analysis tidak tersedia"
        
        try:
            # Prepare context for LLM
            context = self._prepare_llm_context(sensor_data, location_data, selected_crop, evaluation)
            
            # Generate LLM analysis
            llm_analysis = self.llm_service.generate_crop_evaluation(
                sensor_data, location_data, evaluation.get("ml_analysis")
            )
            
            return llm_analysis
            
        except Exception as e:
            print(f"⚠️ LLM analysis error: {e}")
            return f"Error dalam analisis LLM: {str(e)}"
    
    def _prepare_llm_context(self, sensor_data: Dict[str, Any], 
                            location_data: Dict[str, Any] = None,
                            selected_crop: str = None,
                            evaluation: Dict[str, Any] = None) -> str:
        """Prepare comprehensive context for LLM analysis"""
        
        context = f"""
        **Analisis Komprehensif untuk Evaluasi Tanaman**
        
        **Data Sensor:**
        - Nitrogen: {sensor_data.get('nitrogen', 'N/A')} kg/ha
        - Fosfor: {sensor_data.get('phosphorus', 'N/A')} kg/ha
        - Kalium: {sensor_data.get('potassium', 'N/A')} kg/ha
        - Suhu: {sensor_data.get('temperature', 'N/A')}°C
        - Kelembaban: {sensor_data.get('humidity', 'N/A')}%
        - pH: {sensor_data.get('ph', 'N/A')}
        - Curah Hujan: {sensor_data.get('rainfall', 'N/A')} mm
        - Luas Lahan: {sensor_data.get('land_area', 'N/A')} ha
        """
        
        if location_data:
            context += f"""
            
            **Informasi Lokasi:**
            - Alamat: {location_data.get('address', 'N/A')}
            - Koordinat: {location_data.get('lat', 'N/A')}, {location_data.get('lng', 'N/A')}
            """
        
        if selected_crop:
            context += f"""
            
            **Tanaman Target:** {selected_crop}
            """
        
        if evaluation and evaluation.get("ml_analysis"):
            ml_analysis = evaluation["ml_analysis"]
            if ml_analysis.get("available"):
                context += f"""
                
                **Hasil Analisis ML:**
                - Prediksi: {ml_analysis.get('crop_prediction', 'N/A')}
                - Confidence: {ml_analysis.get('confidence', 0):.1%}
                """
        
        return context
    
    def _calculate_suitability_score(self, evaluation: Dict[str, Any]) -> float:
        """Calculate overall suitability score"""
        
        score = 0.0
        weight_total = 0.0
        
        # ML score (40% weight)
        ml_analysis = evaluation.get("ml_analysis")
        if ml_analysis and ml_analysis.get("available"):
            score += ml_analysis.get("confidence", 0) * 0.4
            weight_total += 0.4
        
        # Environmental conditions score (30% weight)
        sensor_data = evaluation.get("sensor_data", {})
        env_score = self._calculate_environmental_score(sensor_data)
        score += env_score * 0.3
        weight_total += 0.3
        
        # Location context score (20% weight)
        location_context = evaluation.get("location_context")
        if location_context:
            loc_score = self._calculate_location_score(location_context, evaluation.get("selected_crop"))
            score += loc_score * 0.2
            weight_total += 0.2
        
        # Knowledge base relevance (10% weight)
        kb_insights = evaluation.get("knowledge_base_insights", [])
        if kb_insights:
            kb_score = sum(insight['similarity_score'] for insight in kb_insights[:3]) / 3
            score += kb_score * 0.1
            weight_total += 0.1
        
        # Normalize score
        if weight_total > 0:
            score = score / weight_total
        
        return min(1.0, max(0.0, score))
    
    def _calculate_environmental_score(self, sensor_data: Dict[str, Any]) -> float:
        """Calculate environmental conditions score"""
        
        score = 0.0
        factors = 0
        
        # pH score
        ph = sensor_data.get('ph', 6.5)
        if 6.0 <= ph <= 7.5:
            score += 1.0
        elif 5.5 <= ph <= 8.0:
            score += 0.7
        else:
            score += 0.3
        factors += 1
        
        # Temperature score
        temp = sensor_data.get('temperature', 25)
        if 20 <= temp <= 30:
            score += 1.0
        elif 15 <= temp <= 35:
            score += 0.7
        else:
            score += 0.3
        factors += 1
        
        # Humidity score
        humidity = sensor_data.get('humidity', 70)
        if 60 <= humidity <= 80:
            score += 1.0
        elif 40 <= humidity <= 90:
            score += 0.7
        else:
            score += 0.3
        factors += 1
        
        # Nutrient balance score
        n = sensor_data.get('nitrogen', 50)
        p = sensor_data.get('phosphorus', 50)
        k = sensor_data.get('potassium', 50)
        
        nutrient_score = 0.0
        if n >= 40:
            nutrient_score += 0.33
        if p >= 30:
            nutrient_score += 0.33
        if k >= 40:
            nutrient_score += 0.34
        
        score += nutrient_score
        factors += 1
        
        return score / factors if factors > 0 else 0.0
    
    def _calculate_location_score(self, location_context: Dict[str, Any], selected_crop: str) -> float:
        """Calculate location-based score"""
        
        score = 0.8  # Base score
        
        regional_data = location_context.get("regional_data", {})
        if selected_crop and "main_crops" in regional_data:
            if selected_crop in regional_data["main_crops"]:
                score = 1.0
        
        # Confidence penalty
        confidence = location_context.get("confidence", 0.5)
        score *= (0.5 + confidence * 0.5)
        
        return score
    
    def _determine_confidence_level(self, evaluation: Dict[str, Any]) -> str:
        """Determine confidence level of evaluation"""
        
        score = evaluation.get("suitability_score", 0.0)
        
        # Check data availability
        data_completeness = 0.0
        if evaluation.get("ml_analysis", {}).get("available"):
            data_completeness += 0.4
        if evaluation.get("location_context"):
            data_completeness += 0.3
        if evaluation.get("knowledge_base_insights"):
            data_completeness += 0.2
        if evaluation.get("llm_analysis"):
            data_completeness += 0.1
        
        # Combined confidence
        combined_confidence = (score + data_completeness) / 2
        
        if combined_confidence >= 0.8:
            return "high"
        elif combined_confidence >= 0.6:
            return "medium"
        else:
            return "low"
    
    def _generate_recommendations(self, evaluation: Dict[str, Any]) -> Dict[str, Any]:
        """Generate comprehensive recommendations"""
        
        recommendations = {
            "immediate_actions": [],
            "short_term_improvements": [],
            "long_term_strategies": [],
            "resource_requirements": {},
            "timeline": {}
        }
        
        sensor_data = evaluation.get("sensor_data", {})
        suitability_score = evaluation.get("suitability_score", 0.0)
        
        # Immediate actions based on suitability score
        if suitability_score >= 0.8:
            recommendations["immediate_actions"].append(
                "✅ Kondisi optimal - Lanjutkan dengan penanaman"
            )
        elif suitability_score >= 0.6:
            recommendations["immediate_actions"].append(
                "⚠️ Kondisi cukup baik - Lakukan optimasi sebelum tanam"
            )
        else:
            recommendations["immediate_actions"].append(
                "❌ Kondisi kurang sesuai - Perbaikan mendasar diperlukan"
            )
        
        # Nutrient management
        n_level = sensor_data.get('nitrogen', 50)
        p_level = sensor_data.get('phosphorus', 50)
        k_level = sensor_data.get('potassium', 50)
        
        if n_level < 40:
            recommendations["immediate_actions"].append(
                f"🧪 Aplikasi pupuk nitrogen - Defisiensi {40 - n_level} kg/ha"
            )
        
        if p_level < 30:
            recommendations["immediate_actions"].append(
                f"🧪 Aplikasi pupuk fosfor - Defisiensi {30 - p_level} kg/ha"
            )
        
        if k_level < 40:
            recommendations["immediate_actions"].append(
                f"🧪 Aplikasi pupuk kalium - Defisiensi {40 - k_level} kg/ha"
            )
        
        # pH management
        ph_level = sensor_data.get('ph', 6.5)
        if ph_level < 5.5:
            recommendations["short_term_improvements"].append(
                f"🧪 Pengapuran untuk menaikkan pH dari {ph_level} ke 6.0-7.0"
            )
        elif ph_level > 8.0:
            recommendations["short_term_improvements"].append(
                f"🧪 Penambahan bahan organik untuk menurunkan pH dari {ph_level}"
            )
        
        # Resource requirements
        land_area = sensor_data.get('land_area', 1.0)
        recommendations["resource_requirements"] = {
            "pupuk_organik": f"{land_area * 2} ton kompos",
            "pupuk_anorganik": f"NPK {land_area * 300} kg",
            "kapur_pertanian": f"{land_area * 500} kg" if ph_level < 5.5 else "Tidak diperlukan",
            "tenaga_kerja": f"{int(land_area * 2)} orang-hari"
        }
        
        # Timeline
        recommendations["timeline"] = {
            "minggu_1": "Persiapan lahan dan pengapuran",
            "minggu_2": "Aplikasi pupuk dasar",
            "minggu_3": "Penanaman",
            "minggu_4-8": "Pemeliharaan dan pemupukan susulan"
        }
        
        return recommendations
    
    def _assess_risks(self, evaluation: Dict[str, Any]) -> Dict[str, Any]:
        """Assess risks for crop cultivation"""
        
        risks = {
            "environmental_risks": [],
            "nutritional_risks": [],
            "location_risks": [],
            "overall_risk_level": "medium"
        }
        
        sensor_data = evaluation.get("sensor_data", {})
        
        # Environmental risks
        temp = sensor_data.get('temperature', 25)
        if temp > 35:
            risks["environmental_risks"].append({
                "risk": "Heat stress",
                "level": "high",
                "mitigation": "Mulsa dan naungan"
            })
        
        ph = sensor_data.get('ph', 6.5)
        if ph < 5.0:
            risks["environmental_risks"].append({
                "risk": "Keracunan aluminium",
                "level": "high",
                "mitigation": "Pengapuran intensif"
            })
        
        # Nutritional risks
        n_level = sensor_data.get('nitrogen', 50)
        if n_level < 20:
            risks["nutritional_risks"].append({
                "risk": "Defisiensi nitrogen parah",
                "level": "high",
                "mitigation": "Aplikasi pupuk nitrogen segera"
            })
        
        # Location risks
        location_context = evaluation.get("location_context")
        if location_context:
            regional_data = location_context.get("regional_data", {})
            challenges = regional_data.get("challenges", [])
            
            for challenge in challenges:
                if challenge == "drought":
                    risks["location_risks"].append({
                        "risk": "Kekeringan musiman",
                        "level": "medium",
                        "mitigation": "Sistem irigasi cadangan"
                    })
        
        # Overall risk assessment
        high_risks = sum(1 for category in risks.values() 
                        if isinstance(category, list) 
                        for risk in category 
                        if isinstance(risk, dict) and risk.get("level") == "high")
        
        if high_risks > 2:
            risks["overall_risk_level"] = "high"
        elif high_risks > 0:
            risks["overall_risk_level"] = "medium"
        else:
            risks["overall_risk_level"] = "low"
        
        return risks
    
    def _create_optimization_plan(self, evaluation: Dict[str, Any]) -> Dict[str, Any]:
        """Create optimization plan for crop cultivation"""
        
        plan = {
            "priority_actions": [],
            "optimization_steps": [],
            "expected_improvements": {},
            "cost_benefit_analysis": {}
        }
        
        sensor_data = evaluation.get("sensor_data", {})
        suitability_score = evaluation.get("suitability_score", 0.0)
        
        # Priority actions
        if suitability_score < 0.6:
            plan["priority_actions"].append({
                "action": "Perbaikan fundamental kondisi tanah",
                "urgency": "tinggi",
                "expected_impact": "Meningkatkan suitability score 20-30%"
            })
        
        # Optimization steps
        ph = sensor_data.get('ph', 6.5)
        if ph < 6.0 or ph > 7.5:
            plan["optimization_steps"].append({
                "step": "Penyesuaian pH tanah",
                "method": "Pengapuran atau penambahan sulfur",
                "target": "pH 6.0-7.0",
                "timeframe": "2-4 minggu"
            })
        
        # Expected improvements
        plan["expected_improvements"] = {
            "suitability_score": f"{suitability_score:.1%} → {min(1.0, suitability_score + 0.2):.1%}",
            "yield_potential": "Peningkatan 15-25%",
            "crop_quality": "Peningkatan standar kualitas",
            "sustainability": "Peningkatan kesehatan tanah jangka panjang"
        }
        
        return plan
    
    def _suggest_alternative_crops(self, evaluation: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Suggest alternative crops based on conditions"""
        
        alternatives = []
        sensor_data = evaluation.get("sensor_data", {})
        location_context = evaluation.get("location_context")
        
        # Get top ML recommendations if available
        ml_analysis = evaluation.get("ml_analysis", {})
        if ml_analysis.get("available") and "top_recommendations" in ml_analysis:
            for i, (crop, confidence) in enumerate(ml_analysis["top_recommendations"][:3]):
                alternatives.append({
                    "crop": crop,
                    "confidence": confidence,
                    "source": "ML Prediction",
                    "rank": i + 1
                })
        
        # Location-based alternatives
        if location_context:
            regional_data = location_context.get("regional_data", {})
            if "main_crops" in regional_data:
                for crop in regional_data["main_crops"][:3]:
                    if not any(alt["crop"] == crop for alt in alternatives):
                        alternatives.append({
                            "crop": crop,
                            "confidence": 0.7,
                            "source": "Regional Suitability",
                            "rank": len(alternatives) + 1
                        })
        
        # Condition-based alternatives
        temp = sensor_data.get('temperature', 25)
        rainfall = sensor_data.get('rainfall', 100)
        
        if temp > 30 and rainfall > 200:
            if not any(alt["crop"] == "palm_oil" for alt in alternatives):
                alternatives.append({
                    "crop": "palm_oil",
                    "confidence": 0.8,
                    "source": "Climate Suitability",
                    "rank": len(alternatives) + 1
                })
        
        return alternatives[:5]
    
    def get_evaluation_summary(self, evaluation: Dict[str, Any]) -> Dict[str, Any]:
        """Generate evaluation summary"""
        
        return {
            "timestamp": evaluation.get("timestamp"),
            "selected_crop": evaluation.get("selected_crop"),
            "suitability_score": evaluation.get("suitability_score"),
            "confidence_level": evaluation.get("confidence_level"),
            "key_recommendations": evaluation.get("recommendations", {}).get("immediate_actions", [])[:3],
            "main_risks": [risk["risk"] for risk in evaluation.get("risk_assessment", {}).get("environmental_risks", [])],
            "alternative_crops": [alt["crop"] for alt in evaluation.get("alternative_crops", [])][:3]
        }
    
    def get_service_status(self) -> Dict[str, Any]:
        """Get evaluation service status"""
        
        return {
            "evaluation_service_available": True,
            "ml_predictor_loaded": self.ml_predictor_loaded,
            "llm_service_available": self.llm_service.llm_manager.is_available(),
            "knowledge_base_available": self.knowledge_base.is_available,
            "location_service_available": True
        }

# ==================== GLOBAL INSTANCE ====================

# Global instance for easy access
evaluation_service = EvaluationService() 