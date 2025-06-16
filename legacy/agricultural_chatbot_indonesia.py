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

def get_ai_response(client, user_role, question, location=""):
    """Get AI response based on user role and question for Indonesian context"""
    try:
        prompt = get_role_specific_prompt(user_role, question, location)
        
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
            max_tokens=1500
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
                response = get_ai_response(client, st.session_state.user_role, topic, st.session_state.location)
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
                response = get_ai_response(client, st.session_state.user_role, question, st.session_state.location)
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
                response = get_ai_response(client, st.session_state.user_role, prompt, st.session_state.location)
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
