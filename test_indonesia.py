#!/usr/bin/env python3
"""
Test script untuk Asisten Pertanian Indonesia
Mendemonstrasikan format respons terstruktur khusus Indonesia dengan parameter
"""

from agricultural_chatbot import initialize_openai_client, get_ai_response, analyze_parameters

def test_indonesian_responses():
    """Test format respons terstruktur dengan skenario Indonesia dan parameter"""
    
    client = initialize_openai_client()
    
    # Test parameters for different scenarios
    test_scenarios = [
        {
            "role": "Petani",
            "location": "Jawa Barat",
            "question": "Sawah padi saya terkena serangan wereng minggu lalu. Berapa lama waktu pemulihan yang dibutuhkan?",
            "crop_type": "padi",
            "parameters": {
                "edaphic": {
                    "n_content": 0.10,  # Low nitrogen
                    "p_content": 0.06,  # Low phosphorus
                    "k_content": 0.12,  # Low potassium
                    "ph_level": 5.2,    # Slightly acidic
                    "organic_matter": 2.0,
                    "soil_temperature": 28.0,
                    "soil_density": 1.3
                },
                "hydrologic": {
                    "rainfall": 250.0,
                    "water_table": 5.0,  # Good for rice
                    "drainage_rate": 0.8,
                    "irrigation_frequency": 2.0,
                    "water_quality_ec": 0.4
                },
                "atmospheric": {
                    "air_temperature": 32.0,  # High temperature
                    "humidity": 85.0,    # High humidity
                    "wind_speed": 6.0,
                    "solar_radiation": 22.0,
                    "photoperiod": 12.5,
                    "atmospheric_pressure": 1010.0,
                    "co2_concentration": 420.0
                }
            }
        },
        {
            "role": "Peternak", 
            "location": "Jawa Timur",
            "question": "Beberapa sapi saya menunjukkan gejala penyakit pernapasan. Bagaimana timeline pemulihannya?",
            "crop_type": "general",
            "parameters": {
                "edaphic": {
                    "n_content": 0.18,
                    "p_content": 0.12,
                    "k_content": 0.20,
                    "ph_level": 6.5,
                    "organic_matter": 3.5,
                    "soil_temperature": 26.0,
                    "soil_density": 1.1
                },
                "hydrologic": {
                    "rainfall": 180.0,
                    "water_table": 80.0,
                    "drainage_rate": 1.2,
                    "irrigation_frequency": 5.0,
                    "water_quality_ec": 0.6
                },
                "atmospheric": {
                    "air_temperature": 29.0,
                    "humidity": 78.0,
                    "wind_speed": 12.0,  # High wind
                    "solar_radiation": 19.0,
                    "photoperiod": 12.0,
                    "atmospheric_pressure": 1015.0,
                    "co2_concentration": 410.0
                }
            }
        },
        {
            "role": "Insinyur Pertanian",
            "location": "Sumatera Utara",
            "question": "Sistem irigasi teknis gagal saat musim kemarau. Apa strategi pemulihan terbaik?",
            "crop_type": "jagung",
            "parameters": {
                "edaphic": {
                    "n_content": 0.15,
                    "p_content": 0.16,  # Good phosphorus
                    "k_content": 0.25,  # Good potassium
                    "ph_level": 6.8,    # Good pH
                    "organic_matter": 4.2,
                    "soil_temperature": 24.0,
                    "soil_density": 1.0
                },
                "hydrologic": {
                    "rainfall": 50.0,   # Very low rainfall (drought)
                    "water_table": 150.0,  # Deep water table
                    "drainage_rate": 2.5,  # Fast drainage
                    "irrigation_frequency": 10.0,  # Infrequent irrigation
                    "water_quality_ec": 0.8
                },
                "atmospheric": {
                    "air_temperature": 35.0,  # Very high temperature
                    "humidity": 55.0,    # Low humidity
                    "wind_speed": 15.0,  # High wind
                    "solar_radiation": 28.0,  # High radiation
                    "photoperiod": 13.0,
                    "atmospheric_pressure": 1008.0,
                    "co2_concentration": 440.0
                }
            }
        }
    ]
    
    print("🌾 Testing Asisten Pertanian Indonesia - Format Respons Terstruktur dengan Parameter")
    print("=" * 90)
    
    for i, scenario in enumerate(test_scenarios, 1):
        print(f"\n🧪 TEST {i}: {scenario['role']} - {scenario['location']}")
        print(f"📝 Pertanyaan: {scenario['question']}")
        print(f"🌱 Jenis Tanaman: {scenario['crop_type'].title()}")
        print("-" * 90)
        
        # Show parameter analysis first
        print("📊 ANALISIS PARAMETER:")
        parameter_analysis = analyze_parameters(scenario['parameters'], scenario['crop_type'])
        
        for category, analysis in parameter_analysis.items():
            category_name = {
                "edaphic": "Edafik (Tanah)",
                "hydrologic": "Hidrologik (Air)", 
                "atmospheric": "Atmosferik (Iklim)"
            }.get(category, category)
            
            print(f"\n{category_name}: {analysis['status'].upper()}")
            if analysis['issues']:
                print("  Masalah:")
                for issue in analysis['issues']:
                    print(f"    - {issue}")
            if analysis['recommendations']:
                print("  Rekomendasi:")
                for rec in analysis['recommendations']:
                    print(f"    - {rec}")
        
        print("\n" + "=" * 90)
        print("🤖 RESPONS AI:")
        print("-" * 90)
        
        try:
            response = get_ai_response(
                client, 
                scenario['role'], 
                scenario['question'], 
                scenario['location'],
                scenario['parameters'],
                scenario['crop_type']
            )
            print(response)
        except Exception as e:
            print(f"❌ Error: {e}")
        
        print("=" * 90)

if __name__ == "__main__":
    test_indonesian_responses()
