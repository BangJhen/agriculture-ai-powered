"""
Agricultural Decision Support System - Complete Single File Version
A simple input-output tool for crop and environmental recommendations.
Powered by ML-based crop prediction and AI-generated environmental suggestions.
All functionality integrated into one file for simplicity.

MongoDB Configuration:
======================
The application uses MongoDB Atlas for persistent interaction history storage.

DEFAULT MONGODB (Ready to Use):
- Database: munawir_datathon2025  
- Collection: interaction_history
- Connection: Automatically configured (no setup required)

CUSTOM MONGODB (Optional):
If you want to use your own MongoDB Atlas database:
1. Create a .env file in the project root directory
2. Add these variables to your .env file:

   MONGODB_CONNECTION_STRING=mongodb+srv://yourusername:yourpassword@yourcluster.mongodb.net/?retryWrites=true&w=majority
   MONGODB_DATABASE=your_database_name
   MONGODB_COLLECTION=your_collection_name

3. Replace the values with your actual MongoDB Atlas credentials
4. Restart the application

Example .env file:
   MONGODB_CONNECTION_STRING=mongodb+srv://myuser:mypass@cluster0.abc123.mongodb.net/?retryWrites=true&w=majority
   MONGODB_DATABASE=my_agricultural_db
   MONGODB_COLLECTION=my_interactions

NOTE: If no .env file is found, the application automatically uses the provided
MongoDB Atlas database which is ready to use immediately.
"""

import streamlit as st
import os
import pandas as pd
import numpy as np
import pickle
from datetime import datetime
import requests
import json
from dotenv import load_dotenv
from typing import Dict, List, Tuple, Any
import warnings
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError
from qdrant_client import QdrantClient
from qdrant_client.http import models
from sentence_transformers import SentenceTransformer

modelembed = SentenceTransformer("all-MiniLM-L6-v2")
client = QdrantClient(url="http://localhost:6333") 


# Suppress warnings first
warnings.filterwarnings('ignore')

# Load environment variables
load_dotenv()

# Load environment variables for production

# Import SHAP and matplotlib after basic setup
try:
    import shap
    # Set matplotlib backend for non-interactive use
    import matplotlib
    matplotlib.use('Agg')  # Use non-interactive backend
    import matplotlib.pyplot as plt
    SHAP_AVAILABLE = True
except ImportError as e:
    st.warning(f"SHAP not available: {e}")
    SHAP_AVAILABLE = False

# ==================== MAP INTEGRATION IMPORTS & SETUP ====================

# Map-related imports with robust error handling
try:
    import folium
    FOLIUM_AVAILABLE = True
except ImportError as e:
    FOLIUM_AVAILABLE = False
    FOLIUM_ERROR = str(e)

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

# ==================== MAP INTEGRATION FUNCTIONS ====================

def create_indonesia_agricultural_map():
    """Create map focused on Indonesia's agricultural regions"""
    if not FOLIUM_AVAILABLE:
        return None
        
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
    
    # Add only a few key agricultural regions as reference
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
    
    # Add instruction marker
    folium.Marker(
        [-10, 118],
        popup="""
        <div style="font-family: Arial; font-size: 16px; color: #1976D2; text-align: center;">
            <h2 style="margin: 0; color: #1976D2;">🎯 SINGLE PIN MODE!</h2>
            <p style="margin: 10px 0; font-size: 14px;">
                ✅ Klik di mana saja untuk pin merah<br/>
                🔄 Klik lagi untuk pindahkan pin<br/>
                📍 Hanya 1 pin aktif bersamaan<br/>
                🖱️ Cursor: Crosshair untuk precision
            </p>
            <div style="background: #FFF3CD; padding: 10px; border-radius: 5px; margin: 10px 0;">
                <strong>🗺️ Mode Pin Tunggal:</strong><br/>
                • Klik pertama = Tambah pin<br/>
                • Klik kedua = Pindah pin<br/>
                • Lebih mudah & fokus pada 1 lokasi
            </div>
        </div>
        """,
        tooltip="📍 MODE: Single Pin - Klik untuk tambah/pindah",
        icon=folium.Icon(color='blue', icon='exclamation', prefix='fa')
    ).add_to(m)
    
    return m

def add_user_marker_to_map(base_map, lat, lng, address):
    """Add a dynamic red pin marker to the map when user clicks"""
    if not base_map:
        return base_map
        
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
        icon=folium.Icon(color='red', icon='map-pin', prefix='fa')
    )
    
    # Add circle around marker for emphasis
    folium.Circle(
        [lat, lng],
        radius=1000,  # 1km radius
        color='red',
        fillColor='red',
        fillOpacity=0.1,
        weight=2,
        tooltip=f"Area radius 1km dari {address.split(',')[0]}"
    ).add_to(base_map)
    
    user_marker.add_to(base_map)
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
        print(f"Geocoding error: {str(e)}")
        return None
    except Exception as e:
        print(f"Unexpected error: {str(e)}")
        return None

def reverse_geocode_location(lat, lng):
    """Reverse geocode coordinates to address with detailed fallback"""
    if not GEOPY_AVAILABLE:
        return estimate_location_from_coords(lat, lng)
        
    try:
        geolocator = Nominatim(user_agent="agricultural_decision_support_v2")
        location = geolocator.reverse(
            f"{lat}, {lng}",
            language='id',  # Indonesian language
            timeout=15,
            exactly_one=True
        )
        
        if location and location.address:
            # Get detailed address components
            address_parts = []
            raw_address = location.raw.get('address', {})
            
            # Try to build a more specific address from components
            if raw_address.get('village'):
                address_parts.append(raw_address['village'])
            elif raw_address.get('suburb'):
                address_parts.append(raw_address['suburb'])
            elif raw_address.get('neighbourhood'):
                address_parts.append(raw_address['neighbourhood'])
            
            if raw_address.get('city'):
                address_parts.append(raw_address['city'])
            elif raw_address.get('town'):
                address_parts.append(raw_address['town'])
            elif raw_address.get('municipality'):
                address_parts.append(raw_address['municipality'])
            
            if raw_address.get('state'):
                address_parts.append(raw_address['state'])
            elif raw_address.get('province'):
                address_parts.append(raw_address['province'])
            
            if raw_address.get('country'):
                address_parts.append(raw_address['country'])
            
            # Create detailed address or use full address
            if address_parts:
                detailed_address = ", ".join(address_parts)
                return detailed_address
            else:
                return location.address
        else:
            return estimate_location_from_coords(lat, lng)
            
    except GeopyError as e:
        print(f"GeoPy Error: {e}")
        return estimate_location_from_coords(lat, lng)
    except Exception as e:
        print(f"Reverse geocoding error: {e}")
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

def display_fallback_location_input():
    """Fallback location input when map libraries are not available"""
    st.markdown("**Lokasi/Daerah**")
    location = st.text_input(
        "Lokasi/Daerah", 
        value="Jawa Barat, Indonesia",
        help="Lokasi umum untuk pertimbangan regional",
        label_visibility="collapsed"
    )
    
    if location:
        return {
            'address': location,
            'coordinates': None,
            'source': 'text_fallback'
        }
    return None

def enhanced_location_input():
    """Enhanced location input with map integration for agricultural chatbot"""
    
    # Initialize single location in session state (only 1 pin allowed)
    if 'selected_location_pin' not in st.session_state:
        st.session_state.selected_location_pin = None
    
    # Check if map functionality is available
    if not STREAMLIT_FOLIUM_AVAILABLE or not FOLIUM_AVAILABLE:
        st.error("⚠️ **Interactive Map tidak tersedia** - Map libraries tidak terinstall")
        st.info("💡 **Solusi:** Gunakan tab 'Search Location' untuk mencari lokasi dengan nama daerah")
        
        # Show only search option as fallback
        st.markdown("### 🔍 Search Location (Fallback Mode)")
        search_query = st.text_input(
            "Cari lokasi...", 
            placeholder="Contoh: Subang, Jawa Barat",
            help="Masukkan nama kota, kecamatan, atau daerah",
            key="fallback_search_input"
        )
        
        if search_query and len(search_query) > 2:
            if st.button("🔍 Cari Lokasi", type="primary", key="fallback_search_btn"):
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
                        'source': 'search_fallback'
                    }
                    
                    # Also store in temp_coordinates for form access
                    st.session_state.temp_coordinates = {'lat': location_result['lat'], 'lng': location_result['lng']}
                else:
                    st.error(f"❌ Lokasi '{search_query}' tidak ditemukan")
        return  # Exit function early for fallback
    
    # Create tabs for different input methods (removed Manual Input)
    tab1, tab2 = st.tabs(["🗺️ Interactive Map", "🔍 Search Location"])
    
    with tab1:
        st.markdown("**🎯 SINGLE PIN MODE - KLIK UNTUK TAMBAH/PINDAH PIN MERAH:**")
        
        # Enhanced instructions for single pin mode
        col1, col2, col3 = st.columns(3)
        with col1:
            st.info("🖱️ **Cursor crosshair** untuk presisi")
        with col2:
            st.info("📍 **1 Pin merah** saja yang aktif")
        with col3:
            st.info("🔄 **Klik lagi** untuk pindah lokasi")
        
        # Create base map
        m = create_indonesia_agricultural_map()
        
        if m is None:
            st.error("❌ Tidak dapat membuat peta")
            st.info("💡 **Solusi:** Gunakan tab 'Search Location' untuk mencari lokasi dengan koordinat GPS")
            return  # Exit function early
        
        # Add single pin if exists
        if st.session_state.selected_location_pin:
            loc = st.session_state.selected_location_pin
            m = add_user_marker_to_map(
                m, 
                loc['lat'], 
                loc['lng'], 
                loc['address']
            )
        
        # Display map with error handling
        try:
            # Use timestamp for map key to ensure refresh when pin updates
            map_key = f"agricultural_map_{st.session_state.get('map_refresh_counter', 0)}"
            
            map_data = st_folium(
                m, 
                width=700, 
                height=400, 
                returned_objects=["last_object_clicked", "last_clicked"],  # Both for better compatibility
                key=map_key,
                feature_group_to_add=None,  # Allow clicking anywhere
                use_container_width=True
            )
            
            # Handle new map clicks (check both last_clicked and last_object_clicked)
            clicked_data = None
            if map_data and map_data.get('last_clicked'):
                clicked_data = map_data['last_clicked']
            elif map_data and map_data.get('last_object_clicked'):
                clicked_data = map_data['last_object_clicked']
            
            if clicked_data and clicked_data.get('lat') and clicked_data.get('lng'):
                lat = clicked_data['lat']
                lng = clicked_data['lng']
                
                # Check if this is a different location from current pin
                is_new_location = True
                if st.session_state.selected_location_pin:
                    current_pin = st.session_state.selected_location_pin
                    if abs(lat - current_pin['lat']) < 0.00001 and abs(lng - current_pin['lng']) < 0.00001:
                        is_new_location = False
                
                if is_new_location:
                    # Get address for the new location
                    action_text = "🔄 Memindahkan pin merah ke lokasi baru..." if st.session_state.selected_location_pin else "🔍 Menambahkan pin merah dan menganalisis lokasi..."
                    with st.spinner(action_text):
                        address = reverse_geocode_location(lat, lng)
                    
                    # Replace the single pin location
                    st.session_state.selected_location_pin = {
                        'lat': lat,
                        'lng': lng,
                        'address': address,
                        'timestamp': 1  # Always 1 since only 1 pin allowed
                    }
                    
                    # Increment refresh counter to force map update
                    st.session_state.map_refresh_counter = st.session_state.get('map_refresh_counter', 0) + 1
                    
                    # Force refresh to show updated marker
                    st.rerun()
                
                # Display current selection info
                is_moved = st.session_state.get('map_refresh_counter', 0) > 1
                success_message = "🔄 **PIN MERAH BERHASIL DIPINDAHKAN!**" if is_moved else "🎉 **PIN MERAH BERHASIL DITAMBAHKAN!**"
                st.success(success_message)
                
                col1, col2 = st.columns(2)
                with col1:
                    st.metric(
                        label="📍 Latitude Saat Ini", 
                        value=f"{lat:.6f}°",
                        help="Koordinat lintang (utara-selatan)"
                    )
                with col2:
                    st.metric(
                        label="📍 Longitude Saat Ini", 
                        value=f"{lng:.6f}°",
                        help="Koordinat bujur (timur-barat)"
                    )
                
                # Show address
                if st.session_state.selected_location_pin:
                    current_address = st.session_state.selected_location_pin['address']
                    st.info(f"🏞️ **Alamat Estimasi:** {current_address}")
                
                # Store in session state for form submission
                st.session_state.selected_location = {
                    'coordinates': {'lat': lat, 'lng': lng},
                    'address': current_address if 'current_address' in locals() else address,
                    'source': 'map_click_with_red_pin',
                    'pin_mode': 'single'  # Indicator for single pin mode
                }
                
                # Also store in temp_coordinates for form access
                st.session_state.temp_coordinates = {'lat': lat, 'lng': lng}
                
            else:
                # Show instructions for single pin mode
                if not st.session_state.selected_location_pin:
                    st.info("🖱️ **Hover cursor di peta - lihat crosshair! Klik untuk menambah pin merah**")
                    st.markdown("""
                    💡 **Mode Pin Tunggal:**
                    - 🖱️ Cursor berubah jadi crosshair untuk presisi
                    - 📍 Klik sekali untuk menambah pin merah
                    - 🔄 Klik lagi untuk memindahkan pin ke lokasi baru
                    - 📍 Hanya 1 pin yang bisa aktif dalam waktu bersamaan
                    """)
                else:
                    st.success("📍 **Pin merah sudah aktif!** Klik lokasi lain untuk memindahkan pin.")
                    
                    # Show current pin information
                    pin = st.session_state.selected_location_pin
                    location_name = pin['address'].split(',')[0]
                    with st.expander("📍 Lokasi Saat Ini Dipilih", expanded=True):
                        st.markdown(f"**📍 {location_name}**")
                        st.markdown(f"**Koordinat:** `{pin['lat']:.6f}°, {pin['lng']:.6f}°`")
                        st.markdown(f"**Alamat Lengkap:** {pin['address']}")
                        st.markdown(f"**Google Maps:** [🗺️ Buka Lokasi](https://www.google.com/maps?q={pin['lat']},{pin['lng']})")
                        
                        col1, col2 = st.columns(2)
                        with col1:
                            if st.button("🔄 Klik Peta untuk Pindah", type="secondary", key="move_pin_info"):
                                st.info("💡 Klik di lokasi baru pada peta untuk memindahkan pin")
                        with col2:
                            if st.button("🗑️ Hapus Pin", type="secondary", key="clear_pin_tab1"):
                                # Clear all location-related session state
                                st.session_state.selected_location_pin = None
                                st.session_state.selected_location = None
                                st.session_state.temp_coordinates = None
                                st.session_state.map_refresh_counter = st.session_state.get('map_refresh_counter', 0) + 1
                                print("🗑️ PIN CLEARED - All location session state reset")
                                st.rerun()
                
        except Exception as e:
            st.error(f"❌ Error loading interactive map: {str(e)}")
            st.info("💡 **Solusi:** Gunakan tab 'Search Location' untuk mencari lokasi dengan koordinat GPS")
    
    with tab2:
        st.markdown("**🔍 Cari lokasi dengan nama daerah untuk mendapat koordinat GPS:**")
        
        # Location search
        search_query = st.text_input(
            "Cari lokasi...", 
            placeholder="Contoh: Subang, Jawa Barat",
            help="Masukkan nama kota, kecamatan, atau daerah",
            key="location_search_input"
        )
        
        if search_query and len(search_query) > 2:
            if st.button("🔍 Cari Lokasi", type="primary", key="search_location_btn"):
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
                    
                    # Also store in temp_coordinates for form access
                    st.session_state.temp_coordinates = {'lat': location_result['lat'], 'lng': location_result['lng']}
                else:
                    st.error(f"❌ Lokasi '{search_query}' tidak ditemukan")
                    st.info("💡 Coba gunakan nama yang lebih spesifik atau gunakan Interactive Map")
    


