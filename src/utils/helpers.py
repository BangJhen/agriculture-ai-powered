"""
Helper utilities for Agricultural Decision Support System
Contains utility functions, library checks, and common operations.
"""

import streamlit as st
from datetime import datetime
from typing import Dict, List, Any, Optional

# Update config with library availability
from .config import (
    SHAP_AVAILABLE, FOLIUM_AVAILABLE, STREAMLIT_FOLIUM_AVAILABLE, 
    GEOPY_AVAILABLE, ERROR_MESSAGES, SUCCESS_MESSAGES
)

# ==================== LIBRARY AVAILABILITY CHECKS ====================

def check_library_availability():
    """Check and update availability of optional libraries"""
    global SHAP_AVAILABLE, FOLIUM_AVAILABLE, STREAMLIT_FOLIUM_AVAILABLE, GEOPY_AVAILABLE
    
    # Check SHAP availability
    try:
        import shap
        import matplotlib
        matplotlib.use('Agg')  # Use non-interactive backend
        import matplotlib.pyplot as plt
        SHAP_AVAILABLE = True
        print("✅ SHAP and matplotlib loaded successfully")
    except ImportError as e:
        SHAP_AVAILABLE = False
        print(f"⚠️ SHAP not available: {e}")
    
    # Check Folium availability
    try:
        import folium
        FOLIUM_AVAILABLE = True
        print("✅ Folium")
    except ImportError as e:
        FOLIUM_AVAILABLE = False
        print(f"❌ Folium: {e}")
    
    # Check Streamlit-Folium availability
    try:
        from streamlit_folium import st_folium
        STREAMLIT_FOLIUM_AVAILABLE = True
        print("✅ Streamlit-Folium")
    except ImportError as e:
        STREAMLIT_FOLIUM_AVAILABLE = False
        print(f"❌ Streamlit-Folium: {e}")
    
    # Check Geopy availability
    try:
        from geopy.geocoders import Nominatim
        from geopy.exc import GeopyError
        GEOPY_AVAILABLE = True
        print("✅ Geopy")
    except ImportError:
        GEOPY_AVAILABLE = False
        print("❌ Geopy")
    
    return {
        'shap': SHAP_AVAILABLE,
        'folium': FOLIUM_AVAILABLE,
        'streamlit_folium': STREAMLIT_FOLIUM_AVAILABLE,
        'geopy': GEOPY_AVAILABLE
    }

# ==================== SESSION STATE HELPERS ====================

def init_session_state():
    """Initialize required session state variables"""
    
    # Location-related session state
    if 'selected_location' not in st.session_state:
        st.session_state.selected_location = None
    if 'temp_coordinates' not in st.session_state:
        st.session_state.temp_coordinates = None
    if 'selected_location_pin' not in st.session_state:
        st.session_state.selected_location_pin = None
    if 'map_refresh_counter' not in st.session_state:
        st.session_state.map_refresh_counter = 0
    
    # GPS-related session state
    if 'gps_location_data' not in st.session_state:
        st.session_state.gps_location_data = None
    if 'gps_permission_requested' not in st.session_state:
        st.session_state.gps_permission_requested = False
    if 'gps_auto_refresh_completed' not in st.session_state:
        st.session_state.gps_auto_refresh_completed = False
    
    # History-related session state
    if 'interaction_history' not in st.session_state:
        st.session_state.interaction_history = []
    if 'current_interaction_id' not in st.session_state:
        st.session_state.current_interaction_id = None
    if 'preset_data' not in st.session_state:
        st.session_state.preset_data = None
    if 'preset_name' not in st.session_state:
        st.session_state.preset_name = None
    if 'sidebar_mode' not in st.session_state:
        st.session_state.sidebar_mode = 'history'  # 'history' or 'new'
    
    # Session management
    if 'session_id' not in st.session_state:
        # Use consistent global session ID for agricultural application
        # This ensures all interactions are persistent across refreshes
        st.session_state.session_id = "agricultural_global_session"

def clear_location_data():
    """Clear all location-related session state"""
    st.session_state.selected_location = None
    st.session_state.temp_coordinates = None
    st.session_state.selected_location_pin = None
    st.session_state.gps_location_data = None
    st.session_state.gps_auto_refresh_completed = False
    st.session_state.gps_permission_requested = False
    st.session_state.map_refresh_counter = st.session_state.get('map_refresh_counter', 0) + 1

# ==================== DATA VALIDATION HELPERS ====================

def validate_coordinates(lat: float, lng: float) -> bool:
    """Validate if coordinates are within Indonesia bounds"""
    # Indonesia approximate bounds
    lat_min, lat_max = -11.0, 6.0
    lng_min, lng_max = 95.0, 141.0
    
    return lat_min <= lat <= lat_max and lng_min <= lng <= lng_max

def validate_sensor_data(data: Dict[str, float]) -> Dict[str, bool]:
    """Validate sensor data ranges"""
    from .config import SENSOR_PARAMS
    
    validation_results = {}
    for param, value in data.items():
        if param in SENSOR_PARAMS:
            param_config = SENSOR_PARAMS[param]
            is_valid = param_config['min'] <= value <= param_config['max']
            validation_results[param] = is_valid
        else:
            validation_results[param] = True  # Unknown param, assume valid
    
    return validation_results

