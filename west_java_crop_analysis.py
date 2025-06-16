# West Java Crop Suitability Analysis for Corn and Cassava
# Agriculture-Environmental AI Assistant for West Java

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple
import json

class WestJavaCropAnalyzer:
    """
    Agriculture-environmental AI assistant for evaluating crop suitability in West Java
    based on edaphic, hydrologic, and atmospheric parameters.
    """
    
    def __init__(self):
        self.initialize_crop_requirements()
        self.initialize_west_java_regions()
        self.initialize_suitability_parameters()
    
    def initialize_crop_requirements(self):
        """Initialize crop-specific requirements for corn and cassava"""
        self.crop_requirements = {
            "corn": {
                # Edaphic (Soil-related) requirements
                "edaphic": {
                    "soil_texture": ["sandy_loam", "loam", "clay_loam"],
                    "ph_range": (5.8, 7.0),
                    "organic_matter": (2.5, 4.0),  # percentage
                    "drainage": "well_drained",
                    "soil_depth": ">60cm",
                    "cec": (15, 25),  # cmol/kg
                    "nitrogen": (0.12, 0.20),  # percentage
                    "phosphorus": (0.10, 0.18),  # percentage
                    "potassium": (0.18, 0.28)   # percentage
                },
                # Hydrologic requirements
                "hydrologic": {
                    "annual_rainfall": (600, 1200),  # mm
                    "growing_season_rainfall": (400, 800),  # mm
                    "water_table_depth": (50, 150),  # cm
                    "flood_risk": "low_to_moderate",
                    "irrigation_access": "beneficial",
                    "water_quality_ec": (0.25, 0.75)  # dS/m
                },
                # Atmospheric requirements
                "atmospheric": {
                    "temperature_range": (20, 30),  # °C
                    "optimal_temperature": (24, 28),  # °C
                    "humidity": (60, 75),  # %
                    "solar_radiation": (18, 25),  # MJ/m²/day
                    "photoperiod": (11, 13),  # hours
                    "wind_tolerance": "moderate",
                    "altitude": (0, 1500)  # meters
                }
            },
            "cassava": {
                # Edaphic requirements
                "edaphic": {
                    "soil_texture": ["sandy_loam", "loam", "sandy"],
                    "ph_range": (5.0, 7.0),
                    "organic_matter": (1.5, 3.5),  # percentage
                    "drainage": "well_drained_to_excessive",
                    "soil_depth": ">40cm",
                    "cec": (8, 20),  # cmol/kg
                    "nitrogen": (0.08, 0.15),  # percentage
                    "phosphorus": (0.06, 0.12),  # percentage
                    "potassium": (0.12, 0.25)   # percentage
                },
                # Hydrologic requirements
                "hydrologic": {
                    "annual_rainfall": (500, 1500),  # mm
                    "growing_season_rainfall": (300, 1000),  # mm
                    "water_table_depth": (80, 200),  # cm
                    "flood_risk": "low",
                    "drought_tolerance": "high",
                    "water_quality_ec": (0.25, 1.0)  # dS/m
                },
                # Atmospheric requirements
                "atmospheric": {
                    "temperature_range": (20, 35),  # °C
                    "optimal_temperature": (25, 32),  # °C
                    "humidity": (50, 80),  # %
                    "solar_radiation": (15, 25),  # MJ/m²/day
                    "photoperiod": (10, 14),  # hours
                    "wind_tolerance": "high",
                    "altitude": (0, 1200)  # meters
                }
            }
        }
    
    def initialize_west_java_regions(self):
        """Initialize West Java district/regency data with characteristics"""
        self.west_java_regions = {
            # Northern Coast (Pantura)
            "Bekasi": {
                "coordinates": (-6.2383, 107.0046),
                "altitude": 8,
                "climate_zone": "tropical_lowland",
                "annual_rainfall": 1800,
                "temperature_range": (24, 33),
                "soil_type": "alluvial",
                "irrigation": "good",
                "flood_risk": "high"
            },
            "Karawang": {
                "coordinates": (-6.3215, 107.3020),
                "altitude": 6,
                "climate_zone": "tropical_lowland",
                "annual_rainfall": 1600,
                "temperature_range": (24, 33),
                "soil_type": "alluvial",
                "irrigation": "excellent",
                "flood_risk": "moderate"
            },
            "Subang": {
                "coordinates": (-6.5716, 107.7650),
                "altitude": 30,
                "climate_zone": "tropical_lowland",
                "annual_rainfall": 1700,
                "temperature_range": (23, 32),
                "soil_type": "alluvial",
                "irrigation": "good",
                "flood_risk": "moderate"
            },
            "Indramayu": {
                "coordinates": (-6.3268, 108.3200),
                "altitude": 8,
                "climate_zone": "tropical_lowland",
                "annual_rainfall": 1400,
                "temperature_range": (25, 34),
                "soil_type": "alluvial",
                "irrigation": "good",
                "flood_risk": "high"
            },
            "Cirebon": {
                "coordinates": (-6.7063, 108.5571),
                "altitude": 7,
                "climate_zone": "tropical_lowland",
                "annual_rainfall": 1500,
                "temperature_range": (24, 33),
                "soil_type": "alluvial",
                "irrigation": "good",
                "flood_risk": "moderate"
            },
            
            # Central Plains
            "Bandung": {
                "coordinates": (-6.9175, 107.6191),
                "altitude": 768,
                "climate_zone": "tropical_highland",
                "annual_rainfall": 2000,
                "temperature_range": (18, 28),
                "soil_type": "andosol",
                "irrigation": "moderate",
                "flood_risk": "low"
            },
            "Bandung Barat": {
                "coordinates": (-6.8619, 107.4917),
                "altitude": 800,
                "climate_zone": "tropical_highland",
                "annual_rainfall": 2200,
                "temperature_range": (18, 27),
                "soil_type": "andosol",
                "irrigation": "moderate",
                "flood_risk": "low"
            },
            "Sumedang": {
                "coordinates": (-6.8570, 107.9177),
                "altitude": 260,
                "climate_zone": "tropical_transition",
                "annual_rainfall": 1900,
                "temperature_range": (20, 30),
                "soil_type": "latosol",
                "irrigation": "moderate",
                "flood_risk": "low"
            },
            "Majalengka": {
                "coordinates": (-6.8364, 108.2275),
                "altitude": 120,
                "climate_zone": "tropical_lowland",
                "annual_rainfall": 1600,
                "temperature_range": (22, 31),
                "soil_type": "latosol",
                "irrigation": "moderate",
                "flood_risk": "moderate"
            },
            "Kuningan": {
                "coordinates": (-6.9756, 108.4836),
                "altitude": 500,
                "climate_zone": "tropical_highland",
                "annual_rainfall": 1800,
                "temperature_range": (19, 29),
                "soil_type": "andosol",
                "irrigation": "moderate",
                "flood_risk": "low"
            },
            
            # Southern Regions
            "Garut": {
                "coordinates": (-7.2125, 107.8972),
                "altitude": 717,
                "climate_zone": "tropical_highland",
                "annual_rainfall": 2200,
                "temperature_range": (18, 28),
                "soil_type": "andosol",
                "irrigation": "moderate",
                "flood_risk": "low"
            },
            "Tasikmalaya": {
                "coordinates": (-7.3506, 108.2170),
                "altitude": 351,
                "climate_zone": "tropical_transition",
                "annual_rainfall": 2000,
                "temperature_range": (20, 29),
                "soil_type": "latosol",
                "irrigation": "moderate",
                "flood_risk": "moderate"
            },
            "Ciamis": {
                "coordinates": (-7.3257, 108.3534),
                "altitude": 155,
                "climate_zone": "tropical_lowland",
                "annual_rainfall": 1900,
                "temperature_range": (21, 30),
                "soil_type": "latosol",
                "irrigation": "moderate",
                "flood_risk": "moderate"
            },
            "Pangandaran": {
                "coordinates": (-7.6861, 108.6500),
                "altitude": 91,
                "climate_zone": "tropical_coastal",
                "annual_rainfall": 2300,
                "temperature_range": (22, 31),
                "soil_type": "regosol",
                "irrigation": "poor",
                "flood_risk": "moderate"
            },
            
            # Eastern Regions
            "Purwakarta": {
                "coordinates": (-6.5569, 107.4331),
                "altitude": 118,
                "climate_zone": "tropical_lowland",
                "annual_rainfall": 1700,
                "temperature_range": (22, 31),
                "soil_type": "latosol",
                "irrigation": "good",
                "flood_risk": "moderate"
            },
            "Cianjur": {
                "coordinates": (-6.8171, 107.1428),
                "altitude": 425,
                "climate_zone": "tropical_transition",
                "annual_rainfall": 2100,
                "temperature_range": (19, 29),
                "soil_type": "andosol",
                "irrigation": "moderate",
                "flood_risk": "low"
            },
            "Sukabumi": {
                "coordinates": (-6.9278, 106.9270),
                "altitude": 584,
                "climate_zone": "tropical_highland",
                "annual_rainfall": 2400,
                "temperature_range": (18, 28),
                "soil_type": "andosol",
                "irrigation": "moderate",
                "flood_risk": "low"
            },
            "Bogor": {
                "coordinates": (-6.5944, 106.7892),
                "altitude": 190,
                "climate_zone": "tropical_transition",
                "annual_rainfall": 2500,
                "temperature_range": (20, 30),
                "soil_type": "latosol",
                "irrigation": "good",
                "flood_risk": "moderate"
            }
        }
    
    def initialize_suitability_parameters(self):
        """Initialize parameter weights and scoring criteria"""
        self.parameter_weights = {
            "edaphic": 0.4,      # 40% weight
            "hydrologic": 0.35,  # 35% weight
            "atmospheric": 0.25  # 25% weight
        }
        
        self.suitability_thresholds = {
            "highly_suitable": 0.8,
            "moderately_suitable": 0.6,
            "marginally_suitable": 0.4,
            "not_suitable": 0.0
        }
    
    def calculate_parameter_score(self, value: float, optimal_range: Tuple[float, float], 
                                tolerance: float = 0.2) -> float:
        """Calculate score for a parameter based on optimal range"""
        min_opt, max_opt = optimal_range
        
        if min_opt <= value <= max_opt:
            return 1.0
        
        # Calculate tolerance ranges
        min_tolerance = min_opt - (min_opt * tolerance)
        max_tolerance = max_opt + (max_opt * tolerance)
        
        if value < min_opt:
            if value >= min_tolerance:
                return 0.5 + 0.5 * (value - min_tolerance) / (min_opt - min_tolerance)
            else:
                return max(0.0, 0.5 * value / min_tolerance)
        else:  # value > max_opt
            if value <= max_tolerance:
                return 0.5 + 0.5 * (max_tolerance - value) / (max_tolerance - max_opt)
            else:
                return max(0.0, 0.5 * (2 * max_tolerance - value) / max_tolerance)
    
    def evaluate_regional_suitability(self, crop: str, region_name: str) -> Dict:
        """Evaluate crop suitability for a specific region"""
        if crop not in self.crop_requirements:
            raise ValueError(f"Crop {crop} not supported")
        
        if region_name not in self.west_java_regions:
            raise ValueError(f"Region {region_name} not found")
        
        region_data = self.west_java_regions[region_name]
        crop_req = self.crop_requirements[crop]
        
        scores = {"edaphic": 0, "hydrologic": 0, "atmospheric": 0}
        detailed_scores = {}
        
        # Edaphic evaluation
        edaphic_scores = []
        
        # Temperature-altitude compatibility
        temp_score = self.calculate_parameter_score(
            np.mean(region_data["temperature_range"]), 
            crop_req["atmospheric"]["temperature_range"]
        )
        edaphic_scores.append(temp_score * 0.3)  # 30% of edaphic score
        
        # Soil type compatibility (simplified scoring)
        soil_compatibility = {
            "corn": {"alluvial": 0.9, "andosol": 0.8, "latosol": 0.7, "regosol": 0.6},
            "cassava": {"alluvial": 0.7, "andosol": 0.6, "latosol": 0.8, "regosol": 0.9}
        }
        soil_score = soil_compatibility[crop].get(region_data["soil_type"], 0.5)
        edaphic_scores.append(soil_score * 0.4)  # 40% of edaphic score
        
        # Altitude compatibility
        altitude_score = self.calculate_parameter_score(
            region_data["altitude"], 
            crop_req["atmospheric"]["altitude"]
        )
        edaphic_scores.append(altitude_score * 0.3)  # 30% of edaphic score
        
        scores["edaphic"] = sum(edaphic_scores)
        detailed_scores["edaphic"] = {
            "temperature_compatibility": temp_score,
            "soil_type_compatibility": soil_score,
            "altitude_compatibility": altitude_score
        }
        
        # Hydrologic evaluation
        hydrologic_scores = []
        
        # Rainfall compatibility
        rainfall_score = self.calculate_parameter_score(
            region_data["annual_rainfall"], 
            crop_req["hydrologic"]["annual_rainfall"]
        )
        hydrologic_scores.append(rainfall_score * 0.5)  # 50% of hydrologic score
        
        # Irrigation access
        irrigation_mapping = {"excellent": 1.0, "good": 0.8, "moderate": 0.6, "poor": 0.3}
        irrigation_score = irrigation_mapping.get(region_data["irrigation"], 0.5)
        hydrologic_scores.append(irrigation_score * 0.3)  # 30% of hydrologic score
        
        # Flood risk (inverse scoring)
        flood_mapping = {"low": 0.9, "moderate": 0.7, "high": 0.4}
        flood_score = flood_mapping.get(region_data["flood_risk"], 0.5)
        hydrologic_scores.append(flood_score * 0.2)  # 20% of hydrologic score
        
        scores["hydrologic"] = sum(hydrologic_scores)
        detailed_scores["hydrologic"] = {
            "rainfall_compatibility": rainfall_score,
            "irrigation_access": irrigation_score,
            "flood_risk_assessment": flood_score
        }
        
        # Atmospheric evaluation
        atmospheric_scores = []
        
        # Temperature range
        temp_atm_score = self.calculate_parameter_score(
            np.mean(region_data["temperature_range"]), 
            crop_req["atmospheric"]["optimal_temperature"]
        )
        atmospheric_scores.append(temp_atm_score * 0.6)  # 60% of atmospheric score
        
        # Climate zone compatibility
        climate_compatibility = {
            "corn": {
                "tropical_lowland": 0.8, "tropical_transition": 0.9, 
                "tropical_highland": 0.7, "tropical_coastal": 0.7
            },
            "cassava": {
                "tropical_lowland": 0.9, "tropical_transition": 0.8, 
                "tropical_highland": 0.6, "tropical_coastal": 0.8
            }
        }
        climate_score = climate_compatibility[crop].get(region_data["climate_zone"], 0.5)
        atmospheric_scores.append(climate_score * 0.4)  # 40% of atmospheric score
        
        scores["atmospheric"] = sum(atmospheric_scores)
        detailed_scores["atmospheric"] = {
            "temperature_optimal": temp_atm_score,
            "climate_zone_compatibility": climate_score
        }
        
        # Calculate overall suitability score
        overall_score = (
            scores["edaphic"] * self.parameter_weights["edaphic"] +
            scores["hydrologic"] * self.parameter_weights["hydrologic"] +
            scores["atmospheric"] * self.parameter_weights["atmospheric"]
        )
        
        # Determine suitability class
        if overall_score >= self.suitability_thresholds["highly_suitable"]:
            suitability_class = "Highly Suitable"
        elif overall_score >= self.suitability_thresholds["moderately_suitable"]:
            suitability_class = "Moderately Suitable"
        elif overall_score >= self.suitability_thresholds["marginally_suitable"]:
            suitability_class = "Marginally Suitable"
        else:
            suitability_class = "Not Suitable"
        
        return {
            "region": region_name,
            "crop": crop,
            "overall_score": round(overall_score, 3),
            "suitability_class": suitability_class,
            "category_scores": {k: round(v, 3) for k, v in scores.items()},
            "detailed_scores": detailed_scores,
            "region_characteristics": region_data
        }
    
    def analyze_all_regions(self, crop: str) -> List[Dict]:
        """Analyze crop suitability for all West Java regions"""
        results = []
        for region_name in self.west_java_regions.keys():
            result = self.evaluate_regional_suitability(crop, region_name)
            results.append(result)
        
        # Sort by overall score (descending)
        results.sort(key=lambda x: x["overall_score"], reverse=True)
        return results
    
    def get_crop_summary(self, crop: str) -> Dict:
        """Get comprehensive crop requirements summary"""
        if crop not in self.crop_requirements:
            raise ValueError(f"Crop {crop} not supported")
        
        req = self.crop_requirements[crop]
        
        return {
            "crop_name": crop.title(),
            "scientific_name": "Zea mays" if crop == "corn" else "Manihot esculenta",
            "requirements_summary": {
                "edaphic": {
                    "soil_types": req["edaphic"]["soil_texture"],
                    "ph_range": f"{req['edaphic']['ph_range'][0]} - {req['edaphic']['ph_range'][1]}",
                    "organic_matter": f"{req['edaphic']['organic_matter'][0]}% - {req['edaphic']['organic_matter'][1]}%",
                    "drainage": req["edaphic"]["drainage"],
                    "nutrients": {
                        "nitrogen": f"{req['edaphic']['nitrogen'][0]}% - {req['edaphic']['nitrogen'][1]}%",
                        "phosphorus": f"{req['edaphic']['phosphorus'][0]}% - {req['edaphic']['phosphorus'][1]}%",
                        "potassium": f"{req['edaphic']['potassium'][0]}% - {req['edaphic']['potassium'][1]}%"
                    }
                },
                "hydrologic": {
                    "annual_rainfall": f"{req['hydrologic']['annual_rainfall'][0]} - {req['hydrologic']['annual_rainfall'][1]} mm",
                    "water_table": f"{req['hydrologic']['water_table_depth'][0]} - {req['hydrologic']['water_table_depth'][1]} cm depth",
                    "irrigation": req["hydrologic"].get("irrigation_access", "beneficial"),
                    "drought_tolerance": req["hydrologic"].get("drought_tolerance", "moderate")
                },
                "atmospheric": {
                    "temperature": f"{req['atmospheric']['temperature_range'][0]}°C - {req['atmospheric']['temperature_range'][1]}°C",
                    "optimal_temperature": f"{req['atmospheric']['optimal_temperature'][0]}°C - {req['atmospheric']['optimal_temperature'][1]}°C",
                    "humidity": f"{req['atmospheric']['humidity'][0]}% - {req['atmospheric']['humidity'][1]}%",
                    "altitude": f"0 - {req['atmospheric']['altitude'][1]} meters",
                    "solar_radiation": f"{req['atmospheric']['solar_radiation'][0]} - {req['atmospheric']['solar_radiation'][1]} MJ/m²/day"
                }
            }
        }

