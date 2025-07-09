"""
Main Application for Agricultural Decision Support System
Entry point for the modular Streamlit application.

To run this application:
1. Make sure you're in the project root directory
2. Run: streamlit run src/main.py

Note: This is a partial refactoring. See REFACTORING_GUIDE.md for continuation steps.
"""

import streamlit as st
import sys
import os
import numpy as np
from datetime import datetime
from typing import Dict, List, Any, Optional

# Add the project root to the Python path so we can import our modules
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)

# Import our modular components
from src.utils.config import UI_CONFIG, CROP_MAPPING, SENSOR_PARAMS
from src.utils.helpers import (
    init_session_state, check_library_availability, 
    clear_location_data, format_timestamp
)
from src.services.database import (
    get_mongodb_manager, init_database_session, 
    save_interaction_to_db, load_interactions_from_db
)
from src.services.location import (
    get_user_gps_location, get_current_location_data, 
    integrate_location_to_form, clear_all_location_data
)
from src.services.mapping import (
    display_interactive_map, handle_map_click, 
    update_map_pin_location, clear_map_pin,
    check_map_dependencies
)
from src.core.ml_predictor import AICropPredictor

# ==================== APP CONFIGURATION ====================

def configure_streamlit():
    """Configure Streamlit page settings"""
    st.set_page_config(
        page_title=UI_CONFIG['page_title'],
        page_icon=UI_CONFIG['page_icon'], 
        layout=UI_CONFIG['layout'],
        initial_sidebar_state="expanded"
    )

def initialize_app():
    """Initialize application state and dependencies"""
    
    # Initialize session state
    init_session_state()
    
    # Initialize database session
    init_database_session()
    
    # Load interaction history from MongoDB if not already loaded
    if not st.session_state.interaction_history:
        mongo_manager = get_mongodb_manager()
        if mongo_manager.is_connected():
            loaded_interactions = load_interactions_from_db()
            if loaded_interactions:
                st.session_state.interaction_history = loaded_interactions
                print(f"✅ Loaded {len(loaded_interactions)} interactions from MongoDB")
                
                # If there's a current_interaction_id set, restore its location data
                if st.session_state.get('current_interaction_id'):
                    from src.components.history_panel import get_current_interaction_data, restore_location_from_interaction
                    current_interaction = get_current_interaction_data()
                    if current_interaction:
                        restore_location_from_interaction(current_interaction)
                        print(f"🔄 Location restored for current interaction on app startup")
        else:
            print("ℹ️ MongoDB not connected - starting with empty history")
    
    # Check library availability
    library_status = check_library_availability()
    
    # Print status to console
    print("📋 Agricultural Decision Support System - Modular Version")
    print("=" * 60)
    for lib, available in library_status.items():
        status = "✅" if available else "❌"
        print(f"{status} {lib.replace('_', ' ').title()}")
    print("=" * 60)

# ==================== LOCATION SELECTION INTERFACE ====================

def display_location_selection():
    """Display location selection interface (GPS + Map + Search)"""
    
    st.markdown("## 📍 Pilih Lokasi Lahan Pertanian")
    
    # Check for existing location states
    if st.session_state.get('selected_location_pin'):
        display_pin_mode()
        return
    
    if st.session_state.get('gps_auto_refresh_completed'):
        display_gps_completed_mode()
        return
    
    # Show location selection tabs
    display_location_tabs()

def display_pin_mode():
    """Display when a map pin is selected"""
    pin = st.session_state.selected_location_pin
    
    st.success("✅ **Lokasi Interactive Map Terpilih**")
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.markdown(f"📍 **Lokasi:** {pin['address']}")
        st.markdown(f"🎯 **Koordinat:** {pin['lat']:.6f}°, {pin['lng']:.6f}°")
        st.markdown(f"🗺️ **Google Maps:** [Buka Lokasi](https://www.google.com/maps?q={pin['lat']},{pin['lng']})")
    
    with col2:
        if st.button("🗑️ Hapus Pin", type="secondary"):
            clear_map_pin()
            st.rerun()
    
    
    map_data = display_interactive_map(existing_pins=pin)
    
    if map_data:
        new_location = handle_map_click(map_data)
        if new_location:
            update_map_pin_location(
                new_location['lat'], 
                new_location['lng'], 
                new_location['address']
            )
            st.rerun()

