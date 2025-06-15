# Asisten Pertanian Ahli Indonesia 🌾

Chatbot khusus yang dirancang untuk profesional pertanian Indonesia, dibangun dengan Streamlit dan didukung oleh AI.

## Fitur

- **Respons khusus peran** untuk berbagai profesional pertanian Indonesia
- **Input parameter lapangan** untuk analisis yang lebih akurat dan spesifik:
  - **Parameter Edafik**: N, P, K, pH, bahan organik, suhu tanah, kepadatan tanah
  - **Parameter Hidrologik**: Curah hujan, kedalaman air tanah, drainase, irigasi, kualitas air
  - **Parameter Atmosferik**: Suhu udara, kelembaban, kecepatan angin, radiasi matahari, tekanan udara, CO₂
- **Analisis parameter otomatis** dengan status optimal/suboptimal dan rekomendasi spesifik
- **Analisis ahli terstruktur** dengan tiga bagian utama:
  - 🔮 **Forecasting Recovery**: Prediksi timeline pemulihan dan langkah remediasi
  - 🤖 **LLM Suggestion**: Wawasan berbasis data menggunakan penalaran ilmiah
  - 🔧 **Problem-Solving Recommendations**: Solusi berdasarkan faktor tanah, air, dan iklim Indonesia
- **Basis pengetahuan komprehensif** mencakup tanaman lokal, ternak, manajemen tanah, dan irigasi Indonesia
- **Interface chat interaktif** dengan riwayat pesan dan pemilihan peran
- **Tombol topik cepat** dan skenario contoh untuk tantangan pertanian umum Indonesia
- **Fungsi pencarian basis pengetahuan** dengan konten Indonesia
- **Respons AI real-time** menggunakan OpenRouter API dengan output terstruktur
- **Konteks lokasi** dengan pilihan provinsi Indonesia

## Peran Pengguna yang Didukung

1. **Petani** - Pengelolaan tanaman dan lahan
2. **Peternak** - Peternakan dan pengembangbiakan hewan
3. **Spesialis Agribisnis** - Bisnis dan analisis pasar pertanian
4. **Insinyur Pertanian** - Teknologi dan peralatan pertanian
5. **Petugas Penyuluh Pertanian** - Pendidikan dan penyuluhan pertanian
6. **Konsultan Pertanian** - Konsultasi pertanian komprehensif

## Installation

1. Clone or download this project
2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

1. Run the Streamlit application:
   ```bash
   streamlit run agricultural_chatbot.py
   ```

2. Open your web browser and navigate to the displayed local URL (usually `http://localhost:8501`)

3. Select your agricultural role from the sidebar

4. Mulai bertanya tentang:
   - Teknik pengelolaan tanaman dan budidaya
   - Perawatan dan breeding ternak
   - Kesehatan dan kesuburan tanah Indonesia
   - Pengendalian hama dan penyakit lokal
   - Sistem irigasi dan pengelolaan air
   - Bisnis dan pasar pertanian Indonesia
   - Teknologi dan peralatan pertanian
   - Praktik pertanian berkelanjutan

5. **Gunakan Input Parameter** untuk analisis yang lebih akurat:
   - Aktifkan "Gunakan Data Parameter" di sidebar
   - Pilih jenis tanaman untuk referensi optimal
   - Input data edafik, hidrologik, dan atmosferik
   - Dapatkan analisis parameter otomatis dan rekomendasi spesifik

## Input Parameter Lapangan

### 🌱 Parameter Edafik (Tanah)
- **Nitrogen (N)**: Kandungan nitrogen dalam tanah (%)
- **Phosphorus (P)**: Kandungan fosfor dalam tanah (%)  
- **Potassium (K)**: Kandungan kalium dalam tanah (%)
- **pH Tanah**: Tingkat keasaman tanah (3.0-9.0)
- **Bahan Organik**: Kandungan bahan organik (%)
- **Suhu Tanah**: Suhu tanah pada kedalaman 10cm (°C)
- **Kepadatan Tanah**: Bulk density tanah (g/cm³)

