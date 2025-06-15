import streamlit as st
import json
from datetime import datetime
from openai import OpenAI

# Indonesian Agricultural knowledge base
INDONESIAN_AGRICULTURAL_KNOWLEDGE = {
    "crop_management": {
        "common_crops": ["padi", "jagung", "cabai", "kelapa sawit", "kakao", "kopi", "pisang", "singkong", "ubi jalar", "kacang tanah"],
        "local_techniques": {
            "jajar_legowo": "Sistem tanam padi dengan jarak tanam tidak sama yang meningkatkan populasi dan hasil panen",
            "tumpangsari": "Sistem tanam campuran beberapa jenis tanaman dalam satu lahan untuk optimalisasi hasil",
            "integrated_farming": "Sistem pertanian terpadu yang menggabungkan tanaman, ternak, dan ikan"
        },
        "planting_seasons": {
            "musim_hujan": ["padi", "jagung", "cabai", "sayuran hijau"],
            "musim_kemarau": ["tembakau", "bawang merah", "kacang tanah"],
            "sepanjang_tahun": ["kelapa sawit", "kakao", "kopi", "pisang"]
        },
        "pest_diseases": {
            "wereng": "Hama utama padi. Pengendalian dengan varietas tahan dan pestisida nabati neem.",
            "blast_padi": "Penyakit jamur pada padi. Perbaiki drainase dan gunakan fungisida berbahan tembaga.",
            "borer_jagung": "Hama penggerek batang jagung. Gunakan perangkap feromon dan pestisida hayati.",
            "antraknosa_cabai": "Penyakit jamur pada cabai. Perbaiki sirkulasi udara dan aplikasi fungisida."
        }
    },
    "livestock": {
        "sapi": {
            "feeding": "Pakan hijauan (rumput gajah, rumput raja) 10-15% berat badan, konsentrat 1-2% berat badan, air bersih 30-50 liter/hari.",
            "health": "Vaksinasi SE, PMK, Antraks. Cacing setiap 6 bulan. Perawatan kuku rutin.",
            "breeding": "Kawin pertama sapi betina umur 18-24 bulan, masa bunting 9 bulan."
        },
        "kambing": {
            "feeding": "Hijauan 3-4 kg/hari (daun turi, lamtoro, rumput), konsentrat 0.5-1 kg. Air 3-4 liter/hari.",
            "housing": "Kandang panggung, ventilasi baik, ukuran 1.5x1m per ekor dewasa.",
            "health": "Vaksinasi SE, cacingan rutin, kontrol parasit eksternal."
        },
        "ayam_kampung": {
            "feeding": "Pakan ayam petelur/broiler dicampur jagung giling, dedak, konsentrat. Tambah sayuran hijau.",
            "housing": "Kandang battery atau postal, 8-10 ekor/m2, tempat bertelur 1:4 ratio.",
            "health": "Vaksinasi ND, IB, Fowl Pox. Sanitasi kandang rutin, air bersih."
        }
    },
    "soil_management": {
        "soil_types": {
            "andosol": "Tanah vulkanis subur, baik untuk tanaman hortikultura. pH 5.5-6.5, drainase baik.",
            "latosol": "Tanah merah-kuning tropis, perlu pupuk organik. pH 4.5-6.0, kandungan Al tinggi.",
            "regosol": "Tanah muda dari material vulkanis, baik untuk tanaman semusim. Perlu bahan organik.",
            "alluvial": "Tanah endapan sungai, sangat subur untuk padi dan palawija. pH 6.0-7.0."
        },
        "fertility": {
            "nitrogen": "Pupuk urea, kompos, pupuk kandang. Aplikasi bertahap sesuai fase pertumbuhan.",
            "phosphorus": "Pupuk TSP, SP-36. Penting untuk pembungaan dan pembentukan buah/biji.",
            "potassium": "Pupuk KCl, abu sekam. Meningkatkan ketahanan terhadap penyakit dan kekeringan.",
            "organic_matter": "Kompos, pupuk kandang, biochar untuk memperbaiki struktur tanah dan retensi air."
        }
    },
    "irrigation": {
        "methods": {
            "irigasi_teknis": "Sistem irigasi permanen dengan bendungan dan saluran primer-tersier.",
            "tadah_hujan": "Sistem pertanian yang mengandalkan air hujan, cocok untuk daerah curah hujan tinggi.",
            "pasang_surut": "Sistem irigasi di lahan rawa yang memanfaatkan air pasang surut.",
            "tetes": "Sistem irigasi hemat air untuk tanaman hortikultura dan perkebunan."
        },
        "water_management": {
            "monsoon": "Kelola air berlebih saat musim hujan, konservasi air saat kemarau.",
            "drainage": "Sistem drainase penting untuk mencegah genangan dan penyakit tanaman.",
            "water_quality": "Air irigasi harus bebas dari pencemaran industri dan limbah domestik."
        }
    },
    "climate_adaptation": {
        "monsoon_cycle": {
            "musim_hujan": "Oktober-Maret: Persiapan drainase, pengendalian hama-penyakit akibat kelembaban tinggi.",
            "musim_kemarau": "April-September: Konservasi air, irigasi efisien, pilih varietas tahan kekeringan."
        },
        "pest_management": {
            "musim_hujan": "Tingkatkan kontrol penyakit jamur dan bakteri, perbaiki sanitasi lingkungan.",
            "musim_kemarau": "Waspada hama serangga, kutu, dan tungau yang berkembang di kondisi kering."
        }
    }
}