def display_gps_completed_mode():
    """Display when GPS auto-refresh is completed"""
    gps_data = st.session_state.gps_location_data
    
    st.success("✅ **GPS Location Berhasil Dideteksi**")
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.markdown(f"📍 **Lokasi:** {gps_data['address']}")
        st.markdown(f"🎯 **Koordinat:** {gps_data['lat']:.6f}°, {gps_data['lng']:.6f}°")
        st.markdown(f"📊 **Akurasi:** {gps_data['accuracy']:.0f}m")
        st.markdown(f"🗺️ **Google Maps:** [Buka Lokasi](https://www.google.com/maps?q={gps_data['lat']},{gps_data['lng']})")
    
    with col2:
        if st.button("✏️ Edit GPS", type="secondary"):
            st.session_state.gps_auto_refresh_completed = False
            st.rerun()

def display_location_tabs():
    """Display location selection tabs"""
    
    tab1, tab2, tab3 = st.tabs(["🛰️ GPS Location", "🗺️ Interactive Map", "🔍 Search Location"])
    
    with tab1:
        st.markdown("### 🛰️ GPS Location Detection")
        get_user_gps_location()
    
    with tab2:
        st.markdown("### 🗺️ Interactive Map")
        if check_map_dependencies()['folium'] and check_map_dependencies()['streamlit_folium']:
            map_data = display_interactive_map()
            
            if map_data:
                new_location = handle_map_click(map_data)
                if new_location:
                    update_map_pin_location(
                        new_location['lat'], 
                        new_location['lng'], 
                        new_location['address']
                    )
                    st.rerun()
        else:
            st.error("⚠️ **Interactive Map tidak tersedia** - Map libraries tidak terinstall")
            st.info("💡 **Solusi:** Install dengan `pip install folium streamlit-folium`")
    
    with tab3:
        st.markdown("### 🔍 Search Location by Name")
        st.info("🚧 **Under Development** - Fitur pencarian lokasi sedang dalam pengembangan")
        st.markdown("💡 **Sementara ini:** Gunakan GPS atau Interactive Map untuk memilih lokasi")

# ==================== SENSOR INPUT FORM ====================

def clamp_sensor_value(param_name: str, value: float) -> float:
    """Clamp sensor value to be within valid range to prevent Streamlit errors"""
    
    if param_name not in SENSOR_PARAMS:
        return value
    
    param_config = SENSOR_PARAMS[param_name]
    min_val = param_config['min']
    max_val = param_config['max']
    
    # Clamp value to be within valid range
    clamped_value = max(min_val, min(max_val, value))
    
    # Log if clamping occurred
    if clamped_value != value:
        print(f"⚠️ CLAMPED {param_name}: {value} → {clamped_value} (range: {min_val}-{max_val})")
    
    return clamped_value

def validate_and_fix_default_data(default_data: dict) -> dict:
    """Validate and fix default data to ensure all values are within valid ranges"""
    
    fixed_data = default_data.copy()
    
    # Map of possible parameter names to standard names
    param_mapping = {
        'N': 'nitrogen',
        'P': 'phosphorus', 
        'K': 'potassium',
        'temperature': 'temperature',
        'humidity': 'humidity',
        'ph': 'ph',
        'rainfall': 'rainfall'
    }
    
    for key, standard_name in param_mapping.items():
        if key in fixed_data:
            try:
                original_value = float(fixed_data[key])
                clamped_value = clamp_sensor_value(standard_name, original_value)
                fixed_data[key] = clamped_value
            except (ValueError, TypeError):
                # If conversion fails, use default from config
                fixed_data[key] = SENSOR_PARAMS[standard_name]['default']
                print(f"⚠️ INVALID {key}: Using default {SENSOR_PARAMS[standard_name]['default']}")
    
    # Also check standard parameter names
    for param_name in ['nitrogen', 'phosphorus', 'potassium', 'temperature', 'humidity', 'ph', 'rainfall']:
        if param_name in fixed_data:
            try:
                original_value = float(fixed_data[param_name])
                clamped_value = clamp_sensor_value(param_name, original_value)
                fixed_data[param_name] = clamped_value
            except (ValueError, TypeError):
                fixed_data[param_name] = SENSOR_PARAMS[param_name]['default']
                print(f"⚠️ INVALID {param_name}: Using default {SENSOR_PARAMS[param_name]['default']}")
    
    return fixed_data

