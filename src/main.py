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

# Import LLM services
from src.services.llm_service import agricultural_llm
from src.services.knowledge_base import knowledge_base
from src.services.location_context import location_context_service
from src.services.recommendation_engine import recommendation_engine
from src.services.evaluation_service import evaluation_service
from src.services.weather_service import weather_service

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
    
    # Check LLM service status
    llm_status = agricultural_llm.get_service_status()
    kb_status = knowledge_base.get_status()
    eval_status = evaluation_service.get_service_status()
    
    # Print status to console
    print("📋 TaniCerdas Nusantara - LLM Enhanced Version")
    print("=" * 60)
    print("🔧 Core Libraries:")
    for lib, available in library_status.items():
        status = "✅" if available else "❌"
        print(f"  {status} {lib.replace('_', ' ').title()}")
    
    print("\n🤖 LLM Services:")
    print(f"  {'✅' if llm_status['ollama']['available'] else '❌'} Ollama LLM")
    print(f"  {'✅' if llm_status['openrouter']['available'] else '❌'} OpenRouter LLM")
    print(f"  {'✅' if kb_status['available'] else '❌'} Knowledge Base (Qdrant)")
    print(f"  {'✅' if eval_status['evaluation_service_available'] else '❌'} Evaluation Service")
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
    
    # ✅ FIXED: Check if gps_data is None to prevent TypeError
    if gps_data is None:
        st.error("❌ **GPS data tidak valid** - Silakan pilih lokasi lagi")
        print("⚠️ GPS completed mode called but gps_location_data is None")
        
        # Clear GPS completion flag and return to location selection
        st.session_state.gps_auto_refresh_completed = False
        st.session_state.gps_location_data = None
        st.session_state.selected_location_pin = None
        st.session_state.selected_location = None
        st.session_state.selected_location_source = None
        st.rerun()
        return
    
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
            st.session_state.gps_location_data = None
            st.session_state.selected_location_pin = None
            st.session_state.selected_location = None
            st.session_state.selected_location_source = None
            st.rerun()