# Indonesian provinces for location context
INDONESIAN_PROVINCES = [
    "Aceh", "Sumatera Utara", "Sumatera Barat", "Riau", "Jambi", "Sumatera Selatan", 
    "Bengkulu", "Lampung", "Kepulauan Bangka Belitung", "Kepulauan Riau",
    "DKI Jakarta", "Jawa Barat", "Jawa Tengah", "DI Yogyakarta", "Jawa Timur", "Banten",
    "Bali", "Nusa Tenggara Barat", "Nusa Tenggara Timur",
    "Kalimantan Barat", "Kalimantan Tengah", "Kalimantan Selatan", "Kalimantan Timur", "Kalimantan Utara",
    "Sulawesi Utara", "Sulawesi Tengah", "Sulawesi Selatan", "Sulawesi Tenggara", "Gorontalo", "Sulawesi Barat",
    "Maluku", "Maluku Utara", "Papua Barat", "Papua"
]

USER_ROLES = {
    "Petani": "Spesialis pengelolaan tanaman dan lahan pertanian",
    "Peternak": "Ahli peternakan dan pengembangbiakan hewan", 
    "Spesialis Agribisnis": "Ahli bisnis dan analisis pasar pertanian",
    "Insinyur Pertanian": "Spesialis teknologi dan peralatan pertanian",
    "Petugas Penyuluh Pertanian": "Profesional pendidikan dan penyuluhan pertanian",
    "Konsultan Pertanian": "Spesialis konsultasi pertanian komprehensif"
}

def initialize_openai_client():
    """Initialize OpenAI client with OpenRouter"""
    return OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key="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",
    )

def get_role_specific_prompt(user_role, question, location=""):
    """Generate Indonesia-specific role prompts with structured format"""
    role_contexts = {
        "Petani": "Anda adalah konsultan pertanian ahli yang membantu petani Indonesia dengan masalah praktis pengelolaan tanaman dan lahan. Fokus pada saran yang dapat diterapkan untuk budidaya tanaman, kesehatan tanah, pengendalian hama, dan praktik pertanian terbaik.",
        
        "Peternak": "Anda adalah spesialis peternakan yang membantu peternak Indonesia. Fokus pada kesehatan hewan, nutrisi, praktik breeding, kandang, dan strategi manajemen ternak.",
        
        "Spesialis Agribisnis": "Anda adalah konsultan agribisnis yang membantu pengambilan keputusan bisnis pertanian di Indonesia. Fokus pada analisis pasar, rantai pasok, ekonomi pertanian, perencanaan bisnis, dan keuangan pertanian.",
        
        "Insinyur Pertanian": "Anda adalah ahli teknik pertanian yang membantu dengan teknologi dan peralatan pertanian di Indonesia. Fokus pada sistem irigasi, mesin pertanian, precision agriculture, otomasi, dan infrastruktur pertanian.",
        
        "Petugas Penyuluh Pertanian": "Anda adalah spesialis penyuluhan pertanian yang membantu pendidikan dan penyuluhan petani di Indonesia. Fokus pada transfer pengetahuan, program pelatihan, pengembangan masyarakat, dan penyebaran praktik pertanian terbaik.",
        
        "Konsultan Pertanian": "Anda adalah konsultan pertanian komprehensif yang memberikan saran ahli di semua aspek pertanian Indonesia. Fokus pada solusi terintegrasi yang mencakup tanaman, ternak, bisnis, teknologi, dan keberlanjutan."
    }
    
    base_prompt = role_contexts.get(user_role, role_contexts["Konsultan Pertanian"])
    
    # Enhanced structured response format for Indonesia
    structured_format = f"""
    
    Anda adalah asisten pertanian cerdas yang dirancang khusus untuk mendukung profesional pertanian di Indonesia.
    
    **Respons Anda HARUS mencakup tepat tiga bagian berikut dalam urutan ini:**

    ## 1. 🔮 Forecasting Recovery (Prakiraan Pemulihan)
    Prediksi pemulihan lingkungan dari kerusakan pertanian (misalnya polusi, degradasi tanah, serangan hama, wabah penyakit):
    - Estimasi waktu pemulihan yang spesifik (hari, minggu, bulan, musim)
    - Daftar 3-5 langkah remediasi yang dapat diterapkan
    - Pertimbangkan kondisi lokal/regional dan faktor musiman Indonesia
    - Pertimbangkan dampak ekonomi dan biaya pemulihan

    ## 2. 🤖 LLM Suggestion (Saran Model AI)
    Berikan saran atau wawasan berbasis model yang relevan dengan masalah pertanian saat ini:
    - Gunakan penalaran ilmiah dan pola berbasis data
    - Sertakan contoh dunia nyata atau studi kasus yang relevan dengan Indonesia
    - Referensikan praktik terbaik dari situasi serupa
    - Sarankan metrik atau indikator monitoring

    ## 3. 🔧 Problem-Solving Recommendations (Rekomendasi Pemecahan Masalah)
    Analisis dan ajukan solusi berdasarkan tiga faktor kritis berikut:
    
    **Faktor Edafik (Sistem Tanah):**
    - Kesehatan tanah, struktur, kesuburan, tingkat pH
    - Jenis tanah Indonesia (andosol, latosol, regosol, alluvial)
    - Manajemen nutrisi dan bahan organik
    
    **Faktor Hidrologik (Sistem Air):**
    - Efisiensi dan penjadwalan irigasi (teknis, tadah hujan, pasang surut)
    - Manajemen drainase dan kualitas air
    - Strategi konservasi air untuk iklim tropis
    
    **Faktor Atmosferik (Sistem Iklim):**
    - Strategi adaptasi iklim tropis dan siklus monsun Indonesia
    - Pertimbangan pola cuaca (musim hujan/kemarau)
    - Optimalisasi kelembaban, angin, dan curah hujan

    **Konteks:**
    - Peran Pengguna: {user_role}
    - Lokasi: {location if location else "Indonesia"}
    - Basis Pengetahuan Pertanian Indonesia: Tanaman ({', '.join(INDONESIAN_AGRICULTURAL_KNOWLEDGE['crop_management']['common_crops'])}), Ternak, Manajemen Tanah, Irigasi
    - Masalah/Pertanyaan: {question}
    
    Gunakan bahasa yang ringkas dan profesional yang sesuai untuk seorang {user_role}. Format dengan heading markdown untuk rendering GUI.
    Fokus pada solusi praktis yang dapat diimplementasikan dengan timeline yang jelas dan hasil yang dapat diukur.
    Sertakan pertimbangan khusus untuk kondisi iklim tropis Indonesia dan praktik pertanian lokal.
    """
    
    return base_prompt + structured_format