def display_sensor_form():
    """Display sensor input form"""
    
    st.markdown("## 🌡️ Input Data Sensor Lahan")
    
    # Get current location for display
    location_data = get_current_location_data()
    
    # Check if loading from history OR from preset
    default_data = {}
    current_interaction_data = None
    
    # Priority 1: Load from current interaction (history)
    if st.session_state.current_interaction_id:
        from src.components.history_panel import get_current_interaction_data
        current_interaction_data = get_current_interaction_data()
        if current_interaction_data and current_interaction_data.get('sensor_data'):
            default_data = current_interaction_data['sensor_data'].copy()
            crop_name = current_interaction_data['sensor_data']['selected_crop_display']
            location_name = current_interaction_data['sensor_data']['location']
            timestamp = current_interaction_data['timestamp']
            st.info(f"🔄 **Loaded from history:** {crop_name} - {location_name} - {timestamp}")
    
    # Priority 2: Load from preset data
    elif st.session_state.preset_data:
        default_data = st.session_state.preset_data.copy()
        preset_name = st.session_state.preset_name or "Custom"
        st.info(f"📋 **Loaded preset:** {preset_name}")
    
    # Priority 3: Use defaults
    else:
        # Use default values from config
        for param in ['nitrogen', 'phosphorus', 'potassium', 'temperature', 'humidity', 'ph', 'rainfall']:
            default_data[param] = SENSOR_PARAMS[param]['default']
    
    # CRITICAL: Validate and fix default data to prevent Streamlit errors
    default_data = validate_and_fix_default_data(default_data)
    
    # Check if location is available for conditional input disabling
    location_available = location_data is not None
    
    # Sensor input form (always complete to avoid Missing Submit Button error)
    with st.form("sensor_form"):
        # Location status display
        if location_available:
            lat = np.round(location_data['coordinates']['lat'], 6)
            lng = np.round(location_data['coordinates']['lng'], 6)
            st.success(f"📍 **Lokasi Terpilih:** {location_data['address']} ({lat}, {lng})")
        else:
            st.warning("⚠️ **Pilih lokasi terlebih dahulu di bagian atas untuk mengaktifkan input sensor**")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### 🧪 Nutrisi Tanah")
            nitrogen = st.number_input(
                "Nitrogen (N)", 
                min_value=SENSOR_PARAMS['nitrogen']['min'],
                max_value=SENSOR_PARAMS['nitrogen']['max'],
                value=float(default_data.get('N', default_data.get('nitrogen', SENSOR_PARAMS['nitrogen']['default']))),
                step=1.0,
                help=f"Kadar nitrogen dalam tanah ({SENSOR_PARAMS['nitrogen']['unit']})" if location_available else "Pilih lokasi terlebih dahulu",
                disabled=not location_available
            )
            
            phosphorus = st.number_input(
                "Phosphorus (P)",
                min_value=SENSOR_PARAMS['phosphorus']['min'],
                max_value=SENSOR_PARAMS['phosphorus']['max'], 
                value=float(default_data.get('P', default_data.get('phosphorus', SENSOR_PARAMS['phosphorus']['default']))),
                step=1.0,
                help=f"Kadar fosfor dalam tanah ({SENSOR_PARAMS['phosphorus']['unit']})" if location_available else "Pilih lokasi terlebih dahulu",
                disabled=not location_available
            )
            
            potassium = st.number_input(
                "Potassium (K)",
                min_value=SENSOR_PARAMS['potassium']['min'],
                max_value=SENSOR_PARAMS['potassium']['max'],
                value=float(default_data.get('K', default_data.get('potassium', SENSOR_PARAMS['potassium']['default']))),
                step=1.0,
                help=f"Kadar kalium dalam tanah ({SENSOR_PARAMS['potassium']['unit']})" if location_available else "Pilih lokasi terlebih dahulu",
                disabled=not location_available
            )
            
            ph = st.number_input(
                "pH Tanah",
                min_value=SENSOR_PARAMS['ph']['min'],
                max_value=SENSOR_PARAMS['ph']['max'],
                value=float(default_data.get('ph', SENSOR_PARAMS['ph']['default'])),
                step=0.1,
                help="Tingkat keasaman tanah (pH)" if location_available else "Pilih lokasi terlebih dahulu",
                disabled=not location_available
            )
        
        with col2:
            st.markdown("### 🌤️ Kondisi Lingkungan")
            temperature = st.number_input(
                "Temperature",
                min_value=SENSOR_PARAMS['temperature']['min'],
                max_value=SENSOR_PARAMS['temperature']['max'],
                value=float(default_data.get('temperature', SENSOR_PARAMS['temperature']['default'])),
                step=0.1,
                help=f"Suhu lingkungan ({SENSOR_PARAMS['temperature']['unit']})" if location_available else "Pilih lokasi terlebih dahulu",
                disabled=not location_available
            )
            
            humidity = st.number_input(
                "Humidity", 
                min_value=SENSOR_PARAMS['humidity']['min'],
                max_value=SENSOR_PARAMS['humidity']['max'],
                value=float(default_data.get('humidity', SENSOR_PARAMS['humidity']['default'])),
                step=1.0,
                help=f"Kelembaban udara ({SENSOR_PARAMS['humidity']['unit']})" if location_available else "Pilih lokasi terlebih dahulu",
                disabled=not location_available
            )
            
            rainfall = st.number_input(
                "Rainfall",
                min_value=SENSOR_PARAMS['rainfall']['min'],
                max_value=SENSOR_PARAMS['rainfall']['max'],
                value=float(default_data.get('rainfall', SENSOR_PARAMS['rainfall']['default'])),
                step=10.0,
                help=f"Curah hujan ({SENSOR_PARAMS['rainfall']['unit']})" if location_available else "Pilih lokasi terlebih dahulu",
                disabled=not location_available
            )
            
        st.markdown("### 🌾 Target Tanaman")
        
        # Get default crop selection
        default_crop = default_data.get('selected_crop', 'rice')
        # Find display name for default crop
        default_crop_display = None
        for display_name, model_name in CROP_MAPPING.items():
            if model_name == default_crop:
                default_crop_display = display_name
                break
        
        if not default_crop_display:
            default_crop_display = list(CROP_MAPPING.keys())[0]  # Fallback to first option
        
        selected_crop_display = st.selectbox(
            "Pilih Tanaman",
            options=list(CROP_MAPPING.keys()),
            index=list(CROP_MAPPING.keys()).index(default_crop_display),
            help="Pilih jenis tanaman yang ingin ditanam" if location_available else "Pilih lokasi terlebih dahulu",
            disabled=not location_available
        )
        
        # Submit button (always present but disabled when no location)
        if location_available:
            submitted = st.form_submit_button("🔍 Analisis Lahan", type="primary")
        else:
            submitted = st.form_submit_button("📍 Pilih Lokasi Dulu", type="secondary", disabled=True)
        
        if submitted and location_available:
            # Prepare sensor data (only if location is available)
            sensor_data = {
                'nitrogen': nitrogen,
                'phosphorus': phosphorus,
                'potassium': potassium,
                'temperature': temperature,
                'humidity': humidity,
                'ph': ph,
                'rainfall': rainfall,
                'selected_crop': CROP_MAPPING[selected_crop_display],
                'selected_crop_display': selected_crop_display,
                'location': location_data['address'],
                'coordinates': location_data['coordinates'],
                'location_source': location_data.get('source', 'unknown')
            }
            
            return sensor_data
    
    # Form was displayed but not submitted or no location available
    return None