def display_location_tabs():
    """Display location selection tabs"""
    
    tab1, tab2 = st.tabs(["🛰️ GPS Location", "🗺️ Interactive Map"])
    
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
    
    # Search Location tab removed based on user request

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
        'rainfall': 'rainfall',
        'land_area': 'land_area'
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
    for param_name in ['nitrogen', 'phosphorus', 'potassium', 'temperature', 'humidity', 'ph', 'rainfall', 'land_area']:
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
    
    st.markdown("##Input Data Sensor Lahan")
    
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
        
        # Show enhanced preset info with suggested location
        suggested_location = default_data.get('suggested_location')
        if suggested_location:
            col1, col2 = st.columns([3, 1])
            with col1:
                st.success(f"📋 **Loaded preset:** {preset_name}")
                st.info(f"💡 **Suggested location:** {suggested_location}")
            with col2:
                # Button to use suggested location
                if st.button("🎯 Use Location", type="primary", help="Use suggested location for this preset"):
                    coordinates = default_data.get('location_coordinates')
                    if coordinates:
                        # Set location data in session state
                        st.session_state.selected_location = {
                            'coordinates': coordinates,
                            'address': suggested_location,
                            'source': 'preset_suggestion'
                        }
                        st.session_state.temp_coordinates = coordinates
                        st.success(f"✅ Location set: {suggested_location}")
                        st.rerun()
        else:
            st.info(f"📋 **Loaded preset:** {preset_name}")
            st.warning("📍 Please select a location to continue")
    
    # Priority 3: Use defaults
    else:
        # Use default values from config
        for param in ['nitrogen', 'phosphorus', 'potassium', 'temperature', 'humidity', 'ph', 'rainfall', 'land_area']:
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
            st.markdown("### Nutrisi Tanah")
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
            
            st.markdown("### Luas Lahan")
            land_area = st.number_input(
                "Luas Lahan Pertanian",
                min_value=SENSOR_PARAMS['land_area']['min'],
                max_value=SENSOR_PARAMS['land_area']['max'],
                value=float(default_data.get('land_area', SENSOR_PARAMS['land_area']['default'])),
                step=0.1,
                help=f"Luas lahan yang akan ditanami ({SENSOR_PARAMS['land_area']['unit']})" if location_available else "Pilih lokasi terlebih dahulu",
                disabled=not location_available
            )
        
        with col2:
            st.markdown("### Kondisi Lingkungan")
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
            
        st.markdown("### Target Tanaman")
        
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
                'land_area': land_area,
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
    """Display beautiful read-only view of loaded interaction from history with consistent tabs"""
    
    # Get current loaded interaction
    from src.components.history_panel import get_current_interaction_data
    interaction_data = get_current_interaction_data()
    
    if not interaction_data:
        st.error("❌ **Tidak dapat memuat data interaksi**")
        return
    
    sensor_data = interaction_data.get('sensor_data', {})
    ml_result = interaction_data.get('ml_result', {})
    ai_result = interaction_data.get('ai_result', {})
    evaluation_result = interaction_data.get('evaluation_result', {})
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
    
    # ML Results - Main Results Section (matching display_comprehensive_results format)
    if ml_result:
        # Main ML Results Display
        result_cols = st.columns(2)
        
        with result_cols[1]:
            recommendation = ml_result.get('recommendation', 'N/A')
            confidence = ml_result.get('confidence', 0)
            # Pilih simbol dan warna background sesuai kategori
            if 'Sangat Cocok' in recommendation:
                symbol = "✅"
                bg_color = "#d1e7dd"  # success (greenish)
                font_color = "#0f5132"
            elif 'Cukup Cocok' in recommendation:
                symbol = "⚠️"
                bg_color = "#fff3cd"  # warning (yellowish)
                font_color = "#664d03"
            else:
                symbol = "❌"
                bg_color = "#f8d7da"  # danger (reddish)
                font_color = "#842029"
            st.markdown(
                f"""
                <div style="background-color: {bg_color}; color: {font_color}; border-radius: 0.5rem; padding: 1.2em 0.5em; text-align: center; border: 1px solid #ccc; margin-right: 1.5em;">
                    <span style="font-size: 1.5em;">{symbol} {recommendation} {confidence:.1%}</span>
                </div>
                """,
                unsafe_allow_html=True
            )
        
        with result_cols[0]:
            crop_display = sensor_data.get('selected_crop_display', 'N/A')
            st.metric("Target Tanaman", crop_display)
        
        st.markdown("---")
        
        # Top Recommendations section (if available)
        if 'top_recommendations' in ml_result and 'confidence' in ml_result:
            selected_crop_confidence = ml_result['confidence']
            top_recs = ml_result['top_recommendations'][:5]  # Top 5
            
            # Check if any recommended crop has higher confidence than selected crop
            better_alternatives = [
                (crop, conf) for crop, conf in top_recs 
                if conf > selected_crop_confidence
            ]
            
            # Only show recommendations if there are better alternatives
            if better_alternatives:
                st.markdown("### 🏆 Rekomendasi Tanaman")
                st.info(f"💡 **Info:** Berikut adalah alternatif tanaman dengan tingkat kesesuaian yang lebih tinggi:")
                
                # Display better alternatives
                rec_cols = st.columns(len(better_alternatives))
                
                for i, (crop, conf) in enumerate(better_alternatives):
                    with rec_cols[i]:
                        if conf > 0.7:
                            color = "🟢"
                            st.metric(
                                label=f"{color} #{i+1}",
                                value=crop.title(),
                                delta=f"+{conf:.1%}%"
                            )
                        elif i == len(better_alternatives) - 1:
                            st.markdown(f"Tidak ada Tanaman yang cocok")
                        
            else:
                # User's crop is already optimal - show congratulatory message
                st.markdown("### Pilihan Tanaman Sudah Optimal")
                st.success(f"🎉 **Selamat!** Tanaman pilihan Anda **{sensor_data['selected_crop_display']}** sudah merupakan pilihan yang optimal dengan tingkat kesesuaian **{selected_crop_confidence:.1%}** berdasarkan kondisi lahan Anda.")
    else:
        # Fallback if ML not available
        st.warning("⚠️ **Hasil Machine Learning tidak tersedia**")
        
        # Show basic metrics from evaluation
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            suitability_score = ai_result.get('suitability_score', 0.0)
            color = "normal" if suitability_score > 0.7 else "inverse"
            st.metric(
                "🎯 Kesesuaian",
                f"{suitability_score:.1%}",
                f"Level: {ai_result.get('confidence_level', 'medium').title()}",
                delta_color=color
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
        
        with col4:
            risk_level = ai_result.get('risk_assessment', {}).get('overall_risk_level', 'medium')
            risk_color = "normal" if risk_level == "low" else "inverse"
            st.metric(
                "⚠️ Tingkat Risiko",
                risk_level.title(),
                delta_color=risk_color
            )
    
    # ✅ NEW: Add tabs for detailed analysis (matching display_comprehensive_results)
    tab1, tab2 = st.tabs([
        "🤖 Analisis AI", "🌤️ Data Cuaca"
    ])
    
    with tab1:
        # ✅ IMPROVED: Handle new clean AI result structure
        ai_result = interaction_data.get('ai_result', {})
        
        # Convert loaded interaction data to evaluation format for display_ai_analysis_tab
        evaluation_for_display = {
            'llm_analysis': ai_result.get('llm_analysis', ''),
            'knowledge_base_insights': [],  # Not stored in clean format
            'recommendations': ai_result.get('recommendations', {}),
            'risk_assessment': {},  # Not stored in clean format  
            'optimization_plan': {},  # Not stored in clean format
            'alternative_crops': [],  # Not stored in clean format
            'suitability_score': ai_result.get('suitability_score', 0.0),
            'confidence_level': ai_result.get('confidence_level', 'medium'),
            'analysis_type': ai_result.get('analysis_type', 'unknown'),
            'analysis_timestamp': ai_result.get('analysis_timestamp', ''),
            'ml_analysis': {
                'available': ml_result.get('available', False),
                'crop_prediction': ml_result.get('recommendation', 'N/A'),
                'confidence': ml_result.get('confidence', 0.0),
                'explanation': ml_result.get('explanation', '')
            } if ml_result else {}
        }
        
        # ✅ DEBUG: Log what AI data is being displayed
        print(f"🖥️ Displaying AI analysis for interaction: {interaction_data.get('id')}")
        print(f"  🎯 Analysis Type: {evaluation_for_display['analysis_type']}")
        print(f"  📝 LLM Analysis: {len(evaluation_for_display['llm_analysis'])} chars")
        print(f"  💡 Recommendations: {list(evaluation_for_display['recommendations'].keys())}")
        
        # Show clean AI analysis info
        if evaluation_for_display['analysis_type'] != 'unknown':
            analysis_info_col1, analysis_info_col2 = st.columns(2)
            with analysis_info_col1:
                st.info(f"🎯 **Analysis Type:** {evaluation_for_display['analysis_type'].title()}")
            with analysis_info_col2:
                if evaluation_for_display['analysis_timestamp']:
                    timestamp_str = evaluation_for_display['analysis_timestamp'][:19]  # Remove milliseconds
                    st.info(f"🕒 **Generated:** {timestamp_str}")
        
        # Use the same AI analysis tab display
        display_ai_analysis_tab(evaluation_for_display)
    
    with tab2:
        # Construct location data from sensor data for weather tab
        coordinates = sensor_data.get('coordinates')
        location_address = sensor_data.get('location', 'Unknown')
        
        if coordinates:
            location_data_for_weather = {
                'coordinates': coordinates,
                'address': location_address
            }
            display_weather_tab(location_data_for_weather, sensor_data)
        else:
            st.warning("⚠️ **Data cuaca tidak tersedia** - Koordinat lokasi tidak ditemukan dalam data historis")
            st.info("💡 **Info:** Data cuaca memerlukan koordinat GPS yang valid")
    
    st.markdown("---")
    
    # Action buttons
    st.markdown("### 🛠️ Edit")
    action_cols = st.columns(2)
        
    with action_cols[0]:
        if st.button("📝 Edit & Re-analyze", type="secondary"):
            # Keep interaction loaded but allow editing
            st.session_state.preset_data = sensor_data.copy()
            st.session_state.preset_name = f"Edit: {sensor_data.get('selected_crop_display', 'Unknown')}"
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
                print(f"✅ Deleted interaction {interaction_id} from MongoDB")
            else:
                print(f"⚠️ Deleted interaction {interaction_id} from session only")
            
            # Clear current interaction and return to new analysis
            st.session_state.current_interaction_id = None
            st.session_state.sidebar_mode = 'history'
            st.success("✅ **Interaction berhasil dihapus**")
            st.rerun()

# ==================== RESULTS DISPLAY ====================

def display_analysis_results(sensor_data: Dict[str, Any]):
    """Display Machine Learning analysis results as main focus"""
    
    st.markdown("## 📊 Hasil Analisis")
    
    # Get location data if available
    location_data = get_current_location_data()
    
    # Show analysis progress
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    try:
        # Step 1: Comprehensive Evaluation
        status_text.text("🔄 Melakukan evaluasi komprehensif...")
        progress_bar.progress(20)
        
        evaluation = evaluation_service.comprehensive_crop_evaluation(
            sensor_data, location_data, sensor_data['selected_crop']
        )
        
        progress_bar.progress(40)
        status_text.text("🤖 Menganalisis dengan AI...")
        
        # Step 2: Additional recommendations
        progress_bar.progress(60)
        status_text.text("🗺️ Menganalisis konteks lokasi...")
        
        location_advice = None
        if location_data:
            location_advice = location_context_service.generate_location_specific_recommendations(
                location_data, sensor_data
            )
        
        progress_bar.progress(80)
        status_text.text("📚 Mencari informasi relevan...")
        
        # Step 3: Finalize
        progress_bar.progress(100)
        status_text.text("✅ Analisis selesai!")
        
        # Clear progress indicators
        progress_bar.empty()
        status_text.empty()
        
        # Display Results
        display_comprehensive_results(evaluation, location_advice, sensor_data)
        
        # Save comprehensive results
        save_comprehensive_results(evaluation, location_advice, sensor_data)
        
    except Exception as e:
        progress_bar.empty()
        status_text.empty()
        
        # ✅ IMPROVED: Better error logging and handling
        print(f"❌ Comprehensive evaluation failed: {str(e)}")
        print(f"📊 Sensor data: {sensor_data}")
        print(f"📍 Location data: {location_data}")
        
        
        # Determine error type for better user feedback
        error_msg = str(e)
        if "LLM" in error_msg or "ollama" in error_msg.lower() or "openrouter" in error_msg.lower():
            st.error("❌ **Error dalam layanan LLM** - Beralih ke analisis dasar")
            print("🔍 Root cause: LLM service error")
        elif "knowledge" in error_msg.lower() or "qdrant" in error_msg.lower():
            st.error("❌ **Error dalam knowledge base** - Beralih ke analisis dasar")
            print("🔍 Root cause: Knowledge base error")
        elif "evaluation_service" in error_msg.lower():
            st.error("❌ **Error dalam evaluation service** - Beralih ke analisis dasar")
            print("🔍 Root cause: Evaluation service error")
        else:
            st.error(f"❌ **Error dalam analisis:** {str(e)}")
            print("🔍 Root cause: Unknown error")
        

def display_comprehensive_results(evaluation: Dict[str, Any], location_advice: Dict[str, Any], sensor_data: Dict[str, Any]):
    """Display Machine Learning results as main focus"""
    
    # Get ML analysis results
    ml_analysis = evaluation.get('ml_analysis', {})
    
    if ml_analysis.get('available'):
        # Main ML Results Display
    

        result_cols = st.columns(2)
        
        with result_cols[1]:
            recommendation = ml_analysis.get('crop_prediction', 'N/A')
            confidence = ml_analysis.get('confidence', 0.0)
            # Pilih simbol dan warna background sesuai kategori
            if 'Sangat Cocok' in recommendation:
                symbol = "✅"
                bg_color = "#d1e7dd"  # success (greenish)
                font_color = "#0f5132"
            elif 'Cukup Cocok' in recommendation:
                symbol = "⚠️"
                bg_color = "#fff3cd"  # warning (yellowish)
                font_color = "#664d03"
            else:
                symbol = "❌"
                bg_color = "#f8d7da"  # danger (reddish)
                font_color = "#842029"
            st.markdown(
                f"""
                <div style="background-color: {bg_color}; color: {font_color}; border-radius: 0.5rem; padding: 1.2em 0.5em; text-align: center; border: 1px solid #ccc; margin-right: 1.5em;">
                    <span style="font-size: 1.5em;">{symbol} {recommendation} {confidence:.1%}</span>
                </div>
                """,
                unsafe_allow_html=True
            )
        

        
        with result_cols[0]:
            crop_display = sensor_data.get('selected_crop_display', 'N/A')
            st.metric("Target Tanaman", crop_display)
        

        # ML Explanation
        # explanation = ml_analysis.get('explanation', '')
        # if explanation:
        #     st.markdown("### 💡 Penjelasan Detail Machine Learning")
        #     st.info(explanation)
        
        st.markdown("---")
        
        # Top Recommendations - only show if there are better alternatives
        if 'top_recommendations' in ml_analysis and 'confidence' in ml_analysis:
            selected_crop_confidence = ml_analysis['confidence']
            top_recs = ml_analysis['top_recommendations'][:5]  # Top 5
            
            # Check if any recommended crop has higher confidence than selected crop
            better_alternatives = [
                (crop, conf) for crop, conf in top_recs 
                if conf > selected_crop_confidence
            ]
            
            # Only show recommendations if there are better alternatives
            if better_alternatives:
                st.markdown("### 🏆 Rekomendasi Tanaman")
                st.info(f"💡 **Info:** Berikut adalah alternatif tanaman dengan tingkat kesesuaian yang lebih tinggi:")
                
                                # Display better alternatives
                rec_cols = st.columns(len(better_alternatives))
                
                for i, (crop, conf) in enumerate(better_alternatives):
                    with rec_cols[i]:
                        # Color coding based on confidence
                        if conf > 0.7:
                            color = "🟢"
                            improvement = ((conf - selected_crop_confidence) / selected_crop_confidence) * 100
                    
                            st.metric(
                                label=f"{color} #{i+1}",
                                value=crop.title(),
                                delta=f"+{conf:.1%}%"
                            )
                        elif i == len(better_alternatives) - 1:
                            st.markdown(f"Tidak ada Tanaman yang cocok")
                        
            else:
                # User's crop is already optimal - show congratulatory message
                st.markdown("### Pilihan Tanaman Sudah Optimal")
                st.success(f"🎉 **Selamat!** Tanaman pilihan Anda **{sensor_data['selected_crop_display']}** sudah merupakan pilihan yang optimal dengan tingkat kesesuaian **{selected_crop_confidence:.1%}** berdasarkan kondisi lahan Anda.")
                
                # Optionally show why it's the best choice
                if top_recs:
                    with st.expander("🔍 Lihat perbandingan dengan tanaman lain"):
                        st.markdown("**Perbandingan tingkat kesesuaian:**")
                        comparison_data = []
                        
                        for crop, conf in top_recs:
                            if crop == sensor_data.get('selected_crop', ''):
                                comparison_data.append({
                                    'Tanaman': f"**{crop.title()} (Pilihan Anda)**",
                                    'Tingkat Kesesuaian': f"**{conf:.1%}**",
                                    'Status': "✅ **Optimal**"
                                })
                            else:
                                comparison_data.append({
                                    'Tanaman': crop.title(),
                                    'Tingkat Kesesuaian': f"{conf:.1%}",
                                    'Status': "📊 Alternatif"
                                })
                        
                        import pandas as pd
                        df = pd.DataFrame(comparison_data)
                        st.table(df)
    else:
        # Fallback if ML not available
        st.warning("⚠️ **Hasil Machine Learning tidak tersedia**")
        
        # Show basic metrics from evaluation
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            suitability_score = evaluation.get('suitability_score', 0.0)
            color = "normal" if suitability_score > 0.7 else "inverse"
            st.metric(
                "🎯 Kesesuaian",
                f"{suitability_score:.1%}",
                f"Level: {evaluation.get('confidence_level', 'medium').title()}",
                delta_color=color
            )
        
        with col2:
            st.metric(
                "🌾 Tanaman",
                sensor_data['selected_crop_display']
            )
        
        with col3:
            if location_advice:
                region = location_advice.get('location_context', {}).get('region', 'Unknown')
                st.metric(
                    "📍 Wilayah",
                    region.replace('_', ' ').title() if region != 'Unknown' else 'Unknown'
                )
            else:
                st.metric(
                    "📍 Lokasi",
                    sensor_data['location'].split(',')[0] if ',' in sensor_data['location'] else sensor_data['location']
                )
        
        with col4:
            risk_level = evaluation.get('risk_assessment', {}).get('overall_risk_level', 'medium')
            risk_color = "normal" if risk_level == "low" else "inverse"
            st.metric(
                "⚠️ Tingkat Risiko",
                risk_level.title(),
                delta_color=risk_color
            )
    
    # Tabs for detailed analysis
    tab1, tab2 = st.tabs([
        "🤖 Analisis AI", "🌤️ Data Cuaca"
    ])
    
    with tab1:
        display_ai_analysis_tab(evaluation)
    
    with tab2:
        # Get location data for weather tab
        current_location_data = get_current_location_data()
        display_weather_tab(current_location_data, sensor_data)

def display_weather_tab(location_data: Dict[str, Any] = None, sensor_data: Dict[str, Any] = None):
    """Display weather information from OpenMeteo API"""
    
    # Get location data if not provided
    if not location_data:
        location_data = get_current_location_data()
    
    if not location_data or 'coordinates' not in location_data:
        st.warning("⚠️ **Data cuaca tidak tersedia** - Lokasi belum ditentukan")
        st.info("💡 **Pilih lokasi terlebih dahulu** menggunakan GPS, map, atau pencarian untuk melihat data cuaca")
        return
    
    coordinates = location_data['coordinates']
    latitude = coordinates.get('lat')
    longitude = coordinates.get('lng')
    
    if latitude is None or longitude is None:
        st.error("❌ **Koordinat tidak valid** - Tidak dapat mengambil data cuaca")
        return
    
    # Show loading message
    with st.spinner("🌤️ Mengambil data cuaca terkini..."):
        # Get weather data from OpenMeteo API
        weather_data = weather_service.get_agricultural_weather_summary(latitude, longitude)
    
    if weather_data.get('status') == 'fallback':
        st.error("❌ **API Cuaca Tidak Tersedia**")
        st.info("🔄 **Coba lagi nanti** - Layanan cuaca OpenMeteo sedang tidak dapat diakses")
        return
    
    # Display location info
    st.markdown("### 📍 Informasi Lokasi")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(
            "🌐 Garis Lintang", 
            f"{latitude:.4f}°"
        )
    
    with col2:
        st.metric(
            "🌐 Garis Bujur", 
            f"{longitude:.4f}°"
        )
    
    with col3:
        elevation = weather_data.get('location', {}).get('elevation', 0)
        st.metric(
            "⛰️ Ketinggian", 
            f"{elevation:.0f} m"
        )
    
    st.markdown("---")
    
    # Current Weather
    st.markdown("### 🌤️ Cuaca Saat Ini")
    current = weather_data.get('current', {})
    
    # Weather overview
    weather_desc = weather_data.get('weather_description', 'Tidak diketahui')
    updated_time = weather_data.get('updated_at', '')
    
    if updated_time:
        from datetime import datetime
        try:
            update_dt = datetime.fromisoformat(updated_time.replace('Z', '+00:00'))
            time_str = update_dt.strftime("%d/%m/%Y %H:%M WIB")
        except:
            time_str = updated_time
    else:
        time_str = "Tidak diketahui"
    
    st.info(f"🌤️ **Kondisi:** {weather_desc} | 🕒 **Diperbarui:** {time_str}")
    
    # Current weather metrics
    current_col1, current_col2, current_col3, current_col4 = st.columns(4)
    
    with current_col1:
        temp = current.get('temperature', 0)
        st.metric(
            "🌡️ Suhu Udara",
            f"{temp:.1f}°C",
            help="Suhu udara pada ketinggian 2 meter"
        )
    
    with current_col2:
        humidity = current.get('humidity', 0)
        st.metric(
            "💧 Kelembapan",
            f"{humidity:.0f}%",
            help="Kelembapan relatif udara"
        )
    
    with current_col3:
        precipitation = current.get('precipitation', 0)
        st.metric(
            "🌧️ Curah Hujan",
            f"{precipitation:.1f} mm",
            help="Curah hujan saat ini"
        )
    
    with current_col4:
        wind_speed = current.get('wind_speed', 0)
        st.metric(
            "💨 Kecepatan Angin",
            f"{wind_speed:.1f} km/h",
            help="Kecepatan angin pada ketinggian 10 meter"
        )
    
    
    # Soil Conditions
    st.markdown("---")
    st.markdown("### 🌱 Kondisi Tanah")
    
    soil = weather_data.get('soil', {})
    soil_temp = soil.get('overall_avg_temp', 0)
    soil_moisture = soil.get('overall_avg_moisture', 0)
    
    soil_col1, soil_col2 = st.columns(2)
    
    with soil_col1:
        st.metric(
            "🌡️ Suhu Tanah Rata-rata",
            f"{soil_temp:.1f}°C",
            help="Rata-rata suhu tanah dari berbagai kedalaman (24 jam terakhir)"
        )
        
        # Soil temperature by depth
        soil_temps = soil.get('temperature', {})
        if soil_temps:
            with st.expander("📊 Detail Suhu Tanah per Kedalaman"):
                depth_labels = {
                    'surface': '0 cm (Permukaan)',
                    'shallow': '6 cm (Dangkal)',
                    'medium': '18 cm (Sedang)',
                    'deep': '54 cm (Dalam)'
                }
                
                for depth, temp in soil_temps.items():
                    if depth in depth_labels:
                        st.write(f"• **{depth_labels[depth]}:** {temp:.1f}°C")
    
    with soil_col2:
        st.metric(
            "💧 Kelembapan Tanah Rata-rata",
            f"{soil_moisture:.3f} m³/m³",
            help="Rata-rata kelembapan tanah dari berbagai kedalaman (24 jam terakhir)"
        )
        
        # Soil moisture by depth
        soil_moistures = soil.get('moisture', {})
        if soil_moistures:
            with st.expander("📊 Detail Kelembapan Tanah per Kedalaman"):
                moisture_labels = {
                    'very_shallow': '0-1 cm (Sangat Dangkal)',
                    'shallow': '1-3 cm (Dangkal)',
                    'medium': '3-9 cm (Sedang)',
                    'deep': '9-27 cm (Dalam)',
                    'very_deep': '27-81 cm (Sangat Dalam)'
                }
                
                for depth, moisture in soil_moistures.items():
                    if depth in moisture_labels:
                        st.write(f"• **{moisture_labels[depth]}:** {moisture:.3f} m³/m³")
    
    # Daily Forecast
    daily_forecast = weather_data.get('daily_forecast', [])
    if daily_forecast:
        st.markdown("---")
        st.markdown("### 📅 Prakiraan 7 Hari ke Depan")
        
        forecast_cols = st.columns(min(len(daily_forecast), 7))
        
        for i, day_data in enumerate(daily_forecast[:7]):
            if i < len(forecast_cols):
                with forecast_cols[i]:
                    date_str = day_data.get('date', '')
                    try:
                        from datetime import datetime
                        date_obj = datetime.fromisoformat(date_str)
                        day_label = date_obj.strftime("%d/%m")
                        day_name = ["Sen", "Sel", "Rab", "Kam", "Jum", "Sab", "Min"][date_obj.weekday()]
                    except:
                        day_label = date_str
                        day_name = ""
                    
                    temp_max = day_data.get('temp_max', 0)
                    temp_min = day_data.get('temp_min', 0)
                    precipitation = day_data.get('precipitation', 0)
                    precip_prob = day_data.get('precipitation_prob', 0)
                    
                    st.markdown(f"**{day_name}**")
                    st.markdown(f"**{day_label}**")
                    st.markdown(f"🌡️ {temp_max:.0f}°/{temp_min:.0f}°C")
                    st.markdown(f"🌧️ {precipitation:.1f}mm")
                    st.markdown(f"☔ {precip_prob:.0f}%")
    
    # Additional Info
    st.markdown("---")
    st.markdown("### ℹ️ Informasi Tambahan")
    
    additional_col1, additional_col2 = st.columns(2)
    
    with additional_col1:
        pressure = current.get('pressure', 0)
        st.markdown(f"**🌊 Tekanan Udara:** {pressure:.1f} hPa")
        
        wind_direction = current.get('wind_direction', 0)
        st.markdown(f"**🧭 Arah Angin:** {wind_direction:.0f}°")
    
    with additional_col2:
        st.markdown("**📡 Sumber Data:** [OpenMeteo API](https://open-meteo.com)")
        st.markdown(f"**⏰ Zona Waktu:** Asia/Jakarta (WIB)")
    
    # Agricultural recommendations based on weather
    if sensor_data:
        st.markdown("---")
        st.markdown("### 💡 Rekomendasi Berdasarkan Cuaca")
        
        selected_crop = sensor_data.get('selected_crop_display', 'tanaman')
        
        recommendations = []
        
        # Temperature recommendations
        if temp < 15:
            recommendations.append("🌡️ **Suhu rendah:** Pertimbangkan penggunaan mulsa atau penutup tanaman untuk melindungi dari dingin")
        elif temp > 35:
            recommendations.append("🌡️ **Suhu tinggi:** Pastikan irigasi yang cukup dan pertimbangkan naungan sementara")
        
        # Humidity recommendations
        if humidity > 80:
            recommendations.append("💧 **Kelembapan tinggi:** Perhatikan sirkulasi udara untuk mencegah penyakit jamur")
        elif humidity < 40:
            recommendations.append("💧 **Kelembapan rendah:** Tingkatkan frekuensi penyiraman dan pertimbangkan mulsa")
        
        # Precipitation recommendations
        if precipitation > 20:
            recommendations.append("🌧️ **Hujan lebat:** Pastikan drainase yang baik untuk mencegah genangan air")
        elif precipitation == 0 and humidity < 50:
            recommendations.append("☀️ **Cuaca kering:** Pastikan irigasi yang cukup untuk tanaman")
        
        # Soil moisture recommendations
        if soil_moisture < 0.1:
            recommendations.append("🌱 **Tanah kering:** Tingkatkan frekuensi irigasi atau gunakan sistem tetes")
        elif soil_moisture > 0.5:
            recommendations.append("🌱 **Tanah basah:** Kurangi irigasi dan pastikan drainase yang baik")
        
        if recommendations:
            for rec in recommendations:
                st.info(rec)
        else:
            st.success(f"✅ **Kondisi cuaca saat ini cukup baik untuk pertumbuhan {selected_crop}**")

def analyze_parameter_with_llm(param_name: str, value: float, crop_type: str, all_sensor_data: Dict[str, Any] = None) -> Dict[str, Any]:
    """Analyze individual parameter using LLM for intelligent contextual assessment"""
    
    try:
        # Access global LLM service (already initialized in main)
        global agricultural_llm
        if 'agricultural_llm' not in globals():
            # Import if not available globally
            from src.services.llm_service import agricultural_llm
        
        # Prepare context for LLM analysis
        context = f"""
        **Analisis Parameter: {param_name}**
        
        **Data Tanaman:**
        - Jenis Tanaman: {crop_type}
        - {param_name}: {value} {'kg/ha' if param_name.lower() in ['nitrogen', 'phosphorus', 'potassium'] else '°C' if param_name.lower() == 'temperature' else '%' if param_name.lower() == 'humidity' else 'mm' if param_name.lower() == 'rainfall' else ''}
        
        **Konteks Parameter Lainnya:**
        """
        
        if all_sensor_data:
            for key, val in all_sensor_data.items():
                if key != param_name.lower() and key not in ['selected_crop', 'selected_crop_display', 'location', 'coordinates', 'location_source', 'land_area']:
                    unit = 'kg/ha' if key in ['nitrogen', 'phosphorus', 'potassium'] else '°C' if key == 'temperature' else '%' if key == 'humidity' else 'mm' if key == 'rainfall' else ''
                    context += f"- {key.title()}: {val} {unit}\n"
        
        # Create prompt for LLM analysis
        prompt = f"""
        Sebagai ahli pertanian AI, analisis parameter {param_name} berikut untuk tanaman {crop_type}:

        {context}

        Berikan analisis dalam format JSON berikut (WAJIB gunakan format ini):
        {{
            "status": "optimal|good|moderate|poor",
            "color": "🟢|🟡|🟠|🔴",
            "details": "penjelasan singkat kondisi parameter",
            "recommendation": "rekomendasi spesifik dan praktis",
            "score": "nilai 0-100"
        }}

        **Panduan Analisis:**
        1. Pertimbangkan kebutuhan spesifik tanaman {crop_type}
        2. Evaluasi dalam konteks parameter lainnya  
        3. Berikan rekomendasi yang praktis dan spesifik untuk petani Indonesia
        4. Gunakan pengetahuan pertanian modern dan best practices
        5. Status: optimal (80-100), good (60-79), moderate (40-59), poor (0-39)

        **Berikan hanya JSON response, tanpa teks tambahan lainnya.**
        """

        # Call LLM for analysis
        response = agricultural_llm.generate_response(
            prompt, 
            context, 
            temperature=0.3, 
            max_tokens=300
        )
        
        if response and response.strip():
            try:
                # Try to parse JSON response
                import json
                import re
                
                # Extract JSON from response
                json_match = re.search(r'\{.*\}', response, re.DOTALL)
                if json_match:
                    json_str = json_match.group()
                    analysis = json.loads(json_str)
                    
                    # Validate required keys
                    required_keys = ['status', 'color', 'details', 'recommendation']
                    if all(key in analysis for key in required_keys):
                        return analysis
                    
            except (json.JSONDecodeError, Exception) as e:
                print(f"⚠️ [DEBUG] LLM JSON parsing error for {param_name}: {e}")
        
        # Fallback if LLM fails
        return get_fallback_parameter_analysis(param_name, value, crop_type)
        
    except Exception as e:
        print(f"⚠️ [DEBUG] LLM parameter analysis error for {param_name}: {e}")
        return get_fallback_parameter_analysis(param_name, value, crop_type)

def get_fallback_parameter_analysis(param_name: str, value: float, crop_type: str) -> Dict[str, Any]:
    """Enhanced fallback analysis with crop-specific and location-aware recommendations"""
    
    # Enhanced rule-based fallback with better logic
    analysis = {
        'status': 'moderate',
        'color': '🟡',
        'details': f'{param_name} dalam kondisi standar',
        'recommendation': f'Pantau {param_name} secara berkala',
        'score': 50,
        'source': 'fallback'  # Indicator that this is fallback analysis
    }
    
    # Parameter-specific analysis with crop-aware thresholds
    param_lower = param_name.lower()
    
    if param_lower == 'nitrogen':
        if value >= 80:
            analysis.update({
                'status': 'optimal', 
                'color': '🟢', 
                'score': 85, 
                'details': 'Nitrogen sangat baik untuk pertumbuhan vegetatif',
                'recommendation': f'Pertahankan level nitrogen untuk {crop_type}. Aplikasi pupuk urea sesuai jadwal tanam.'
            })
        elif value >= 50:
            analysis.update({
                'status': 'good', 
                'color': '🟡', 
                'score': 70, 
                'details': 'Nitrogen cukup baik namun bisa dioptimalkan',
                'recommendation': f'Tambahkan pupuk urea 100-150 kg/ha untuk meningkatkan pertumbuhan {crop_type}.'
            })
        elif value < 20:
            analysis.update({
                'status': 'poor', 
                'color': '🔴', 
                'score': 30, 
                'details': 'Nitrogen sangat rendah, menghambat pertumbuhan',
                'recommendation': f'Segera aplikasi pupuk urea 200-250 kg/ha. Pertimbangkan pupuk organik untuk {crop_type}.'
            })
        else:
            analysis.update({
                'recommendation': f'Aplikasi pupuk nitrogen bertahap untuk {crop_type}. Gunakan urea 150-200 kg/ha.'
            })
    
    elif param_lower == 'phosphorus':
        if value >= 60:
            analysis.update({
                'status': 'optimal', 
                'color': '🟢', 
                'score': 85, 
                'details': 'Fosfor excellent untuk pembungaan dan perakaran',
                'recommendation': f'Level fosfor optimal untuk {crop_type}. Pertahankan dengan pupuk TSP/SP-36.'
            })
        elif value >= 30:
            analysis.update({
                'status': 'good', 
                'color': '🟡', 
                'score': 65, 
                'details': 'Fosfor cukup baik, mendukung perkembangan akar',
                'recommendation': f'Tambahkan TSP 100-150 kg/ha untuk optimalisasi pembungaan {crop_type}.'
            })
        elif value < 15:
            analysis.update({
                'status': 'poor', 
                'color': '🔴', 
                'score': 25, 
                'details': 'Fosfor sangat rendah, akar lemah',
                'recommendation': f'Aplikasi TSP/SP-36 200 kg/ha segera. Fosfor kritis untuk {crop_type}.'
            })
        else:
            analysis.update({
                'recommendation': f'Gunakan pupuk fosfat 150-200 kg/ha untuk mendukung perakaran {crop_type}.'
            })
    
    elif param_lower == 'potassium':
        if value >= 100:
            analysis.update({
                'status': 'optimal', 
                'color': '🟢', 
                'score': 90, 
                'details': 'Kalium optimal untuk kualitas hasil dan ketahanan',
                'recommendation': f'Kalium excellent untuk {crop_type}. Pertahankan dengan KCl sesuai kebutuhan.'
            })
        elif value >= 60:
            analysis.update({
                'status': 'good', 
                'color': '🟡', 
                'score': 70, 
                'details': 'Kalium baik, mendukung kualitas hasil',
                'recommendation': f'Tambahkan KCl 100-150 kg/ha untuk meningkatkan kualitas buah {crop_type}.'
            })
        elif value < 30:
            analysis.update({
                'status': 'poor', 
                'color': '🔴', 
                'score': 35, 
                'details': 'Kalium rendah, hasil berkualitas buruk',
                'recommendation': f'Aplikasi KCl 200 kg/ha segera. Kalium vital untuk kualitas {crop_type}.'
            })
        else:
            analysis.update({
                'recommendation': f'Gunakan pupuk kalium 150-200 kg/ha untuk meningkatkan kualitas {crop_type}.'
            })
    
    elif param_lower == 'ph':
        if 6.0 <= value <= 7.0:
            analysis.update({
                'status': 'optimal', 
                'color': '🟢', 
                'score': 95, 
                'details': 'pH ideal untuk penyerapan nutrisi maksimal',
                'recommendation': f'pH sempurna untuk {crop_type}. Pertahankan dengan manajemen bahan organik.'
            })
        elif 5.5 <= value < 6.0:
            analysis.update({
                'status': 'good', 
                'color': '🟡', 
                'score': 75, 
                'details': 'pH agak asam, masih dalam toleransi',
                'recommendation': f'Aplikasi kapur pertanian 500-1000 kg/ha untuk {crop_type}. Tambahkan kompos.'
            })
        elif 7.0 < value <= 7.5:
            analysis.update({
                'status': 'good', 
                'color': '🟡', 
                'score': 75, 
                'details': 'pH agak basa, perlu penyesuaian',
                'recommendation': f'Tambahkan bahan organik dan sulfur untuk menurunkan pH. Sesuaikan untuk {crop_type}.'
            })
        elif value < 5.0:
            analysis.update({
                'status': 'poor', 
                'color': '🔴', 
                'score': 25, 
                'details': 'pH sangat asam, menghambat nutrisi',
                'recommendation': f'Kapur dolomit 2-3 ton/ha sangat diperlukan. pH kritikal untuk {crop_type}.'
            })
        elif value > 8.0:
            analysis.update({
                'status': 'poor', 
                'color': '🔴', 
                'score': 25, 
                'details': 'pH sangat basa, nutrisi terkunci',
                'recommendation': f'Aplikasi sulfur dan kompos 2-3 ton/ha. pH terlalu tinggi untuk {crop_type}.'
            })
    
    elif param_lower == 'temperature':
        if 20 <= value <= 30:
            analysis.update({
                'status': 'optimal', 
                'color': '🟢', 
                'score': 90, 
                'details': 'Suhu ideal untuk fotosintesis dan pertumbuhan',
                'recommendation': f'Suhu optimal untuk {crop_type}. Pertahankan dengan naungan jika perlu.'
            })
        elif 15 <= value < 20:
            analysis.update({
                'status': 'good', 
                'color': '🟡', 
                'score': 70, 
                'details': 'Suhu agak dingin, pertumbuhan melambat',
                'recommendation': f'Gunakan mulsa plastik hitam untuk menghangatkan tanah {crop_type}.'
            })
        elif 30 < value <= 35:
            analysis.update({
                'status': 'good', 
                'color': '🟡', 
                'score': 70, 
                'details': 'Suhu agak panas, perlu perhatian',
                'recommendation': f'Pasang paranet 25-50% dan tingkatkan irigasi untuk {crop_type}.'
            })
        elif value < 10:
            analysis.update({
                'status': 'poor', 
                'color': '🔴', 
                'score': 20, 
                'details': 'Suhu terlalu dingin, pertumbuhan terhenti',
                'recommendation': f'Gunakan greenhouse/tunnel untuk melindungi {crop_type} dari dingin.'
            })
        elif value > 40:
            analysis.update({
                'status': 'poor', 
                'color': '🔴', 
                'score': 20, 
                'details': 'Suhu ekstrem panas, stress tanaman',
                'recommendation': f'Pasang shade net 70% dan sistem irigasi otomatis untuk {crop_type}.'
            })
    
    elif param_lower == 'humidity':
        if 60 <= value <= 70:
            analysis.update({
                'status': 'optimal', 
                'color': '🟢', 
                'score': 85, 
                'details': 'Kelembaban ideal untuk pertumbuhan',
                'recommendation': f'Kelembaban sempurna untuk {crop_type}. Jaga sirkulasi udara yang baik.'
            })
        elif 50 <= value < 60:
            analysis.update({
                'status': 'good', 
                'color': '🟡', 
                'score': 70, 
                'details': 'Kelembaban agak rendah, perlu peningkatan',
                'recommendation': f'Tingkatkan irigasi sprinkler dan mulsa organik untuk {crop_type}.'
            })
        elif 70 < value <= 80:
            analysis.update({
                'status': 'good', 
                'color': '🟡', 
                'score': 70, 
                'details': 'Kelembaban agak tinggi, awas penyakit',
                'recommendation': f'Perbaiki drainase dan sirkulasi udara. Aplikasi fungisida preventif untuk {crop_type}.'
            })
        elif value < 30:
            analysis.update({
                'status': 'poor', 
                'color': '🔴', 
                'score': 25, 
                'details': 'Kelembaban sangat rendah, tanaman stress',
                'recommendation': f'Sistem irigasi tetes dan mulsa tebal sangat diperlukan untuk {crop_type}.'
            })
        elif value > 95:
            analysis.update({
                'status': 'poor', 
                'color': '🔴', 
                'score': 25, 
                'details': 'Kelembaban sangat tinggi, risiko jamur',
                'recommendation': f'Perbaiki drainase dan ventilasi segera. Monitor penyakit pada {crop_type}.'
            })
    
    elif param_lower == 'rainfall':
        if 150 <= value <= 250:
            analysis.update({
                'status': 'optimal', 
                'color': '🟢', 
                'score': 85, 
                'details': 'Curah hujan ideal untuk pertumbuhan',
                'recommendation': f'Curah hujan optimal untuk {crop_type}. Pertahankan sistem drainase.'
            })
        elif 100 <= value < 150:
            analysis.update({
                'status': 'good', 
                'color': '🟡', 
                'score': 70, 
                'details': 'Curah hujan cukup, perlu irigasi tambahan',
                'recommendation': f'Siapkan irigasi suplemen untuk musim kering. Gunakan mulsa untuk {crop_type}.'
            })
        elif 250 < value <= 300:
            analysis.update({
                'status': 'good', 
                'color': '🟡', 
                'score': 70, 
                'details': 'Curah hujan agak tinggi, perlu drainase',
                'recommendation': f'Buat saluran drainase dan bedengan tinggi untuk {crop_type}.'
            })
        elif value < 50:
            analysis.update({
                'status': 'poor', 
                'color': '🔴', 
                'score': 30, 
                'details': 'Curah hujan sangat rendah, kekeringan',
                'recommendation': f'Sistem irigasi tetes/sprinkler wajib. Pilih varietas tahan kering untuk {crop_type}.'
            })
        elif value > 400:
            analysis.update({
                'status': 'poor', 
                'color': '🔴', 
                'score': 30, 
                'details': 'Curah hujan sangat tinggi, banjir',
                'recommendation': f'Sistem drainase intensif dan bedengan tinggi untuk {crop_type}.'
            })
    
    # Crop-specific adjustments for Indonesian conditions
    crop_lower = crop_type.lower()
    
    if 'rice' in crop_lower or 'padi' in crop_lower:
        if param_lower == 'humidity' and value > 75:
            analysis.update({
                'status': 'optimal', 
                'color': '🟢', 
                'score': 90, 
                'details': 'Kelembaban tinggi cocok untuk padi',
                'recommendation': 'Kelembaban tinggi ideal untuk padi. Jaga genangan air 5-10 cm.'
            })
        elif param_lower == 'rainfall' and value > 200:
            analysis.update({
                'status': 'optimal', 
                'color': '🟢', 
                'score': 85, 
                'details': 'Curah hujan tinggi sangat baik untuk padi',
                'recommendation': 'Curah hujan tinggi sangat mendukung padi. Atur sistem pengairan sawah.'
            })
        elif param_lower == 'nitrogen' and value >= 60:
            analysis.update({
                'recommendation': 'Aplikasi urea 300 kg/ha dalam 3 tahap untuk padi. Fase vegetatif butuh N tinggi.'
            })
    
    elif 'corn' in crop_lower or 'jagung' in crop_lower:
        if param_lower == 'nitrogen' and value >= 70:
            analysis.update({
                'recommendation': 'Nitrogen tinggi excellent untuk jagung. Aplikasi urea 400 kg/ha bertahap.'
            })
        elif param_lower == 'potassium' and value >= 80:
            analysis.update({
                'recommendation': 'Kalium tinggi untuk kualitas bulir jagung. Pertahankan dengan KCl.'
            })
    
    elif 'potato' in crop_lower or 'kentang' in crop_lower:
        if param_lower == 'potassium' and value >= 90:
            analysis.update({
                'recommendation': 'Kalium tinggi excellent untuk kentang. Kualitas umbi akan optimal.'
            })
        elif param_lower == 'ph' and 5.0 <= value <= 6.5:
            analysis.update({
                'recommendation': 'pH agak asam ideal untuk kentang. Hindari tanah alkalin.'
            })
    
    elif 'tomato' in crop_lower or 'tomat' in crop_lower:
        if param_lower == 'ph' and 6.0 <= value <= 6.8:
            analysis.update({
                'recommendation': 'pH ideal untuk tomat. Pertahankan dengan kompos dan kapur.'
            })
        elif param_lower == 'potassium' and value >= 80:
            analysis.update({
                'recommendation': 'Kalium tinggi untuk rasa manis tomat. Tingkatkan KCl di fase buah.'
            })
    
    elif 'chili' in crop_lower or 'cabai' in crop_lower:
        if param_lower == 'potassium' and value >= 85:
            analysis.update({
                'recommendation': 'Kalium tinggi untuk kepedasan cabai optimal. Gunakan KCl dan abu sekam.'
            })
        elif param_lower == 'humidity' and 50 <= value <= 65:
            analysis.update({
                'recommendation': 'Kelembaban sedang ideal untuk cabai. Hindari kelembaban tinggi.'
            })
    
    elif 'onion' in crop_lower or 'bawang' in crop_lower:
        if param_lower == 'sulfur' and value >= 20:
            analysis.update({
                'recommendation': 'Sulfur tinggi untuk aroma bawang. Tambahkan pupuk sulfat.'
            })
        elif param_lower == 'ph' and 6.0 <= value <= 7.0:
            analysis.update({
                'recommendation': 'pH netral optimal untuk bawang. Hindari tanah asam.'
            })
    
    # Add regional Indonesia-specific advice
    if 'recommendation' in analysis:
        base_rec = analysis['recommendation']
        # Add Indonesia-specific context
        if param_lower in ['humidity', 'rainfall']:
            analysis['recommendation'] = f"{base_rec} Sesuaikan dengan musim hujan/kemarau Indonesia."
        elif param_lower == 'temperature':
            analysis['recommendation'] = f"{base_rec} Pertimbangkan iklim tropis Indonesia."
        elif param_lower in ['nitrogen', 'phosphorus', 'potassium']:
            analysis['recommendation'] = f"{base_rec} Gunakan pupuk lokal yang tersedia di Indonesia."
    
    return analysis

def display_ai_analysis_tab(evaluation: Dict[str, Any]):
    """Display AI analysis results"""
    
    st.markdown("### Analisis Paramater")
    
    # Get sensor data for parameter analysis
    sensor_data = evaluation.get('sensor_data', {})
    selected_crop = sensor_data.get('selected_crop', '')
    
    
    # Check LLM availability status
    llm_available = False
    try:
        global agricultural_llm
        if 'agricultural_llm' not in globals():
            from src.services.llm_service import agricultural_llm
        llm_available = agricultural_llm.llm_manager.is_available()
    except:
        llm_available = False
    
    # Show LLM status
    if not llm_available:
        st.warning("⚠️ **Status:** Menggunakan analisis dasar (LLM tidak tersedia)")
    
    # Define parameters to analyze
    parameters = [
        ('Nitrogen', sensor_data.get('nitrogen', 0), 'kg/ha'),
        ('Phosphorus', sensor_data.get('phosphorus', 0), 'kg/ha'),
        ('Potassium', sensor_data.get('potassium', 0), 'kg/ha'),
        ('pH', sensor_data.get('ph', 7.0), ''),
        ('Temperature', sensor_data.get('temperature', 25), '°C'),
        ('Humidity', sensor_data.get('humidity', 60), '%'),
        ('Rainfall', sensor_data.get('rainfall', 150), 'mm'),
    ]
    
    # Create two columns for parameter analysis
    col1, col2 = st.columns(2)
    
    # Analysis with loading indicator
    with st.spinner("🤖 Menganalisis parameter dengan AI..."):
        param_analyses = []
        
        for i, (param_name, value, unit) in enumerate(parameters):
            # Get LLM analysis for this parameter
            analysis = analyze_parameter_with_llm(param_name, value, selected_crop, sensor_data)
            param_analyses.append(analysis)
            
            # Alternate between columns for display
            with col1 if i % 2 == 0 else col2:
                with st.container():
                    st.markdown(f"**{param_name}:** {value} {unit}")
                    
                    # Status badge with score
                    score = analysis.get('score', 50)
                    if analysis['status'] == 'optimal':
                        st.success(f"✅ **Status:** {analysis['status'].title()} ({score}/100)")
                    elif analysis['status'] == 'good':
                        st.info(f"ℹ️ **Status:** {analysis['status'].title()} ({score}/100)")
                    elif analysis['status'] == 'moderate':
                        st.warning(f"⚠️ **Status:** {analysis['status'].title()} ({score}/100)")
                    else:
                        st.error(f"❌ **Status:** {analysis['status'].title()} ({score}/100)")
                    
                    # Details and recommendation
                    st.caption(f"📝 {analysis['details']}")
                    if analysis['recommendation']:
                        st.caption(f"💡 **Rekomendasi:** {analysis['recommendation']}")
                    
                    st.markdown("---")
    
    # Overall Parameter Assessment
    st.markdown("#### 🎯 Ringkasan Status Parameter")
    
    # Calculate overall status from already computed analyses
    optimal_count = sum(1 for a in param_analyses if a['status'] == 'optimal')
    good_count = sum(1 for a in param_analyses if a['status'] == 'good')
    moderate_count = sum(1 for a in param_analyses if a['status'] == 'moderate')
    poor_count = sum(1 for a in param_analyses if a['status'] == 'poor')
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("🟢 Optimal", optimal_count, f"{optimal_count/len(parameters)*100:.0f}%")
    with col2:
        st.metric("🟡 Baik", good_count, f"{good_count/len(parameters)*100:.0f}%")
    with col3:
        st.metric("🟠 Cukup", moderate_count, f"{moderate_count/len(parameters)*100:.0f}%")
    with col4:
        st.metric("🔴 Perlu Perbaikan", poor_count, f"{poor_count/len(parameters)*100:.0f}%")
    
    # Overall recommendation with average score
    avg_score = sum(a.get('score', 50) for a in param_analyses) / len(param_analyses)


def display_recommendations_tab(evaluation: Dict[str, Any]):
    """Display recommendations"""
    
    st.markdown("### 📋 Rekomendasi Komprehensif")
    
    recommendations = evaluation.get('recommendations', {})
    
    # Immediate Actions
    if recommendations.get('immediate_actions'):
        st.markdown("#### ⚡ Tindakan Segera")
        for action in recommendations['immediate_actions']:
            st.markdown(f"- {action}")
    
    # Short-term Improvements
    if recommendations.get('short_term_improvements'):
        st.markdown("#### 🔧 Perbaikan Jangka Pendek")
        for improvement in recommendations['short_term_improvements']:
            st.markdown(f"- {improvement}")
    
    # Long-term Strategies
    if recommendations.get('long_term_strategies'):
        st.markdown("#### 🎯 Strategi Jangka Panjang")
        for strategy in recommendations['long_term_strategies']:
            st.markdown(f"- {strategy}")
    
    # Resource Requirements
    if recommendations.get('resource_requirements'):
        st.markdown("#### 💰 Kebutuhan Sumber Daya")
        resources = recommendations['resource_requirements']
        
        col1, col2 = st.columns(2)
        with col1:
            for key, value in list(resources.items())[:len(resources)//2]:
                st.markdown(f"**{key.replace('_', ' ').title()}:** {value}")
        with col2:
            for key, value in list(resources.items())[len(resources)//2:]:
                st.markdown(f"**{key.replace('_', ' ').title()}:** {value}")
    
    # Timeline
    if recommendations.get('timeline'):
        st.markdown("#### 📅 Timeline Implementasi")
        timeline = recommendations['timeline']
        for period, activity in timeline.items():
            st.markdown(f"**{period.replace('_', ' ').title()}:** {activity}")

def display_location_context_tab(evaluation: Dict[str, Any], location_advice: Dict[str, Any]):
    """Display location context analysis"""
    
    st.markdown("### 📍 Analisis Konteks Lokasi")
    
    location_context = evaluation.get('location_context')
    
    if location_context:
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### 🗺️ Informasi Wilayah")
            st.markdown(f"**Region:** {location_context.get('region', 'Unknown').replace('_', ' ').title()}")
            st.markdown(f"**Zona Iklim:** {location_context.get('climate_zone', 'Unknown').replace('_', ' ').title()}")
            st.markdown(f"**Estimasi Ketinggian:** {location_context.get('elevation_estimate', 0)} meter")
            st.markdown(f"**Confidence:** {location_context.get('confidence', 0):.1%}")
        
        with col2:
            regional_data = location_context.get('regional_data', {})
            if regional_data:
                st.markdown("#### 🌾 Data Regional")
                if 'main_crops' in regional_data:
                    st.markdown(f"**Tanaman Utama:** {', '.join(regional_data['main_crops'])}")
                if 'rainfall' in regional_data:
                    st.markdown(f"**Curah Hujan:** {regional_data['rainfall']}")
                if 'temperature' in regional_data:
                    st.markdown(f"**Suhu:** {regional_data['temperature']}")
    
    # Location-specific advice
    if location_advice:
        st.markdown("#### 🎯 Saran Spesifik Lokasi")
        
        # Crop recommendations
        crop_recs = location_advice.get('crop_recommendations', [])
        if crop_recs:
            st.markdown("**Rekomendasi Tanaman:**")
            for crop in crop_recs:
                st.markdown(f"- {crop}")
        
        # Climate adaptations
        climate_adapt = location_advice.get('climate_adaptations', [])
        if climate_adapt:
            st.markdown("**Adaptasi Iklim:**")
            for adaptation in climate_adapt:
                st.markdown(f"- {adaptation}")

def display_risk_analysis_tab(evaluation: Dict[str, Any]):
    """Display risk analysis"""
    
    st.markdown("### ⚠️ Analisis Risiko")
    
    risk_assessment = evaluation.get('risk_assessment', {})
    
    # Overall risk level
    overall_risk = risk_assessment.get('overall_risk_level', 'medium')
    risk_color = "🟢" if overall_risk == "low" else "🟡" if overall_risk == "medium" else "🔴"
    st.markdown(f"#### {risk_color} Tingkat Risiko Keseluruhan: {overall_risk.title()}")
    
    # Specific risks
    col1, col2 = st.columns(2)
    
    with col1:
        env_risks = risk_assessment.get('environmental_risks', [])
        if env_risks:
            st.markdown("**🌍 Risiko Lingkungan:**")
            for risk in env_risks:
                severity = risk.get('level', 'medium')
                severity_icon = "🔴" if severity == "high" else "🟡" if severity == "medium" else "🟢"
                st.markdown(f"- {severity_icon} {risk.get('risk', 'Unknown')}")
                st.markdown(f"  *Mitigasi: {risk.get('mitigation', 'N/A')}*")
    
    with col2:
        nut_risks = risk_assessment.get('nutritional_risks', [])
        if nut_risks:
            st.markdown("**🧪 Risiko Nutrisi:**")
            for risk in nut_risks:
                severity = risk.get('level', 'medium')
                severity_icon = "🔴" if severity == "high" else "🟡" if severity == "medium" else "🟢"
                st.markdown(f"- {severity_icon} {risk.get('risk', 'Unknown')}")
                st.markdown(f"  *Mitigasi: {risk.get('mitigation', 'N/A')}*")
    
    # Location risks
    loc_risks = risk_assessment.get('location_risks', [])
    if loc_risks:
        st.markdown("**📍 Risiko Lokasi:**")
        for risk in loc_risks:
            severity = risk.get('level', 'medium')
            severity_icon = "🔴" if severity == "high" else "🟡" if severity == "medium" else "🟢"
            st.markdown(f"- {severity_icon} {risk.get('risk', 'Unknown')}")
            st.markdown(f"  *Mitigasi: {risk.get('mitigation', 'N/A')}*")

def display_alternatives_tab(evaluation: Dict[str, Any]):
    """Display alternative crop suggestions"""
    
    st.markdown("### 🔄 Alternatif Tanaman")
    
    alternatives = evaluation.get('alternative_crops', [])
    ml_analysis = evaluation.get('ml_analysis', {})
    
    # Show ML-based alternatives only if they're better than user's choice
    if ml_analysis.get('available') and 'top_recommendations' in ml_analysis and 'confidence' in ml_analysis:
        selected_crop_confidence = ml_analysis['confidence']
        top_recs = ml_analysis['top_recommendations'][:5]
        
        better_alternatives = [
            (crop, conf) for crop, conf in top_recs 
            if conf > selected_crop_confidence
        ]
        
        if better_alternatives:
            st.markdown("#### 🌾 Tanaman Alternatif dengan Kesesuaian Lebih Tinggi")
            st.info(f"Berdasarkan analisis ML, tanaman berikut memiliki tingkat kesesuaian lebih tinggi dari pilihan Anda ({selected_crop_confidence:.1%}):")
            
            for i, (crop, conf) in enumerate(better_alternatives, 1):
                col1, col2, col3 = st.columns([2, 1, 1])
                
                with col1:
                    st.markdown(f"**{i}. {crop.replace('_', ' ').title()}**")
                
                with col2:
                    improvement = ((conf - selected_crop_confidence) / selected_crop_confidence) * 100
                    st.markdown(f"Confidence: {conf:.1%}")
                    st.markdown(f"*Peningkatan: +{improvement:.1f}%*")
                
                with col3:
                    st.markdown("*Machine Learning*")
        else:
            st.markdown("#### ✅ Pilihan Tanaman Optimal")
            st.success("Tanaman pilihan Anda sudah optimal berdasarkan analisis ML!")
    
    # Show other alternatives from evaluation service
    if alternatives:
        st.markdown("#### 🔄 Alternatif Lainnya")
        
        for i, alt in enumerate(alternatives, 1):
            col1, col2, col3 = st.columns([2, 1, 1])
            
            with col1:
                st.markdown(f"**{i}. {alt['crop'].replace('_', ' ').title()}**")
            
            with col2:
                st.markdown(f"Confidence: {alt['confidence']:.1%}")
            
            with col3:
                st.markdown(f"*{alt['source']}*")
    
    # Optimization suggestions
    optimization = evaluation.get('optimization_suggestions', [])
    if optimization:
        st.markdown("#### 🔧 Saran Optimasi")
        for suggestion in optimization:
            st.markdown(f"- {suggestion}")
    
    # Alternative crops based on condition improvement
    st.markdown("#### 💡 Jika Kondisi Diperbaiki")
    
    suitability_score = evaluation.get('suitability_score', 0.0)
    if suitability_score < 0.6:
        st.markdown("Dengan perbaikan kondisi tanah dan nutrisi, tanaman berikut mungkin lebih cocok:")
        
        # Get location context for better suggestions
        location_context = evaluation.get('location_context')
        if location_context:
            regional_data = location_context.get('regional_data', {})
            main_crops = regional_data.get('main_crops', [])
            
            for crop in main_crops[:3]:
                st.markdown(f"- 🌱 {crop.replace('_', ' ').title()}")
        else:
            st.markdown("- 🌱 Konsultasikan dengan petani lokal untuk rekomendasi spesifik")

def save_comprehensive_results(evaluation: Dict[str, Any], location_advice: Dict[str, Any], sensor_data: Dict[str, Any]):
    """Save comprehensive evaluation results with clean MongoDB document format"""
    
    import uuid
    
    # Extract ML results from evaluation
    ml_analysis = evaluation.get('ml_analysis', {})
    ml_result = {
        'recommendation': ml_analysis.get('crop_prediction', 'N/A'),
        'confidence': ml_analysis.get('confidence', 0.0),
        'explanation': ml_analysis.get('explanation', ''),
        'available': ml_analysis.get('available', False)
    } if ml_analysis.get('available') else None
    
    # ✅ IMPROVED: Clean AI results format - only essential data
    llm_analysis = evaluation.get('llm_analysis', '')
    recommendations = evaluation.get('recommendations', {})
    
    # Extract only essential recommendation data
    essential_recommendations = {}
    if recommendations:
        # Only keep immediate actions and key insights
        if 'immediate_actions' in recommendations:
            essential_recommendations['immediate_actions'] = recommendations['immediate_actions'][:3]  # Max 3 items
        if 'key_insights' in recommendations:
            essential_recommendations['key_insights'] = recommendations['key_insights'][:2]  # Max 2 items
        if 'fertilizer_recommendations' in recommendations:
            essential_recommendations['fertilizer'] = recommendations['fertilizer_recommendations']
    
    # ✅ CLEAN: Simplified ai_result structure for MongoDB
    ai_result = {
        'llm_analysis': llm_analysis[:1000] if llm_analysis else '',  # Limit text length
        'recommendations': essential_recommendations,
        'suitability_score': evaluation.get('suitability_score', 0.0),
        'confidence_level': evaluation.get('confidence_level', 'medium'),
        'analysis_timestamp': datetime.now().isoformat(),
        'analysis_type': 'comprehensive' if llm_analysis else 'basic'
    }
    
    # ✅ CLEAN: Simplified location context (only essential data)
    location_context = None
    if location_advice:
        location_context = {
            'region': location_advice.get('location_context', {}).get('region', 'unknown'),
            'climate_suitability': location_advice.get('location_context', {}).get('climate_suitability', 'medium'),
            'main_crops': location_advice.get('location_context', {}).get('regional_data', {}).get('main_crops', [])[:3]
        }
    
    # ✅ CLEAN: MongoDB document structure
    interaction_data = {
        'id': str(uuid.uuid4())[:8],
        'timestamp': datetime.now(),
        'sensor_data': sensor_data,
        'ml_result': ml_result,
        'ai_result': ai_result,  # ✅ Clean AI results
        'location_context': location_context,  # ✅ Essential location data only
        'title': f"{sensor_data['selected_crop_display']} - {sensor_data['location'].split(',')[0]}",
        'suitability_score': evaluation.get('suitability_score', 0.0),
        'confidence_level': evaluation.get('confidence_level', 'medium'),
        'analysis_status': 'completed'
    }
    
    # ✅ DEBUG: Log what AI data is being saved
    print(f"💾 Saving AI analysis to MongoDB:")
    print(f"  🤖 LLM Analysis: {len(ai_result['llm_analysis'])} characters")
    print(f"  💡 Recommendations: {len(essential_recommendations)} categories")
    print(f"  📊 Suitability Score: {ai_result['suitability_score']:.2f}")
    print(f"  🎯 Analysis Type: {ai_result['analysis_type']}")
    
    # Clear preset data after successful submission
    if st.session_state.preset_data:
        preset_name = st.session_state.preset_name
        st.session_state.preset_data = None
        st.session_state.preset_name = None
        print(f"✅ Preset '{preset_name}' successfully used and cleared")
    
    # Save to session state
    if 'interaction_history' not in st.session_state:
        st.session_state.interaction_history = []
    
    st.session_state.interaction_history.append(interaction_data)
    st.session_state.current_interaction_id = interaction_data['id']
    
    # Keep only last 50 interactions in session state
    if len(st.session_state.interaction_history) > 50:
        st.session_state.interaction_history = st.session_state.interaction_history[-50:]
    
    # Save to MongoDB
    if save_interaction_to_db(interaction_data):
        st.success("✅ **Analisis AI telah disimpan ke database dan history**")
        print(f"✅ AI analysis successfully saved to MongoDB: {interaction_data['id']}")
        st.session_state.sidebar_mode = 'history'
    else:
        st.success("✅ **Analisis AI telah disimpan ke session history**")
        print(f"⚠️ AI analysis saved to session only: {interaction_data['id']}")
        st.session_state.sidebar_mode = 'history'
    
    # Show action buttons
    col1 = st.columns(1)
    
    with col1:
        if st.button("🔄 Analisis Baru", type="secondary"):
            reset_session_to_default()
            st.rerun()
    

def display_basic_analysis_fallback(sensor_data: Dict[str, Any]):
    """Fallback to basic ML analysis if comprehensive analysis fails"""
    
    try:
        predictor = AICropPredictor()
        
        if not predictor.is_model_loaded():
            st.error("❌ **Model ML tidak dapat dimuat** - Periksa file model di folder `data/`")
            return
        
        # Get prediction
        recommendation, confidence, explanation = predictor.evaluate_crop_suitability(
            sensor_data, sensor_data['selected_crop']
        )
        
        # Display basic results
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric(
                "🎯 Rekomendasi (ML)",
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
        
        # Show explanation
        st.markdown("### 💡 Penjelasan ML Model")
        st.markdown(explanation)
        
        st.info("ℹ️ **Menampilkan analisis dasar karena layanan LLM tidak tersedia**")
        
        # ✅ FIXED: Save basic analysis results to history and MongoDB
        try:
            import uuid
            
            # ✅ CLEAN: Basic AI result using same format as comprehensive
            basic_ai_result = {
                'llm_analysis': '',  # Empty for basic analysis
                'recommendations': {
                    'immediate_actions': [f"Tanaman {sensor_data['selected_crop_display']} {recommendation.lower()} untuk kondisi lahan ini"]
                },
                'suitability_score': confidence,
                'confidence_level': "high" if confidence > 0.7 else "medium" if confidence > 0.5 else "low",
                'analysis_timestamp': datetime.now().isoformat(),
                'analysis_type': 'basic'
            }
            
            # ML result
            ml_result = {
                'recommendation': recommendation,
                'confidence': confidence,
                'explanation': explanation,
                'available': True
            }
            
            # ✅ CLEAN: Same document structure as comprehensive analysis
            interaction_data = {
                'id': str(uuid.uuid4())[:8],
                'timestamp': datetime.now(),
                'sensor_data': sensor_data,
                'ml_result': ml_result,
                'ai_result': basic_ai_result,  # ✅ Clean basic AI results
                'location_context': None,  # No location context for basic
                'title': f"{sensor_data['selected_crop_display']} - {sensor_data['location'].split(',')[0]} (Basic)",
                'suitability_score': confidence,
                'confidence_level': basic_ai_result['confidence_level'],
                'analysis_status': 'completed'
            }
            
            # ✅ DEBUG: Log basic AI data being saved
            print(f"💾 Saving Basic AI analysis to MongoDB:")
            print(f"  🎯 Analysis Type: {basic_ai_result['analysis_type']}")
            print(f"  📊 Suitability Score: {basic_ai_result['suitability_score']:.2f}")
            print(f"  💡 Recommendations: {len(basic_ai_result['recommendations'])} categories")
            
            # Save to session state
            if 'interaction_history' not in st.session_state:
                st.session_state.interaction_history = []
            
            st.session_state.interaction_history.append(interaction_data)
            st.session_state.current_interaction_id = interaction_data['id']
            
            # Keep only last 50 interactions in session state
            if len(st.session_state.interaction_history) > 50:
                st.session_state.interaction_history = st.session_state.interaction_history[-50:]
            
            # Save to MongoDB
            if save_interaction_to_db(interaction_data):
                st.success("✅ **Analisis dasar AI telah disimpan ke database dan history**") 
                print(f"✅ Basic AI analysis saved to MongoDB: {interaction_data['id']}")
            else:
                st.success("✅ **Analisis dasar AI telah disimpan ke session history**")
                print(f"⚠️ Basic AI analysis saved to session only: {interaction_data['id']}")
            
            # Update sidebar mode to show history
            st.session_state.sidebar_mode = 'history'
            
        except Exception as save_error:
            print(f"❌ Error saving basic analysis results: {str(save_error)}")
            st.warning("⚠️ **Hasil analisis ditampilkan tetapi tidak dapat disimpan ke history**")
        
    except Exception as e:
        pass

# ==================== SIDEBAR ====================

def reset_session_to_default():
    """Reset entire session state to default values for new analysis"""
    
    # Clear all analysis-related data
    session_keys_to_clear = [
        'current_interaction_id',
        'preset_data',
        'preset_name',
        #'interaction_history',
        'loaded_interaction_data',
        
        # Location-related data
        'selected_location',
        'selected_location_pin',
        'temp_coordinates',
        'gps_location_data',
        'location_source',
        'pin_mode_active',
        'gps_completed',
        
        # Form and sensor data
        'current_sensor_data',
        'backup_sensor_data',
        'form_submitted',
        
        # Modal and analysis states
        'show_analysis_modal',
        'modal_stage',
        'modal_generated_questions',
        'modal_llm_answers',
        'analysis_results',
        
        # UI states  
        'show_llm_dialog',
        'map_center',
        'map_zoom',
        'last_clicked_coordinates'
    ]
    
    # Clear specified session state keys
    for key in session_keys_to_clear:
        if key in st.session_state:
            del st.session_state[key]
    
    # Reset sidebar mode to default
    st.session_state.sidebar_mode = 'new'
    
    # Reset location tab to default
    if 'location_tab' in st.session_state:
        st.session_state.location_tab = 'GPS'
    
    # Reset map state to default
    st.session_state.map_center = [-6.2088, 106.8456]  # Default Jakarta
    st.session_state.map_zoom = 10
    
    print("✅ Session state reset to default - ready for new analysis")

def display_sidebar():
    """Display sidebar with history and controls - Enhanced with better integration"""
    
    st.sidebar.markdown(f"# 📊 {UI_CONFIG['page_title']} Center")
    
    # Status indicators
    preset_loaded = bool(st.session_state.preset_data)
    history_loaded = bool(st.session_state.current_interaction_id)
    
    if preset_loaded:
        preset_name = st.session_state.preset_name or "Custom"
        st.sidebar.success(f"📋 **{preset_name}** loaded")
    elif history_loaded:
        st.sidebar.info("🔄 **History interaction** loaded")
    
    # Mode selection buttons with enhanced labels
    col1, col2 = st.sidebar.columns(2)
    with col1:
        history_count = len(st.session_state.interaction_history)
        history_label = f"📋 History" if history_count > 0 else "📋 History"
        if st.button(history_label, type="primary" if st.session_state.sidebar_mode == 'history' else "secondary"):
            st.session_state.sidebar_mode = 'history'
    with col2:
        new_label = "➕ New" + (" ✨" if preset_loaded else "")
        if st.button(new_label, type="primary" if st.session_state.sidebar_mode == 'new' else "secondary"):
            reset_session_to_default()
            st.session_state.sidebar_mode = 'history'
            st.rerun()
    
    st.sidebar.markdown("---")
    
    # Display appropriate sidebar content based on mode
    if st.session_state.sidebar_mode == 'history':
        from src.components.history_panel import display_interaction_history
        display_interaction_history()

# ==================== MAIN APPLICATION ====================

def main():
    """Main application function"""
    
    # Configure Streamlit
    configure_streamlit()
    
    # Initialize app
    initialize_app()
    
    # Display header (use new title from config)
    st.markdown(f"# {UI_CONFIG['page_icon']} {UI_CONFIG['page_title']}")
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
    
        
        # Show real-time system statu



if __name__ == "__main__":
    main() 