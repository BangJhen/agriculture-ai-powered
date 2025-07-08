"""
Map Integration Preview for Agricultural Decision Support System
Enhanced version with robust error handling and fallback options
"""

import streamlit as st

# MUST be first Streamlit command
st.set_page_config(
    page_title="🗺️ Map Integration Preview",
    page_icon="🌾",
    layout="wide"
)

import folium
import json

# Robust imports with fallbacks (moved error handling to main function)
try:
    from streamlit_folium import st_folium
    STREAMLIT_FOLIUM_AVAILABLE = True
except ImportError as e:
    STREAMLIT_FOLIUM_AVAILABLE = False
    STREAMLIT_FOLIUM_ERROR = str(e)

try:
    from geopy.geocoders import Nominatim
    from geopy.exc import GeopyError
    GEOPY_AVAILABLE = True
except ImportError:
    GEOPY_AVAILABLE = False

# PyArrow fallback handling (no UI calls here)
try:
    import pyarrow
    PYARROW_AVAILABLE = True
except ImportError as e:
    PYARROW_AVAILABLE = False
    PYARROW_ERROR = str(e)

def create_basic_folium_map():
    """Create basic folium map without custom components"""
    indonesia_center = [-2.5, 118.0]
    
    m = folium.Map(
        location=indonesia_center,
        zoom_start=5,
        tiles='OpenStreetMap'
    )
    
    # Add agricultural regions
    agricultural_regions = [
        {"name": "Jawa Barat - Rice Belt", "coords": [-6.9, 107.6], "crop": "🌾"},
        {"name": "Jawa Tengah - Corn Region", "coords": [-7.3, 110.4], "crop": "🌽"},
        {"name": "Jawa Timur - Sugar Cane", "coords": [-7.8, 112.5], "crop": "🎋"},
        {"name": "Sumatra Utara - Palm Oil", "coords": [3.6, 98.7], "crop": "🌴"},
        {"name": "Sulawesi Selatan - Rice", "coords": [-5.1, 119.4], "crop": "🌾"},
    ]
    
    for region in agricultural_regions:
        folium.Marker(
            region["coords"],
            popup=f"{region['crop']} {region['name']}",
            tooltip=f"Agricultural Region: {region['name']}",
            icon=folium.Icon(color='green', icon='leaf')
        ).add_to(m)
    
    return m

def create_indonesia_agricultural_map():
    """Create map focused on Indonesia's agricultural regions"""
    
    # Center on Indonesia's main agricultural areas
    indonesia_center = [-2.5, 118.0]
    
    # Create map with better tiles and crosshair cursor
    m = folium.Map(
        location=indonesia_center,
        zoom_start=5,
        tiles='OpenStreetMap',
        attr='Map data © OpenStreetMap contributors'
    )
    
    # Add CSS for crosshair cursor to indicate clickable areas
    cursor_css = """
    <style>
    .leaflet-container {
        cursor: crosshair !important;
    }
    .leaflet-clickable {
        cursor: crosshair !important;
    }
    </style>
    """
    m.get_root().html.add_child(folium.Element(cursor_css))
    
    # Add alternative tile layers
    folium.TileLayer(
        tiles='https://{s}.tile.openstreetmap.fr/hot/{z}/{x}/{y}.png',
        attr='© OpenStreetMap contributors, Tiles style by Humanitarian OpenStreetMap Team',
        name='Humanitarian',
        overlay=False,
        control=True
    ).add_to(m)
    
    # Add only a few key agricultural regions as reference (reduced from 5 to 3)
    agricultural_regions = [
        {
            "name": "Jawa Barat - Rice Belt", 
            "coords": [-6.9, 107.6], 
            "crop": "🌾",
            "info": "Referensi: Major rice production area"
        },
        {
            "name": "Sumatra Utara - Palm Oil", 
            "coords": [3.6, 98.7], 
            "crop": "🌴",
            "info": "Referensi: Major palm oil plantation region"
        },
        {
            "name": "Sulawesi Selatan - Rice", 
            "coords": [-5.1, 119.4], 
            "crop": "🌾",
            "info": "Referensi: Eastern Indonesia rice production"
        }
    ]
    
    for region in agricultural_regions:
        popup_text = f"""
        <div style="font-family: Arial; font-size: 12px;">
            <h4 style="margin: 0; color: #2E7D32;">{region['crop']} {region['name']}</h4>
            <p style="margin: 5px 0; color: #666;">{region['info']}</p>
            <p style="margin: 0; font-size: 10px; color: #888;">
                📍 {region['coords'][0]:.2f}°, {region['coords'][1]:.2f}°
            </p>
        </div>
        """
        
        folium.Marker(
            region["coords"],
            popup=folium.Popup(popup_text, max_width=250),
            tooltip=f"🌱 Referensi: {region['name']}",
            icon=folium.Icon(color='lightgreen', icon='leaf', prefix='fa')
        ).add_to(m)
    
    # Add layer control
    folium.LayerControl().add_to(m)
    
    # Add ONE prominent instruction marker
    folium.Marker(
        [-10, 118],
        popup="""
        <div style="font-family: Arial; font-size: 16px; color: #1976D2; text-align: center;">
            <h2 style="margin: 0; color: #1976D2;">🎯 KLIK DI AREA KOSONG!</h2>
            <p style="margin: 10px 0; font-size: 14px;">
                ✅ Klik di mana saja pada peta<br/>
                ✅ Pin merah akan muncul otomatis<br/>
                ✅ Dapatkan koordinat + deskripsi<br/>
                🖱️ Cursor: Crosshair untuk precision
            </p>
            <div style="background: #FFF3CD; padding: 10px; border-radius: 5px; margin: 10px 0;">
                <strong>🗺️ Coba klik di:</strong><br/>
                • Area laut • Area hutan • Area kota<br/>
                • Pegunungan • Pantai • Area rural
            </div>
        </div>
        """,
        tooltip="📍 INSTRUKSI: Cursor crosshair - Klik area kosong",
        icon=folium.Icon(color='blue', icon='exclamation', prefix='fa')
    ).add_to(m)
    
    return m