# ==================== LOADED HISTORY DISPLAY ====================

def display_loaded_interaction_results():
    """Display beautiful read-only view of loaded interaction from history"""
    
    # Get current loaded interaction
    from src.components.history_panel import get_current_interaction_data
    interaction_data = get_current_interaction_data()
    
    if not interaction_data:
        st.error("❌ **Tidak dapat memuat data interaksi**")
        return
    
    sensor_data = interaction_data.get('sensor_data', {})
    ml_result = interaction_data.get('ml_result', {})
    timestamp = interaction_data.get('timestamp', datetime.now())
    
    # Header with beautiful styling
    st.markdown("## 📋 Riwayat Analisis Lahan")
    
    # Timestamp and ID info
    col1, col2 = st.columns([3, 1])
    with col1:
        st.caption(f"⏰ **Dibuat pada:** {timestamp.strftime('%d %B %Y, %H:%M:%S')}")
    with col2:
        st.caption(f"🆔 **ID:** {interaction_data.get('id', 'N/A')}")
    
    st.markdown("---")
    
    # Location Information - Beautiful Card
    st.markdown("### 📍 Informasi Lokasi")
    location_container = st.container()
    with location_container:
        col1, col2 = st.columns([2, 1])
        
        with col1:
            location = sensor_data.get('location', 'Tidak tersedia')
            coordinates = sensor_data.get('coordinates', {})
            location_source = sensor_data.get('location_source', 'unknown')
            
            # Location with icon based on source
            source_icons = {
                'gps': '🛰️',
                'map_pin': '📍', 
                'map_click_with_red_pin': '📍',
                'search': '🔍',
                'unknown': '❓'
            }
            source_icon = source_icons.get(location_source, '❓')
            
            st.info(f"{source_icon} **{location}**")
            
            if coordinates:
                lat = coordinates.get('lat', 0)
                lng = coordinates.get('lng', 0)
                st.caption(f"📊 Koordinat: {lat:.6f}°, {lng:.6f}°")
        
        with col2:
            # GPS accuracy if available
            if 'gps_accuracy' in sensor_data:
                accuracy = sensor_data['gps_accuracy']
                st.metric("🎯 Akurasi GPS", f"{accuracy}m")
    
    st.markdown("---")
    
    # Sensor Parameters - Beautiful Grid
    st.markdown("### 🌡️ Parameter Sensor Lahan")
    
    # Create 3x3 grid for parameters
    param_cols = st.columns(3)
    
    param_display = [
        ('🧪 Nitrogen (N)', sensor_data.get('nitrogen', 0), 'kg/ha'),
        ('🧪 Phosphorus (P)', sensor_data.get('phosphorus', 0), 'kg/ha'),
        ('🧪 Potassium (K)', sensor_data.get('potassium', 0), 'kg/ha'),
        ('🌡️ Temperature', sensor_data.get('temperature', 0), '°C'),
        ('💧 Humidity', sensor_data.get('humidity', 0), '%'),
        ('🧪 pH Tanah', sensor_data.get('ph', 0), ''),
        ('🌧️ Rainfall', sensor_data.get('rainfall', 0), 'mm'),
    ]
    
    # Display parameters in grid
    for i, (label, value, unit) in enumerate(param_display):
        with param_cols[i % 3]:
            st.metric(label, f"{value:.1f} {unit}")
    
    st.markdown("---")
    
    # ML Results - Main Results Section
    if ml_result:
        st.markdown("### 📊 Hasil Analisis Machine Learning")
        
        # Key metrics in prominent display
        result_cols = st.columns(3)
        
        with result_cols[0]:
            recommendation = ml_result.get('recommendation', 'N/A')
            # Color based on recommendation
            if 'Sangat Cocok' in recommendation:
                st.success(f"🎯 **{recommendation}**")
            elif 'Cukup Cocok' in recommendation:
                st.warning(f"🎯 **{recommendation}**") 
            else:
                st.error(f"🎯 **{recommendation}**")
        
        with result_cols[1]:
            confidence = ml_result.get('confidence', 0)
            st.metric("📈 Confidence", f"{confidence:.1%}")
        
        with result_cols[2]:
            crop_display = sensor_data.get('selected_crop_display', 'N/A')
            st.metric("🌾 Target Tanaman", crop_display)
        
        # Detailed explanation
        explanation = ml_result.get('explanation', '')
        if explanation:
            st.markdown("### 💡 Penjelasan Detail AI")
            st.markdown(explanation)
    else:
        st.warning("⚠️ **Hasil ML tidak tersedia untuk interaction ini**")
    
    st.markdown("---")
    
    # Action buttons
    st.markdown("### 🛠️ Edit")
    action_cols = st.columns(2)
        
    with action_cols[0]:
        if st.button("📝 Edit & Re-analyze", type="secondary"):
            # Keep interaction loaded but allow editing
            st.session_state.preset_data = sensor_data.copy()
            st.session_state.preset_name = f"Edit: {crop_display}"
            st.session_state.current_interaction_id = None  # Clear to enable form
            st.rerun()
    
    with action_cols[1]:
        if st.button("🗑️ Hapus Interaction", type="secondary"):
            # Import database service
            from src.services.database import get_mongodb_manager
            
            # Remove from session state
            interaction_id = interaction_data.get('id')
            st.session_state.interaction_history = [
                i for i in st.session_state.interaction_history 
                if i.get('id') != interaction_id
            ]
            
            # Remove from MongoDB
            mongo_manager = get_mongodb_manager()
            if mongo_manager.is_connected():
                mongo_manager.delete_interaction(interaction_id)
            
            # Clear current interaction
            st.session_state.current_interaction_id = None
            st.success("✅ Interaction berhasil dihapus!")
            st.rerun()