def get_ai_response(client, user_role, question, location="", parameters=None, crop_type="general"):
    """Get AI response based on user role and question for Indonesian context with parameter analysis"""
    try:
        # Base prompt
        prompt = get_role_specific_prompt(user_role, question, location)
        
        # Add parameter analysis if provided
        if parameters:
            parameter_summary = format_parameter_summary(parameters)
            parameter_analysis = analyze_parameters(parameters, crop_type)
            
            parameter_context = f"""
            
            {parameter_summary}
            
            **Analisis Parameter Otomatis:**
            
            *Kondisi Edafik (Tanah):* {parameter_analysis['edaphic']['status'].title()}
            {('- Masalah: ' + '; '.join(parameter_analysis['edaphic']['issues'])) if parameter_analysis['edaphic']['issues'] else '- Kondisi tanah dalam rentang optimal'}
            {('- Rekomendasi: ' + '; '.join(parameter_analysis['edaphic']['recommendations'])) if parameter_analysis['edaphic']['recommendations'] else ''}
            
            *Kondisi Hidrologik (Air):* {parameter_analysis['hydrologic']['status'].title()}
            {('- Masalah: ' + '; '.join(parameter_analysis['hydrologic']['issues'])) if parameter_analysis['hydrologic']['issues'] else '- Kondisi air dalam rentang optimal'}
            {('- Rekomendasi: ' + '; '.join(parameter_analysis['hydrologic']['recommendations'])) if parameter_analysis['hydrologic']['recommendations'] else ''}
            
            *Kondisi Atmosferik (Iklim):* {parameter_analysis['atmospheric']['status'].title()}
            {('- Masalah: ' + '; '.join(parameter_analysis['atmospheric']['issues'])) if parameter_analysis['atmospheric']['issues'] else '- Kondisi iklim dalam rentang optimal'}
            {('- Rekomendasi: ' + '; '.join(parameter_analysis['atmospheric']['recommendations'])) if parameter_analysis['atmospheric']['recommendations'] else ''}
            
            **PENTING: Gunakan data parameter dan analisis di atas untuk memberikan rekomendasi yang lebih spesifik dan akurat dalam respons Anda.**
            """
            
            prompt += parameter_context
        
        completion = client.chat.completions.create(
            model="mistralai/mistral-tiny",
            messages=[
                {
                    "role": "system",
                    "content": prompt
                },
                {
                    "role": "user", 
                    "content": question
                }
            ],
            temperature=0.7,
            max_tokens=1800
        )
        
        return completion.choices[0].message.content
    except Exception as e:
        return f"Error mendapatkan respons AI: {str(e)}"