def display_map_system_status():
    """Display map system status for debugging"""
    with st.expander("🗺️ Map System Status", expanded=False):
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if STREAMLIT_FOLIUM_AVAILABLE:
                st.success("✅ Streamlit-Folium")
            else:
                st.error("❌ Streamlit-Folium")
                if 'STREAMLIT_FOLIUM_ERROR' in globals():
                    st.caption(f"Error: {STREAMLIT_FOLIUM_ERROR}")
        
        with col2:
            if FOLIUM_AVAILABLE:
                st.success("✅ Folium")
            else:
                st.error("❌ Folium")
                if 'FOLIUM_ERROR' in globals():
                    st.caption(f"Error: {FOLIUM_ERROR}")
        
        with col3:
            if GEOPY_AVAILABLE:
                st.success("✅ Geopy")
            else:
                st.warning("⚠️ Geopy: Limited")

# ==================== MONGODB INTEGRATION ====================

class MongoDBManager:
    """MongoDB Manager for persistent storage of interaction history."""
    
    def __init__(self):
        """Initialize MongoDB connection"""
        self.client = None
        self.db = None
        self.collection = None
        self.connected = False
        self._connect()
    
    def _connect(self):
        """Establish connection to MongoDB Atlas"""
        try:
            # Check for custom MongoDB configuration from environment variables first
            connection_string = os.getenv('MONGODB_CONNECTION_STRING')
            database_name = os.getenv('MONGODB_DATABASE')
            collection_name = os.getenv('MONGODB_COLLECTION')
            
            # If no environment variables, use default provided MongoDB
            if not connection_string or connection_string.startswith("mongodb+srv://<username>"):
                connection_string = "mongodb+srv://Munawir:ardavagay@cluster0.9puyslt.mongodb.net/?retryWrites=true&w=majority"
                database_name = "munawir_datathon2025"
                collection_name = "interaction_history"
                print("🔗 Using provided MongoDB Atlas connection")
            else:
                print("🔗 Using custom MongoDB from environment variables")
            
            # Create MongoDB client with timeout
            self.client = MongoClient(connection_string, serverSelectionTimeoutMS=5000)
            
            # Test connection
            self.client.admin.command('ping')
            
            # Get database and collection
            self.db = self.client[database_name]
            self.collection = self.db[collection_name]
            
            # Create indexes for better performance
            self.collection.create_index("interaction_id", unique=True)
            self.collection.create_index("timestamp")
            self.collection.create_index("user_session")
            
            self.connected = True
            print(f"✅ MongoDB Atlas connection established successfully to {database_name}")
            return True
            
        except ConnectionFailure:
            print("⚠️ MongoDB connection failed - check network or credentials")
            return False
        except ServerSelectionTimeoutError:
            print("⚠️ MongoDB connection timeout - check network connectivity")
            return False
        except Exception as e:
            print(f"⚠️ MongoDB error: {str(e)}")
            return False
    
    def save_interaction(self, interaction_data: Dict) -> bool:
        """Save interaction to MongoDB with detailed debugging"""
        if not self.connected:
            print("⚠️ MongoDB not connected - skipping database save")
            return False
            
        try:
            # Debug: Print location and coordinates data before saving
            sensor_data = interaction_data.get("sensor_data", {})
            coordinates = sensor_data.get("coordinates")
            location = sensor_data.get("location")
            location_source = sensor_data.get("location_source", "N/A")
            
            print(f"🔍 Saving interaction to MongoDB with:")
            print(f"  📍 Location: {location}")
            print(f"  🌍 Coordinates: {coordinates}")
            print(f"  📊 Location Source: {location_source}")
            
            # Prepare document with proper datetime handling
            document = {
                "interaction_id": interaction_data["id"],
                "user_session": st.session_state.get('session_id', 'anonymous'),
                "timestamp": interaction_data["timestamp"],  # MongoDB handles Python datetime
                "sensor_data": interaction_data["sensor_data"],
                "ml_result": interaction_data.get("ml_result"),
                "ai_result": interaction_data.get("ai_result"),
                "title": interaction_data.get("title"),  # ✅ Save title field
                "created_at": datetime.now(),
                "updated_at": datetime.now()
            }
            
            # Upsert (update if exists, insert if not)
            result = self.collection.replace_one(
                {"interaction_id": interaction_data["id"]},
                document,
                upsert=True
            )
            
            if result.acknowledged:
                print(f"✅ Interaction successfully saved to MongoDB")
                if coordinates:
                    print(f"  🌍 GPS coordinates confirmed saved: {coordinates}")
                return True
            else:
                print("❌ Failed to save interaction to MongoDB")
                return False
            
        except Exception as e:
            print(f"⚠️ Could not save to database: {str(e)}")
            return False
    
    def load_interactions(self, limit: int = 50) -> List[Dict]:
        """Load recent interactions from MongoDB with debugging"""
        if not self.connected:
            print("⚠️ MongoDB not connected - cannot load from database")
            return []
            
        try:
            user_session = st.session_state.get('session_id', 'anonymous')
            print(f"🔍 Querying MongoDB for user_session: '{user_session}'")
            
            # Query recent interactions for current user
            cursor = self.collection.find(
                {"user_session": user_session}
            ).sort("timestamp", -1).limit(limit)
            
            interactions = []
            for doc in cursor:
                # Create title if it doesn't exist (backward compatibility)
                title = doc.get("title")
                if not title:
                    # Generate title from sensor data
                    sensor_data = doc.get("sensor_data", {})
                    crop = sensor_data.get("selected_crop", "Unknown")
                    location = sensor_data.get("location", "Unknown")
                    title = f"{crop.title()} - {location}"
                
                interaction = {
                    "id": doc["interaction_id"],
                    "timestamp": doc["timestamp"],
                    "sensor_data": doc["sensor_data"],
                    "ml_result": doc.get("ml_result"),
                    "ai_result": doc.get("ai_result"),
                    "title": title  # ✅ Include title field
                }
                interactions.append(interaction)
            
            print(f"📊 Found {len(interactions)} interactions in MongoDB")
            if len(interactions) > 0:
                latest = interactions[0]['timestamp']
                print(f"📅 Latest interaction: {latest}")
            
            return interactions
            
        except Exception as e:
            print(f"⚠️ Could not load from database: {str(e)}")
            return []
    
    def delete_interaction(self, interaction_id: str) -> bool:
        """Delete specific interaction from MongoDB"""
        if not self.connected:
            return False
            
        try:
            user_session = st.session_state.get('session_id', 'anonymous')
            result = self.collection.delete_one({
                "interaction_id": interaction_id,
                "user_session": user_session
            })
            
            return result.deleted_count > 0
            
        except Exception as e:
            print(f"⚠️ Could not delete from database: {str(e)}")
            return False
    
    def clear_all_interactions(self) -> bool:
        """Clear all interactions for current user"""
        if not self.connected:
            return False
            
        try:
            user_session = st.session_state.get('session_id', 'anonymous')
            result = self.collection.delete_many({"user_session": user_session})
            
            return True
            
        except Exception as e:
            print(f"⚠️ Could not clear database: {str(e)}")
            return False
    
    def update_interaction_results(self, interaction_id: str, ml_result=None, ai_result=None) -> bool:
        """Update interaction with ML/AI results"""
        if not self.connected:
            return False
            
        try:
            user_session = st.session_state.get('session_id', 'anonymous')
            update_data = {"updated_at": datetime.now()}
            
            if ml_result:
                update_data["ml_result"] = ml_result
            if ai_result:
                update_data["ai_result"] = ai_result
            
            result = self.collection.update_one(
                {
                    "interaction_id": interaction_id,
                    "user_session": user_session
                },
                {"$set": update_data}
            )
            
            return result.modified_count > 0
            
        except Exception as e:
            print(f"⚠️ Error updating MongoDB: {str(e)}")
            return False
    


# Initialize MongoDB manager
@st.cache_resource
def get_mongodb_manager():
    """Get MongoDB manager instance (cached)"""
    return MongoDBManager()

# ==================== ML CROP PREDICTOR CLASS ====================