# ==================== RESULTS DISPLAY ====================

def display_analysis_results(sensor_data: Dict[str, Any]):
    """Display ML analysis results"""
    
    st.markdown("## 📊 Hasil Analisis Lahan")
    
    # Initialize ML predictor
    try:
        predictor = AICropPredictor()
        
        if not predictor.is_model_loaded():
            st.error("❌ **Model ML tidak dapat dimuat** - Periksa file model di folder `data/`")
            return
        
        # Get prediction
        recommendation, confidence, explanation = predictor.evaluate_crop_suitability(
            sensor_data, sensor_data['selected_crop']
        )
        
        # Display results
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric(
                "🎯 Rekomendasi",
                recommendation,
                f"Confidence: {confidence:.1%}"
            )
        
        with col2:
            st.metric(
                "🌾 Tanaman", 
                sensor_data['selected_crop_display']
            )
        
        with col3:
            st.metric(
                "📍 Lokasi",
                sensor_data['location'].split(',')[0] if ',' in sensor_data['location'] else sensor_data['location']
            )
        
        # Show detailed explanation
        st.markdown("### 💡 Penjelasan Detail")
        st.markdown(explanation)
        
        # Save to database and session state
        import uuid
        interaction_data = {
            'id': str(uuid.uuid4())[:8],
            'timestamp': datetime.now(),
            'sensor_data': sensor_data,
            'ml_result': {
                'recommendation': recommendation,
                'confidence': confidence,
                'explanation': explanation
            },
            'title': f"{sensor_data['selected_crop_display']} - {sensor_data['location'].split(',')[0]}"
        }
        
        # Clear preset data after successful submission
        if st.session_state.preset_data:
            st.session_state.preset_data = None
            st.session_state.preset_name = None
        
        # Save to session state
        if 'interaction_history' not in st.session_state:
            st.session_state.interaction_history = []
        
        st.session_state.interaction_history.append(interaction_data)
        st.session_state.current_interaction_id = interaction_data['id']
        
        # Keep only last 50 interactions in session state to prevent memory issues
        if len(st.session_state.interaction_history) > 50:
            st.session_state.interaction_history = st.session_state.interaction_history[-50:]
        
        # Save to MongoDB
        if save_interaction_to_db(interaction_data):
            st.success("✅ **Hasil analisis telah disimpan ke database dan history**")
            # Force sidebar to show updated history
            st.session_state.sidebar_mode = 'history'
        else:
            st.success("✅ **Hasil analisis telah disimpan ke session history**")
            st.session_state.sidebar_mode = 'history'
        
        # Immediate refresh to update sidebar with new interaction  
        st.rerun()
        
    except Exception as e:
        st.error(f"❌ **Error dalam analisis:** {str(e)}")

