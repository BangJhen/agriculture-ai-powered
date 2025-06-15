# Dokumentasi Asisten Pertanian Indonesia 🌾

## Gambaran Umum

Asisten Pertanian Indonesia adalah chatbot cerdas yang dirancang khusus untuk mendukung profesional pertanian di Indonesia. Sistem ini menggunakan teknologi AI untuk memberikan analisis ahli yang terstruktur dengan mempertimbangkan kondisi iklim tropis, praktik pertanian lokal, dan karakteristik unik pertanian Indonesia.

## Keunggulan Sistem

### 🎯 Spesialisasi Indonesia
- **Tanaman Lokal**: Padi, jagung, cabai, kelapa sawit, kakao, kopi, pisang, singkong
- **Teknik Tradisional**: Jajar legowo, tumpangsari, integrated farming
- **Jenis Tanah**: Andosol, latosol, regosol, alluvial
- **Sistem Irigasi**: Teknis, tadah hujan, pasang surut, tetes
- **Iklim Tropis**: Adaptasi musim hujan dan kemarau

### 🔬 Format Respons 3-Bagian dengan Parameter
1. **Forecasting Recovery**: Prakiraan pemulihan dengan timeline spesifik berdasarkan kondisi lapangan
2. **LLM Suggestion**: Wawasan AI berbasis penalaran ilmiah dengan data parameter
3. **Problem-Solving**: Rekomendasi berdasarkan faktor edafik, hidrologik, atmosferik

### 📊 **Input Parameter Lapangan Baru**
- **20+ Parameter Terukur**: Dari kondisi tanah, air, hingga iklim
- **Analisis Otomatis**: Status optimal/suboptimal untuk setiap parameter
- **Rekomendasi Spesifik**: Saran perbaikan berdasarkan data aktual
- **Referensi Tanaman**: Nilai optimal untuk padi, jagung, cabai
- **Interface Intuitif**: Input dengan tabs terorganisir

### 👥 6 Peran Profesional
- **Petani**: Pengelolaan tanaman dan lahan
- **Peternak**: Peternakan dan breeding
- **Spesialis Agribisnis**: Analisis bisnis dan pasar
- **Insinyur Pertanian**: Teknologi dan peralatan
- **Penyuluh Pertanian**: Pendidikan dan penyuluhan
- **Konsultan Pertanian**: Konsultasi komprehensif

## Contoh Penggunaan

### Skenario 1: Petani Padi
**Input**: "Sawah padi saya di Jawa Barat terkena serangan wereng. Bagaimana cara pemulihannya?"

**Output Terstruktur**:
- 🔮 **Forecasting Recovery**: Timeline 2-3 minggu, langkah remediasi spesifik
- 🤖 **LLM Suggestion**: Strategi IPM dan varietas tahan wereng
- 🔧 **Problem-Solving**: Analisis tanah sawah, manajemen air, kondisi iklim

### Skenario 2: Peternak Sapi
**Input**: "Sapi saya di Lampung menunjukkan gejala penyakit pernapasan. Timeline pemulihan?"

**Output Terstruktur**:
- 🔮 **Forecasting Recovery**: Estimasi 7-14 hari dengan pengobatan tepat
- 🤖 **LLM Suggestion**: Protokol kesehatan dan biosekuriti
- 🔧 **Problem-Solving**: Kondisi kandang, kualitas pakan, faktor cuaca

## Basis Pengetahuan

### Tanaman Utama Indonesia
- **Padi**: Varietas lokal, hama wereng, penyakit blast
- **Cabai**: Antraknosa, thrips, manajemen kelembaban
- **Kelapa Sawit**: Pest management, sustainable practices
- **Jagung**: Borer control, nutrient management

### Praktik Lokal
- **Jajar Legowo**: Sistem tanam padi untuk meningkatkan hasil
- **Tumpangsari**: Intercropping untuk optimalisasi lahan
- **Integrated Farming**: Kombinasi tanaman-ternak-ikan

### Kondisi Iklim
- **Musim Hujan**: Oktober-Maret, manajemen drainase
- **Musim Kemarau**: April-September, konservasi air
- **Monsun**: Adaptasi pola tanam

## Teknologi

### Platform
- **Frontend**: Streamlit dengan interface Bahasa Indonesia
- **Backend**: OpenRouter API dengan model Mistral
- **Database**: Knowledge base lokal Indonesia