def add_user_marker_to_map(base_map, lat, lng, address):
    """Add a dynamic red pin marker to the map when user clicks"""
    
    # Create simple popup with only location name and coordinates
    popup_html = f"""
    <div style="font-family: Arial; font-size: 14px; text-align: center; min-width: 200px;">
        <h3 style="margin: 0; color: #D32F2F;">📍 {address.split(',')[0]}</h3>
        <hr style="margin: 8px 0; border: 1px solid #D32F2F;">
        
        <div style="background: #FFEBEE; padding: 8px; border-radius: 5px; margin: 8px 0;">
            <p style="margin: 0; font-family: monospace; font-size: 12px;">
                <strong>Latitude:</strong> {lat:.6f}°<br/>
                <strong>Longitude:</strong> {lng:.6f}°
            </p>
        </div>
        
        <div style="margin-top: 8px;">
            <small style="color: #666;">📍 Klik untuk detail lengkap di sidebar</small>
        </div>
    </div>
    """
    
    # Add the red pin marker with simple popup
    user_marker = folium.Marker(
        [lat, lng],
        popup=folium.Popup(popup_html, max_width=250),
        tooltip=f"📍 {address.split(',')[0]}: {lat:.4f}°, {lng:.4f}°",
        icon=folium.Icon(
            color='red', 
            icon='map-pin', 
            prefix='fa'
        )
    )
    
    user_marker.add_to(base_map)
    
    # Add a subtle circle around the pin for better visibility
    folium.CircleMarker(
        [lat, lng],
        radius=8,
        popup=f"📍 {address.split(',')[0]}",
        color='red',
        fill=True,
        fillColor='red',
        fillOpacity=0.3,
        weight=2
    ).add_to(base_map)
    
    return base_map

def geocode_location(address):
    """Geocode an address to coordinates using Nominatim"""
    if not GEOPY_AVAILABLE:
        return None
        
    try:
        geolocator = Nominatim(user_agent="agricultural_decision_support")
        location = geolocator.geocode(
            address, 
            country_codes=['id'],  # Limit to Indonesia
            timeout=10
        )
        
        if location:
            return {
                'lat': location.latitude,
                'lng': location.longitude,
                'display_name': location.address
            }
        else:
            return None
            
    except GeopyError as e:
        st.error(f"Geocoding error: {str(e)}")
        return None
    except Exception as e:
        st.error(f"Unexpected error: {str(e)}")
        return None