# ==================== SIDEBAR ====================

def display_sidebar():
    """Display sidebar with history and controls - matches original implementation"""
    
    st.sidebar.markdown("# Menu Interaction History")
    
    # Mode selection buttons
    col1, col2 = st.sidebar.columns(2)
    with col1:
        if st.button("📋 History", type="primary" if st.session_state.sidebar_mode == 'history' else "secondary"):
            st.session_state.sidebar_mode = 'history'
    with col2:
        if st.button("➕ New", type="primary" if st.session_state.sidebar_mode == 'new' else "secondary"):
            st.session_state.sidebar_mode = 'new'
            st.session_state.current_interaction_id = None
            st.session_state.preset_data = None
            st.session_state.preset_name = None
    
    st.sidebar.markdown("---")
    
    # Display appropriate sidebar content based on mode
    if st.session_state.sidebar_mode == 'history':
        from src.components.history_panel import display_interaction_history
        display_interaction_history()
    else:
        from src.components.history_panel import display_new_interaction_form
        display_new_interaction_form()

# ==================== MAIN APPLICATION ====================

def main():
    """Main application function"""
    
    # Configure Streamlit
    configure_streamlit()
    
    # Initialize app
    initialize_app()
    
    # Display header
    st.markdown("# 🌾 Agricultural Decision Support System")
    st.markdown("*Dapatkan rekomendasi tanaman instan dan saran optimisasi lingkungan berdasarkan kondisi lahan Anda*")
    
    # Display sidebar
    display_sidebar()
    
    # Main content
    st.markdown("---")
    
    # Check if we're viewing a loaded interaction from history
    if st.session_state.current_interaction_id:
        # Display read-only view of loaded interaction
        display_loaded_interaction_results()
    else:
        # Normal new analysis flow
        
        # Location selection
        display_location_selection()
        
        st.markdown("---")
        
        # Sensor input form
        sensor_data = display_sensor_form()
        
        # Display results if form submitted
        if sensor_data:
            st.markdown("---")
            display_analysis_results(sensor_data)
    
    # Development notes
    with st.expander("🔧 Development Notes - Modular Structure", expanded=False):
        st.markdown("""
        ### 📁 Modular Structure Created:
        
        ```
        src/
        ├── utils/
        │   ├── config.py          ✅ Configuration & settings
        │   └── helpers.py         ✅ Utility functions
        ├── services/
        │   ├── database.py        ✅ MongoDB operations
        │   ├── location.py        ✅ GPS & geocoding
        │   └── mapping.py         ✅ Map functionality
        ├── core/
        │   └── ml_predictor.py    ✅ AI/ML models
        └── main.py                ✅ Main application
        ```
        
        ### 🚧 **Remaining to Extract:**
        - `src/core/llm_service.py` - LLM integration
        - `src/core/decision_system.py` - Decision support logic
        - `src/components/sensor_form.py` - Form components
        - `src/components/results_display.py` - Results UI
        - `src/components/history_panel.py` - History sidebar
        
        ### 📖 **See REFACTORING_GUIDE.md for complete instructions**
        """)

if __name__ == "__main__":
    main() 