def search_knowledge_base(query):
    """Search the Indonesian agricultural knowledge base for relevant information"""
    query_lower = query.lower()
    results = []
    
    # Search through different categories
    for category, content in INDONESIAN_AGRICULTURAL_KNOWLEDGE.items():
        if isinstance(content, dict):
            for subcategory, info in content.items():
                if isinstance(info, dict):
                    for key, value in info.items():
                        if (query_lower in key.lower() or 
                            query_lower in str(value).lower()):
                            results.append({
                                "category": category,
                                "subcategory": subcategory,
                                "item": key,
                                "info": value
                            })
                elif isinstance(info, list):
                    for item in info:
                        if query_lower in item.lower():
                            results.append({
                                "category": category,
                                "subcategory": subcategory,
                                "item": item,
                                "info": f"Informasi tentang {item}"
                            })
    
    return results

# Parameter definitions for comprehensive agricultural analysis
AGRICULTURAL_PARAMETERS = {
    "edaphic": {
        "n_content": {
            "name": "Nitrogen (N)",
            "unit": "%",
            "description": "Kandungan nitrogen dalam tanah",
            "optimal_range": {"padi": (0.15, 0.25), "jagung": (0.12, 0.20), "cabai": (0.20, 0.30)},
            "min_val": 0.0,
            "max_val": 1.0,
            "default": 0.15
        },
        "p_content": {
            "name": "Phosphorus (P)",
            "unit": "%",
            "description": "Kandungan fosfor dalam tanah",
            "optimal_range": {"padi": (0.08, 0.15), "jagung": (0.10, 0.18), "cabai": (0.12, 0.20)},
            "min_val": 0.0,
            "max_val": 0.5,
            "default": 0.10
        },
        "k_content": {
            "name": "Potassium (K)",
            "unit": "%",
            "description": "Kandungan kalium dalam tanah",
            "optimal_range": {"padi": (0.15, 0.25), "jagung": (0.18, 0.28), "cabai": (0.20, 0.35)},
            "min_val": 0.0,
            "max_val": 1.0,
            "default": 0.18
        },
        "ph_level": {
            "name": "pH Tanah",
            "unit": "",
            "description": "Tingkat keasaman tanah",
            "optimal_range": {"padi": (5.5, 6.5), "jagung": (6.0, 7.0), "cabai": (6.0, 6.8)},
            "min_val": 3.0,
            "max_val": 9.0,
            "default": 6.0
        },
        "organic_matter": {
            "name": "Bahan Organik",
            "unit": "%",
            "description": "Kandungan bahan organik dalam tanah",
            "optimal_range": {"general": (2.5, 5.0)},
            "min_val": 0.0,
            "max_val": 10.0,
            "default": 3.0
        },
        "soil_temperature": {
            "name": "Suhu Tanah",
            "unit": "°C",
            "description": "Suhu tanah pada kedalaman 10cm",
            "optimal_range": {"padi": (25, 35), "jagung": (20, 30), "cabai": (20, 28)},
            "min_val": 10.0,
            "max_val": 45.0,
            "default": 27.0
        },
        "soil_density": {
            "name": "Kepadatan Tanah",
            "unit": "g/cm³",
            "description": "Bulk density tanah",
            "optimal_range": {"general": (1.0, 1.4)},
            "min_val": 0.8,
            "max_val": 2.0,
            "default": 1.2
        }
    },
    "hydrologic": {
        "rainfall": {
            "name": "Curah Hujan",
            "unit": "mm/bulan",
            "description": "Curah hujan bulanan",
            "optimal_range": {"padi": (150, 300), "jagung": (100, 200), "cabai": (80, 150)},
            "min_val": 0.0,
            "max_val": 1000.0,
            "default": 200.0
        },
        "water_table": {
            "name": "Kedalaman Air Tanah",
            "unit": "cm",
            "description": "Kedalaman muka air tanah dari permukaan",
            "optimal_range": {"padi": (0, 15), "jagung": (50, 100), "cabai": (40, 80)},
            "min_val": 0.0,
            "max_val": 300.0,
            "default": 50.0
        },
        "drainage_rate": {
            "name": "Laju Drainase",
            "unit": "cm/jam",
            "description": "Kecepatan drainase air dalam tanah",
            "optimal_range": {"general": (0.5, 2.0)},
            "min_val": 0.0,
            "max_val": 10.0,
            "default": 1.0
        },
        "irrigation_frequency": {
            "name": "Frekuensi Irigasi",
            "unit": "hari",
            "description": "Interval pemberian air irigasi",
            "optimal_range": {"padi": (1, 3), "jagung": (3, 7), "cabai": (2, 4)},
            "min_val": 1.0,
            "max_val": 30.0,
            "default": 3.0
        },
        "water_quality_ec": {
            "name": "EC Air",
            "unit": "dS/m",
            "description": "Electrical Conductivity air irigasi",
            "optimal_range": {"general": (0.25, 0.75)},
            "min_val": 0.0,
            "max_val": 5.0,
            "default": 0.5
        }
    },
    "atmospheric": {
        "air_temperature": {
            "name": "Suhu Udara",
            "unit": "°C",
            "description": "Suhu udara rata-rata harian",
            "optimal_range": {"padi": (25, 35), "jagung": (20, 30), "cabai": (20, 28)},
            "min_val": 10.0,
            "max_val": 45.0,
            "default": 28.0
        },
        "humidity": {
            "name": "Kelembaban Relatif",
            "unit": "%",
            "description": "Kelembaban udara relatif",
            "optimal_range": {"padi": (70, 85), "jagung": (60, 75), "cabai": (60, 70)},
            "min_val": 30.0,
            "max_val": 100.0,
            "default": 75.0
        },
        "wind_speed": {
            "name": "Kecepatan Angin",
            "unit": "km/jam",
            "description": "Kecepatan angin rata-rata",
            "optimal_range": {"general": (5, 15)},
            "min_val": 0.0,
            "max_val": 50.0,
            "default": 8.0
        },
        "solar_radiation": {
            "name": "Radiasi Matahari",
            "unit": "MJ/m²/hari",
            "description": "Intensitas radiasi matahari harian",
            "optimal_range": {"general": (15, 25)},
            "min_val": 5.0,
            "max_val": 35.0,
            "default": 20.0
        },
        "photoperiod": {
            "name": "Lama Penyinaran",
            "unit": "jam/hari",
            "description": "Durasi sinar matahari per hari",
            "optimal_range": {"general": (10, 14)},
            "min_val": 6.0,
            "max_val": 16.0,
            "default": 12.0
        },
        "atmospheric_pressure": {
            "name": "Tekanan Udara",
            "unit": "hPa",
            "description": "Tekanan atmosfer",
            "optimal_range": {"general": (1000, 1020)},
            "min_val": 950.0,
            "max_val": 1050.0,
            "default": 1013.0
        },
        "co2_concentration": {
            "name": "Konsentrasi CO₂",
            "unit": "ppm",
            "description": "Konsentrasi karbon dioksida di udara",
            "optimal_range": {"general": (350, 450)},
            "min_val": 300.0,
            "max_val": 800.0,
            "default": 400.0
        }
    }
}