### Struktur Respons
```
## 1. 🔮 Forecasting Recovery
- Timeline pemulihan
- Langkah remediasi
- Kondisi lokal Indonesia

## 2. 🤖 LLM Suggestion  
- Penalaran ilmiah
- Contoh kasus Indonesia
- Best practices lokal

## 3. 🔧 Problem-Solving Recommendations
- Faktor Edafik (tanah Indonesia)
- Faktor Hidrologik (sistem air tropis)
- Faktor Atmosferik (iklim monsun)
```

## Cara Penggunaan

1. **Pilih Peran**: Tentukan profesi pertanian Anda
2. **Set Lokasi**: Pilih provinsi untuk konteks regional
3. **Ajukan Pertanyaan**: Gunakan skenario spesifik
4. **Terima Analisis**: Dapatkan respons terstruktur 3-bagian

## Keunggulan Kompetitif

- ✅ **Konteks Indonesia**: Tidak generic, fokus pada kondisi lokal
- ✅ **Multi-Peran**: Mendukung 6 jenis profesional pertanian
- ✅ **Respons Terstruktur**: Format konsisten dan komprehensif
- ✅ **Basis Pengetahuan Lokal**: Tanaman, tanah, iklim Indonesia
- ✅ **Interface Bahasa Indonesia**: Aksesibilitas untuk petani lokal

## Roadmap Pengembangan

### Fase 1 (Saat Ini)
- ✅ Sistem respons terstruktur
- ✅ Knowledge base Indonesia
- ✅ 6 peran profesional
- ✅ Interface Bahasa Indonesia

### Fase 2 (Rencana)
- 📋 Integrasi data cuaca real-time
- 📋 Database harga komoditas
- 📋 Sistem alert hama/penyakit
- 📋 Mobile app version

### Fase 3 (Visi)
- 📋 IoT sensor integration
- 📋 Precision agriculture
- 📋 Blockchain for supply chain
- 📋 AI-powered crop monitoring

## Kontak & Support

Untuk pertanyaan teknis atau saran pengembangan, silakan buka issue di repository ini atau hubungi tim developer.

---

**Dibuat dengan ❤️ untuk kemajuan pertanian Indonesia** 🇮🇩

## Parameter Input System

### 📊 Komprehensif Parameter Coverage

#### 🌱 Edafik (Tanah) - 7 Parameter
- **NPK Content**: Nitrogen, Phosphorus, Potassium (%)
- **pH Level**: Keasaman tanah (3.0-9.0)
- **Organic Matter**: Bahan organik (%)
- **Soil Temperature**: Suhu tanah 10cm (°C)
- **Soil Density**: Bulk density (g/cm³)

#### 💧 Hidrologik (Air) - 5 Parameter  
- **Rainfall**: Curah hujan bulanan (mm)
- **Water Table**: Kedalaman air tanah (cm)
- **Drainage Rate**: Laju drainase (cm/jam)
- **Irrigation Frequency**: Frekuensi irigasi (hari)
- **Water EC**: Electrical conductivity (dS/m)

#### 🌤️ Atmosferik (Iklim) - 7 Parameter
- **Air Temperature**: Suhu udara (°C)
- **Humidity**: Kelembaban relatif (%)
- **Wind Speed**: Kecepatan angin (km/jam)
- **Solar Radiation**: Radiasi matahari (MJ/m²/hari)
- **Photoperiod**: Lama penyinaran (jam)
- **Atmospheric Pressure**: Tekanan udara (hPa)
- **CO₂ Concentration**: Konsentrasi CO₂ (ppm)

### 🎯 Intelligent Analysis

#### Crop-Specific Optimization
```python
optimal_ranges = {
    "padi": {"N": (0.15, 0.25), "pH": (5.5, 6.5)},
    "jagung": {"N": (0.12, 0.20), "pH": (6.0, 7.0)},
    "cabai": {"N": (0.20, 0.30), "pH": (6.0, 6.8)}
}
```

#### Automated Assessment
- **Status Classification**: Optimal vs Suboptimal
- **Issue Detection**: Parameter values outside optimal range
- **Specific Recommendations**: Targeted solutions for each parameter
- **Visual Indicators**: Color-coded status display

### 🔧 Implementation Features

#### Real-time Analysis
- Parameter validation and range checking
- Immediate feedback on parameter status
- Integration with AI response system
- Context-aware recommendations

#### User Experience
- **Tabbed Interface**: Organized parameter input
- **Crop Selection**: Optimized ranges per crop type
- **Visual Status**: Green/yellow indicators
- **Help Text**: Descriptions for each parameter