def sanitize_string(text: str, max_length: int = 100) -> str:
    """Sanitize and truncate string input"""
    if not isinstance(text, str):
        return str(text)[:max_length]
    return text.strip()[:max_length]

# ==================== FORMATTING HELPERS ====================

def format_timestamp(timestamp: datetime) -> str:
    """Format timestamp for display"""
    return timestamp.strftime("%d/%m/%Y %H:%M")

def format_coordinates(lat: float, lng: float, precision: int = 6) -> str:
    """Format coordinates for display"""
    return f"{lat:.{precision}f}°, {lng:.{precision}f}°"

def format_accuracy_level(accuracy: float) -> str:
    """Format GPS accuracy level with emoji"""
    from .config import GPS_CONFIG
    
    if accuracy < GPS_CONFIG['accuracy_excellent']:
        return f"🎯 Excellent ({accuracy:.0f}m)"
    elif accuracy < GPS_CONFIG['accuracy_good']:
        return f"✅ Good ({accuracy:.0f}m)"
    else:
        return f"⚠️ Fair ({accuracy:.0f}m)"

def format_confidence_score(confidence: float) -> str:
    """Format ML confidence score with emoji"""
    if confidence >= 0.8:
        return f"🎯 High ({confidence:.1%})"
    elif confidence >= 0.6:
        return f"✅ Medium ({confidence:.1%})"
    else:
        return f"⚠️ Low ({confidence:.1%})"

# ==================== ERROR HANDLING HELPERS ====================

def handle_error(error_type: str, details: str = "", show_streamlit: bool = True) -> str:
    """Handle and display errors consistently"""
    error_message = ERROR_MESSAGES.get(error_type, f"❌ Unknown error: {error_type}")
    
    if details:
        full_message = f"{error_message}\nDetails: {details}"
    else:
        full_message = error_message
    
    if show_streamlit:
        st.error(full_message)
    
    # Log to console
    print(f"[ERROR] {error_type}: {details}")
    
    return full_message

def show_success(success_type: str, details: str = "", show_streamlit: bool = True) -> str:
    """Show success messages consistently"""
    success_message = SUCCESS_MESSAGES.get(success_type, f"✅ Success: {success_type}")
    
    if details:
        full_message = f"{success_message}\n{details}"
    else:
        full_message = success_message
    
    if show_streamlit:
        st.success(full_message)
    
    # Log to console  
    print(f"[SUCCESS] {success_type}: {details}")
    
    return full_message

# ==================== DATA TRANSFORMATION HELPERS ====================

def safe_float(value: Any, default: float = 0.0) -> float:
    """Safely convert value to float with fallback"""
    try:
        return float(value)
    except (ValueError, TypeError):
        return default

def safe_int(value: Any, default: int = 0) -> int:
    """Safely convert value to int with fallback"""
    try:
        return int(value)
    except (ValueError, TypeError):
        return default

def clean_dict(data: Dict[str, Any], remove_none: bool = True) -> Dict[str, Any]:
    """Clean dictionary by removing None values and empty strings"""
    cleaned = {}
    for key, value in data.items():
        if remove_none and value is None:
            continue
        if isinstance(value, str) and value.strip() == "":
            continue
        cleaned[key] = value
    return cleaned

# ==================== URL AND API HELPERS ====================

def create_google_maps_url(lat: float, lng: float) -> str:
    """Create Google Maps URL for coordinates"""
    return f"https://www.google.com/maps?q={lat},{lng}"

def create_openstreetmap_url(lat: float, lng: float, zoom: int = 15) -> str:
    """Create OpenStreetMap URL for coordinates"""
    return f"https://www.openstreetmap.org/?mlat={lat}&mlon={lng}&zoom={zoom}"

# ==================== DEBUG HELPERS ====================

def debug_print(message: str, data: Any = None, enabled: bool = False):
    """Debug print helper that can be toggled"""
    if enabled:
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[DEBUG {timestamp}] {message}")
        if data is not None:
            print(f"[DEBUG {timestamp}] Data: {data}")

def get_session_state_summary() -> Dict[str, Any]:
    """Get summary of current session state for debugging"""
    summary = {}
    
    # Location data
    summary['location'] = {
        'selected_location': bool(st.session_state.get('selected_location')),
        'temp_coordinates': bool(st.session_state.get('temp_coordinates')),
        'selected_location_pin': bool(st.session_state.get('selected_location_pin')),
        'gps_location_data': bool(st.session_state.get('gps_location_data'))
    }
    
    # Flags
    summary['flags'] = {
        'gps_permission_requested': st.session_state.get('gps_permission_requested', False),
        'gps_auto_refresh_completed': st.session_state.get('gps_auto_refresh_completed', False)
    }
    
    # History
    summary['history'] = {
        'interaction_count': len(st.session_state.get('interaction_history', [])),
        'current_interaction_id': st.session_state.get('current_interaction_id')
    }
    
    return summary 