def analyze_parameters(parameters, crop_type="general"):
    """Analyze agricultural parameters and provide assessment"""
    analysis = {
        "edaphic": {"status": "optimal", "issues": [], "recommendations": []},
        "hydrologic": {"status": "optimal", "issues": [], "recommendations": []},
        "atmospheric": {"status": "optimal", "issues": [], "recommendations": []}
    }
    
    for category, params in parameters.items():
        if category in AGRICULTURAL_PARAMETERS:
            for param_key, value in params.items():
                if param_key in AGRICULTURAL_PARAMETERS[category]:
                    param_info = AGRICULTURAL_PARAMETERS[category][param_key]
                    
                    # Get optimal range for the crop or general
                    optimal_range = param_info["optimal_range"].get(crop_type) or param_info["optimal_range"].get("general")
                    
                    if optimal_range:
                        min_opt, max_opt = optimal_range
                        
                        if value < min_opt:
                            analysis[category]["status"] = "suboptimal"
                            analysis[category]["issues"].append(f"{param_info['name']} terlalu rendah ({value} {param_info['unit']}, optimal: {min_opt}-{max_opt} {param_info['unit']})")
                            
                            # Add specific recommendations
                            if param_key == "n_content":
                                analysis[category]["recommendations"].append("Aplikasi pupuk nitrogen (urea/ZA) bertahap")
                            elif param_key == "p_content":
                                analysis[category]["recommendations"].append("Tambahkan pupuk fosfat (TSP/SP-36)")
                            elif param_key == "k_content":
                                analysis[category]["recommendations"].append("Gunakan pupuk kalium (KCl/abu sekam)")
                            elif param_key == "ph_level":
                                analysis[category]["recommendations"].append("Lakukan pengapuran dengan dolomit/kapur pertanian")
                            elif param_key == "rainfall":
                                analysis[category]["recommendations"].append("Tingkatkan irigasi atau gunakan mulsa untuk konservasi air")
                            elif param_key == "humidity":
                                analysis[category]["recommendations"].append("Perbaiki sirkulasi udara dan drainase")
                                
                        elif value > max_opt:
                            analysis[category]["status"] = "suboptimal"
                            analysis[category]["issues"].append(f"{param_info['name']} terlalu tinggi ({value} {param_info['unit']}, optimal: {min_opt}-{max_opt} {param_info['unit']})")
                            
                            # Add specific recommendations
                            if param_key == "ph_level":
                                analysis[category]["recommendations"].append("Tambahkan bahan organik (kompos) untuk menurunkan pH")
                            elif param_key == "rainfall":
                                analysis[category]["recommendations"].append("Perbaiki sistem drainase untuk mencegah genangan")
                            elif param_key == "humidity":
                                analysis[category]["recommendations"].append("Tingkatkan ventilasi dan kurangi irigasi berlebihan")
    
    return analysis