# Analysis execution and reporting functions
def generate_comprehensive_report():
    """Generate comprehensive crop suitability report for West Java"""
    analyzer = WestJavaCropAnalyzer()
    
    # Analyze both crops
    corn_results = analyzer.analyze_all_regions("corn")
    cassava_results = analyzer.analyze_all_regions("cassava")
    
    # Get crop summaries
    corn_summary = analyzer.get_crop_summary("corn")
    cassava_summary = analyzer.get_crop_summary("cassava")
    
    report = {
        "analysis_date": "2025-06-16",
        "region": "West Java, Indonesia",
        "crops_analyzed": ["corn", "cassava"],
        "crop_summaries": {
            "corn": corn_summary,
            "cassava": cassava_summary
        },
        "regional_analysis": {
            "corn": corn_results,
            "cassava": cassava_results
        },
        "methodology": {
            "parameters": ["edaphic", "hydrologic", "atmospheric"],
            "scoring_system": "0-1 scale with weighted categories",
            "weights": analyzer.parameter_weights
        }
    }
    
    return report

def get_traditional_practices_and_risks():
    """Get traditional planting practices and risk assessments for each region"""
    practices_and_risks = {
        "corn": {
            "traditional_practices": {
                "northern_coast": {
                    "regions": ["Bekasi", "Karawang", "Subang", "Indramayu", "Cirebon"],
                    "practices": [
                        "Tanam jagung setelah padi pada musim kemarau (April-Juli)",
                        "Sistem tumpangsari jagung-kacang tanah",
                        "Penggunaan benih lokal varietas Bisma dan Lamuru",
                        "Irigasi dari saluran teknis dan pompa air tanah"
                    ],
                    "pest_risks": [
                        "Penggerek batang jagung (Ostrinia furnacalis)",
                        "Ulat grayak (Spodoptera frugiperda)",
                        "Penyakit bulai (Peronosclerospora maydis)"
                    ],
                    "climate_threats": [
                        "Banjir pada musim hujan (Desember-Februari)",
                        "Kekeringan ekstrem saat El Niño",
                        "Angin kencang saat musim pancaroba"
                    ]
                },
                "highlands": {
                    "regions": ["Bandung", "Bandung Barat", "Garut", "Kuningan"],
                    "practices": [
                        "Tanam jagung manis untuk pasar segar",
                        "Sistem terasering untuk konservasi tanah",
                        "Rotasi jagung-kentang-kubis",
                        "Penggunaan mulsa organik"
                    ],
                    "pest_risks": [
                        "Ulat tanah (Agrotis ipsilon)",
                        "Trips (Thrips tabaci)",
                        "Penyakit karat daun"
                    ],
                    "climate_threats": [
                        "Hujan berlebih menyebabkan busuk batang",
                        "Suhu dingin menghambat pertumbuhan",
                        "Kabut tebal mengurangi fotosintesis"
                    ]
                }
            }
        },
        "cassava": {
            "traditional_practices": {
                "dry_areas": {
                    "regions": ["Indramayu", "Cirebon", "Majalengka", "Kuningan"],
                    "practices": [
                        "Tanam singkong pada awal musim hujan",
                        "Sistem guludan untuk drainase",
                        "Varietas lokal Adira-1 dan Malang-6",
                        "Tumpangsari dengan kacang tanah atau jagung"
                    ],
                    "pest_risks": [
                        "Kutu putih singkong (Phenacoccus manihoti)",
                        "Tungau merah (Tetranychus urticae)",
                        "Penyakit layu bakteri"
                    ],
                    "climate_threats": [
                        "Kekeringan berkepanjangan",
                        "Hujan deras saat panen menyebabkan busuk umbi",
                        "Suhu tinggi >35°C mengurangi hasil"
                    ]
                },
                "marginal_lands": {
                    "regions": ["Tasikmalaya", "Ciamis", "Pangandaran", "Sukabumi"],
                    "practices": [
                        "Penanaman di lahan marginal dan lereng",
                        "Konservasi tanah dengan tanaman penutup",
                        "Pemanenan bertahap (8-12 bulan)",
                        "Pengolahan langsung menjadi tepung tapioka"
                    ],
                    "pest_risks": [
                        "Belalang kembara saat musim kering",
                        "Ulat daun singkong",
                        "Penyakit mosaik singkong"
                    ],
                    "climate_threats": [
                        "Erosi tanah saat hujan deras",
                        "Longsor di area berlereng",
                        "Variabilitas curah hujan tinggi"
                    ]
                }
            }
        }
    }
    
    return practices_and_risks