### 💧 Parameter Hidrologik (Air)
- **Curah Hujan**: Curah hujan bulanan (mm/bulan)
- **Kedalaman Air Tanah**: Kedalaman muka air tanah (cm)
- **Laju Drainase**: Kecepatan drainase air (cm/jam)
- **Frekuensi Irigasi**: Interval pemberian air (hari)
- **EC Air**: Electrical Conductivity air irigasi (dS/m)

### 🌤️ Parameter Atmosferik (Iklim)
- **Suhu Udara**: Suhu udara rata-rata harian (°C)
- **Kelembaban Relatif**: Kelembaban udara relatif (%)
- **Kecepatan Angin**: Kecepatan angin rata-rata (km/jam)
- **Radiasi Matahari**: Intensitas radiasi matahari (MJ/m²/hari)
- **Lama Penyinaran**: Durasi sinar matahari per hari (jam)
- **Tekanan Udara**: Tekanan atmosfer (hPa)
- **Konsentrasi CO₂**: Konsentrasi karbon dioksida (ppm)

## Format Respons Terstruktur

Chatbot memberikan analisis ahli dalam tiga bagian terstruktur:

### 🔮 Forecasting Recovery (Prakiraan Pemulihan)
- **Timeline Pemulihan**: Kerangka waktu spesifik (hari, minggu, bulan, musim)
- **Langkah Remediasi**: 3-5 langkah yang dapat ditindaklanjuti untuk mengatasi masalah
- **Kondisi Lokal**: Mempertimbangkan faktor regional dan musiman Indonesia
- **Dampak Ekonomi**: Mempertimbangkan biaya pemulihan dan kebutuhan sumber daya

### 🤖 LLM Suggestion (Saran Model AI)
- **Penalaran Ilmiah**: Wawasan berbasis data dan rekomendasi berdasarkan bukti
- **Contoh Dunia Nyata**: Studi kasus dan praktik yang terbukti di Indonesia
- **Praktik Terbaik**: Standar industri dan implementasi yang berhasil
- **Metrik Monitoring**: Indikator kunci untuk melacak kemajuan

### 🔧 Problem-Solving Recommendations (Rekomendasi Pemecahan Masalah)
- **Faktor Edafik**: Kesehatan tanah, struktur, kesuburan, manajemen pH, jenis tanah Indonesia
- **Faktor Hidrologik**: Irigasi, drainase, optimalisasi kualitas air, sistem monsun
- **Faktor Atmosferik**: Adaptasi iklim tropis, pertimbangan cuaca, strategi musiman

## Konten Khusus Indonesia

### Tanaman Lokal
- Padi, jagung, cabai, kelapa sawit, kakao, kopi, pisang, singkong
- Teknik lokal: jajar legowo, tumpangsari, integrated farming

### Ternak Indonesia
- Sapi, kambing, ayam kampung dengan pakan dan perawatan khusus Indonesia

### Jenis Tanah Indonesia
- Andosol, Latosol, Regosol, Alluvial dengan karakteristik masing-masing

### Sistem Irigasi
- Irigasi teknis, tadah hujan, pasang surut, tetes

## Contoh Pertanyaan

Coba tanyakan pertanyaan berbasis skenario seperti:
- "Sawah padi saya terkena blast. Berapa lama waktu pemulihan?"
- "Tanaman cabai menunjukkan gejala antraknosa. Apa rencana pemulihan?"
- "Sapi saya menunjukkan tanda-tanda penyakit pernapasan. Timeline pemulihan?"
- "pH tanah turun menjadi 4.5 setelah hujan asam. Langkah remediasi?"

## Knowledge Base Coverage

### Crop Management
- Common crops and planting seasons
- Pest and disease identification
- Treatment recommendations

### Livestock Management
- Cattle, poultry, and swine care
- Feeding guidelines
- Health management
- Breeding practices

### Soil Management
- Soil types and characteristics
- Fertility and nutrient management
- pH and soil health

### Irrigation
- Different irrigation methods
- Water management strategies
- Scheduling recommendations

## API Configuration

The chatbot uses OpenRouter API for AI responses. The API key is already configured in the code, but you may want to replace it with your own for production use.

## Contributing

Feel free to extend the knowledge base or add new features to better serve the agricultural community.

## License

This project is open source and available for educational and commercial use in agriculture.