def reverse_geocode_location(lat, lng):
    """Reverse geocode coordinates to address"""
    if not GEOPY_AVAILABLE:
        return estimate_location_from_coords(lat, lng)
        
    try:
        geolocator = Nominatim(user_agent="agricultural_decision_support")
        location = geolocator.reverse(
            f"{lat}, {lng}",
            language='id',  # Indonesian language
            timeout=10
        )
        
        if location:
            return location.address
        else:
            return estimate_location_from_coords(lat, lng)
            
    except GeopyError:
        return estimate_location_from_coords(lat, lng)
    except Exception:
        return estimate_location_from_coords(lat, lng)

def estimate_location_from_coords(lat, lng):
    """Estimate location name from coordinates (simplified)"""
    
    # Simple region detection based on coordinates
    if -8 <= lat <= -5 and 105 <= lng <= 115:
        if 105 <= lng <= 108:
            return "Jawa Barat, Indonesia"
        elif 108 <= lng <= 112:
            return "Jawa Tengah, Indonesia"  
        else:
            return "Jawa Timur, Indonesia"
    elif -3 <= lat <= 6 and 95 <= lng <= 108:
        if 95 <= lng <= 100:
            return "Sumatra Barat, Indonesia"
        elif 100 <= lng <= 104:
            return "Sumatra Utara, Indonesia"
        else:
            return "Sumatra, Indonesia"
    elif -6 <= lat <= 2 and 108 <= lng <= 120:
        return "Kalimantan, Indonesia"
    elif -12 <= lat <= 2 and 115 <= lng <= 125:
        return "Sulawesi, Indonesia"
    elif -10 <= lat <= -8 and 105 <= lng <= 125:
        return "Nusa Tenggara, Indonesia"
    elif -6 <= lat <= 6 and 125 <= lng <= 145:
        return "Papua, Indonesia"
    else:
        return f"Indonesia ({lat:.2f}°, {lng:.2f}°)"

def display_fallback_map():
    """Fallback map display without st_folium"""
    st.warning("🔄 Using fallback map mode (limited interactivity)")
    
    # Create basic map
    m = create_basic_folium_map()
    
    # Save map as HTML
    map_html = m._repr_html_()
    
    # Display in streamlit
    st.components.v1.html(map_html, height=400)
    
    # Manual coordinate input as fallback
    st.markdown("### 📝 Manual Coordinate Input")
    col1, col2 = st.columns(2)
    
    with col1:
        lat = st.number_input("Latitude", value=-6.9, format="%.6f", key="fallback_lat")
    
    with col2:
        lng = st.number_input("Longitude", value=107.6, format="%.6f", key="fallback_lng")
    
    if st.button("Use These Coordinates", type="primary"):
        address = reverse_geocode_location(lat, lng)
        location_data = {
            'coordinates': {'lat': lat, 'lng': lng},
            'address': address,
            'source': 'fallback_manual'
        }
        st.session_state.selected_location = location_data
        return location_data
    
    return None