def get_mapping_visualization_guide():
    """Provide guide for Python-based visual mapping implementation"""
    mapping_guide = {
        "recommended_libraries": [
            "folium - Interactive web maps",
            "geopandas - Geospatial data manipulation",
            "matplotlib - Static plotting",
            "plotly - Interactive visualizations",
            "contextily - Basemap tiles"
        ],
        "data_structure": {
            "geospatial_data": {
                "format": "GeoJSON or Shapefile",
                "source": "Indonesia Geospatial Information Agency (BIG)",
                "level": "District/Regency boundaries of West Java"
            },
            "suitability_scores": {
                "format": "Pandas DataFrame",
                "columns": [
                    "region_name", "crop_type", "overall_score",
                    "edaphic_score", "hydrologic_score", "atmospheric_score",
                    "latitude", "longitude", "suitability_class"
                ]
            }
        },
        "visualization_types": {
            "choropleth_map": {
                "description": "Color-coded regions by suitability score",
                "color_scheme": {
                    "highly_suitable": "#006837",      # Dark green
                    "moderately_suitable": "#31a354", # Medium green
                    "marginally_suitable": "#78c679", # Light green
                    "not_suitable": "#c2e699"         # Very light green
                }
            },
            "multi_parameter_dashboard": {
                "description": "Interactive dashboard showing individual parameter scores",
                "components": [
                    "Regional map with dropdown crop selection",
                    "Parameter score radar charts",
                    "Ranking table with sortable columns",
                    "Climate data time series"
                ]
            }
        },
        "implementation_example": """
import folium
import geopandas as gpd
import pandas as pd
from folium.plugins import MarkerCluster

def create_suitability_map(suitability_data, geojson_path):
    # Create base map centered on West Java
    m = folium.Map(location=[-6.9, 107.6], zoom_start=8)
    
    # Load West Java boundaries
    gdf = gpd.read_file(geojson_path)
    
    # Merge with suitability data
    merged = gdf.merge(suitability_data, left_on='NAME', right_on='region_name')
    
    # Create choropleth
    folium.Choropleth(
        geo_data=merged.to_json(),
        data=merged,
        columns=['region_name', 'overall_score'],
        key_on='feature.properties.NAME',
        fill_color='YlGn',
        fill_opacity=0.7,
        line_opacity=0.2,
        legend_name='Crop Suitability Score'
    ).add_to(m)
    
    return m
        """,
        "data_sources": {
            "geospatial": [
                "Indonesia Geospatial Information Agency (BIG)",
                "OpenStreetMap Indonesia",
                "GADM (Global Administrative Areas)"
            ],
            "climate": [
                "BMKG (Indonesian Meteorological Agency)",
                "WorldClim",
                "NASA Giovanni"
            ],
            "soil": [
                "Indonesian Soil Research Institute",
                "ISRIC World Soil Information",
                "FAO Soil Portal"
            ]
        }
    }
    
    return mapping_guide

if __name__ == "__main__":
    # Generate comprehensive analysis
    print("Generating West Java Crop Suitability Analysis...")
    
    # Generate main report
    report = generate_comprehensive_report()
    
    # Get traditional practices and risks
    practices_risks = get_traditional_practices_and_risks()
    
    # Get mapping guide
    mapping_guide = get_mapping_visualization_guide()
    
    # Save results
    with open("data/west_java_crop_analysis_report.json", "w") as f:
        json.dump(report, f, indent=2)
    
    with open("data/traditional_practices_risks.json", "w") as f:
        json.dump(practices_risks, f, indent=2)
    
    with open("data/mapping_visualization_guide.json", "w") as f:
        json.dump(mapping_guide, f, indent=2)
    
    print("Analysis complete! Files generated:")
    print("- data/west_java_crop_analysis_report.json")
    print("- data/traditional_practices_risks.json") 
    print("- data/mapping_visualization_guide.json")
