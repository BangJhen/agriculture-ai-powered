"""
Location Context Service for Agricultural Decision Support System
Provides location-specific agricultural insights and context-aware recommendations.
"""

import os
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
import json
import math

# Import services
from .llm_service import agricultural_llm
from .knowledge_base import knowledge_base
from ..utils.helpers import safe_float

# ==================== LOCATION CONTEXT SERVICE ====================

class LocationContextService:
    """Service for providing location-specific agricultural context and recommendations"""
    
    def __init__(self):
        self.llm_service = agricultural_llm
        self.knowledge_base = knowledge_base
        self.indonesia_regions = self._load_indonesia_regions()
        self.climate_zones = self._load_climate_zones()
        
    def _load_indonesia_regions(self) -> Dict[str, Dict[str, Any]]:
        """Load Indonesian regional agricultural data"""
        return {
            "java_west": {
                "name": "Jawa Barat",
                "climate": "tropical_monsoon",
                "elevation": "0-3000m",
                "rainfall": "1500-4000mm",
                "temperature": "20-32°C",
                "main_crops": ["rice", "corn", "soybean", "vegetables"],
                "soil_type": "alluvial, latosol, andosol",
                "growing_seasons": ["musim_hujan", "musim_kemarau"],
                "challenges": ["flooding", "drought", "pests"]
            },
            "java_central": {
                "name": "Jawa Tengah",
                "climate": "tropical_monsoon",
                "elevation": "0-3000m",
                "rainfall": "1200-3000mm",
                "temperature": "22-30°C",
                "main_crops": ["rice", "corn", "sugarcane", "tobacco"],
                "soil_type": "alluvial, latosol, regosol",
                "growing_seasons": ["musim_hujan", "musim_kemarau"],
                "challenges": ["drought", "soil_erosion", "pest_outbreak"]
            },
            "java_east": {
                "name": "Jawa Timur",
                "climate": "tropical_dry",
                "elevation": "0-3000m",
                "rainfall": "800-2500mm",
                "temperature": "23-32°C",
                "main_crops": ["rice", "corn", "sugarcane", "tobacco"],
                "soil_type": "alluvial, latosol, mediteran",
                "growing_seasons": ["musim_hujan", "musim_kemarau"],
                "challenges": ["water_scarcity", "soil_degradation", "salinity"]
            },
            "sumatra": {
                "name": "Sumatera",
                "climate": "tropical_rainforest",
                "elevation": "0-3800m",
                "rainfall": "2000-4000mm",
                "temperature": "24-28°C",
                "main_crops": ["rice", "palm_oil", "rubber", "coffee"],
                "soil_type": "podzolic, latosol, organosol",
                "growing_seasons": ["year_round"],
                "challenges": ["excessive_rainfall", "acidic_soil", "peat_fires"]
            },
            "kalimantan": {
                "name": "Kalimantan",
                "climate": "tropical_rainforest",
                "elevation": "0-4000m",
                "rainfall": "2500-4000mm",
                "temperature": "25-28°C",
                "main_crops": ["rice", "palm_oil", "rubber", "fruits"],
                "soil_type": "podzolic, latosol, organosol",
                "growing_seasons": ["year_round"],
                "challenges": ["peat_soil", "flooding", "deforestation"]
            },
            "sulawesi": {
                "name": "Sulawesi",
                "climate": "tropical_monsoon",
                "elevation": "0-3400m",
                "rainfall": "1000-3000mm",
                "temperature": "22-30°C",
                "main_crops": ["rice", "corn", "cocoa", "coffee"],
                "soil_type": "alluvial, latosol, andosol",
                "growing_seasons": ["musim_hujan", "musim_kemarau"],
                "challenges": ["drought", "volcanic_ash", "slope_farming"]
            },
            "papua": {
                "name": "Papua",
                "climate": "tropical_rainforest",
                "elevation": "0-5000m",
                "rainfall": "2500-7000mm",
                "temperature": "18-32°C",
                "main_crops": ["rice", "sweet_potato", "sago", "fruits"],
                "soil_type": "podzolic, latosol, alluvial",
                "growing_seasons": ["year_round"],
                "challenges": ["mountainous_terrain", "remote_access", "infrastructure"]
            }
        }
    
    def _load_climate_zones(self) -> Dict[str, Dict[str, Any]]:
        """Load climate zone data for Indonesia"""
        return {
            "tropical_rainforest": {
                "characteristics": "High rainfall year-round, high humidity",
                "suitable_crops": ["rice", "palm_oil", "rubber", "cocoa", "fruits"],
                "challenges": ["fungal_diseases", "nutrient_leaching", "pest_pressure"],
                "recommendations": ["drainage", "organic_matter", "pest_management"]
            },
            "tropical_monsoon": {
                "characteristics": "Distinct wet and dry seasons",
                "suitable_crops": ["rice", "corn", "soybean", "vegetables"],
                "challenges": ["seasonal_drought", "flooding", "timing_issues"],
                "recommendations": ["water_storage", "crop_rotation", "drought_resistant_varieties"]
            },
            "tropical_dry": {
                "characteristics": "Low rainfall, high temperatures",
                "suitable_crops": ["corn", "sorghum", "millet", "legumes"],
                "challenges": ["water_scarcity", "heat_stress", "soil_degradation"],
                "recommendations": ["irrigation", "mulching", "drought_tolerant_crops"]
            }
        }
    
    def determine_location_context(self, location_data: Dict[str, Any]) -> Dict[str, Any]:
        """Determine location context based on coordinates or address"""
        
        context = {
            "region": "unknown",
            "climate_zone": "unknown",
            "elevation_estimate": 0,
            "regional_data": {},
            "climate_data": {},
            "confidence": 0.0
        }
        
        try:
            # Extract location information
            lat = location_data.get('lat', 0)
            lng = location_data.get('lng', 0)
            address = location_data.get('address', '').lower()
            
            # Determine region based on coordinates and address
            region = self._determine_region(lat, lng, address)
            context["region"] = region
            context["confidence"] = self._calculate_location_confidence(lat, lng, address)
            
            # Get regional data
            if region in self.indonesia_regions:
                context["regional_data"] = self.indonesia_regions[region]
                
                # Determine climate zone
                climate_zone = context["regional_data"].get("climate", "unknown")
                if climate_zone in self.climate_zones:
                    context["climate_zone"] = climate_zone
                    context["climate_data"] = self.climate_zones[climate_zone]
            
            # Estimate elevation based on coordinates
            context["elevation_estimate"] = self._estimate_elevation(lat, lng)
            
        except Exception as e:
            print(f"⚠️ Error determining location context: {e}")
        
        return context
    
    def _determine_region(self, lat: float, lng: float, address: str) -> str:
        """Determine Indonesian region based on coordinates and address"""
        
        # Address-based determination (more reliable)
        if any(keyword in address for keyword in ["jawa barat", "jabar", "bandung", "bogor", "depok", "bekasi"]):
            return "java_west"
        elif any(keyword in address for keyword in ["jawa tengah", "jateng", "semarang", "solo", "yogya", "jogja"]):
            return "java_central"
        elif any(keyword in address for keyword in ["jawa timur", "jatim", "surabaya", "malang", "kediri"]):
            return "java_east"
        elif any(keyword in address for keyword in ["sumatera", "sumatra", "medan", "palembang", "lampung", "riau"]):
            return "sumatra"
        elif any(keyword in address for keyword in ["kalimantan", "borneo", "pontianak", "banjarmasin", "samarinda"]):
            return "kalimantan"
        elif any(keyword in address for keyword in ["sulawesi", "makassar", "manado", "palu", "kendari"]):
            return "sulawesi"
        elif any(keyword in address for keyword in ["papua", "jayapura", "sorong", "merauke"]):
            return "papua"
        
        # Coordinate-based determination (fallback)
        if lat != 0 and lng != 0:
            # Java
            if -8.5 <= lat <= -5.5 and 105.5 <= lng <= 115.0:
                if lng < 108.0:
                    return "java_west"
                elif lng < 111.0:
                    return "java_central"
                else:
                    return "java_east"
            # Sumatra
            elif -6.0 <= lat <= 6.0 and 95.0 <= lng <= 107.0:
                return "sumatra"
            # Kalimantan
            elif -4.0 <= lat <= 7.0 and 108.0 <= lng <= 119.0:
                return "kalimantan"
            # Sulawesi
            elif -6.0 <= lat <= 2.0 and 118.0 <= lng <= 125.0:
                return "sulawesi"
            # Papua
            elif -9.0 <= lat <= 0.0 and 130.0 <= lng <= 145.0:
                return "papua"
        
        return "unknown"
    
    def _calculate_location_confidence(self, lat: float, lng: float, address: str) -> float:
        """Calculate confidence score for location determination"""
        
        confidence = 0.0
        
        # Address confidence
        if address and len(address.strip()) > 5:
            confidence += 0.5
        
        # Coordinate confidence
        if lat != 0 and lng != 0:
            # Check if coordinates are within Indonesia bounds
            if -11.0 <= lat <= 6.0 and 95.0 <= lng <= 141.0:
                confidence += 0.4
            else:
                confidence -= 0.2
        
        # GPS accuracy (if available)
        accuracy = 0  # This would come from GPS data
        if accuracy > 0:
            if accuracy < 100:
                confidence += 0.1
            elif accuracy > 1000:
                confidence -= 0.1
        
        return max(0.0, min(1.0, confidence))
    
    def _estimate_elevation(self, lat: float, lng: float) -> int:
        """Estimate elevation based on coordinates (simplified)"""
        
        # This is a very simplified elevation estimation
        # In a real implementation, you'd use a digital elevation model
        
        if lat == 0 and lng == 0:
            return 0
        
        # Simple heuristic based on known geographical features
        # Java mountains
        if -8.0 <= lat <= -6.5 and 106.0 <= lng <= 112.0:
            return 500  # Mountainous areas
        
        # Sumatra mountains
        if -3.0 <= lat <= 6.0 and 95.0 <= lng <= 102.0:
            return 300  # Mountainous areas
        
        # Coastal areas (low elevation)
        if abs(lat) < 1.0 or abs(lng - 110.0) > 10.0:
            return 20  # Coastal areas
        
        return 100  # Default lowland
    
    def generate_location_specific_recommendations(self, location_data: Dict[str, Any], 
                                                 sensor_data: Dict[str, Any] = None) -> Dict[str, Any]:
        """Generate comprehensive location-specific recommendations"""
        
        location_context = self.determine_location_context(location_data)
        
        recommendations = {
            "location_context": location_context,
            "crop_recommendations": [],
            "climate_adaptations": [],
            "soil_management": [],
            "water_management": [],
            "pest_disease_risks": [],
            "seasonal_planning": [],
            "market_opportunities": [],
            "infrastructure_considerations": []
        }
        
        regional_data = location_context.get("regional_data", {})
        climate_data = location_context.get("climate_data", {})
        
        # Crop recommendations based on region
        if "main_crops" in regional_data:
            recommendations["crop_recommendations"] = [
                f"🌾 {crop.replace('_', ' ').title()}" 
                for crop in regional_data["main_crops"]
            ]
        
        # Climate adaptations
        if "challenges" in regional_data:
            for challenge in regional_data["challenges"]:
                if challenge == "drought":
                    recommendations["climate_adaptations"].append(
                        "🌵 Implementasi sistem irigasi tetes dan varietas tahan kekeringan"
                    )
                elif challenge == "flooding":
                    recommendations["climate_adaptations"].append(
                        "🌊 Siapkan sistem drainase dan bed tinggi untuk mencegah genangan"
                    )
                elif challenge == "excessive_rainfall":
                    recommendations["climate_adaptations"].append(
                        "☔ Gunakan greenhouse atau tunnel untuk perlindungan dari hujan berlebih"
                    )
        
        # Soil management
        if "soil_type" in regional_data:
            soil_types = regional_data["soil_type"].split(", ")
            for soil_type in soil_types:
                if "latosol" in soil_type:
                    recommendations["soil_management"].append(
                        "🌱 Tanah latosol: Aplikasi pupuk organik dan kapur untuk meningkatkan pH"
                    )
                elif "podzolic" in soil_type:
                    recommendations["soil_management"].append(
                        "🌱 Tanah podzolic: Perbaikan drainase dan penambahan bahan organik"
                    )
                elif "alluvial" in soil_type:
                    recommendations["soil_management"].append(
                        "🌱 Tanah alluvial: Tanah subur, optimal untuk berbagai tanaman"
                    )
        
        # Water management
        if "rainfall" in regional_data:
            rainfall_info = regional_data["rainfall"]
            if "1500-4000mm" in rainfall_info:
                recommendations["water_management"].append(
                    "💧 Curah hujan tinggi: Fokus pada sistem drainase yang baik"
                )
            elif "800-2500mm" in rainfall_info:
                recommendations["water_management"].append(
                    "💧 Curah hujan sedang: Kombinasi irigasi dan tadah hujan"
                )
        
        # Seasonal planning
        if "growing_seasons" in regional_data:
            seasons = regional_data["growing_seasons"]
            if "year_round" in seasons:
                recommendations["seasonal_planning"].append(
                    "📅 Dapat menanam sepanjang tahun dengan rotasi tanaman"
                )
            else:
                recommendations["seasonal_planning"].append(
                    "📅 Perencanaan tanam berdasarkan musim hujan dan kemarau"
                )
        
        # Market opportunities (simplified)
        if "main_crops" in regional_data:
            main_crops = regional_data["main_crops"]
            if "rice" in main_crops:
                recommendations["market_opportunities"].append(
                    "🏪 Peluang pasar beras lokal dan ekspor"
                )
            if "palm_oil" in main_crops:
                recommendations["market_opportunities"].append(
                    "🏪 Peluang industri kelapa sawit dan produk turunannya"
                )
        
        # Infrastructure considerations
        elevation = location_context.get("elevation_estimate", 0)
        if elevation > 1000:
            recommendations["infrastructure_considerations"].append(
                "🚛 Akses transportasi terbatas di daerah pegunungan"
            )
        elif elevation < 50:
            recommendations["infrastructure_considerations"].append(
                "🚛 Akses transportasi baik di daerah dataran rendah"
            )
        
        return recommendations
    
    def get_seasonal_calendar(self, location_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate seasonal agricultural calendar for location"""
        
        location_context = self.determine_location_context(location_data)
        regional_data = location_context.get("regional_data", {})
        
        calendar = {
            "location": location_data.get('address', 'Unknown'),
            "region": location_context.get("region", "unknown"),
            "months": {}
        }
        
        # Generate monthly recommendations
        months = [
            "Januari", "Februari", "Maret", "April", "Mei", "Juni",
            "Juli", "Agustus", "September", "Oktober", "November", "Desember"
        ]
        
        for i, month in enumerate(months, 1):
            calendar["months"][month] = self._get_month_recommendations(
                i, regional_data, location_context
            )
        
        return calendar
    
    def _get_month_recommendations(self, month_num: int, regional_data: Dict[str, Any], 
                                  location_context: Dict[str, Any]) -> Dict[str, Any]:
        """Get recommendations for specific month"""
        
        recommendations = {
            "season": "",
            "activities": [],
            "crop_suggestions": [],
            "weather_preparation": []
        }
        
        # Determine season (simplified for Indonesia)
        if month_num in [12, 1, 2, 3]:
            recommendations["season"] = "Musim Hujan"
            recommendations["activities"].extend([
                "Tanam padi sawah",
                "Persiapan drainase",
                "Pengendalian hama dan penyakit"
            ])
        elif month_num in [4, 5]:
            recommendations["season"] = "Peralihan"
            recommendations["activities"].extend([
                "Panen padi",
                "Persiapan lahan musim kemarau"
            ])
        elif month_num in [6, 7, 8, 9]:
            recommendations["season"] = "Musim Kemarau"
            recommendations["activities"].extend([
                "Tanam jagung/kedelai",
                "Irigasi intensif",
                "Pemeliharaan tanaman tahunan"
            ])
        else:  # [10, 11]
            recommendations["season"] = "Peralihan"
            recommendations["activities"].extend([
                "Panen musim kemarau",
                "Persiapan lahan musim hujan"
            ])
        
        # Add crop suggestions based on region
        if "main_crops" in regional_data:
            recommendations["crop_suggestions"] = regional_data["main_crops"][:3]
        
        return recommendations
    
    def get_climate_risk_assessment(self, location_data: Dict[str, Any]) -> Dict[str, Any]:
        """Assess climate risks for the location"""
        
        location_context = self.determine_location_context(location_data)
        regional_data = location_context.get("regional_data", {})
        
        risk_assessment = {
            "location": location_data.get('address', 'Unknown'),
            "overall_risk": "medium",
            "specific_risks": [],
            "mitigation_strategies": [],
            "preparedness_level": "medium"
        }
        
        # Assess risks based on regional challenges
        if "challenges" in regional_data:
            for challenge in regional_data["challenges"]:
                if challenge == "drought":
                    risk_assessment["specific_risks"].append({
                        "type": "Kekeringan",
                        "severity": "high",
                        "probability": "medium",
                        "impact": "Gagal panen, penurunan produktivitas"
                    })
                elif challenge == "flooding":
                    risk_assessment["specific_risks"].append({
                        "type": "Banjir",
                        "severity": "high",
                        "probability": "medium",
                        "impact": "Kerusakan tanaman, erosi tanah"
                    })
                elif challenge == "pests":
                    risk_assessment["specific_risks"].append({
                        "type": "Serangan Hama",
                        "severity": "medium",
                        "probability": "high",
                        "impact": "Penurunan kualitas dan kuantitas hasil"
                    })
        
        return risk_assessment
    
    def generate_llm_enhanced_location_advice(self, location_data: Dict[str, Any], 
                                            sensor_data: Dict[str, Any] = None) -> str:
        """Generate LLM-enhanced location advice"""
        
        if not self.llm_service.llm_manager.is_available():
            return "⚠️ LLM service tidak tersedia untuk saran lokasi yang lebih detail"
        
        location_context = self.determine_location_context(location_data)
        structured_recommendations = self.generate_location_specific_recommendations(
            location_data, sensor_data
        )
        
        # Prepare context for LLM
        context = f"""
        **Konteks Lokasi:**
        - Alamat: {location_data.get('address', 'N/A')}
        - Koordinat: {location_data.get('lat', 'N/A')}, {location_data.get('lng', 'N/A')}
        - Wilayah: {location_context.get('region', 'N/A')}
        - Zona Iklim: {location_context.get('climate_zone', 'N/A')}
        - Estimasi Ketinggian: {location_context.get('elevation_estimate', 'N/A')} meter
        
        **Data Regional:**
        - Tanaman Utama: {', '.join(structured_recommendations['crop_recommendations'])}
        - Adaptasi Iklim: {', '.join(structured_recommendations['climate_adaptations'])}
        - Manajemen Tanah: {', '.join(structured_recommendations['soil_management'])}
        """
        
        if sensor_data:
            context += f"""
            
            **Data Sensor:**
            - Suhu: {sensor_data.get('temperature', 'N/A')}°C
            - Kelembaban: {sensor_data.get('humidity', 'N/A')}%
            - pH: {sensor_data.get('ph', 'N/A')}
            - Curah Hujan: {sensor_data.get('rainfall', 'N/A')} mm
            """
        
        prompt = f"""
        Berdasarkan analisis lokasi berikut, berikan saran pertanian yang spesifik dan praktis:
        
        {context}
        
        Harap berikan:
        1. 🗺️ **Analisis Lokasi** - Keunggulan dan tantangan lokasi ini
        2. 🌾 **Rekomendasi Tanaman** - Tanaman yang paling cocok dan menguntungkan
        3. 📅 **Strategi Musiman** - Perencanaan tanam berdasarkan musim
        4. 🔧 **Teknologi Tepat Guna** - Alat dan teknologi yang sesuai
        5. 💰 **Analisis Ekonomi** - Potensi keuntungan dan biaya
        6. 🤝 **Kerjasama Lokal** - Peluang kemitraan dengan petani/kelompok tani
        
        Berikan saran yang actionable dan sesuai dengan kondisi lokal Indonesia.
        """
        
        return self.llm_service.llm_manager.call_llm(
            prompt=prompt,
            system_prompt=self.llm_service.agricultural_context,
            temperature=0.7,
            max_tokens=2000
        )
    
    def get_service_status(self) -> Dict[str, Any]:
        """Get location context service status"""
        
        return {
            "location_context_available": True,
            "regions_loaded": len(self.indonesia_regions),
            "climate_zones_loaded": len(self.climate_zones),
            "llm_service_available": self.llm_service.llm_manager.is_available(),
            "knowledge_base_available": self.knowledge_base.is_available
        }

# ==================== GLOBAL INSTANCE ====================

# Global instance for easy access
location_context_service = LocationContextService() 