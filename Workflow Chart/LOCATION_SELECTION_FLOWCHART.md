# 📍 Flowchart Pemilihan Lokasi - Agricultural Chatbot (Simplified)

## Alur Pemilihan Lokasi Lahan Pertanian - Versi Sederhana

```mermaid
flowchart TD
    Start[🌾 User Masuk ke Aplikasi] --> Check{Cek Status Lokasi}
    
    %% Status Checking
    Check -->|Pin Map Aktif| PinFlow[📍 Mode Pin Map]
    Check -->|GPS Selesai| GPSFlow[🛰️ Mode GPS Completed]
    Check -->|Belum Ada Lokasi| TabFlow[📋 Mode Pilih Lokasi]
    
    %% Pin Map Mode
    PinFlow --> PinInfo[📍 Tampilkan Info Pin]
    PinInfo --> PinAction{User Action}
    PinAction -->|Geser Pin| MovPin[🔄 Pindah Pin] 
    PinAction -->|Hapus Pin| DelPin[🗑️ Hapus Pin]
    MovPin --> PinInfo
    DelPin --> TabFlow
    
    %% GPS Completed Mode  
    GPSFlow --> GPSInfo[✅ Tampilkan Status GPS]
    GPSInfo --> GPSAction{User Action}
    GPSAction -->|Reset| ResetGPS[🗑️ Reset GPS]
    ResetGPS --> TabFlow
    
    %% Tab Selection Mode
    TabFlow --> ChooseTab{Pilih Metode}
    
    ChooseTab -->|Tab 1| GPS[🛰️ GPS Location]
    ChooseTab -->|Tab 2| Map[🗺️ Interactive Map] 
    ChooseTab -->|Tab 3| Search[🔍 Search Location]
    
    %% GPS Flow
    GPS --> GPSDetect[📱 Deteksi GPS]
    GPSDetect --> GPSSuccess{Berhasil?}
    GPSSuccess -->|Ya| GPSAutoRefresh[🔄 Auto-Refresh]
    GPSSuccess -->|Tidak| GPS
    GPSAutoRefresh --> GPSFlow
    
    %% Map Flow
    Map --> ShowMap[🗺️ Tampilkan Peta]
    ShowMap --> ClickMap[👆 Klik Lokasi]
    ClickMap --> AddPin[📍 Tambah Pin Merah]
    AddPin --> PinFlow
    
    %% Search Flow
    Search --> TypeLocation[⌨️ Ketik Nama Lokasi]
    TypeLocation --> SearchAPI[🔍 Cari Koordinat]
    SearchAPI --> SearchResult{Ditemukan?}
    SearchResult -->|Ya| SaveSearch[💾 Simpan Lokasi]
    SearchResult -->|Tidak| TypeLocation
    SaveSearch --> FormReady
    
    %% Final Steps
    PinInfo --> FormReady[📊 Lokasi Siap untuk Form]
    GPSInfo --> FormReady
    
    FormReady --> SubmitForm[🚀 Submit Form Sensor]
    SubmitForm --> SaveDB[💾 Simpan ke MongoDB]
    
    %% Styling
    classDef startStyle fill:#e3f2fd,stroke:#1565c0,stroke-width:3px
    classDef checkStyle fill:#fce4ec,stroke:#c2185b,stroke-width:2px
    classDef gpsStyle fill:#e8f5e8,stroke:#4caf50,stroke-width:2px
    classDef mapStyle fill:#f3e5f5,stroke:#9c27b0,stroke-width:2px
    classDef searchStyle fill:#fff3e0,stroke:#ff9800,stroke-width:2px
    classDef finalStyle fill:#e0f2f1,stroke:#00796b,stroke-width:2px
    
    class Start startStyle
    class Check,PinAction,GPSAction,ChooseTab,GPSSuccess,SearchResult checkStyle
    class GPS,GPSDetect,GPSAutoRefresh,GPSFlow,GPSInfo,ResetGPS gpsStyle
    class Map,ShowMap,ClickMap,AddPin,PinFlow,PinInfo,MovPin,DelPin mapStyle
    class Search,TypeLocation,SearchAPI,SaveSearch searchStyle
    class FormReady,SubmitForm,SaveDB finalStyle
```

## 📋 Penjelasan Alur Sederhana

### 🔄 **3 Mode Utama:**

| Mode | Kondisi | Tampilan |
|------|---------|----------|
| 📍 **Pin Map** | Ada pin aktif | Info pin + map untuk geser |
| 🛰️ **GPS Completed** | GPS berhasil | Status GPS + tombol reset |
| 📋 **Pilih Lokasi** | Belum ada lokasi | 3 tabs lokasi |

### 📱 **3 Metode Input:**

| Tab | Metode | Hasil |
|-----|--------|-------|
| **1** | 🛰️ GPS Location | Auto-hide tabs |
| **2** | 🗺️ Interactive Map | Auto-hide tabs + pin aktif |
| **3** | 🔍 Search Location | Langsung ke form |

### 🗑️ **Reset Actions:**

- **Hapus Pin** → Kembali ke mode tabs
- **Reset GPS** → Kembali ke mode tabs  
- **Reset Semua** → Clear semua data lokasi

### 📊 **Flow Linear:**

```
Start → Cek Status → Mode Aktif → User Action → Form → MongoDB
```

---

*Flowchart sederhana tanpa garis bersilangan - fokus pada 3 mode utama dan flow linear.* 🎯 