def enhanced_location_input():
    """Enhanced location input with map integration"""
    
    st.markdown("### 📍 Pilih Lokasi Lahan Pertanian")
    st.markdown("*Pilih lokasi yang tepat untuk mendapatkan rekomendasi yang akurat*")
    
    # Create tabs for different input methods
    if STREAMLIT_FOLIUM_AVAILABLE:
        tab1, tab2, tab3 = st.tabs(["🗺️ Interactive Map", "🔍 Search Location", "📝 Manual Input"])
    else:
        tab1, tab2 = st.tabs(["🗺️ Basic Map", "📝 Manual Input"])
    
    if STREAMLIT_FOLIUM_AVAILABLE:
        with tab1:
            st.markdown("**🎯 KLIK DI AREA KOSONG UNTUK MENAMBAH PIN MERAH:**")
            
            # Enhanced instructions for clicking empty areas
            col1, col2, col3 = st.columns(3)
            with col1:
                st.info("🖱️ **Cursor crosshair** untuk presisi")
            with col2:
                st.info("📍 **Pin merah** muncul otomatis")
            with col3:
                st.info("💬 **Deskripsi lengkap** di popup")
            
            # Emphasize dynamic marker functionality
            st.warning("🎯 **FITUR BARU**: Setiap klik akan menambah pin merah dengan deskripsi koordinat lengkap!")
            
            st.markdown("---")
            
            # Initialize clicked locations in session state
            if 'clicked_locations' not in st.session_state:
                st.session_state.clicked_locations = []
            
            # Create base map
            m = create_indonesia_agricultural_map()
            
            # Add all previously clicked markers to the map
            for i, loc in enumerate(st.session_state.clicked_locations):
                m = add_user_marker_to_map(
                    m, 
                    loc['lat'], 
                    loc['lng'], 
                    loc['address']
                )
            
            # Display map with error handling
            try:
                map_data = st_folium(
                    m, 
                    width=700, 
                    height=450, 
                    returned_objects=["last_clicked"],
                    key=f"agricultural_map_{len(st.session_state.clicked_locations)}"  # Dynamic key to force refresh
                )
                
                # Handle new map clicks
                if map_data and map_data.get('last_clicked'):
                    lat = map_data['last_clicked']['lat']
                    lng = map_data['last_clicked']['lng']
                    
                    # Check if this is a new click (not the same as last one)
                    is_new_click = True
                    if st.session_state.clicked_locations:
                        last_loc = st.session_state.clicked_locations[-1]
                        if abs(lat - last_loc['lat']) < 0.00001 and abs(lng - last_loc['lng']) < 0.00001:
                            is_new_click = False
                    
                    if is_new_click:
                        # Get address for the new location
                        with st.spinner("🔍 Menambahkan pin merah dan menganalisis lokasi..."):
                            address = reverse_geocode_location(lat, lng)
                        
                        # Add to clicked locations
                        new_location = {
                            'lat': lat,
                            'lng': lng,
                            'address': address,
                            'timestamp': len(st.session_state.clicked_locations) + 1
                        }
                        st.session_state.clicked_locations.append(new_location)
                        
                        # Force refresh to show new marker
                        st.rerun()
                    
                    # Display current selection info
                    st.success("🎉 **PIN MERAH BERHASIL DITAMBAHKAN!**")
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        st.metric(
                            label="📍 Latitude Terbaru", 
                            value=f"{lat:.6f}°",
                            help="Koordinat lintang (utara-selatan)"
                        )
                    with col2:
                        st.metric(
                            label="📍 Longitude Terbaru", 
                            value=f"{lng:.6f}°",
                            help="Koordinat bujur (timur-barat)"
                        )
                    
                    # Show address
                    if st.session_state.clicked_locations:
                        current_address = st.session_state.clicked_locations[-1]['address']
                        st.info(f"🏞️ **Alamat Estimasi:** {current_address}")
                    
                    # Detailed coordinate information in sidebar (since popup is simplified)
                    with st.expander("📊 Detail Koordinat Lengkap (Pin Terbaru)", expanded=True):
                        st.markdown(f"""
                        **🎯 Informasi Koordinat Presisi:**
                        - **Latitude (Lintang):** `{lat:.6f}°`
                        - **Longitude (Bujur):** `{lng:.6f}°`
                        - **Akurasi:** ±1 meter (6 decimal precision)
                        
                        **🗺️ Format Multiple Koordinat:**
                        - **Decimal Degrees:** `{lat:.6f}, {lng:.6f}`
                        - **GPS Format:** `{lat:.6f}°{'N' if lat >= 0 else 'S'}, {lng:.6f}°{'E' if lng >= 0 else 'W'}`
                        - **DMS Format:** `{abs(lat):.0f}°{((abs(lat) % 1) * 60):.0f}'{((((abs(lat) % 1) * 60) % 1) * 60):.1f}\"{'N' if lat >= 0 else 'S'} {abs(lng):.0f}°{((abs(lng) % 1) * 60):.0f}'{((((abs(lng) % 1) * 60) % 1) * 60):.1f}\"{'E' if lng >= 0 else 'W'}`
                        
                        **🚀 Quick Actions & Links:**
                        - 📱 [Buka di Google Maps](https://www.google.com/maps?q={lat},{lng})
                        - 📱 [Buka di Google Earth](https://earth.google.com/web/@{lat},{lng},1000a,35y,0h,0t,0r)
                        - 📋 **Copy Coordinates:** `{lat:.6f}, {lng:.6f}`
                        - 💾 **Database Ready:** JSON format tersedia
                        
                        **📍 Status Lokasi:**
                        - ✅ Pin merah aktif di peta
                        - ✅ Koordinat tersimpan di sesi
                        - ✅ Siap untuk integrasi sistem
                        """)
                    
                    # Show summary of all clicked locations
                    if len(st.session_state.clicked_locations) > 1:
                        with st.expander(f"📍 Semua Lokasi yang Dipilih ({len(st.session_state.clicked_locations)} pin)"):
                            for i, loc in enumerate(st.session_state.clicked_locations):
                                # Extract location name (first part before comma)
                                location_name = loc['address'].split(',')[0]
                                st.markdown(f"""
                                **📍 Pin #{i+1}: {location_name}**
                                - **Koordinat:** `{loc['lat']:.6f}°, {loc['lng']:.6f}°`
                                - **Alamat Lengkap:** {loc['address']}
                                - **Google Maps:** [Buka Lokasi](https://www.google.com/maps?q={loc['lat']},{loc['lng']})
                                - **Copy Coordinates:** `{loc['lat']:.6f}, {loc['lng']:.6f}`
                                """)
                            
                            st.markdown("---")
                            col1, col2 = st.columns(2)
                            with col1:
                                if st.button("🗑️ Hapus Semua Pin", type="secondary"):
                                    st.session_state.clicked_locations = []
                                    st.rerun()
                            with col2:
                                if st.button("📋 Export Koordinat", type="primary"):
                                    coordinates_text = "\n".join([
                                        f"{loc['lat']:.6f}, {loc['lng']:.6f}"
                                        for loc in st.session_state.clicked_locations
                                    ])
                                    st.text_area("📋 Copy Koordinat (satu per baris):", coordinates_text, height=100)
                    
                    # Store in session state for persistence (last clicked)
                    st.session_state.selected_location = {
                        'coordinates': {'lat': lat, 'lng': lng},
                        'address': current_address if 'current_address' in locals() else address,
                        'source': 'map_click_with_red_pin',
                        'total_pins': len(st.session_state.clicked_locations)
                    }
                    
                    return st.session_state.selected_location
                    
                else:
                    # Show instructions and current pin count
                    pin_count = len(st.session_state.clicked_locations)
                    if pin_count == 0:
                        st.info("🖱️ **Hover cursor di peta - lihat crosshair! Klik untuk menambah pin merah**")
                    else:
                        st.success(f"📍 **{pin_count} pin merah** sudah ditambahkan. Klik lagi untuk menambah lebih banyak!")
                    
                    st.markdown("""
                    💡 **Fitur Pin Merah:**
                    - 🖱️ Cursor berubah jadi crosshair untuk presisi
                    - 📍 Setiap klik menambah pin merah permanen
                    - 💬 Klik pin untuk lihat deskripsi koordinat lengkap
                    - 🗺️ Multiple pins bisa ditambahkan sekaligus
                    - 🔗 Direct link ke Google Maps di setiap pin
                    
                    🎯 **Contoh Area untuk Diklik:**
                    - Area pertanian baru • Lokasi survei lapangan
                    - Titik referensi GPS • Area penelitian
                    - Lokasi proyek • Koordinat penting lainnya
                    """)
                    
            except Exception as e:
                st.error(f"❌ Error loading interactive map: {str(e)}")
                st.info("🔄 Switching to fallback mode...")
                return display_fallback_map()
        
        with tab2:
            st.markdown("**Cari lokasi dengan nama daerah:**")
            
            # Location search
            search_query = st.text_input(
                "Cari lokasi...", 
                placeholder="Contoh: Subang, Jawa Barat",
                help="Masukkan nama kota, kecamatan, atau daerah"
            )
            
            if search_query and len(search_query) > 2:
                if st.button("🔍 Cari Lokasi", type="primary"):
                    with st.spinner(f"🔍 Mencari '{search_query}'..."):
                        location_result = geocode_location(search_query)
                        
                    if location_result:
                        st.success(f"✅ **Lokasi ditemukan:** {location_result['display_name']}")
                        
                        col1, col2 = st.columns(2)
                        with col1:
                            st.info(f"📍 **Latitude:** {location_result['lat']:.6f}")
                        with col2:
                            st.info(f"📍 **Longitude:** {location_result['lng']:.6f}")
                        
                        # Store in session state
                        st.session_state.selected_location = {
                            'coordinates': {'lat': location_result['lat'], 'lng': location_result['lng']},
                            'address': location_result['display_name'],
                            'source': 'search'
                        }
                        
                        return st.session_state.selected_location
                    else:
                        st.error(f"❌ Lokasi '{search_query}' tidak ditemukan")
                        st.info("💡 Coba gunakan nama yang lebih spesifik atau gunakan Interactive Map")
        
        with tab3:
            st.markdown("**Input manual lokasi:**")
            
            # Fallback to text input
            manual_location = st.text_input(
                "Lokasi/Daerah", 
                value="Subang, Jawa Barat, Indonesia",
                help="Masukkan nama daerah, kecamatan, atau koordinat"
            )
            
            if manual_location:
                st.session_state.selected_location = {
                    'address': manual_location,
                    'coordinates': None,
                    'source': 'manual'
                }
                return st.session_state.selected_location
    
    else:
        # Fallback interface when streamlit-folium not available
        with tab1:
            return display_fallback_map()
        
        with tab2:
            st.markdown("**Input manual lokasi:**")
            
            manual_location = st.text_input(
                "Lokasi/Daerah", 
                value="Subang, Jawa Barat, Indonesia",
                help="Masukkan nama daerah, kecamatan, atau koordinat"
            )
            
            if manual_location:
                st.session_state.selected_location = {
                    'address': manual_location,
                    'coordinates': None,
                    'source': 'manual'
                }
                return st.session_state.selected_location
    
    # Return previously selected location if available
    return st.session_state.get('selected_location', None)

