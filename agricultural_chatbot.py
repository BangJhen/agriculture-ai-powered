import streamlit as st
import json
import os
from datetime import datetime
from openai import OpenAI
from dotenv import load_dotenv
# Import West Java crop analysis functionality
from west_java_crop_analysis import WestJavaCropAnalyzer, generate_comprehensive_report, get_traditional_practices_and_risks

# Load environment variables from .env file
load_dotenv()

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
    "Petani Konservasi": "Praktisi pertanian yang memperhatikan keberlanjutan lingkungan dan produktivitas",
    "Penyuluh Pertanian Lapangan": "Pendamping petani dalam praktik pertanian berkelanjutan dan konservasi", 
    "Konsultan Pertanian Berkelanjutan": "Ahli sistem pertanian ramah lingkungan dan efisien secara ekonomi",
    "Agroekolog": "Peneliti hubungan antara pertanian, ekologi, dan masyarakat lokal",
    "Spesialis Konservasi Tanah & Air": "Ahli intervensi berbasis ekosistem untuk wilayah rawan erosi dan kekeringan",
    "Fasilitator Agroforestri Komunitas": "Pendamping pengembangan sistem wanatani di daerah rawan deforestasi",
    "Ahli Iklim Pertanian": "Spesialis mitigasi dan adaptasi dampak perubahan iklim pada pertanian"
}

# Sustainable agriculture and conservation knowledge base for Indonesia
SUSTAINABLE_AGRICULTURE_KNOWLEDGE = {
    "agroecological_methods": {
        "tumpangsari": {
            "description": "Sistem tanam campuran untuk meningkatkan keanekaragaman hayati dan efisiensi lahan",
            "crops": ["padi-ikan", "jagung-kacang", "kelapa-kakao", "kopi-pisang"],
            "benefits": ["stabilitas hasil", "pengendalian hama alami", "kesuburan tanah", "diversifikasi pendapatan"]
        },
        "agroforestry_wanatani": {
            "description": "Integrasi pohon dengan tanaman pertanian untuk konservasi dan produktivitas",
            "systems": ["talun", "kebun campuran", "silvopastura", "alley cropping"],
            "tree_species": ["albasia", "mahoni", "sengon", "petai", "durian", "kemiri"]
        },
        "sri_system": {
            "description": "System of Rice Intensification untuk meningkatkan produktivitas dengan input minimal",
            "techniques": ["tanam muda", "jarak tanam lebar", "irigasi berselang", "penyiangan mekanis"],
            "benefits": ["hemat air 50%", "hemat benih 90%", "produktivitas naik 20-50%"]
        },
        "bioorganic_inputs": {
            "pupuk_hayati": ["rhizobium", "mikoriza", "azotobacter", "pseudomonas"],
            "pestisida_nabati": ["neem", "mimba", "tembakau", "serai wangi", "daun pepaya"],
            "kompos_organik": ["bokashi", "kascing", "kompos jerami", "pupuk kandang fermentasi"]
        }
    },
    "environmental_conservation": {
        "soil_conservation": {
            "terasering": "Pembuatan teras untuk mencegah erosi di lahan miring",
            "vetiver_grass": "Penanaman rumput vetiver sebagai penguat lereng dan filter sedimen",
            "cover_crops": "Tanaman penutup tanah seperti legum untuk mencegah erosi",
            "mulching": "Penutupan permukaan tanah dengan bahan organik"
        },
        "water_conservation": {
            "embung": "Kolam penampungan air hujan untuk irigasi saat kemarau",
            "drainase_mikro": "Sistem drainase kecil untuk mengatur aliran air",
            "biopori": "Lubang resapan untuk meningkatkan infiltrasi air",
            "rain_harvesting": "Penampungan air hujan dari atap dan permukaan"
        },
        "biodiversity_protection": {
            "refuge_areas": "Area perlindungan untuk musuh alami hama",
            "flower_strips": "Jalur bunga untuk mendukung penyerbuk",
            "native_species": "Pemanfaatan spesies lokal yang adaptif",
            "corridor_planting": "Penanaman koridor untuk konektivitas habitat"
        }
    },
    "climate_adaptation": {
        "drought_management": {
            "varietas_tahan": ["padi gogo", "jagung hibrida", "ubi jalar ungu"],
            "water_efficient": ["irigasi tetes", "mulsa plastik", "hidroponik"],
            "scheduling": "Penyesuaian waktu tanam dengan pola hujan"
        },
        "flood_management": {
            "early_warning": "Sistem peringatan dini banjir",
            "drainage_systems": "Sistem drainase yang memadai",
            "flood_resistant": "Varietas tahan genangan air"
        },
        "pest_climate_adaptation": {
            "ipm_approach": "Pengendalian hama terpadu berbasis ekosistem",
            "beneficial_insects": "Pemanfaatan serangga berguna",
            "trap_crops": "Tanaman perangkap untuk mengendalikan hama"
        }
    },
    "regional_solutions": {
        "jawa": {
            "challenges": ["konversi lahan", "degradasi tanah", "pencemaran air"],
            "solutions": ["urban farming", "hidroponik vertikal", "bioremediasi"]
        },
        "sumatera": {
            "challenges": ["deforestasi", "kebakaran lahan", "erosi gambut"],
            "solutions": ["agroforestri karet", "rewetting gambut", "fire prevention"]
        },
        "kalimantan": {
            "challenges": ["alih fungsi lahan", "pencemaran tambang", "banjir"],
            "solutions": ["agroforestri komunitas", "fitoremediasi", "early warning system"]
        },
        "sulawesi": {
            "challenges": ["erosi lereng", "kekeringan", "salinitas"],
            "solutions": ["terasering", "konservasi air", "toleran salin"]
        },
        "nusa_tenggara": {
            "challenges": ["kekeringan ekstrem", "tanah marginal", "angin kencang"],
            "solutions": ["agrosilvikultura", "xerophytic crops", "windbreak planting"]
        },
        "papua": {
            "challenges": ["deforestasi", "erosi tanah", "akses teknologi"],
            "solutions": ["agroforestri tradisional", "konservasi in-situ", "teknologi tepat guna"]
        }
    }
}