class AICropPredictor:
    """AI-powered crop predictor with environmental improvement suggestions."""
    
    def __init__(self, model_path: str = "data"):
        """Initialize the crop predictor with trained models and data."""
        self.model_path = model_path
        self.model = None
        self.label_encoder = None
        self.scaler = None
        self.X_train = None
        self.X_test = None
        self.y_train = None
        self.y_test = None
        self.feature_columns = ['N', 'P', 'K', 'temperature', 'humidity', 'ph', 'rainfall']
        self.explainer = None  # SHAP explainer
        
        self.load_models()
        self.initialize_explainer()
    
    def load_models(self):
        """Load the trained models and reference data."""
        try:
            # Load the trained Random Forest model
            with open(os.path.join(self.model_path, 'best_model_random_forest.pkl'), 'rb') as f:
                self.model = pickle.load(f)
            
            # Load the label encoder
            with open(os.path.join(self.model_path, 'label_encoder.pkl'), 'rb') as f:
                self.label_encoder = pickle.load(f)
            
            # Load the scaler
            with open(os.path.join(self.model_path, 'scaler.pkl'), 'rb') as f:
                self.scaler = pickle.load(f)
            
            # Load training and test data for reference
            self.X_train = pd.read_csv(os.path.join(self.model_path, 'X_train.csv'))
            self.X_test = pd.read_csv(os.path.join(self.model_path, 'X_test.csv'))
            
            # Load training and test labels for analysis
            self.y_train = pd.read_csv(os.path.join(self.model_path, 'y_train.csv'))
            self.y_test = pd.read_csv(os.path.join(self.model_path, 'y_test.csv'))
            
            return True
            
        except Exception as e:
            st.error(f"Error loading models: {str(e)}")
            return False
    
    def initialize_explainer(self):
        """Initialize SHAP explainer for model interpretability."""
        if not SHAP_AVAILABLE:
            self.explainer = None
            return False
            
        try:
            if self.model and self.X_train is not None:
                # Use a subset of training data as background for TreeExplainer
                background_data = self.X_train.sample(min(100, len(self.X_train)), random_state=42)
                self.explainer = shap.TreeExplainer(self.model, background_data)
                return True
        except Exception as e:
            st.warning(f"Could not initialize SHAP explainer: {str(e)}")
            self.explainer = None
            return False
    
    def get_feature_explanation(self, input_data: Dict[str, float], selected_crop: str, confidence: float) -> str:
        """Generate SHAP-based explanation for low confidence predictions."""
        if not SHAP_AVAILABLE or not self.explainer or confidence >= 0.5:  # Only explain low confidence
            return ""
        
        def safe_float(value):
            """Safely convert value to float, handling numpy arrays"""
            try:
                if hasattr(value, 'item'):  # numpy scalar
                    return float(value.item())
                elif hasattr(value, '__float__'):
                    return float(value)
                else:
                    return float(value)
            except (ValueError, TypeError):
                return 0.0
        
        try:
            # Preprocess input
            processed_input = self.preprocess_input(input_data)
            
            # Get SHAP values
            shap_values = self.explainer.shap_values(processed_input)
            
            # Get feature names (after preprocessing)
            feature_names = self.X_train.columns.tolist()
            
            # Find the index for selected crop
            class_names = self.label_encoder.classes_
            if selected_crop not in class_names:
                return "Tanaman yang dipilih tidak ada dalam model prediksi."
            
            crop_index = list(class_names).index(selected_crop)
            
            # Get SHAP values for the selected crop
            if isinstance(shap_values, list):  # Multi-class classification
                if crop_index < len(shap_values):
                    crop_shap_values = shap_values[crop_index]
                    # Handle case where shap_values might be 2D
                    if hasattr(crop_shap_values, 'shape') and len(crop_shap_values.shape) > 1:
                        crop_shap_values = crop_shap_values[0]  # First instance
                else:
                    return f"❌ Crop index {crop_index} tidak ditemukan dalam SHAP values"
            else:
                crop_shap_values = shap_values[0]  # Single instance
            
            # Ensure we have the right shape
            if not hasattr(crop_shap_values, '__len__'):
                return "❌ Format SHAP values tidak sesuai"
            
            # Create feature importance ranking with safe conversion
            try:
                feature_importance = []
                for i, (fname, sval, fval) in enumerate(zip(feature_names, crop_shap_values, processed_input[0])):
                    safe_sval = safe_float(sval)
                    safe_fval = safe_float(fval)
                    feature_importance.append((fname, safe_sval, safe_fval))
                
                # Sort by absolute SHAP value (most impactful features first)
                feature_importance.sort(key=lambda x: abs(x[1]), reverse=True)
                
            except Exception as e:
                return f"❌ Error dalam pemrosesan feature importance: {str(e)}"
            
            # Generate explanation
            explanation = "### 🔍 Analisis Faktor Penghambat (Confidence Rendah)\n\n"
            explanation += "Berdasarkan analisis model ML, berikut faktor-faktor yang paling mempengaruhi rendahnya kesesuaian tanaman:\n\n"
            
            # Map technical feature names to Indonesian descriptions
            feature_map = {
                'N': 'Nitrogen (N)',
                'P': 'Fosfor (P)', 
                'K': 'Kalium (K)',
                'temperature': 'Suhu',
                'humidity': 'Kelembaban',
                'ph': 'pH Tanah',
                'rainfall': 'Curah Hujan',
                'NPK_sum': 'Total NPK',
                'NP_ratio': 'Rasio N:P',
                'NK_ratio': 'Rasio N:K',
                'PK_ratio': 'Rasio P:K',
                'temp_humidity_interaction': 'Interaksi Suhu-Kelembaban',
                'rainfall_humidity_ratio': 'Rasio Curah Hujan:Kelembaban',
                'ph_acidity_level': 'Level Keasaman pH'
            }
            
            # Show top 5 most impactful features
            for i, (feature, shap_val, feature_val) in enumerate(feature_importance[:5]):
                feature_name = feature_map.get(feature, feature)
                impact = "mengurangi" if shap_val < 0 else "meningkatkan"
                
                explanation += f"**{i+1}. {feature_name}** (Nilai: {feature_val:.2f})\n"
                explanation += f"   - SHAP Impact: {shap_val:.3f} ({impact} kesesuaian)\n"
                
                # Add specific recommendations based on feature
                if feature in ['N', 'P', 'K']:
                    if shap_val < 0:
                        explanation += f"   - 💡 **Rekomendasi**: Pertimbangkan penambahan pupuk {feature_name}\n"
                    else:
                        explanation += f"   - ✅ **Status**: Level {feature_name} sudah mendukung\n"
                elif feature == 'ph':
                    if shap_val < 0:
                        if feature_val < 6.0:
                            explanation += "   - 💡 **Rekomendasi**: Tanah terlalu asam, pertimbangkan pengapuran\n"
                        elif feature_val > 7.0:
                            explanation += "   - 💡 **Rekomendasi**: Tanah terlalu basa, pertimbangkan penambahan bahan organik\n"
                elif feature == 'temperature':
                    if shap_val < 0:
                        explanation += "   - 💡 **Rekomendasi**: Suhu tidak optimal untuk tanaman ini\n"
                elif feature == 'humidity':
                    if shap_val < 0:
                        explanation += "   - 💡 **Rekomendasi**: Kelembaban perlu diatur (drainage atau irigasi)\n"
                elif feature == 'rainfall':
                    if shap_val < 0:
                        explanation += "   - 💡 **Rekomendasi**: Curah hujan tidak optimal, pertimbangkan irigasi\n"
                
                explanation += "\n"
            
            explanation += "**💭 Catatan**: Analisis ini menunjukkan faktor-faktor yang paling berpengaruh terhadap rendahnya tingkat kesesuaian tanaman yang dipilih dengan kondisi lingkungan saat ini.\n\n"
            
            return explanation
            
        except Exception as e:
            return f"❌ Error dalam analisis faktor: {str(e)}"
    
    def engineer_features(self, input_data: Dict[str, float]) -> pd.DataFrame:
        """Engineer features exactly as done during training."""
        # Create base dataframe
        df = pd.DataFrame([input_data])
        
        # Feature engineering (matching training process)
        df['NPK_sum'] = df['N'] + df['P'] + df['K']
        
        # Ratios (with small epsilon to avoid division by zero)
        epsilon = 1e-8
        df['NP_ratio'] = df['N'] / (df['P'] + epsilon)
        df['NK_ratio'] = df['N'] / (df['K'] + epsilon)
        df['PK_ratio'] = df['P'] / (df['K'] + epsilon)
        
        # Interactions
        df['temp_humidity_interaction'] = df['temperature'] * df['humidity']
        df['rainfall_humidity_ratio'] = df['rainfall'] / (df['humidity'] + epsilon)
        
        # pH acidity level (categorical to numerical)
        def ph_acidity_level(ph):
            if ph < 6.0:
                return -1  # Acidic
            elif ph > 7.0:
                return 1   # Alkaline
            else:
                return 0   # Neutral
        
        df['ph_acidity_level'] = df['ph'].apply(ph_acidity_level)
        
        return df
    
    def preprocess_input(self, input_data: Dict[str, float]) -> np.ndarray:
        """Preprocess user input exactly as done during training."""
        # Engineer features
        df_engineered = self.engineer_features(input_data)
        
        # Ensure column order matches training data
        feature_order = self.X_train.columns.tolist()
        df_engineered = df_engineered[feature_order]
        
        # Scale the features
        scaled_features = self.scaler.transform(df_engineered)
        
        return scaled_features
    
    def evaluate_crop_suitability(self, input_data: Dict[str, float], selected_crop: str) -> Tuple[str, float, str]:
        """Evaluate the suitability of selected crop based on environmental conditions.
        Returns: (crop_name, confidence, explanation)
        """
        if not self.model:
            return selected_crop, 0.0, ""
        
        try:
            # Preprocess input
            processed_input = self.preprocess_input(input_data)
            
            # Make prediction probabilities for all classes
            prediction_proba = self.model.predict_proba(processed_input)[0]
            
            # Get class names
            class_names = self.label_encoder.classes_
            probabilities = dict(zip(class_names, prediction_proba))
            
            # Find probability for selected crop
            if selected_crop in probabilities:
                confidence = probabilities[selected_crop]
            else:
                # If crop not found in model, give low confidence
                confidence = 0.1
            
            # Generate explanation if confidence is low
            explanation = self.get_feature_explanation(input_data, selected_crop, confidence)
            
            return selected_crop, confidence, explanation
            
        except Exception as e:
            st.error(f"Error mengevaluasi kesesuaian tanaman: {str(e)}")
            return selected_crop, 0.0, ""

# ==================== OLLAMA CLIENT INITIALIZATION ====================

def check_ollama_connection():
    """Check if Ollama is available and return the best available model"""
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        models = response.json()
        model_names = [model['name'] for model in models.get('models', [])]
        
        # Return the best available Gemma model
        if 'gemma3:4b' in model_names:
            return True, "gemma3:4b"
        elif 'gemma2:9b' in model_names:
            return True, "gemma2:9b"
        elif 'gemma:7b' in model_names:
            return True, "gemma:7b"
        elif any('llama' in name for name in model_names):
            return True, next(name for name in model_names if 'llama' in name)
        else:
            return True, "llama3.2:1b"  # Default expected model
    except Exception as e:
        print(f"⚠️ Ollama not available: {str(e)}")
        return False, None

def check_openrouter_connection():
    """Check if OpenRouter is available and return the model"""
    try:
        from openai import OpenAI
        
        client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key="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",
        )
        
        # Simple test request to validate the API key
        completion = client.chat.completions.create(
            extra_headers={
                "HTTP-Referer": "https://agricultural-chatbot.streamlit.app",
                "X-Title": "Agricultural Decision Support System",
            },
            model="mistralai/mistral-tiny",
            messages=[{"role": "user", "content": "Test"}],
            max_tokens=10
        )
        
        if completion.choices[0].message.content:
            return True, "mistralai/mistral-tiny"
        else:
            print(f"⚠️ OpenRouter test failed - no response content")
            return False, None
            
    except ImportError:
        print("⚠️ OpenAI package not installed - falling back to requests method")
        return check_openrouter_connection_fallback()
    except Exception as e:
        print(f"⚠️ OpenRouter not available: {str(e)}")
        return False, None