def display_system_status():
    """Display system status for libraries"""
    with st.expander("🔧 System Status"):
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if STREAMLIT_FOLIUM_AVAILABLE:
                st.success("✅ Streamlit-Folium: Available")
            else:
                st.error("❌ Streamlit-Folium: Not Available")
                st.code(f"Error: {STREAMLIT_FOLIUM_ERROR}")
        
        with col2:
            if GEOPY_AVAILABLE:
                st.success("✅ Geopy: Available")
            else:
                st.warning("⚠️ Geopy: Limited")
        
        with col3:
            if PYARROW_AVAILABLE:
                st.success("✅ PyArrow: Available")
            else:
                st.warning("⚠️ PyArrow: Fallback Mode")
                st.code(f"Error: {PYARROW_ERROR}")

# Demo usage
if __name__ == "__main__":
    st.title("🗺️ Agricultural Map Integration Preview")
    st.markdown("*Enhanced preview with robust error handling and fallback options*")
    
    # Add status information (moved here after set_page_config)
    display_system_status()
    
    # Add info about the preview
    with st.expander("ℹ️ About This Preview"):
        st.markdown("""
        **Features Demonstrated:**
        - 🗺️ **Interactive Map**: Click-to-select location with agricultural regions
        - 🔍 **Location Search**: Search by address with geocoding
        - 📝 **Manual Input**: Fallback text input option
        - 🌾 **Agricultural Context**: Pre-marked farming regions across Indonesia
        - 💾 **Data Persistence**: Location data ready for MongoDB integration
        - 🛡️ **Robust Fallbacks**: Works even with library compatibility issues
        
        **Technologies Used:**
        - **Folium**: Open-source mapping library
        - **OpenStreetMap**: Free map data
        - **Nominatim**: Free geocoding service
        - **Streamlit-Folium**: Streamlit integration (with fallback)
        """)
    
    # Main location input
    location_data = enhanced_location_input()
    
    # Display results
    if location_data:
        st.markdown("---")
        st.markdown("### 📊 Selected Location Data:")
        
        # Pretty display of location data
        col1, col2 = st.columns(2)
        
        with col1:
            st.json(location_data)
        
        with col2:
            st.markdown("### 🌾 Integration Notes:")
            st.markdown(f"- **Source:** {location_data['source']}")
            
            if location_data.get('coordinates'):
                coords = location_data['coordinates']
                st.markdown(f"- **Precise Coordinates:** Available")
                st.markdown(f"- **Weather API Ready:** Yes")
                st.markdown(f"- **Soil Data Integration:** Possible")
            else:
                st.markdown(f"- **Coordinates:** Not available (manual input)")
                st.markdown(f"- **Geocoding Needed:** Yes")
            
            st.markdown("- **MongoDB Storage:** Ready")
            st.markdown("- **Regional Analysis:** Available")
        
        # Sample integration preview
        st.markdown("### 🚀 Next Steps for Integration:")
        st.code(f"""
# Data structure for agricultural_chatbot.py integration:
sensor_data = {{
    'N': 80, 'P': 40, 'K': 40,
    'temperature': 26, 'humidity': 80,
    'ph': 6.5, 'rainfall': 1200,
    'location': {location_data},
    # ... other sensor data
}}

# This will be saved to MongoDB with coordinates for:
# - Weather API integration
# - Regional crop recommendations  
# - Precision agriculture features
# - Government agricultural data integration
        """) 