def initialize_openai_client():
    """Initialize OpenAI client with OpenRouter using environment variables"""
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

def get_role_specific_prompt(user_role, question, location=""):
    """Generate sustainable agriculture role prompts with environmental conservation focus"""
    role_contexts = {
        "Petani Konservasi": "Anda adalah konsultan pertanian berkelanjutan yang membantu petani Indonesia menerapkan praktik agroekologi. Fokus pada metode ramah lingkungan seperti tumpangsari, agroforestri, pupuk hayati, dan konservasi tanah-air.",
        
        "Penyuluh Pertanian Lapangan": "Anda adalah penyuluh lapangan yang mendampingi petani dalam praktik pertanian berkelanjutan. Fokus pada edukasi konservasi lingkungan, transfer teknologi ramah lingkungan, dan pemberdayaan masyarakat petani.",
        
        "Konsultan Pertanian Berkelanjutan": "Anda adalah ahli sistem pertanian berkelanjutan yang merancang solusi ramah lingkungan dan efisien ekonomi. Fokus pada sistem terintegrasi, analisis keberlanjutan, dan strategi mitigasi risiko lingkungan.",
        
        "Agroekolog": "Anda adalah peneliti dan praktisi agroekologi yang memahami hubungan kompleks antara pertanian, ekologi, dan masyarakat lokal Indonesia. Fokus pada pendekatan holistik berbasis ekosistem.",
        
        "Spesialis Konservasi Tanah & Air": "Anda adalah ahli konservasi yang bekerja di wilayah rawan erosi, longsor, dan kekeringan. Fokus pada intervensi berbasis ekosistem seperti terasering, embung, dan bioremediasi.",
        
        "Fasilitator Agroforestri Komunitas": "Anda adalah pendamping masyarakat dalam pengembangan sistem wanatani di daerah rawan deforestasi. Fokus pada integrasi pohon-tanaman, konservasi biodiversitas, dan ekonomi berkelanjutan.",
        
        "Ahli Iklim Pertanian": "Anda adalah spesialis adaptasi dan mitigasi perubahan iklim di sektor pertanian. Fokus pada strategi climate-smart agriculture, early warning system, dan resiliensi ekosistem."
    }
    
    base_prompt = role_contexts.get(user_role, role_contexts["Konsultan Pertanian Berkelanjutan"])
    
    # Enhanced structured response format for sustainable agriculture
    structured_format = f"""
    
    Anda adalah AI asisten untuk mendukung profesional yang bekerja dalam pertanian berkelanjutan dan konservasi lingkungan di Indonesia.
    
    **Respons Anda HARUS selalu mencerminkan:**
    - Metode agroekologi yang relevan untuk iklim dan bentang lahan Indonesia
    - Risiko lingkungan seperti degradasi lahan, limpasan pestisida, deforestasi, dan kelangkaan air
    - Solusi ekologi spesifik Indonesia: tumpangsari, agroforestri (wanatani), pupuk hayati, SRI, drainase mikro, sistem lahan basah

    **Respons Anda HARUS mencakup tepat tiga bagian berikut:**

    ## 1. 🔮 Forecasting Recovery (Prakiraan Pemulihan)
    Estimasi waktu dan upaya yang diperlukan untuk memulihkan keseimbangan pertanian dan ekologi setelah gangguan lingkungan:
    - Timeline pemulihan spesifik dengan pertimbangan ekosistem lokal
    - Solusi tradisional dan modern Indonesia (terasering, embung, kompos organik, vetiver grass)
    - Langkah remediasi berbasis konservasi dan keberlanjutan
    - Biaya dan sumber daya yang diperlukan untuk pemulihan ekologis

    ## 2. 🤖 LLM-Based Suggestions (Saran Berbasis LLM)
    Wawasan dan saran dari basis pengetahuan LLM yang disesuaikan dengan konteks lingkungan dan agroklimat Indonesia:
    - Pendekatan agroekologi yang sesuai dengan kondisi lokal
    - Contoh praktik terbaik dari daerah dengan kondisi serupa di Indonesia
    - Integrasi pengetahuan ilmiah dengan kearifan lokal
    - Strategi jangka panjang untuk keberlanjutan

    ## 3. 🔧 Sustainable Problem-Solving (Pemecahan Masalah Berkelanjutan)
    Solusi detail dan dapat ditindaklanjuti berdasarkan:
    
    **Kesehatan Tanah (Edafik):**
    - Kekayaan mikroba tanah dan biodiversitas
    - Pengelolaan bahan organik dan struktur tanah
    - Pencegahan erosi dengan metode konservasi
    - Bioremediasi untuk tanah terdegradasi
    
    **Sistem Air (Hidrologik):**
    - Konservasi air dan pengelolaan DAS (Daerah Aliran Sungai)
    - Manajemen air berkelanjutan dan efisiensi irigasi
    - Teknologi hemat air dan rain water harvesting
    - Pencegahan pencemaran air dari aktivitas pertanian
    
    **Faktor Iklim (Atmosferik):**
    - Adaptasi terhadap variabilitas iklim dan perubahan cuaca
    - Persiapan menghadapi intensitas hujan dan musim kering
    - Strategi mitigasi emisi karbon dari pertanian
    - Pemanfaatan early warning system untuk cuaca ekstrem

    **Konteks:**
    - Peran Pengguna: {user_role}
    - Lokasi: {location if location else "Indonesia"}
    - Basis Pengetahuan Agroekologi: Tumpangsari, Agroforestri, SRI, Konservasi Tanah-Air, Pupuk Hayati
    - Masalah/Pertanyaan: {question}
    
    Gunakan Bahasa Indonesia dan berikan contoh spesifik regional bila memungkinkan.
    Sesuaikan nada dan tingkat teknis berdasarkan peran profesional yang dipilih.
    Fokus pada solusi praktis, berkelanjutan, dan ramah lingkungan dengan timeline yang jelas.
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
            model=os.getenv('OPENROUTER_MODEL', 'mistralai/mistral-tiny'),
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

def display_crop_analysis_dashboard():
    """Display comprehensive crop analysis dashboard"""
    st.markdown("## 🗺️ Dashboard Analisis Kesesuaian Tanaman Jawa Barat")
    
    try:
        analyzer = st.session_state.crop_analyzer
        
        # Generate analysis for both crops
        corn_results = analyzer.analyze_all_regions("corn")
        cassava_results = analyzer.analyze_all_regions("cassava")
        
        # Summary statistics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("📊 Total Wilayah", len(analyzer.west_java_regions))
        
        with col2:
            corn_suitable = len([r for r in corn_results if r["overall_score"] >= 0.6])
            st.metric("🌽 Wilayah Cocok Jagung", corn_suitable)
        
        with col3:
            cassava_suitable = len([r for r in cassava_results if r["overall_score"] >= 0.6])
            st.metric("🥔 Wilayah Cocok Singkong", cassava_suitable)
        
        with col4:
            both_suitable = len([r for r in corn_results if r["overall_score"] >= 0.6 and 
                               any(c["region"] == r["region"] and c["overall_score"] >= 0.6 for c in cassava_results)])
            st.metric("🌟 Cocok Keduanya", both_suitable)
        
        # Top regions for each crop
        st.markdown("### 🏆 Wilayah Terbaik")
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### 🌽 Top 5 Wilayah untuk Jagung")
            for i, result in enumerate(corn_results[:5]):
                score_color = "🟢" if result["overall_score"] >= 0.8 else "🟡" if result["overall_score"] >= 0.6 else "🟠"
                st.markdown(f"{i+1}. {score_color} **{result['region']}** - {result['overall_score']:.3f} ({result['suitability_class']})")
        
        with col2:
            st.markdown("#### 🥔 Top 5 Wilayah untuk Singkong")
            for i, result in enumerate(cassava_results[:5]):
                score_color = "🟢" if result["overall_score"] >= 0.8 else "🟡" if result["overall_score"] >= 0.6 else "🟠"
                st.markdown(f"{i+1}. {score_color} **{result['region']}** - {result['overall_score']:.3f} ({result['suitability_class']})")
        
        # Detailed comparison table
        st.markdown("### 📋 Tabel Perbandingan Lengkap")
        
        # Create comparison dataframe
        import pandas as pd
        comparison_data = []
        
        for corn_result in corn_results:
            cassava_result = next((c for c in cassava_results if c["region"] == corn_result["region"]), None)
            if cassava_result:
                comparison_data.append({
                    "Wilayah": corn_result["region"],
                    "Skor Jagung": corn_result["overall_score"],
                    "Kelas Jagung": corn_result["suitability_class"],
                    "Skor Singkong": cassava_result["overall_score"],
                    "Kelas Singkong": cassava_result["suitability_class"],
                    "Ketinggian": corn_result["region_characteristics"]["altitude"],
                    "Curah Hujan": corn_result["region_characteristics"]["annual_rainfall"],
                    "Jenis Tanah": corn_result["region_characteristics"]["soil_type"]
                })
        
        df = pd.DataFrame(comparison_data)
        st.dataframe(df, use_container_width=True)
        
    except Exception as e:
        st.error(f"Error dalam analisis: {str(e)}")

def display_single_crop_analysis(crop_type, selected_region):
    """Display analysis for a single crop"""
    st.markdown(f"## {'🌽 Analisis Kesesuaian Jagung' if crop_type == 'corn' else '🥔 Analisis Kesesuaian Singkong'}")
    
    try:
        analyzer = st.session_state.crop_analyzer
        
        if selected_region == "Semua Wilayah":
            # Show all regions analysis
            results = analyzer.analyze_all_regions(crop_type)
            
            # Display crop requirements
            crop_summary = analyzer.get_crop_summary(crop_type)
            
            with st.expander("📋 Persyaratan Tumbuh", expanded=True):
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.markdown("**🌱 Faktor Edafik (Tanah)**")
                    req = crop_summary["requirements_summary"]["edaphic"]
                    st.markdown(f"• pH: {req['ph_range']}")
                    st.markdown(f"• Bahan Organik: {req['organic_matter']}")
                    st.markdown(f"• Drainase: {req['drainage']}")
                    st.markdown(f"• Jenis Tanah: {', '.join(req['soil_types'])}")
                
                with col2:
                    st.markdown("**💧 Faktor Hidrologik (Air)**")
                    req = crop_summary["requirements_summary"]["hydrologic"]
                    st.markdown(f"• Curah Hujan: {req['annual_rainfall']}")
                    st.markdown(f"• Kedalaman Air Tanah: {req['water_table']}")
                    st.markdown(f"• Toleransi Kekeringan: {req['drought_tolerance']}")
                
                with col3:
                    st.markdown("**🌤️ Faktor Atmosferik (Iklim)**")
                    req = crop_summary["requirements_summary"]["atmospheric"]
                    st.markdown(f"• Suhu: {req['temperature']}")
                    st.markdown(f"• Suhu Optimal: {req['optimal_temperature']}")
                    st.markdown(f"• Kelembaban: {req['humidity']}")
                    st.markdown(f"• Ketinggian: {req['altitude']}")
            
            # Display results
            st.markdown("### 🎯 Hasil Analisis Kesesuaian")
            
            for result in results:
                score_color = "🟢" if result["overall_score"] >= 0.8 else "🟡" if result["overall_score"] >= 0.6 else "🟠" if result["overall_score"] >= 0.4 else "🔴"
                
                with st.expander(f"{score_color} {result['region']} - {result['suitability_class']} ({result['overall_score']:.3f})"):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.markdown("**📊 Skor Kategori:**")
                        st.markdown(f"• Edafik: {result['category_scores']['edaphic']:.3f}")
                        st.markdown(f"• Hidrologik: {result['category_scores']['hydrologic']:.3f}")
                        st.markdown(f"• Atmosferik: {result['category_scores']['atmospheric']:.3f}")
                    
                    with col2:
                        st.markdown("**🌍 Karakteristik Wilayah:**")
                        char = result["region_characteristics"]
                        st.markdown(f"• Ketinggian: {char['altitude']} m")
                        st.markdown(f"• Curah Hujan: {char['annual_rainfall']} mm/tahun")
                        st.markdown(f"• Suhu: {char['temperature_range'][0]}-{char['temperature_range'][1]}°C")
                        st.markdown(f"• Jenis Tanah: {char['soil_type']}")
        
        else:
            # Show specific region analysis
            result = analyzer.evaluate_regional_suitability(crop_type, selected_region)
            
            # Display result with detailed breakdown
            score_color = "🟢" if result["overall_score"] >= 0.8 else "🟡" if result["overall_score"] >= 0.6 else "🟠" if result["overall_score"] >= 0.4 else "🔴"
            
            st.markdown(f"### {score_color} {result['region']} - {result['suitability_class']}")
            st.markdown(f"**Skor Keseluruhan: {result['overall_score']:.3f}**")
            
            # Progress bars for category scores
            col1, col2, col3 = st.columns(3)
            with col1:
                st.markdown("**🌱 Edafik**")
                st.progress(result['category_scores']['edaphic'])
                st.markdown(f"{result['category_scores']['edaphic']:.3f}")
            
            with col2:
                st.markdown("**💧 Hidrologik**")
                st.progress(result['category_scores']['hydrologic'])
                st.markdown(f"{result['category_scores']['hydrologic']:.3f}")
            
            with col3:
                st.markdown("**🌤️ Atmosferik**")
                st.progress(result['category_scores']['atmospheric'])
                st.markdown(f"{result['category_scores']['atmospheric']:.3f}")
            
            # Regional characteristics
            st.markdown("### 🌍 Karakteristik Wilayah")
            char = result["region_characteristics"]
            
            col1, col2 = st.columns(2)
            with col1:
                st.markdown(f"**Koordinat:** {char['coordinates']}")
                st.markdown(f"**Ketinggian:** {char['altitude']} meter")
                st.markdown(f"**Zona Iklim:** {char['climate_zone']}")
                st.markdown(f"**Curah Hujan:** {char['annual_rainfall']} mm/tahun")
            
            with col2:
                st.markdown(f"**Rentang Suhu:** {char['temperature_range'][0]}-{char['temperature_range'][1]}°C")
                st.markdown(f"**Jenis Tanah:** {char['soil_type']}")
                st.markdown(f"**Akses Irigasi:** {char['irrigation']}")
                st.markdown(f"**Risiko Banjir:** {char['flood_risk']}")
            
            # Traditional practices and risks
            practices_risks = get_traditional_practices_and_risks()
            crop_practices = practices_risks.get(crop_type, {}).get("traditional_practices", {})
            
            for practice_type, practice_data in crop_practices.items():
                if selected_region in practice_data.get("regions", []):
                    st.markdown(f"### 🌾 Praktik Tradisional ({practice_type.replace('_', ' ').title()})")
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        st.markdown("**Praktik Budidaya:**")
                        for practice in practice_data.get("practices", []):
                            st.markdown(f"• {practice}")
                    
                    with col2:
                        st.markdown("**Risiko Hama & Penyakit:**")
                        for risk in practice_data.get("pest_risks", []):
                            st.markdown(f"• {risk}")
                    
                    st.markdown("**Ancaman Iklim:**")
                    for threat in practice_data.get("climate_threats", []):
                        st.markdown(f"• {threat}")
    
    except Exception as e:
        st.error(f"Error dalam analisis: {str(e)}")

def display_crop_comparison():
    """Display comparison between corn and cassava suitability"""
    st.markdown("## ⚖️ Perbandingan Kesesuaian Jagung vs Singkong")
    
    try:
        analyzer = st.session_state.crop_analyzer
        
        corn_results = analyzer.analyze_all_regions("corn")
        cassava_results = analyzer.analyze_all_regions("cassava")
        
        # Create side-by-side comparison
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### 🌽 Jagung (Zea mays)")
            corn_summary = analyzer.get_crop_summary("corn")
            
            st.markdown("**Keunggulan:**")
            st.markdown("• Produktivitas tinggi di tanah subur")
            st.markdown("• Pasar yang besar dan stabil")
            st.markdown("• Teknologi budidaya sudah maju")
            st.markdown("• Dapat digunakan untuk pakan dan pangan")
            
            st.markdown("**Tantangan:**")
            st.markdown("• Memerlukan input nutrisi tinggi")
            st.markdown("• Rentan terhadap hama penggerek")
            st.markdown("• Membutuhkan irigasi yang baik")
            
            avg_corn_score = sum(r["overall_score"] for r in corn_results) / len(corn_results)
            st.metric("Rata-rata Skor Kesesuaian", f"{avg_corn_score:.3f}")
        
        with col2:
            st.markdown("### 🥔 Singkong (Manihot esculenta)")
            cassava_summary = analyzer.get_crop_summary("cassava")
            
            st.markdown("**Keunggulan:**")
            st.markdown("• Toleran kekeringan tinggi")
            st.markdown("• Dapat tumbuh di lahan marginal")
            st.markdown("• Input rendah, pemeliharaan mudah")
            st.markdown("• Sumber karbohidrat penting")
            
            st.markdown("**Tantangan:**")
            st.markdown("• Harga pasar relatif rendah")
            st.markdown("• Proses pengolahan lebih kompleks")
            st.markdown("• Umur panen lebih lama")
            
            avg_cassava_score = sum(r["overall_score"] for r in cassava_results) / len(cassava_results)
            st.metric("Rata-rata Skor Kesesuaian", f"{avg_cassava_score:.3f}")
        
        # Regional comparison chart
        st.markdown("### 📊 Perbandingan per Wilayah")
        
        import pandas as pd
        
        comparison_data = []
        for corn_result in corn_results:
            cassava_result = next((c for c in cassava_results if c["region"] == corn_result["region"]), None)
            if cassava_result:
                comparison_data.append({
                    "region": corn_result["region"],
                    "corn_score": corn_result["overall_score"],
                    "cassava_score": cassava_result["overall_score"],
                    "difference": cassava_result["overall_score"] - corn_result["overall_score"]
                })
        
        df = pd.DataFrame(comparison_data)
        
        # Display as bar chart using Streamlit's built-in charting
        chart_data = df.set_index('region')[['corn_score', 'cassava_score']]
        chart_data.columns = ['Jagung', 'Singkong']
        st.bar_chart(chart_data)
        
        # Recommendations based on comparison
        st.markdown("### 💡 Rekomendasi Regional")
        
        for data in comparison_data:
            region = data["region"]
            corn_score = data["corn_score"]
            cassava_score = data["cassava_score"]
            diff = data["difference"]
            
            if abs(diff) < 0.1:
                recommendation = "🟡 Kedua tanaman cocok - pilih berdasarkan aspek ekonomi"
            elif diff > 0.1:
                recommendation = "🥔 Singkong lebih cocok untuk wilayah ini"
            else:
                recommendation = "🌽 Jagung lebih cocok untuk wilayah ini"
            
            st.markdown(f"**{region}**: {recommendation} (Selisih: {diff:+.3f})")
    
    except Exception as e:
        st.error(f"Error dalam perbandingan: {str(e)}")

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
        st.session_state.user_role = list(USER_ROLES.keys())[0]  # Use first role in the list
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
            index=list(USER_ROLES.keys()).index(st.session_state.user_role) if st.session_state.user_role in USER_ROLES else 0
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
        
        # West Java Crop Suitability Analysis
        st.markdown("### 🗺️ Analisis Kesesuaian Tanaman Jawa Barat")
        st.markdown("*Evaluasi potensi tanam jagung dan singkong berdasarkan kondisi edafik, hidrologik, dan atmosferik*")
        
        # Initialize West Java analyzer session state
        if 'show_crop_analysis' not in st.session_state:
            st.session_state.show_crop_analysis = False
        if 'crop_analyzer' not in st.session_state:
            st.session_state.crop_analyzer = WestJavaCropAnalyzer()
        
        crop_analysis_tab = st.radio(
            "Pilih Analisis:",
            ["📊 Dashboard", "🌽 Jagung", "🥔 Singkong", "📈 Perbandingan"],
            horizontal=True
        )
        
        if crop_analysis_tab == "📊 Dashboard":
            if st.button("📋 Lihat Ringkasan Lengkap", key="crop_dashboard"):
                st.session_state.show_crop_analysis = True
                st.session_state.crop_analysis_type = "dashboard"
        
        elif crop_analysis_tab == "🌽 Jagung":
            selected_region = st.selectbox(
                "Pilih Kabupaten/Kota:",
                ["Semua Wilayah"] + list(st.session_state.crop_analyzer.west_java_regions.keys()),
                key="corn_region"
            )
            
            if st.button("🔍 Analisis Kesesuaian Jagung", key="analyze_corn"):
                st.session_state.show_crop_analysis = True
                st.session_state.crop_analysis_type = "corn"
                st.session_state.selected_region = selected_region
        
        elif crop_analysis_tab == "🥔 Singkong":
            selected_region = st.selectbox(
                "Pilih Kabupaten/Kota:",
                ["Semua Wilayah"] + list(st.session_state.crop_analyzer.west_java_regions.keys()),
                key="cassava_region"
            )
            
            if st.button("🔍 Analisis Kesesuaian Singkong", key="analyze_cassava"):
                st.session_state.show_crop_analysis = True
                st.session_state.crop_analysis_type = "cassava"
                st.session_state.selected_region = selected_region
        
        elif crop_analysis_tab == "📈 Perbandingan":
            if st.button("⚖️ Bandingkan Kedua Tanaman", key="compare_crops"):
                st.session_state.show_crop_analysis = True
                st.session_state.crop_analysis_type = "comparison"
        
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
    
    # Display West Java Crop Analysis if requested
    if st.session_state.get('show_crop_analysis', False):
        analysis_type = st.session_state.get('crop_analysis_type', 'dashboard')
        
        if analysis_type == "dashboard":
            display_crop_analysis_dashboard()
        elif analysis_type == "corn":
            display_single_crop_analysis("corn", st.session_state.get('selected_region', 'Semua Wilayah'))
        elif analysis_type == "cassava":
            display_single_crop_analysis("cassava", st.session_state.get('selected_region', 'Semua Wilayah'))
        elif analysis_type == "comparison":
            display_crop_comparison()
        
        # Add button to close analysis
        if st.button("❌ Tutup Analisis Tanaman", key="close_analysis"):
            st.session_state.show_crop_analysis = False
            st.rerun()
        
        st.markdown("---")
    
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