def check_openrouter_connection_fallback():
    """Fallback OpenRouter connection check using requests"""
    try:
        # Test connection to OpenRouter
        test_headers = {
            "Authorization": "Bearer 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",
            "Content-Type": "application/json"
        }
        
        # Simple test request to validate the API key
        test_response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers=test_headers,
            json={
                "model": "mistralai/mistral-tiny",
                "messages": [{"role": "user", "content": "Test"}],
                "max_tokens": 10
            },
            timeout=10
        )
        
        if test_response.status_code == 200:
            return True, "mistralai/mistral-tiny"
        else:
            print(f"⚠️ OpenRouter test failed with status {test_response.status_code}")
            return False, None
            
    except Exception as e:
        print(f"⚠️ OpenRouter not available: {str(e)}")
        return False, None

def get_available_llm():
    """Get the best available LLM service and model"""
    # First try Ollama (preferred for local deployment)
    ollama_available, ollama_model = check_ollama_connection()
    if ollama_available:
        print(f"✅ Using Ollama with model: {ollama_model}")
        return "ollama", ollama_model
    
    # Fallback to OpenRouter (for deployment)
    openrouter_available, openrouter_model = check_openrouter_connection()
    if openrouter_available:
        print(f"✅ Using OpenRouter with model: {openrouter_model}")
        return "openrouter", openrouter_model
    
    # No LLM available
    print("❌ No LLM service available")
    return None, None

def initialize_llm_client():
    """Initialize and verify LLM client (Ollama or OpenRouter)"""
    llm_service, model_name = get_available_llm()
    
    if llm_service is None:
        st.error("❌ **Error**: Tidak ada layanan LLM yang tersedia!")
        st.info(f"""
        **Setup LLM Diperlukan:**
        
        **Opsi 1 - Ollama (Lokal):**
        1. Install Ollama: `curl -fsSL https://ollama.com/install.sh | sh`
        2. Jalankan Ollama: `ollama serve`
        3. Download model Gemma: `ollama pull gemma2:9b` atau `ollama pull gemma:7b`
        4. Restart aplikasi ini
        
        **Opsi 2 - OpenRouter (Cloud):**
        - Sistem akan otomatis menggunakan OpenRouter jika Ollama tidak tersedia
        - Model yang digunakan: mistralai/mistral-tiny
        
        **Verifikasi:**
        - Ollama server: http://localhost:11434
        - Model tersedia: `ollama list`
        """)
        st.stop()
    
    return llm_service, model_name
    
def call_llm(llm_service: str, model_name: str, prompt: str, system_prompt: str = None, temperature: float = 0.7, max_tokens: int = 2000):
    """Call LLM with the specified service and model"""
    if llm_service == "ollama":
        return call_ollama_llm(model_name, prompt, system_prompt, temperature, max_tokens)
    elif llm_service == "openrouter":
        return call_openrouter_llm(model_name, prompt, system_prompt, temperature, max_tokens)
    else:
        raise ValueError(f"Unknown LLM service: {llm_service}")

def call_ollama_llm(model_name: str, prompt: str, system_prompt: str = None, temperature: float = 0.7, max_tokens: int = 2000):
    """Call Ollama LLM with the specified model"""
    # Prepare the payload
    payload = {
        "model": model_name,
        "prompt": prompt,
        "stream": False,
        "options": {
            "temperature": temperature,
            "num_predict": max_tokens
        }
    }
    
    # Add system prompt if provided
    if system_prompt:
        payload["system"] = system_prompt
    
    # Make the request
    response = requests.post(
        "http://localhost:11434/api/generate",
        json=payload,
        timeout=120
    )
    
    result = response.json()
    return result.get("response", "")