def format_parameter_summary(parameters):
    """Format parameter summary for AI prompt"""
    summary = "\n**Data Parameter Lapangan:**\n"
    
    for category, params in parameters.items():
        category_name = {
            "edaphic": "Faktor Edafik (Tanah)",
            "hydrologic": "Faktor Hidrologik (Air)", 
            "atmospheric": "Faktor Atmosferik (Iklim)"
        }.get(category, category)
        
        summary += f"\n*{category_name}:*\n"
        
        for param_key, value in params.items():
            if category in AGRICULTURAL_PARAMETERS and param_key in AGRICULTURAL_PARAMETERS[category]:
                param_info = AGRICULTURAL_PARAMETERS[category][param_key]
                summary += f"- {param_info['name']}: {value} {param_info['unit']}\n"
    
    return summary

def main():
    st.set_page_config(
        page_title="Asisten Pertanian Indonesia",
        page_icon="🌾",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Initialize session state
    if 'messages' not in st.session_state:
        st.session_state.messages = []
    if 'user_role' not in st.session_state:
        st.session_state.user_role = "Petani"
    if 'location' not in st.session_state:
        st.session_state.location = ""
    
    # Initialize OpenAI client
    client = initialize_openai_client()
    
    # Sidebar
    with st.sidebar:
        st.title("🌾 Asisten Pertanian Indonesia")
        st.markdown("### Peran Anda")
        
        selected_role = st.selectbox(
            "Pilih peran pertanian Anda:",
            list(USER_ROLES.keys()),
            index=list(USER_ROLES.keys()).index(st.session_state.user_role)
        )
        
        if selected_role != st.session_state.user_role:
            st.session_state.user_role = selected_role
            st.rerun()
        
        st.markdown(f"**Deskripsi Peran:** {USER_ROLES[selected_role]}")
        
        # Location selection
        st.markdown("### 📍 Lokasi")
        selected_location = st.selectbox(
            "Pilih provinsi (opsional):",
            [""] + INDONESIAN_PROVINCES,
            index=0 if st.session_state.location == "" else INDONESIAN_PROVINCES.index(st.session_state.location) + 1
        )
        
        if selected_location != st.session_state.location:
            st.session_state.location = selected_location
        
        # Parameter Input
        st.markdown("### 📊 Parameter Lapangan")
        st.markdown("*Input data lapangan untuk analisis yang lebih akurat*")
        
        # Initialize parameter session state
        if 'use_parameters' not in st.session_state:
            st.session_state.use_parameters = False
        if 'parameters' not in st.session_state:
            st.session_state.parameters = {"edaphic": {}, "hydrologic": {}, "atmospheric": {}}
        if 'crop_type' not in st.session_state:
            st.session_state.crop_type = "general"
        
        use_parameters = st.checkbox("Gunakan Data Parameter", value=st.session_state.use_parameters)
        st.session_state.use_parameters = use_parameters
        
        if use_parameters:
            # Crop type selection for optimal ranges
            crop_type = st.selectbox(
                "Jenis Tanaman:",
                ["general", "padi", "jagung", "cabai"],
                index=["general", "padi", "jagung", "cabai"].index(st.session_state.crop_type)
            )
            st.session_state.crop_type = crop_type
            
            # Parameter input tabs
            param_tab1, param_tab2, param_tab3 = st.tabs(["🌱 Edafik", "💧 Hidrologik", "🌤️ Atmosferik"])
            
            with param_tab1:
                st.markdown("**Faktor Tanah**")
                for param_key, param_info in AGRICULTURAL_PARAMETERS["edaphic"].items():
                    value = st.number_input(
                        f"{param_info['name']} ({param_info['unit']})",
                        min_value=param_info['min_val'],
                        max_value=param_info['max_val'],
                        value=st.session_state.parameters["edaphic"].get(param_key, param_info['default']),
                        help=param_info['description'],
                        key=f"edaphic_{param_key}"
                    )
                    st.session_state.parameters["edaphic"][param_key] = value
            
            with param_tab2:
                st.markdown("**Faktor Air**")
                for param_key, param_info in AGRICULTURAL_PARAMETERS["hydrologic"].items():
                    value = st.number_input(
                        f"{param_info['name']} ({param_info['unit']})",
                        min_value=param_info['min_val'],
                        max_value=param_info['max_val'],
                        value=st.session_state.parameters["hydrologic"].get(param_key, param_info['default']),
                        help=param_info['description'],
                        key=f"hydrologic_{param_key}"
                    )
                    st.session_state.parameters["hydrologic"][param_key] = value
            
            with param_tab3:
                st.markdown("**Faktor Iklim**")
                for param_key, param_info in AGRICULTURAL_PARAMETERS["atmospheric"].items():
                    value = st.number_input(
                        f"{param_info['name']} ({param_info['unit']})",
                        min_value=param_info['min_val'],
                        max_value=param_info['max_val'],
                        value=st.session_state.parameters["atmospheric"].get(param_key, param_info['default']),
                        help=param_info['description'],
                        key=f"atmospheric_{param_key}"
                    )
                    st.session_state.parameters["atmospheric"][param_key] = value
        
        st.markdown("### Pencarian Pengetahuan")
        search_query = st.text_input("Cari topik pertanian:")
        if search_query:
            results = search_knowledge_base(search_query)
            if results:
                st.markdown("#### Hasil Basis Pengetahuan:")
                for result in results[:3]:  # Show top 3 results
                    with st.expander(f"{result['category']} - {result['item']}"):
                        st.write(result['info'])
            else:
                st.info("Tidak ada hasil yang ditemukan dalam basis pengetahuan.")
        
        st.markdown("### 🎯 Topik Analisis Ahli")
        st.markdown("*Dapatkan prakiraan terstruktur, wawasan AI, dan rekomendasi pemecahan masalah*")
        
        indonesian_topic_buttons = [
            "Pemulihan sawah setelah banjir",
            "Penanganan wereng pada padi", 
            "Strategi mitigasi dampak kekeringan",
            "Remediasi kontaminasi pestisida",
            "Pencegahan dan pemulihan penyakit ternak",
            "Penilaian dan pemulihan kerusakan akibat banjir",
            "Timeline koreksi defisiensi nutrisi tanah",
            "Perencanaan adaptasi perubahan iklim"
        ]
        
        for topic in indonesian_topic_buttons:
            if st.button(topic, key=f"topic_{topic}"):
                st.session_state.messages.append({
                    "role": "user",
                    "content": topic,
                    "timestamp": datetime.now()
                })
                # Use parameters if enabled
                parameters = st.session_state.parameters if st.session_state.use_parameters else None
                crop_type = st.session_state.crop_type if st.session_state.use_parameters else "general"
                
                response = get_ai_response(
                    client, 
                    st.session_state.user_role, 
                    topic, 
                    st.session_state.location,
                    parameters,
                    crop_type
                )
                st.session_state.messages.append({
                    "role": "assistant", 
                    "content": response,
                    "timestamp": datetime.now()
                })
                st.rerun()
        
        if st.button("Hapus Riwayat Chat"):
            st.session_state.messages = []
            st.rerun()
        
        st.markdown("### 💡 Contoh Pertanyaan")
        st.markdown("Coba tanyakan tentang skenario spesifik:")
        indonesian_example_questions = [
            "Sawah padi saya terkena blast. Berapa lama waktu pemulihan?",
            "Tanaman cabai menunjukkan gejala antraknosa. Apa rencana pemulihan?", 
            "Sapi saya menunjukkan tanda-tanda penyakit pernapasan. Timeline pemulihan?",
            "pH tanah turun menjadi 4.5 setelah hujan asam. Langkah remediasi?",
            "Sistem irigasi gagal saat musim kemarau. Strategi pemulihan?"
        ]
        
        for i, question in enumerate(indonesian_example_questions[:3]):
            if st.button(f"📝 {question[:40]}...", key=f"example_{i}"):
                st.session_state.messages.append({
                    "role": "user",
                    "content": question,
                    "timestamp": datetime.now()
                })
                # Use parameters if enabled
                parameters = st.session_state.parameters if st.session_state.use_parameters else None
                crop_type = st.session_state.crop_type if st.session_state.use_parameters else "general"
                
                response = get_ai_response(
                    client, 
                    st.session_state.user_role, 
                    question, 
                    st.session_state.location,
                    parameters,
                    crop_type
                )
                st.session_state.messages.append({
                    "role": "assistant", 
                    "content": response,
                    "timestamp": datetime.now()
                })
                st.rerun()
    
    # Main content area
    st.title("🌾 Asisten Pertanian Ahli Indonesia")
    st.markdown(f"**Peran Saat Ini:** {st.session_state.user_role}")
    if st.session_state.location:
        st.markdown(f"**Lokasi:** {st.session_state.location}")
    
    # Parameter status display
    if st.session_state.use_parameters:
        st.markdown(f"**📊 Parameter Analysis:** Aktif (Tanaman: {st.session_state.crop_type.title()})")
        
        # Show parameter analysis summary
        parameter_analysis = analyze_parameters(st.session_state.parameters, st.session_state.crop_type)
        
        col1, col2, col3 = st.columns(3)
        with col1:
            status_color = "🟢" if parameter_analysis["edaphic"]["status"] == "optimal" else "🟡"
            st.markdown(f"{status_color} **Edafik:** {parameter_analysis['edaphic']['status'].title()}")
        with col2:
            status_color = "🟢" if parameter_analysis["hydrologic"]["status"] == "optimal" else "🟡"
            st.markdown(f"{status_color} **Hidrologik:** {parameter_analysis['hydrologic']['status'].title()}")
        with col3:
            status_color = "🟢" if parameter_analysis["atmospheric"]["status"] == "optimal" else "🟡"
            st.markdown(f"{status_color} **Atmosferik:** {parameter_analysis['atmospheric']['status'].title()}")
    else:
        st.markdown("**📊 Parameter Analysis:** Tidak aktif (Gunakan analisis umum)")
    
    # Information about structured responses
    with st.expander("ℹ️ Cara Kerja Chatbot Ini", expanded=False):
        st.markdown("""
        Asisten pertanian cerdas ini memberikan **analisis ahli terstruktur** dengan tiga bagian utama:
        
        🔮 **Forecasting Recovery** - Prediksi timeline pemulihan dan langkah remediasi untuk kerusakan pertanian
        
        🤖 **LLM Suggestion** - Wawasan berbasis data menggunakan penalaran ilmiah dan contoh dunia nyata
        
        🔧 **Problem-Solving Recommendations** - Solusi berdasarkan:
        - **Edafik** (kesehatan tanah, kesuburan, pH, jenis tanah Indonesia)
        - **Hidrologik** (irigasi, drainase, kualitas air, sistem monsun)  
        - **Atmosferik** (iklim tropis, pola cuaca, adaptasi musiman)
        
        **📊 Parameter Input:** Aktifkan input parameter untuk mendapatkan analisis yang lebih spesifik berdasarkan kondisi lapangan aktual Anda.
        
        **Khusus untuk kondisi pertanian Indonesia** dengan pengetahuan tentang tanaman lokal, teknik pertanian tradisional, dan iklim tropis.
        """)
    
    st.markdown("💬 **Tanyakan tentang tantangan pertanian, skenario pemulihan, atau masalah teknis!**")
    
    # Display chat messages
    chat_container = st.container()
    with chat_container:
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.write(message["content"])
                if "timestamp" in message:
                    st.caption(f"_{message['timestamp'].strftime('%Y-%m-%d %H:%M:%S')}_")
    
    # Chat input
    if prompt := st.chat_input("Tanyakan pertanyaan pertanian Anda..."):
        # Add user message
        st.session_state.messages.append({
            "role": "user",
            "content": prompt,
            "timestamp": datetime.now()
        })
        
        # Display user message
        with st.chat_message("user"):
            st.write(prompt)
            st.caption(f"_{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}_")
        
        # Get and display AI response
        with st.chat_message("assistant"):
            with st.spinner("Berpikir..."):
                # Use parameters if enabled
                parameters = st.session_state.parameters if st.session_state.use_parameters else None
                crop_type = st.session_state.crop_type if st.session_state.use_parameters else "general"
                
                response = get_ai_response(
                    client, 
                    st.session_state.user_role, 
                    prompt, 
                    st.session_state.location,
                    parameters,
                    crop_type
                )
            st.write(response)
            response_time = datetime.now()
            st.caption(f"_{response_time.strftime('%Y-%m-%d %H:%M:%S')}_")
            
            # Add assistant response to session state
            st.session_state.messages.append({
                "role": "assistant",
                "content": response,
                "timestamp": response_time
            })
    
    # Footer with Indonesian agricultural tips
    st.markdown("---")
    with st.expander("💡 Tips Pertanian Indonesia"):
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("**🌱 Perawatan Tanaman**")
            st.markdown("• Cek kelembaban tanah secara rutin")
            st.markdown("• Rotasi tanaman setiap musim")
            st.markdown("• Monitor hama dan penyakit harian")
            st.markdown("• Gunakan varietas lokal yang adaptif")
        
        with col2:
            st.markdown("**🐄 Perawatan Ternak**")
            st.markdown("• Sediakan air bersih setiap hari")
            st.markdown("• Jaga kebersihan kandang")
            st.markdown("• Ikuti jadwal vaksinasi")
            st.markdown("• Pakan hijauan lokal berkualitas")
        
        with col3:
            st.markdown("**💰 Tips Bisnis**")
            st.markdown("• Catat pengeluaran dengan teliti")
            st.markdown("• Pantau harga pasar regional")
            st.markdown("• Rencanakan untuk perubahan musiman")
            st.markdown("• Manfaatkan teknologi digital")

if __name__ == "__main__":
    main()
