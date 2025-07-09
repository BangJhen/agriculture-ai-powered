# 📋 Interaction History Feature Flowchart

## Alur Fitur Interaction History - Sistem Pendukung Keputusan Pertanian

```mermaid
flowchart TD
    A[🚀 App Start / Refresh] --> B{MongoDB Connected?}
    
    B -->|Yes| C[📥 Load from MongoDB]
    B -->|No| D[📝 Start Empty History]
    
    C --> E{Data Found?}
    E -->|Yes| F[✅ Load to Session]
    E -->|No| D
    
    F --> G[📋 Display in Sidebar]
    D --> G
    
    G --> H[🎯 User Action]
    
    H --> I{What Action?}
    
    I -->|Create New| J[📝 Fill Form]
    I -->|Load Existing| K[📂 Click History]
    I -->|Clear All| L[🗑️ Clear Data]
    
    J --> M[✏️ Submit Form]
    M --> N[💾 Save to Database]
    N --> O[🔄 Update Sidebar]
    
    K --> P{Title Exists?}
    P -->|Yes| Q[📋 Load to Form]
    P -->|No| R[🔧 Generate Title]
    R --> Q
    
    Q --> S[🖥️ Display Form]
    
    L --> T[🗑️ Clear Session]
    T --> U[🗑️ Clear MongoDB]
    U --> V[🔄 Refresh UI]
    
    O --> G
    S --> G
    V --> G
    
    style A fill:#e1f5fe
    style G fill:#f3e5f5
    style N fill:#e8f5e8
    style R fill:#fff3e0
    style U fill:#ffebee
```

## 🔍 Penjelasan Alur

### 1. **Initialization (App Start)**
- Aplikasi dimulai atau di-refresh
- Cek koneksi MongoDB Atlas
- Load interaction history jika tersedia

### 2. **Data Loading**
- **MongoDB Connected**: Load data dari database
- **MongoDB Failed**: Mulai dengan history kosong
- **Backward Compatibility**: Generate title untuk data lama

### 3. **User Interactions**
- **Create New**: Input data baru → Save ke MongoDB & session
- **Load Existing**: Klik item history → Load ke form
- **Clear All**: Hapus semua data dari MongoDB & session

### 4. **Error Handling**
- ✅ **Title Missing**: Auto-generate dari sensor data
- ✅ **MongoDB Offline**: Fallback ke session state
- ✅ **Data Corruption**: Safe access dengan fallback

### 5. **Persistence**
- 💾 **Primary Storage**: MongoDB Atlas (persistent)
- 🔄 **Secondary Storage**: Streamlit session state (temporary)
- 🌍 **Global Session**: Shared across all users

## 🎯 Key Features

| Feature | Description |
|---------|-------------|
| **🔄 Auto-Load** | History dimuat otomatis saat app start |
| **💾 Dual Storage** | MongoDB primary + session state backup |
| **🛡️ Error Safe** | Backward compatibility dengan data lama |
| **🌍 Global Mode** | Shared history untuk semua pengguna |
| **⚡ Real-time** | Update sidebar secara real-time |

## 🔧 Technical Implementation

```mermaid
graph LR
    A[User Input] --> B[save_interaction]
    B --> C[MongoDB Save]
    B --> D[Session Update]
    
    E[App Refresh] --> F[MongoDB Load]
    F --> G[Session Init]
    
    H[Load Item] --> I[get_interaction_data]
    I --> J[display_form]
    
    style A fill:#e3f2fd
    style C fill:#e8f5e8
    style F fill:#fff3e0
```

---

*Diagram ini menunjukkan alur lengkap fitur interaction history yang telah diimplementasikan dengan error handling dan persistence yang robust.* 