def create_query(SC, MLC) :
        """Create a query for the knowledge base"""
        prompt = f"Sekarang saya memiliki db knowledge base yang berisi informasi tentang pertanian di Indonesia. Saya ingin mencari informasi terkait dengan pertanian, tanaman, dan lingkungan. Berikut adalah pertanyaan saya:\n\n{SC}\n\nSaya juga ingin mempertimbangkan hasil evaluasi ML berikut:\n\n{MLC}\n\n berikan saya query ke qdrant yang relevan untuk menapatkan informasi yang relevan dalam bahasa inggris."
        response =  client.chat.completions.create(
                model="anthropic/claude-3.5-sonnet",
                messages=[
                    {"role": "system", "content": "You are an expert Indonesian agricultural advisor focused on environmental optimization and sustainable farming practices."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=2000
            )
        return response.choices[0].message.content.strip()

def query_knowledge_base(query_text, top_k=3):
        # Buat embedding dari query
        embeddings = modelembed.encode(query_text)
        # Query ke Qdrant
        results = client.qdrant_client.search(
            collection_name="pdf_knowledge",
            query_vector=embeddings,
            limit=top_k
        )
        # Ambil hasil payload (teks knowledge)
        knowledge_chunks = [hit.payload.get("text", "") for hit in results]
        return knowledge_chunks

def call_openrouter_llm(model_name: str, prompt: str, system_prompt: str = None, temperature: float = 0.7, max_tokens: int = 2000):
    """Call OpenRouter LLM with the specified model using OpenAI client"""
    try:
        from openai import OpenAI
        
        client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key="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",
        )
        
        # Prepare messages
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        
        # Make the request
        completion = client.chat.completions.create(
            extra_headers={
                "HTTP-Referer": "https://agricultural-chatbot.streamlit.app",
                "X-Title": "Agricultural Decision Support System",
            },
            model=model_name,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens
        )
        
        return completion.choices[0].message.content
        
    except ImportError:
        print("⚠️ OpenAI package not installed. Using fallback requests method.")
        return call_openrouter_llm_fallback(model_name, prompt, system_prompt, temperature, max_tokens)
    except Exception as e:
        print(f"⚠️ OpenRouter API error: {e}")
        return ""

def call_openrouter_llm_fallback(model_name: str, prompt: str, system_prompt: str = None, temperature: float = 0.7, max_tokens: int = 2000):
    """Fallback OpenRouter LLM call using requests if OpenAI package is not available"""
    headers = {
        "Authorization": "Bearer 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",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://agricultural-chatbot.streamlit.app",
        "X-Title": "Agricultural Decision Support System"
    }
    
    # Prepare messages
    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.append({"role": "user", "content": prompt})
    
    # Prepare the payload
    payload = {
        "model": model_name,
        "messages": messages,
        "temperature": temperature,
        "max_tokens": max_tokens
    }
    
    # Make the request
    response = requests.post(
        "https://openrouter.ai/api/v1/chat/completions",
        headers=headers,
        json=payload,
        timeout=120
    )
    
    result = response.json()
    if 'choices' in result and len(result['choices']) > 0:
        return result['choices'][0]['message']['content']
    else:
        print(f"⚠️ OpenRouter API error: {result}")
        return ""

# ==================== DECISION SUPPORT SYSTEM ====================

class DecisionSupportSystem:
    """Main class for agricultural decision support functionality"""
    
    def __init__(self):
        self.llm_service, self.model_name = get_available_llm()
        self.ai_predictor = None
        self.ai_predictor_loaded = False
        self.ai_predictor_error = None
    
    def get_ai_predictor(self):
        """Lazy load the AI predictor when first needed"""
        if not self.ai_predictor_loaded:
            try:
                st.info("🤖 Initializing ML models for the first time...")
                with st.spinner("Loading ML models (this may take a moment)..."):
                    self.ai_predictor = AICropPredictor()
                st.success("✅ ML models loaded successfully")
                self.ai_predictor_loaded = True
            except Exception as e:
                self.ai_predictor_error = str(e)
                st.warning(f"⚠️ Could not load ML models: {str(e)}")
                st.info("Application will continue with AI-only recommendations")
                self.ai_predictor = None
                self.ai_predictor_loaded = True
        
        return self.ai_predictor
    
    def generate_environmental_advice(self, sensor_data, ml_evaluation=None):
        """Generate AI-powered environmental optimization advice"""
        
        # Prepare sensor data context
        sensor_context = ""
        if sensor_data:
            sensor_context = f"""
            **Kondisi Lingkungan Saat Ini:**
            - Nitrogen: {sensor_data.get('N', 'N/A')} kg/ha
            - Fosfor: {sensor_data.get('P', 'N/A')} kg/ha  
            - Kalium: {sensor_data.get('K', 'N/A')} kg/ha
            - Suhu: {sensor_data.get('temperature', 'N/A')}°C
            - Kelembaban: {sensor_data.get('humidity', 'N/A')}%
            - pH: {sensor_data.get('ph', 'N/A')}
            - Curah Hujan: {sensor_data.get('rainfall', 'N/A')} mm
            - Lokasi: {sensor_data.get('location', 'Indonesia')}
            """
        
        # Prepare ML evaluation context
        ml_context = ""
        if ml_evaluation:
            # Handle tuple format returned by evaluator: (crop_name, confidence, explanation)
            if isinstance(ml_evaluation, (tuple, list)) and len(ml_evaluation) >= 2:
                selected_crop = ml_evaluation[0] if ml_evaluation[0] else 'N/A'
                confidence = ml_evaluation[1] if ml_evaluation[1] else 0
                explanation = ml_evaluation[2] if len(ml_evaluation) > 2 else ""
                
                # Basic ML evaluation
                ml_context = f"""
                **Evaluasi Tanaman Berbasis ML:**
                - Tanaman yang Dipilih: {selected_crop}
                - Tingkat Kesesuaian: {confidence*100:.1f}%
                """
                
                # Add detailed feature impact analysis if explanation exists
                if explanation and not explanation.startswith("❌"):
                    # Extract key insights from SHAP explanation for LLM context
                    ml_context += f"""
                - Status Kesesuaian: {"Rendah" if confidence < 0.5 else "Sedang" if confidence < 0.7 else "Tinggi"}
                
                **Analisis Faktor Pembatas (dari Model ML):**
                """
                    
                    # Parse the explanation to extract feature impacts
                    if "**1." in explanation:
                        lines = explanation.split('\n')
                        feature_impacts = []
                        current_feature = None
                        
                        for line in lines:
                            line = line.strip()
                            if line.startswith("**") and "." in line and "(" in line:
                                # Extract feature name and value
                                try:
                                    parts = line.split("**")
                                    if len(parts) >= 2:
                                        feature_info = parts[1].split("(")
                                        if len(feature_info) >= 2:
                                            feature_name = feature_info[0].strip().split(".")[1].strip()
                                            feature_val = feature_info[1].replace(")", "").replace("Nilai:", "").strip()
                                            current_feature = {"name": feature_name, "value": feature_val}
                                except (IndexError, ValueError):
                                    # Skip malformed lines
                                    pass
                            elif line.startswith("- SHAP Impact:") and current_feature:
                                # Extract SHAP impact
                                impact_info = line.replace("- SHAP Impact:", "").strip()
                                current_feature["impact"] = impact_info
                            elif line.startswith("- 💡") and current_feature:
                                # Extract recommendation
                                recommendation = line.replace("- 💡 **Rekomendasi**:", "").strip()
                                current_feature["recommendation"] = recommendation
                                feature_impacts.append(current_feature)
                                current_feature = None
                            elif line.startswith("- ✅") and current_feature:
                                # Extract status
                                status = line.replace("- ✅ **Status**:", "").strip()
                                current_feature["status"] = status
                                feature_impacts.append(current_feature)
                                current_feature = None
                        
                        # Add top limiting factors to ML context
                        for i, feature in enumerate(feature_impacts[:3]):  # Top 3 factors
                            ml_context += f"""
                {i+1}. {feature['name']}: {feature['value']}
                   - Impact: {feature.get('impact', 'N/A')}
                   - {"Rekomendasi: " + feature.get('recommendation', '') if 'recommendation' in feature else "Status: " + feature.get('status', '')}
                """
                    
                    ml_context += """
                **Petunjuk untuk Rekomendasi Lingkungan:**
                - Fokuskan saran pada faktor-faktor pembatas utama yang diidentifikasi ML
                - Berikan solusi spesifik untuk meningkatkan parameter yang bermasalah
                - Pertimbangkan interaksi antar faktor dalam rekomendasi
                """
                
            else:
                # Fallback for unexpected format
                ml_context = f"""
                **Evaluasi Tanaman Berbasis ML:**
                - Hasil: {str(ml_evaluation)}
                """
        query_text = self.create_query(ml_context, sensor_context)
        knowledge_chunks = self.query_knowledge_base(query_text, top_k=3)
        knowledge_context = "\n\n".join([f"Referensi {i+1}: {chunk}" for i, chunk in enumerate(knowledge_chunks) if chunk])

        # Enhanced prompt with technical research insights
        technical_context = """
        **Konteks Teknis Berdasarkan Penelitian (99.5% Akurasi):**
        
        **Model ML yang Digunakan:**
        - Random Forest Classifier dengan akurasi 99.5% (2,200 sampel, 22 tanaman)
        - Cross-validation score: 99.15% ± 0.5%
        - Menggunakan 14 fitur (7 data asli + 7 hasil feature engineering)
        - Confidence analysis: 95% prediksi dengan confidence >0.9
        
        **Hierarki Kepentingan Fitur (Berdasarkan 5 Metode Analisis):**
        1. Kelembaban (0.7886) - DOMINAN: Tekanan penyakit, stress air, evapotranspirasi
        2. Kalium/K (0.6825) - Resistensi penyakit, kualitas buah, regulasi air
        3. Curah Hujan (0.6152) - Sumber air utama, kebutuhan irigasi
        4. Fosfor/P (0.5791) - Perkembangan akar, pembungaan, transfer energi
        5. Rasio Curah Hujan:Kelembaban (0.4931) - Indikator efisiensi penggunaan air
        6. Total NPK (0.4691) - Ketersediaan nutrisi total
        7. Nitrogen/N (0.4127) - Pertumbuhan daun, fotosintesis, sintesis protein
        
        **Pola Kegagalan Prediksi yang Ditemukan:**
        - muskmelon ↔ watermelon: Kebutuhan air dan suhu serupa (solusi: fokus rasio K/P)
        - kidneybeans ↔ blackgram: Sesama legum dengan NPK serupa (solusi: optimalisasi pH)
        - mango ↔ orange: Buah pohon dengan zona iklim overlap (solusi: rasio rainfall:humidity)
        
        **Aturan Keputusan Kritis yang Ditemukan:**
        - Kelembaban Tinggi (>80%) + Curah Hujan Tinggi (>200mm): Tanaman suka air (padi, pisang)
        - K Tinggi (>100) + Kelembaban Sedang (40-60%): Tanaman cash crop (kapas, rami)
        - P Tinggi (>80) + Kelembaban Rendah (<40%): Sayuran akar, kacang-kacangan
        - Rasio curah hujan:kelembaban optimal (1.5-2.5): Tanaman buah (mangga, jeruk)
        
        **Insight Agronomis Tervalidasi:**
        - Kelembaban adalah faktor dominan (skor 0.7886) - prioritas monitoring #1
        - Urutan prioritas nutrisi: K > P > N (berbeda dari pemahaman umum N-P-K)
        - Interaksi iklim (suhu-kelembaban) dan efisiensi air sangat penting
        - Feature engineering memberikan peningkatan 20.4% dalam prediksi
        
        **Dampak Ekonomi Terukur:**
        - Potensi peningkatan hasil: 15-25% per hektar
        - ROI: 300-500% dalam satu musim tanam
        - Peningkatan profit: +36% per hektar (+$580/ha)
        - Penghematan air: 20-30% melalui crop-climate matching optimal
        """
        
        # prompt = f"""
        # Anda adalah penasihat pertanian Indonesia yang ahli, didukung oleh penelitian machine learning terdepan dengan akurasi 99.5%.
        
        
        # {sensor_context}
        # {ml_context}
        
        # Berikan rekomendasi optimalisasi lingkungan yang komprehensif dalam bahasa Indonesia untuk petani Indonesia, berdasarkan penelitian machine learning dengan 99.5% akurasi dan analisis 2,200 sampel pertanian. Pertimbangkan:

        # **Prioritas Berdasarkan Penelitian (Evidence-Based):**
        # 1. **KELEMBABAN** (faktor paling penting - skor 0.7886): Monitoring dan kontrol kelembaban adalah prioritas utama
        # 2. **KALIUM** (skor 0.6825): Lebih penting dari N dan P untuk kebanyakan tanaman
        # 3. **CURAH HUJAN** (skor 0.6152): Sumber air utama, perlu optimalisasi dengan kelembaban
        # 4. **FOSFOR** (skor 0.5791): Kritial untuk fase reproduktif tanaman
        # 5. **Efisiensi Air** (rasio curah hujan:kelembaban): Indikator kunci untuk tanaman buah
        
        # **Tingkat Error Berdasarkan Kategori (untuk Pencegahan):**
        # - Serealia (padi, jagung): 0.5% error rate - sangat robust
        # - Legum (kacang-kacangan): 1.2% error rate - ada inter-legume confusion
        # - Buah-buahan: 2.1% error rate - kompleksitas tertinggi
        # - Tanaman komersial: 0.8% error rate - kebutuhan yang distinktif
        
        # **Kondisi Spesifik Indonesia:**
        # - Iklim tropis dengan kelembaban tinggi (rata-rata 71.48%)
        # - Variasi curah hujan ekstrem (20-298mm dalam dataset)
        # - Tantangan musim hujan/kemarau
        # - Ketersediaan sumber daya lokal
        
        # **PRIORITASKAN** rekomendasi berdasarkan hierarchy kepentingan fitur dan faktor pembatas yang diidentifikasi ML.
        
        # Strukturkan rekomendasi sebagai berikut:
        
        # ## 🎯 Fokus Utama (Berdasarkan Penelitian ML 99.5% Akurasi)
        # - **KELEMBABAN (Prioritas #1)**: Kontrol kelembaban adalah faktor paling kritis (skor 0.7886)
        # - **KALIUM (Prioritas #2)**: Optimalisasi K lebih penting dari N/P (skor 0.6825) 
        # - **MANAJEMEN AIR (Prioritas #3)**: Curah hujan dan efisiensi air sangat penting (skor 0.6152)
        # - Prioritaskan perbaikan berdasarkan hierarchy penelitian: Kelembaban → K → Curah Hujan → P → N
        # - Jelaskan mengapa faktor-faktor ini kritikal berdasarkan temuan ilmiah
        
        # ## 🌱 Optimalisasi Kesehatan Tanah (Berdasarkan Hierarki K>P>N)
        # - **KALIUM FIRST**: Fokus utama pada kalium (resistensi penyakit, kualitas buah) - prioritas tertinggi
        # - **FOSFOR SECOND**: Perkembangan akar dan pembungaan - prioritas kedua  
        # - **NITROGEN THIRD**: Pertumbuhan vegetatif - prioritas ketiga
        # - Strategi pH berdasarkan interaksi dengan NPK dan kondisi tropis
        # - Kompos dan bahan organik untuk mendukung keseimbangan nutrisi optimal
        # - **Atasi kekurangan berdasarkan urutan K→P→N** sesuai penelitian
        
        # ## 💧 Manajemen Air (Faktor Kritis #1 dan #3)
        # - **KELEMBABAN CONTROL**: Prioritas utama - monitoring dan pengaturan kelembaban (faktor terpenting)
        # - **RASIO OPTIMUM**: Target rasio curah hujan:kelembaban 1.5-2.5 untuk tanaman buah
        # - Strategi irigasi berdasarkan target kelembaban spesifik tanaman
        # - Drainase untuk mencegah kelembaban berlebih (>80%) pada tanaman sensitif
        # - **Efisiensi air** sebagai indikator kunci performa tanaman
        
        # ## 🌡️ Adaptasi Iklim (Interaksi Suhu-Kelembaban)
        # - **CLIMATE STRESS INDEX**: Monitoring interaksi suhu-kelembaban sebagai indikator stress
        # - Strategi cooling untuk mengurangi stress heat kombinasi suhu-kelembaban tinggi
        # - Manajemen microclimate berdasarkan kebutuhan kelembaban spesifik
        # - Preparasi musiman dengan fokus pada kontrol kelembaban
        # - **Kelembaban sebagai driver utama** adaptasi iklim
        
        # ## 🔧 Panduan Implementasi (Evidence-Based Priority)
        # - **IMMEDIATE (0-2 minggu)**: Setup monitoring kelembaban dan optimalisasi kalium
        # - **SHORT-TERM (1-3 bulan)**: Sistem manajemen air dan balans nutrisi K>P>N  
        # - **LONG-TERM (musim)**: Optimalisasi rasio curah hujan:kelembaban dan microclimate
        # - Budget allocation: 40% kelembaban, 25% nutrisi (prioritas K), 20% irigasi, 15% lainnya
        # - **KPI monitoring**: Kelembaban harian, level K tanah, rasio air-kelembaban
        
        # **Target Quantitatif Berdasarkan Penelitian:**
        # - Kelembaban optimal: Sesuaikan dengan threshold per crop category (80%+ untuk padi, 40-60% untuk cotton)
        # - Rasio rainfall:humidity target: 1.5-2.5 untuk buah-buahan
        # - K threshold: >100 kg/ha untuk cash crops, disesuaikan untuk kategori lain
        # - Expected improvement: 15-25% yield increase dengan 99.5% confidence
        
        # ## 🌾 Rekomendasi Khusus Indonesia
        # - Tanaman pendamping yang cocok untuk iklim Indonesia
        # - Teknik pertanian organik yang tepat
        # - Pemanfaatan pupuk lokal (kompos, pupuk kandang) **yang menargetkan kekurangan yang diidentifikasi**
        # - Strategi pengendalian hama yang ramah lingkungan
        
        # Berikan rekomendasi yang praktis, spesifik, dan dapat ditindaklanjuti. Fokus pada perbaikan yang dapat diukur yang selaras dengan kondisi pertanian Indonesia dan **secara langsung mengatasi faktor-faktor pembatas yang diidentifikasi oleh model ML**.
        
        # Jawab dalam bahasa Indonesia yang mudah dipahami oleh petani dengan latar belakang pendidikan beragam.
        # """
        
        system_prompt = "Anda adalah ahli pertanian Indonesia yang berpengalaman dalam optimalisasi lingkungan dan praktik pertanian berkelanjutan. Berikan saran yang praktis, spesifik, dan dapat diterapkan oleh petani Indonesia."
        
        response = call_llm(
            llm_service=self.llm_service,
            model_name=self.model_name,
            prompt=technical_context + "\n\n" + sensor_context + "\n\n" + ml_context + "\n\n" + knowledge_context,
            system_prompt=system_prompt,
            temperature=0.7,
            max_tokens=2000
        )
        
        return response

# ==================== STREAMLIT UI FUNCTIONS ====================

def display_sensor_input_form():
    """Display sensor data input form"""
    st.markdown("### 📊 Input Data Sensor Lingkungan")
    
    # Check if loading from history OR from preset
    current_interaction = get_current_interaction_data()
    preset_data = st.session_state.get('preset_data', None)
    
    if current_interaction:
        # Safe access to title with fallback
        title = current_interaction.get('title')
        if not title:
            # Generate title from sensor data as fallback
            sensor_data = current_interaction.get('sensor_data', {})
            crop = sensor_data.get('selected_crop', 'Unknown')
            location = sensor_data.get('location', 'Unknown')
            title = f"{crop.title()} - {location}"
        
        timestamp_str = current_interaction['timestamp'].strftime('%d/%m/%Y %H:%M')
        st.info(f"📋 Loading data from: **{title}** ({timestamp_str})")
        default_data = current_interaction['sensor_data']
        data_source = "interaction"
        
        # Restore location data to session state (important for refresh/reload scenarios)
        restore_location_from_interaction(current_interaction)
    elif preset_data:
        preset_name = st.session_state.get('preset_name', 'Preset')
        st.info(f"📋 Using preset: **{preset_name}** (you can modify parameters below)")
        default_data = preset_data
        data_source = "preset"
    else:
        st.markdown("*Masukkan kondisi lingkungan lahan Anda untuk mendapatkan rekomendasi yang dipersonalisasi*")
        default_data = {}
        data_source = "new"
    
    # Map Integration Section (OUTSIDE FORM for interactivity)
    st.markdown("---")
    st.markdown("### 📍 Lokasi Lahan Pertanian")
    
    # Display map system status (optional debug info)
    display_map_system_status()
    
    # Enhanced location input with map (OUTSIDE form for click functionality)
    enhanced_location_input()  # This function now stores data in session state
    
    # Extract location information from session state with debugging
    location_data = st.session_state.get('selected_location', None)
    selected_pin = st.session_state.get('selected_location_pin', None)
    
    # Debug session state
    print(f"🔍 Form location extraction:")
    print(f"  📍 selected_location: {location_data}")
    print(f"  📍 selected_location_pin: {selected_pin}")
    
    # Priority: Use pin data if available (more persistent)
    if selected_pin:
        location = selected_pin['address']
        st.session_state.temp_coordinates = {'lat': selected_pin['lat'], 'lng': selected_pin['lng']}
        st.session_state.selected_location = {
            'coordinates': {'lat': selected_pin['lat'], 'lng': selected_pin['lng']},
            'address': selected_pin['address'],
            'source': 'map_click_with_red_pin'
        }
        print(f"  ✅ Using pin data: {location} @ {st.session_state.temp_coordinates}")
    elif location_data:
        if location_data.get('coordinates'):
            # Use formatted address from map
            location = location_data['address']
            # Store coordinates for potential future use
            st.session_state.temp_coordinates = location_data['coordinates']
            print(f"  ✅ Using selected_location with coords: {location} @ {st.session_state.temp_coordinates}")
        else:
            # Use manual input address
            location = location_data['address']
            st.session_state.temp_coordinates = None
            print(f"  📝 Using manual input: {location}")
    else:
        # No location selected - encourage user to use available methods
        location = "Belum dipilih - gunakan Interactive Map atau Search Location"
        st.session_state.temp_coordinates = None
        print(f"  ⚠️ No location selected - user needs to choose method")
    
    # Create stable form key (don't change based on preset_data content)
    form_key = f"sensor_data_form_{data_source}_{st.session_state.current_interaction_id or 'new'}"
    
    with st.form(form_key):
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("**Nutrisi Tanah (kg/ha)**")
            nitrogen = st.number_input("Nitrogen (N)", min_value=0.0, max_value=300.0, value=float(default_data.get('N', 0.0)), step=1.0, help="Kandungan nitrogen dalam tanah (kg/ha)")
            phosphorus = st.number_input("Fosfor (P)", min_value=0.0, max_value=150.0, value=float(default_data.get('P', 0.0)), step=1.0, help="Fosfor tersedia dalam tanah (kg/ha)")
            potassium = st.number_input("Kalium (K)", min_value=0.0, max_value=300.0, value=float(default_data.get('K', 0.0)), step=1.0, help="Kalium dapat ditukar dalam tanah (kg/ha)")
        
        with col2:
            st.markdown("**Kondisi Iklim**")
            temperature = st.number_input("Suhu (°C)", min_value=10.0, max_value=50.0, value=float(default_data.get('temperature', 25.0)), step=0.1, help="Suhu rata-rata")
            humidity = st.number_input("Kelembaban (%)", min_value=0.0, max_value=100.0, value=float(default_data.get('humidity', 60.0)), step=1.0, help="Persentase kelembaban relatif")
            rainfall = st.number_input("Curah Hujan (mm)", min_value=0.0, max_value=3000.0, value=float(default_data.get('rainfall', 1000.0)), step=10.0, help="Curah hujan tahunan dalam mm")
        
        with col3:
            st.markdown("**Kondisi Tanah**")
            ph = st.number_input("Tingkat pH", min_value=3.0, max_value=10.0, value=float(default_data.get('ph', 6.5)), step=0.1, help="Tingkat pH tanah")
            
            # Additional context
            st.markdown("**Opsional**")
            field_size = st.number_input("Ukuran Lahan (hektar)", min_value=0.1, max_value=1000.0, value=float(default_data.get('field_size', 1.0)), step=0.1, help="Ukuran lahan pertanian")
        
        # Location info display (read-only in form)
        st.markdown("---")
        st.markdown("**📍 Lokasi Terpilih**")
        if location:
            st.info(f"📍 **Lokasi:** {location}")
            if hasattr(st.session_state, 'temp_coordinates') and st.session_state.temp_coordinates:
                coords = st.session_state.temp_coordinates
                st.info(f"🎯 **Koordinat GPS:** {coords['lat']:.6f}°, {coords['lng']:.6f}°")
                # Show source information
                source = "Map Click" if st.session_state.get('selected_location_pin') else "Search/Manual"
                st.success(f"✅ **Sumber:** {source} | **Status:** Koordinat tersedia")
            else:
                st.warning("⚠️ **Tidak ada koordinat GPS** - gunakan tab Interactive Map atau Search Location di atas")
        else:
            st.warning("⚠️ Silakan pilih lokasi di atas terlebih dahulu")
        
        # Crop selection section below the 3 columns
        st.markdown("---")
        col4, col5 = st.columns(2)
        
        with col4:
            st.markdown("**Pilihan Tanaman (Wajib)**")
            crop_options = [
                "Rice", "Maize", "Chickpea", "Kidney Beans", "Pigeon Peas", 
                "Moth Beans", "Mung Bean", "Black Gram", "Lentil", "Pomegranate", 
                "Banana", "Mango", "Watermelon", "Muskmelon", 
                "Orange", "Papaya", "Cotton", "Jute", "Coffee"
            ]
            
            # Create mapping from display names to model names
            crop_mapping = {
                "Rice": "rice",
                "Maize": "maize", 
                "Chickpea": "chickpea",
                "Kidney Beans": "kidneybeans",
                "Pigeon Peas": "pigeonpeas",
                "Moth Beans": "mothbeans",
                "Mung Bean": "mungbean",
                "Black Gram": "blackgram",
                "Lentil": "lentil",
                "Pomegranate": "pomegranate",
                "Banana": "banana",
                "Mango": "mango",
                "Watermelon": "watermelon",
                "Muskmelon": "muskmelon",
                "Orange": "orange",
                "Papaya": "papaya",
                "Cotton": "cotton",
                "Jute": "jute",
                "Coffee": "coffee"
            }
            
            # Get default crop selection
            default_crop = default_data.get('selected_crop', 'rice')
            # Find display name for default crop
            default_crop_display = None
            for display_name, model_name in crop_mapping.items():
                if model_name == default_crop:
                    default_crop_display = display_name
                    break
            if not default_crop_display:
                default_crop_display = crop_options[0]
            
            # Get index for default selection
            default_index = crop_options.index(default_crop_display) if default_crop_display in crop_options else 0
            
            selected_crop_display = st.selectbox("Pilih Tanaman", crop_options, index=default_index, help="Pilih tanaman yang ingin Anda tanam")
            selected_crop = crop_mapping.get(selected_crop_display, selected_crop_display.lower())
        
        with col5:
            # Empty column for spacing
            st.markdown("")
        
        # Submit button
        submitted = st.form_submit_button("🔍 Dapatkan Rekomendasi Tanaman & Lingkungan", type="primary")

        # --- LLM Evaluation Summary (from your previous notebook results) ---
        llm_evaluation_summary = """
## Evaluation Results Summary

### 1. Masked Language Modeling Performance
- Perplexity: 9.18 (lower is better)
- Top-1 Accuracy: 55.1% - The model correctly predicts the masked word on first try
- Top-5 Accuracy: 79.1% - The correct word appears in the top 5 predictions
- Average Loss: 2.22

### 2. Agricultural Domain Knowledge
- Overall Domain Accuracy: 97.4% - Excellent performance on agricultural terms
- Terms Evaluated: 23 agricultural terms
- Perfect Performance: Terms like "germination", "organic", "rotation", "farming", "irrigation" achieved 100% accuracy
- Strong Performance: "soil" achieved 95% accuracy with 20 samples

### 3. Semantic Coherence
- Mean Q-A Similarity: 0.538 - Moderate semantic alignment between questions and answers
- Similarity Range: Varies from very low to very high coherence

### 4. Fill-Mask Task Performance
- Fill-Mask Accuracy: 76.9% - Good performance on contextual word prediction
- Examples Evaluated: 13 real-world agricultural texts

### 5. Overall Performance Rating
- Composite Score: 0.805/1.000
- Rating: EXCELLENT
- Model Specifications: 109.9M parameters, 31K vocabulary
"""

        # Use session state to control dialog visibility
        if 'show_llm_dialog' not in st.session_state:
            st.session_state['show_llm_dialog'] = False

        if submitted:
            # Debug all session state data before processing
            print(f"🚀 FORM SUBMISSION STARTED:")
            print(f"  📍 Current location variable: {location}")
            print(f"  🗺️ selected_location_pin: {st.session_state.get('selected_location_pin')}")
            print(f"  📊 selected_location: {st.session_state.get('selected_location')}")
            print(f"  🎯 temp_coordinates: {st.session_state.get('temp_coordinates')}")
            
            # Prepare sensor data with enhanced location information
            sensor_data = {
                'N': nitrogen,
                'P': phosphorus,
                'K': potassium,
                'temperature': temperature,
                'humidity': humidity,
                'ph': ph,
                'rainfall': rainfall,
                'field_size': field_size,
                'location': location,
                'selected_crop': selected_crop
            }
            
            # Determine location source and coordinates with priority logic
            if st.session_state.get('selected_location_pin'):
                # Highest priority: Direct pin data
                pin_data = st.session_state.selected_location_pin
                sensor_data['coordinates'] = {'lat': pin_data['lat'], 'lng': pin_data['lng']}
                sensor_data['location_source'] = 'map_click_with_red_pin'
                print(f"✅ Using PIN DATA - Coordinates: {sensor_data['coordinates']}")
            elif hasattr(st.session_state, 'temp_coordinates') and st.session_state.temp_coordinates:
                # Second priority: temp_coordinates
                sensor_data['coordinates'] = st.session_state.temp_coordinates
                source_data = st.session_state.get('selected_location', {})
                sensor_data['location_source'] = source_data.get('source', 'map_click_with_red_pin')
                print(f"✅ Using TEMP_COORDINATES - Coordinates: {sensor_data['coordinates']}")
            else:
                # No coordinates available - user needs to select location
                sensor_data['location_source'] = 'not_selected'
                print(f"⚠️ NO COORDINATES - User must select location using Interactive Map or Search")
            
            # Debug: Print final sensor data before saving
            print(f"📊 FINAL SENSOR DATA:")
            print(f"  📍 Location: {sensor_data.get('location')}")
            print(f"  🌍 Coordinates: {sensor_data.get('coordinates')}")
            print(f"  📊 Location Source: {sensor_data.get('location_source')}")
            
            # Validate location selection
            if sensor_data.get('location_source') == 'not_selected' or not sensor_data.get('coordinates'):
                st.error("❌ **Lokasi belum dipilih!** Silakan pilih lokasi menggunakan:")
                st.info("🗺️ **Interactive Map** - Klik pada peta untuk menambah pin merah")
                st.info("🔍 **Search Location** - Cari nama daerah untuk mendapat koordinat GPS")
                return None
            
            print(f"  🔄 Validation passed - Ready for MongoDB save")
            
            # ✅ Clear preset data AFTER successful form submission
            if preset_data:
                st.session_state.preset_data = None
                st.session_state.preset_name = None
            
            # ✅ IMMEDIATELY save interaction when user submits
            interaction_id = save_interaction(sensor_data)
            if interaction_id:
                st.success("✅ Interaction saved to history!")
                # Force sidebar to show updated history
                st.session_state.sidebar_mode = 'history'
                # Store dialog and data for after rerun
                st.session_state['show_llm_dialog'] = True
                st.session_state['last_sensor_data'] = sensor_data
                # Force immediate UI refresh to update sidebar
                st.rerun()

        # Show dialog if triggered (after rerun)
        if st.session_state.get('show_llm_dialog', False):
            @st.dialog("Hasil Evaluation LLM")
            def show_llm_dialog():
                st.markdown(llm_evaluation_summary)
                if st.button("Tutup", key="close_llm_dialog"):
                    st.session_state['show_llm_dialog'] = False
                    st.rerun()
            show_llm_dialog()

        # Process form submission (return data for analysis)
        if submitted and not st.session_state.get('show_llm_dialog', False):
            sensor_data = st.session_state.get('last_sensor_data')
            if sensor_data:
                return sensor_data
    return None

def display_results(sensor_data, decision_system):
    """Display ML crop evaluation and AI environmental recommendations"""
    
    st.markdown("---")
    st.markdown("## 📈 Hasil Analisis")
    
    # ML Crop Evaluation Section
    ml_evaluation = None
    ai_evaluation = None
    ai_predictor = decision_system.get_ai_predictor()
    
    if ai_predictor:
        st.markdown("### 🤖 Evaluasi Kesesuaian Tanaman")
        
        with st.spinner("Mengevaluasi kesesuaian tanaman dengan kondisi lingkungan"):
            try:
                # Get ML evaluation - returns tuple (crop_name, confidence, explanation)
                selected_crop = sensor_data.get('selected_crop', 'Unknown')
                crop_name, confidence, explanation = ai_predictor.evaluate_crop_suitability(sensor_data, selected_crop)
                
                # Display evaluation results
                col1, col2 = st.columns(2)
                
                with col1:
                    st.success(f"**Tanaman yang Dipilih:** {crop_name}")
                
                with col2:
                    # Determine color based on suitability level
                    if confidence >= 0.7:
                        st.success(f"**Tingkat Kesesuaian:** {confidence*100:.1f}% - Sangat Cocok")
                    elif confidence >= 0.5:
                        st.warning(f"**Tingkat Kesesuaian:** {confidence*100:.1f}% - Cukup Cocok")
                    else:
                        st.error(f"**Tingkat Kesesuaian:** {confidence*100:.1f}% - Kurang Cocok")
                
                # Show SHAP explanation for low confidence
                if explanation and confidence < 0.5:
                    st.markdown("---")
                    st.markdown(explanation)
                
                ml_evaluation = (crop_name, confidence, explanation)
                
            except Exception as e:
                st.error(f"❌ ML prediction error: {str(e)}")
                st.info("Continuing with AI-only analysis...")
    else:
        if decision_system.ai_predictor_error:
            st.warning(f"⚠️ Evaluasi tanaman ML tidak tersedia: {decision_system.ai_predictor_error}")
        st.info("📊 Melanjutkan dengan analisis lingkungan AI saja...")
    
    # AI Environmental Recommendations Section  
    st.markdown("### 🧠 Optimisasi Lingkungan AI")
    
    with st.spinner("Menghasilkan rekomendasi lingkungan yang dipersonalisasi..."):
        environmental_advice = decision_system.generate_environmental_advice(sensor_data, ml_evaluation)
        ai_evaluation = environmental_advice  # Store AI result
        st.markdown(environmental_advice)
    
    # Summary Section
    st.markdown("### 📋 Ringkasan Cepat")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Ukuran Lahan", f"{sensor_data.get('field_size', 'N/A')} ha")
        st.metric("pH Tanah", f"{sensor_data.get('ph', 'N/A')}")
    
    with col2:
        st.metric("Suhu", f"{sensor_data.get('temperature', 'N/A')}°C")
        st.metric("Curah Hujan", f"{sensor_data.get('rainfall', 'N/A')} mm")
    
    with col3:
        if ml_evaluation and len(ml_evaluation) >= 2:
            # Handle tuple format (crop_name, confidence, explanation)
            confidence = ml_evaluation[1] * 100  # Convert to percentage
            st.metric("Tingkat Kesesuaian", f"{confidence:.1f}%")
        st.metric("Tanggal Analisis", datetime.now().strftime("%Y-%m-%d"))
    
    with col4:
        # Enhanced location display with coordinates
        location_display = sensor_data.get('location', 'N/A')
        if len(location_display) > 25:
            location_display = location_display[:22] + "..."
        st.metric("Lokasi", location_display)
        
        # Show coordinates if available
        if sensor_data.get('coordinates'):
            coords = sensor_data['coordinates']
            st.metric("Koordinat", f"{coords['lat']:.3f}°, {coords['lng']:.3f}°")
        else:
            st.metric("Sumber Lokasi", sensor_data.get('location_source', 'Manual'))
    
    # Enhanced location information section
    if sensor_data.get('coordinates') or sensor_data.get('location_source') == 'map':
        st.markdown("---")
        st.markdown("### 📍 Detail Lokasi Lengkap")
        
        with st.expander("🗺️ Informasi Lokasi & Koordinat", expanded=False):
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**📌 Informasi Lokasi:**")
                st.markdown(f"- **Alamat:** {sensor_data.get('location', 'N/A')}")
                st.markdown(f"- **Sumber:** {sensor_data.get('location_source', 'Manual')}")
                
                if sensor_data.get('coordinates'):
                    coords = sensor_data['coordinates']
                    st.markdown(f"- **Akurasi Koordinat:** ±10 meter")
                    st.markdown(f"- **Format GPS:** {coords['lat']:.6f}°, {coords['lng']:.6f}°")
            
            with col2:
                if sensor_data.get('coordinates'):
                    coords = sensor_data['coordinates']
                    st.markdown("**🔗 Link Eksternal:**")
                    st.markdown(f"- [📱 Google Maps](https://www.google.com/maps?q={coords['lat']},{coords['lng']})")
                    st.markdown(f"- [🌍 Google Earth](https://earth.google.com/web/@{coords['lat']},{coords['lng']},1000a,35y,0h,0t,0r)")
                    st.markdown(f"- **📋 Copy Koordinat:** `{coords['lat']:.6f}, {coords['lng']:.6f}`")
                else:
                    st.markdown("**ℹ️ Info:**")
                    st.markdown("- Koordinat GPS tidak tersedia")
                    st.markdown("- Gunakan Interactive Map untuk koordinat presisi")
                    st.markdown("- Analisis berdasarkan nama lokasi")
    
    # Update current interaction with results
    if st.session_state.current_interaction_id and (ml_evaluation or ai_evaluation):
        update_interaction_results(st.session_state.current_interaction_id, ml_evaluation, ai_evaluation)

# ==================== INTERACTION HISTORY MANAGEMENT ====================

def save_interaction(sensor_data, ml_result=None, ai_result=None):
    """Save current interaction to history with MongoDB persistence"""
    try:
        import uuid
        from datetime import datetime
        
        # Validate input
        if not sensor_data or not isinstance(sensor_data, dict):
            raise ValueError("sensor_data must be a non-empty dictionary")
        
        # Create interaction
        interaction = {
            'id': str(uuid.uuid4())[:8],
            'timestamp': datetime.now(),
            'sensor_data': sensor_data.copy(),
            'ml_result': ml_result,
            'ai_result': ai_result,
            'title': f"{sensor_data.get('selected_crop', 'Unknown')} - {sensor_data.get('location', 'Unknown')}"
        }
        
        # Initialize history if not exists
        if 'interaction_history' not in st.session_state:
            st.session_state.interaction_history = []
        
        # Append to local session state
        st.session_state.interaction_history.append(interaction)
        st.session_state.current_interaction_id = interaction['id']
        
        # Save to MongoDB
        mongo_manager = get_mongodb_manager()
        if mongo_manager.connected:
            save_result = mongo_manager.save_interaction(interaction)
        else:
            print("⚠️ MongoDB not connected - data saved only to session state")
        
        # Keep only last 50 interactions in session state to prevent memory issues
        if len(st.session_state.interaction_history) > 50:
            st.session_state.interaction_history = st.session_state.interaction_history[-50:]
        
        return interaction['id']
        
    except Exception as e:
        st.error(f"❌ Failed to save interaction: {str(e)}")
        return None

def load_interaction(interaction_id):
    """Load interaction from history"""
    for interaction in st.session_state.interaction_history:
        if interaction['id'] == interaction_id:
            return interaction
    return None

def restore_location_from_interaction(interaction_data):
    """Restore location data to session state from loaded interaction"""
    if not interaction_data:
        print("⚠️ No interaction data to restore location from")
        return
    
    sensor_data = interaction_data.get('sensor_data', {})
    coordinates = sensor_data.get('coordinates')
    location = sensor_data.get('location')
    location_source = sensor_data.get('location_source', 'unknown')
    
    print(f"🔄 Restoring location from interaction:")
    print(f"  📍 Location: {location}")
    print(f"  🌍 Coordinates: {coordinates}")
    print(f"  📊 Source: {location_source}")
    
    if coordinates and location:
        # Restore to session state for map display and form usage
        st.session_state.selected_location = {
            'coordinates': coordinates,
            'address': location,
            'source': location_source
        }
        
        # Also restore temp_coordinates for form integration
        st.session_state.temp_coordinates = coordinates
        
        # If it's from map click, also restore to pin state for map display
        if location_source == 'map_click_with_red_pin':
            st.session_state.selected_location_pin = {
                'lat': coordinates['lat'],
                'lng': coordinates['lng'],
                'address': location,
                'timestamp': 1  # Single pin mode
            }
            # Force map refresh to show restored pin
            st.session_state.map_refresh_counter = st.session_state.get('map_refresh_counter', 0) + 1
        else:
            # Clear pin state for non-map sources
            st.session_state.selected_location_pin = None
        
        print(f"✅ Location restored to session state:")
        print(f"  📍 selected_location: {st.session_state.selected_location}")
        print(f"  🌍 temp_coordinates: {st.session_state.temp_coordinates}")
        if hasattr(st.session_state, 'selected_location_pin') and st.session_state.selected_location_pin:
            print(f"  📍 selected_location_pin: {st.session_state.selected_location_pin}")
    else:
        print("⚠️ No coordinates found in interaction - clearing location session state")
        # Clear location session state if no coordinates
        st.session_state.selected_location = None
        st.session_state.temp_coordinates = None
        st.session_state.selected_location_pin = None

def display_interaction_history():
    """Display interaction history in sidebar"""
    st.markdown("### 📋 Interaction History")
    
    if not st.session_state.interaction_history:
        st.info("Belum ada interaksi tersimpan")
        st.markdown("*Gunakan **➕ New** untuk membuat preset atau input manual*")
        return
    
    # Show total count with summary
    total = len(st.session_state.interaction_history)
    if total == 1:
        st.caption(f"📊 Total: {total} interaction")
    else:
        st.caption(f"📊 Total: {total} interactions")
    
    # Sort by timestamp (newest first)
    sorted_history = sorted(st.session_state.interaction_history, 
                           key=lambda x: x['timestamp'], reverse=True)
    
    for i, interaction in enumerate(sorted_history):
        timestamp = interaction['timestamp'].strftime("%d/%m")
        time_only = interaction['timestamp'].strftime("%H:%M")
        
        # Convert to Indonesian date format
        months_indo = {
            1: 'Januari', 2: 'Februari', 3: 'Maret', 4: 'April',
            5: 'Mei', 6: 'Juni', 7: 'Juli', 8: 'Agustus',
            9: 'September', 10: 'Oktober', 11: 'November', 12: 'Desember'
        }
        dt = interaction['timestamp']
        timestamp_indo = f"{dt.day} {months_indo[dt.month]} {dt.year}"
        
        sensor_data = interaction['sensor_data']
        
        # Get crop info with icon
        crop = sensor_data.get('selected_crop', 'unknown')
        crop_icons = {
            'rice': '🌾', 'maize': '🌽', 'cotton': '🏭', 'banana': '🍌',
            'mango': '🥭', 'orange': '🍊', 'coffee': '☕', 'pomegranate': '🍇',
            'watermelon': '🍉', 'chickpea': '🫘', 'kidneybeans': '🫘',
            'lentil': '🫘', 'blackgram': '🫘', 'mungbean': '🫘',
            'pigeonpeas': '🫘', 'mothbeans': '🫘', 'papaya': '🍈',
            'jute': '🌿', 'muskmelon': '🍈'
        }
        crop_icon = crop_icons.get(crop, '🌱')
        crop_display = crop.replace('_', ' ').title()
        
        # Get location (simplified)
        location = sensor_data.get('location', 'Unknown')
        location_short = location.split(',')[0] if ',' in location else location
        
        # Create interactive card button
        is_active = interaction['id'] == st.session_state.current_interaction_id
        
        if is_active:
            # Active card with improved spacing
            st.markdown(f"""
            <div style="
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                border-radius: 10px;
                padding: 12px 14px;
                margin: 6px 0;
                color: white;
                box-shadow: 0 2px 8px rgba(102, 126, 234, 0.3);
                border: 1px solid #667eea;
            ">
                <div style="display: flex; align-items: center; justify-content: space-between;">
                    <div style="display: flex; align-items: center; gap: 10px;">
                        <span style="font-size: 18px;">{crop_icon}</span>
                        <div>
                            <div style="font-weight: bold; font-size: 14px; line-height: 1.3; margin-bottom: 3px;">
                                {crop_display}
                            </div>
                            <div style="font-size: 11px; opacity: 0.85; line-height: 1.2;">
                                {location_short} - {timestamp_indo}
                            </div>
                        </div>
                    </div>
                    <span style="font-size: 10px; opacity: 0.9;">🟢</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
        else:
            # Interactive card button with improved spacing
            card_html = f"""
            <div style="
                background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
                border-radius: 10px;
                padding: 12px 14px;
                margin: 6px 0;
                color: #2c3e50;
                border: 1px solid #e0e6ed;
                transition: all 0.2s ease;
                cursor: pointer;
                box-shadow: 0 1px 6px rgba(0,0,0,0.1);
            " onmouseover="this.style.transform='translateY(-1px)'; this.style.boxShadow='0 2px 12px rgba(0,0,0,0.15)';" 
               onmouseout="this.style.transform='translateY(0px)'; this.style.boxShadow='0 1px 6px rgba(0,0,0,0.1)';">
                <div style="display: flex; align-items: center; justify-content: space-between;">
                    <div style="display: flex; align-items: center; gap: 10px; flex: 1; min-width: 0;">
                        <span style="font-size: 18px;">{crop_icon}</span>
                        <div style="flex: 1; min-width: 0;">
                            <div style="font-weight: bold; font-size: 14px; line-height: 1.3; color: #2c3e50; margin-bottom: 3px;">
                                {crop_display}
                            </div>
                            <div style="font-size: 11px; color: #34495e; line-height: 1.2;">
                                {location_short} - {timestamp_indo}
                            </div>
                        </div>
                    </div>
                    <span style="font-size: 11px; color: #7f8c8d;">🔄</span>
                </div>
            </div>
            """
            
            # Create clickable container with improved alignment
            container_col1, container_col2 = st.columns([8, 2])
            with container_col1:
                st.markdown(card_html, unsafe_allow_html=True)
            with container_col2:
                # Add top margin to align button with card center
                st.markdown('<div style="margin-top: 6px;"></div>', unsafe_allow_html=True)
                if st.button("📂", key=f"load_{interaction['id']}", help=f"Load {crop_display} from {location_short}", 
                           use_container_width=True, type="secondary"):
                    st.session_state.current_interaction_id = interaction['id']
                    # Restore location data to session state for map display
                    restore_location_from_interaction(interaction)
                    st.rerun()
        
        # Add confidence badge if available
        if interaction['ml_result'] and len(interaction['ml_result']) >= 2:
            confidence = interaction['ml_result'][1] * 100
            if confidence >= 70:
                badge_color = "#27ae60"
                badge_text = "HIGH"
            elif confidence >= 50:
                badge_color = "#f39c12"
                badge_text = "MED"
            else:
                badge_color = "#e74c3c"
                badge_text = "LOW"
            
            # Use same column layout for badge alignment
            badge_col1, badge_col2 = st.columns([8, 2])
            with badge_col1:
                st.markdown(f"""
                <div style="
                    background: {badge_color};
                    color: white;
                    padding: 2px 6px;
                    border-radius: 8px;
                    font-size: 9px;
                    font-weight: bold;
                    text-align: center;
                    margin: -2px 0 8px 0;
                    display: inline-block;
                ">
                    🤖 {badge_text} ({confidence:.0f}%)
                </div>
                """, unsafe_allow_html=True)
        else:
            # Add spacing when no confidence badge
            st.markdown("<div style='margin-bottom: 4px;'></div>", unsafe_allow_html=True)

def display_new_interaction_form():
    """Display form for creating new interaction in sidebar"""
    st.markdown("### ➕ New Interaction")
    
    with st.form("sidebar_new_interaction", clear_on_submit=False):
        st.markdown("**Quick Setup**")
        
        # Quick presets
        preset = st.selectbox("📋 Preset", [
            "Custom", "Rice - Tropical", "Maize - Dry Season", 
            "Cotton - Commercial", "Banana - Humid"
        ])
        
        # Show preset info
        if preset != "Custom":
            if preset == "Rice - Tropical":
                st.info("🌾 Padi untuk iklim tropis dengan kelembaban tinggi")
            elif preset == "Maize - Dry Season":
                st.info("🌽 Jagung untuk musim kemarau dengan curah hujan sedang")
            elif preset == "Cotton - Commercial":
                st.info("🏭 Kapas komersial dengan nutrisi tinggi")
            elif preset == "Banana - Humid":
                st.info("🍌 Pisang untuk daerah lembab")
        
        # Submit button (always visible)
        if preset != "Custom":
            submitted = st.form_submit_button("📝 Use Main Form", type="primary")
        else:
            submitted = st.form_submit_button("📝 Use Main Form", type="secondary")
        
        # Handle submission
        if submitted:
            if preset != "Custom":
                # Define preset data (don't save as interaction yet)
                preset_data = {}
                if preset == "Rice - Tropical":
                    preset_data = {
                        'N': 80, 'P': 40, 'K': 40, 'temperature': 26, 
                        'humidity': 80, 'ph': 6.5, 'rainfall': 1200,
                        'field_size': 2.0, 'selected_crop': 'rice', 'location': 'Jawa Barat'
                    }
                elif preset == "Maize - Dry Season":
                    preset_data = {
                        'N': 90, 'P': 50, 'K': 30, 'temperature': 28,
                        'humidity': 55, 'ph': 6.8, 'rainfall': 800,
                        'field_size': 3.0, 'selected_crop': 'maize', 'location': 'Jawa Tengah'
                    }
                elif preset == "Cotton - Commercial":
                    preset_data = {
                        'N': 120, 'P': 70, 'K': 150, 'temperature': 30,
                        'humidity': 45, 'ph': 7.2, 'rainfall': 600,
                        'field_size': 5.0, 'selected_crop': 'cotton', 'location': 'Sulawesi'
                    }
                elif preset == "Banana - Humid":
                    preset_data = {
                        'N': 100, 'P': 60, 'K': 180, 'temperature': 27,
                        'humidity': 85, 'ph': 6.0, 'rainfall': 1500,
                        'field_size': 1.5, 'selected_crop': 'banana', 'location': 'Kalimantan'
                    }
                
                # Store preset data in session state for main form to use
                st.session_state.preset_data = preset_data
                st.session_state.preset_name = preset
                st.session_state.current_interaction_id = None  # Clear any loaded interaction
                st.session_state.sidebar_mode = 'history'
                st.success(f"✅ {preset} loaded to main form! Please review and edit parameters, then submit.")
                st.rerun()
            else:
                # Custom - just clear current interaction and switch to main form
                st.session_state.sidebar_mode = 'history'
                st.session_state.current_interaction_id = None
                st.session_state.preset_data = None
                st.session_state.preset_name = None
                st.info("💡 Use the main form to create a custom interaction")
                st.rerun()
    
    # Management tools
    if len(st.session_state.interaction_history) > 0:
        st.markdown("---")
        st.markdown("**🛠️ Management**")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🗑️ Clear", type="secondary", help="Clear all saved interactions"):
                # Clear session state
                st.session_state.interaction_history = []
                st.session_state.current_interaction_id = None
                st.session_state.preset_data = None
                st.session_state.preset_name = None
                
                # Clear MongoDB
                mongo_manager = get_mongodb_manager()
                if mongo_manager.connected:
                    if mongo_manager.clear_all_interactions():
                        st.success("✅ History cleared from database and session!")
                    else:
                        st.warning("⚠️ Session cleared, but database clear failed")
                else:
                    st.success("✅ Session history cleared!")
                
                st.rerun()
        
        with col2:
            total_interactions = len(st.session_state.interaction_history)
            st.caption(f"💾 {total_interactions} saved")
    


def update_interaction_results(interaction_id, ml_result=None, ai_result=None):
    """Update interaction with ML and AI results in both session state and MongoDB"""
    # Update session state
    for i, interaction in enumerate(st.session_state.interaction_history):
        if interaction['id'] == interaction_id:
            if ml_result:
                st.session_state.interaction_history[i]['ml_result'] = ml_result
            if ai_result:
                st.session_state.interaction_history[i]['ai_result'] = ai_result
            break
    
    # Update MongoDB
    mongo_manager = get_mongodb_manager()
    if mongo_manager.connected:
        mongo_manager.update_interaction_results(interaction_id, ml_result, ai_result)

def get_current_interaction_data():
    """Get current interaction data if any"""
    if st.session_state.current_interaction_id:
        return load_interaction(st.session_state.current_interaction_id)
    return None



# ==================== MAIN APPLICATION ====================

def main():
    """Main application function"""
    
    st.set_page_config(
        page_title="Sistem Pendukung Keputusan Pertanian",
        page_icon="🌾",
        layout="wide",
        initial_sidebar_state="auto"
    )
    
    # Initialize session state with global session mode (no user isolation)
    if 'session_id' not in st.session_state:
        # Use consistent global session ID for agricultural application
        # This ensures all interactions are persistent across refreshes
        st.session_state.session_id = "agricultural_global_session"
    
    if 'interaction_history' not in st.session_state:
        st.session_state.interaction_history = []
        # Try to load existing interactions from MongoDB
        mongo_manager = get_mongodb_manager()
        if mongo_manager.connected:
            loaded_interactions = mongo_manager.load_interactions()
            if loaded_interactions:
                st.session_state.interaction_history = loaded_interactions
                # Show success message to user (but keep it brief per memory)
                print(f"✅ Loaded {len(loaded_interactions)} interactions from MongoDB")
                
                # If there's a current_interaction_id set, restore its location data
                if st.session_state.get('current_interaction_id'):
                    current_interaction = get_current_interaction_data()
                    if current_interaction:
                        restore_location_from_interaction(current_interaction)
                        print(f"🔄 Location restored for current interaction on app startup")
        else:
            print("ℹ️ MongoDB not connected - starting with empty history")
    
    if 'current_interaction_id' not in st.session_state:
        st.session_state.current_interaction_id = None
    if 'sidebar_mode' not in st.session_state:
        st.session_state.sidebar_mode = 'history'  # 'history' or 'new'
    
    # Initialize preset-related session state
    if 'preset_data' not in st.session_state:
        st.session_state.preset_data = None
    if 'preset_name' not in st.session_state:
        st.session_state.preset_name = None
    
    # Sidebar
    with st.sidebar:
        st.markdown("# 🌾 Menu")
        st.markdown("---")
        
        # Mode selection
        col1, col2 = st.columns(2)
        with col1:
            if st.button("📋 History", type="primary" if st.session_state.sidebar_mode == 'history' else "secondary"):
                st.session_state.sidebar_mode = 'history'
        with col2:
            if st.button("➕ New", type="primary" if st.session_state.sidebar_mode == 'new' else "secondary"):
                st.session_state.sidebar_mode = 'new'
                st.session_state.current_interaction_id = None
                st.session_state.preset_data = None
                st.session_state.preset_name = None
        
        st.markdown("---")
        
        if st.session_state.sidebar_mode == 'history':
            display_interaction_history()
        else:
            display_new_interaction_form()
    
    # Header
    st.title("🌾 Sistem Pendukung Keputusan Pertanian Indonesia")
    st.markdown("*Dapatkan rekomendasi tanaman instan dan saran optimisasi lingkungan berdasarkan kondisi lahan Anda*")
    
    # Map integration status
    if STREAMLIT_FOLIUM_AVAILABLE and FOLIUM_AVAILABLE:
        st.success("🗺️ **NEW**: Interactive Map (Single Pin Mode) - Klik untuk tambah/pindah pin dengan koordinat presisi!")
    elif FOLIUM_AVAILABLE:
        st.warning("🗺️ Map mode tersedia terbatas (folium only)")
    else:
        st.info("🗺️ Map mode tidak tersedia - menggunakan input lokasi manual")
    

    

    
    # Initialize decision support system
    decision_system = DecisionSupportSystem()
    
    # Main input form
    sensor_data = display_sensor_input_form()
    
    # Display results if data is submitted
    if sensor_data:
        display_results(sensor_data, decision_system)
        
        # Action buttons
        st.markdown("---")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("🔄 Analisis Kondisi Berbeda", type="secondary"):
                st.rerun()
        
        with col2:
            if st.button("📊 Ekspor Hasil", type="secondary"):
                st.info("Fitur ekspor akan segera hadir!")
        
        with col3:
            if st.button("📖 Lihat Panduan Detail", type="secondary"):
                st.info("Panduan implementasi detail akan segera hadir!")
    
    # Footer
    st.markdown("---")

if __name__ == "__main__":
    main()