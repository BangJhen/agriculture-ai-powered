"""
Mapping Services for Agricultural Decision Support System
Contains Folium map functionality and map-related operations.
"""

import streamlit as st
from typing import Optional, Dict, Any

# Import config and utilities
from ..utils.config import MAP_CONFIG, ERROR_MESSAGES
from ..utils.helpers import handle_error, validate_coordinates
from .location import reverse_geocode_location

# Import map libraries if available
try:
    import folium
    FOLIUM_AVAILABLE = True
except ImportError:
    FOLIUM_AVAILABLE = False

try:
    from streamlit_folium import st_folium
    STREAMLIT_FOLIUM_AVAILABLE = True
except ImportError:
    STREAMLIT_FOLIUM_AVAILABLE = False

# ==================== MAP CREATION FUNCTIONS ====================

def create_indonesia_agricultural_map():
    """Create base map centered on Indonesia for agricultural purposes"""
    
    if not FOLIUM_AVAILABLE:
        handle_error('folium_not_available', 'Folium library not available for mapping')
        return None
    
    try:
        # Create map centered on Indonesia
        indonesia_map = folium.Map(
            location=MAP_CONFIG['default_center'],  # [-2.5, 118.0]
            zoom_start=MAP_CONFIG['default_zoom'],  # 5
            tiles='OpenStreetMap'
        )
        
        # Add Indonesia bounds marker for reference
        folium.Marker(
            MAP_CONFIG['default_center'],
            popup="🌾 Indonesia - Agricultural Region",
            tooltip="Klik di mana saja untuk menandai lokasi lahan",
            icon=folium.Icon(color='green', icon='leaf', prefix='fa')
        ).add_to(indonesia_map)
        
        # Add attribution
        folium.plugins.FloatImage(
            image='data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg==',
            bottom=5,
            left=85,
            width='15%',
            height='5%'
        ).add_to(indonesia_map)
        
        return indonesia_map
        
    except Exception as e:
        handle_error('map_creation_failed', f"Failed to create map: {str(e)}")
        return None

def add_user_marker_to_map(base_map, lat: float, lng: float, address: str):
    """Add user location marker to the map"""
    
    if not base_map or not FOLIUM_AVAILABLE:
        return base_map
    
    try:
        # Validate coordinates
        if not validate_coordinates(lat, lng):
            print(f"⚠️ Invalid coordinates: {lat}, {lng}")
            return base_map
        
        # Create popup HTML with address and coordinates
        popup_html = f"""
        <div style="font-family: Arial, sans-serif; max-width: 200px;">
            <h4 style="margin: 0 0 8px 0; color: #d32f2f;">📍 Lokasi Terpilih</h4>
            <p style="margin: 4px 0; font-size: 13px;">
                <strong>📍 Alamat:</strong><br/>
                {address}
            </p>
            <p style="margin: 4px 0; font-size: 12px;">
                <strong>🎯 Koordinat:</strong><br/>
                Lat: {lat:.6f}°<br/>
                Lng: {lng:.6f}°
            </p>
            <p style="margin: 8px 0 0 0; font-size: 11px; color: #666;">
                <a href="https://www.google.com/maps?q={lat},{lng}" target="_blank" 
                   style="color: #1976d2; text-decoration: none;">
                    🗺️ Buka di Google Maps
                </a>
            </p>
        </div>
        """
        
        # Add the red pin marker with popup
        user_marker = folium.Marker(
            [lat, lng],
            popup=folium.Popup(popup_html, max_width=250),
            tooltip=f"📍 {address.split(',')[0]}: {lat:.4f}°, {lng:.4f}°",
            icon=folium.Icon(color=MAP_CONFIG['pin_color'], icon='map-pin', prefix='fa')
        )
        
        # Add circle around marker for emphasis
        folium.Circle(
            [lat, lng],
            radius=MAP_CONFIG['circle_radius'],  # 1km radius
            color=MAP_CONFIG['pin_color'],
            fillColor=MAP_CONFIG['pin_color'],
            fillOpacity=0.1,
            weight=2,
            tooltip=f"Area radius 1km dari {address.split(',')[0]}"
        ).add_to(base_map)
        
        user_marker.add_to(base_map)
        
        # Center map on user location
        base_map.location = [lat, lng]
        base_map.zoom_start = 12  # Zoom in on user location
        
        return base_map
        
    except Exception as e:
        print(f"Error adding marker to map: {e}")
        return base_map

# ==================== MAP INTERACTION FUNCTIONS ====================

def display_interactive_map(existing_pins: Optional[Dict[str, Any]] = None):
    """Display interactive map with click handling"""
    
    if not FOLIUM_AVAILABLE or not STREAMLIT_FOLIUM_AVAILABLE:
        st.error("⚠️ **Interactive Map tidak tersedia** - Map libraries tidak terinstall")
        st.info("💡 **Solusi:** Gunakan tab 'Search Location' untuk mencari lokasi dengan nama daerah")
        return None
    
    try:
        # Create base map
        m = create_indonesia_agricultural_map()
        
        if m is None:
            st.error("❌ Tidak dapat membuat peta")
            return None
        
        # Add existing pins if any
        if existing_pins:
            m = add_user_marker_to_map(
                m,
                existing_pins['lat'],
                existing_pins['lng'],
                existing_pins['address']
            )
        
        # Display map with error handling
        map_key = f"agricultural_map_{st.session_state.get('map_refresh_counter', 0)}"
        
        map_data = st_folium(
            m,
            width=MAP_CONFIG['map_width'],
            height=MAP_CONFIG['map_height'],
            returned_objects=["last_object_clicked", "last_clicked"],
            key=map_key,
            feature_group_to_add=None,  # Allow clicking anywhere
            use_container_width=True
        )
        
        return map_data
        
    except Exception as e:
        handle_error('map_display_failed', f"Error displaying map: {str(e)}")
        return None

def handle_map_click(map_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Handle map click events and return location data"""
    
    if not map_data:
        return None
    
    # Handle map clicks (check both last_clicked and last_object_clicked)
    clicked_data = None
    if map_data.get('last_clicked'):
        clicked_data = map_data['last_clicked']
    elif map_data.get('last_object_clicked'):
        clicked_data = map_data['last_object_clicked']
    
    if not clicked_data or not clicked_data.get('lat') or not clicked_data.get('lng'):
        return None
    
    lat = clicked_data['lat']
    lng = clicked_data['lng']
    
    # Validate coordinates
    if not validate_coordinates(lat, lng):
        handle_error('invalid_coordinates', f"Coordinates outside Indonesia: {lat}, {lng}")
        return None
    
    # Check if this is a different location from current pin
    is_new_location = True
    if st.session_state.get('selected_location_pin'):
        current_pin = st.session_state.selected_location_pin
        if abs(lat - current_pin['lat']) < 0.00001 and abs(lng - current_pin['lng']) < 0.00001:
            is_new_location = False
    
    if not is_new_location:
        return None  # Same location, no action needed
    
    # Get address for the new location
    with st.spinner("🔍 Menganalisis lokasi..."):
        address = reverse_geocode_location(lat, lng)
    
    # Create location data
    location_data = {
        'lat': lat,
        'lng': lng,
        'address': address,
        'timestamp': 1,  # Single pin mode
        'source': 'map_click'
    }
    
    return location_data

def update_map_pin_location(lat: float, lng: float, address: str) -> bool:
    """Update pin location in session state"""
    
    try:
        # Update pin location
        st.session_state.selected_location_pin = {
            'lat': lat,
            'lng': lng,
            'address': address,
            'timestamp': 1  # Always 1 since only 1 pin allowed
        }
        
        # Update session state for form submission
        st.session_state.selected_location = {
            'coordinates': {'lat': lat, 'lng': lng},
            'address': address,
            'source': 'map_click_with_red_pin',
            'pin_mode': 'single'  # Indicator for single pin mode
        }
        
        # Also store in temp_coordinates for form access
        st.session_state.temp_coordinates = {'lat': lat, 'lng': lng}
        
        # Increment refresh counter to force map update
        st.session_state.map_refresh_counter = st.session_state.get('map_refresh_counter', 0) + 1
        
        return True
        
    except Exception as e:
        handle_error('pin_update_failed', f"Failed to update pin: {str(e)}")
        return False

def clear_map_pin() -> bool:
    """Clear map pin from session state"""
    
    try:
        # Clear pin-related session state
        st.session_state.selected_location_pin = None
        
        # Clear related location data if it came from map
        if (st.session_state.get('selected_location', {}).get('source') == 'map_click_with_red_pin'):
            st.session_state.selected_location = None
            st.session_state.temp_coordinates = None
        
        # Increment refresh counter
        st.session_state.map_refresh_counter = st.session_state.get('map_refresh_counter', 0) + 1
        
        return True
        
    except Exception as e:
        handle_error('pin_clear_failed', f"Failed to clear pin: {str(e)}")
        return False

# ==================== MAP SYSTEM STATUS ====================

def display_map_system_status():
    """Display map system status for debugging"""
    
    status = {
        'folium': FOLIUM_AVAILABLE,
        'streamlit_folium': STREAMLIT_FOLIUM_AVAILABLE
    }
    
    for library, available in status.items():
        if available:
            print(f"✅ {library.replace('_', '-').title()}")
        else:
            print(f"❌ {library.replace('_', '-').title()}")
    
    return status

def check_map_dependencies() -> Dict[str, bool]:
    """Check map dependencies and return status"""
    
    dependencies = {
        'folium': FOLIUM_AVAILABLE,
        'streamlit_folium': STREAMLIT_FOLIUM_AVAILABLE
    }
    
    all_available = all(dependencies.values())
    
    if not all_available:
        missing = [lib for lib, available in dependencies.items() if not available]
        handle_error(
            'map_dependencies_missing',
            f"Missing map libraries: {', '.join(missing)}",
            show_streamlit=False
        )
    
    return dependencies

# ==================== MAP UTILITIES ====================

def get_map_bounds_indonesia() -> Dict[str, float]:
    """Get Indonesia map bounds for validation"""
    
    return {
        'lat_min': -11.0,
        'lat_max': 6.0,
        'lng_min': 95.0,
        'lng_max': 141.0
    }

def calculate_map_zoom_level(lat: float, lng: float, accuracy: Optional[float] = None) -> int:
    """Calculate appropriate zoom level based on location and accuracy"""
    
    # Default zoom levels
    zoom_levels = {
        'country': 5,
        'province': 7,
        'city': 10,
        'district': 12,
        'street': 15,
        'building': 17
    }
    
    # If accuracy is provided, use it to determine zoom
    if accuracy:
        if accuracy < 10:  # Very accurate
            return zoom_levels['building']
        elif accuracy < 50:  # Good accuracy
            return zoom_levels['street']
        elif accuracy < 100:  # Moderate accuracy
            return zoom_levels['district']
        else:  # Low accuracy
            return zoom_levels['city']
    
    # Default zoom for manual selections
    return zoom_levels['district']

def create_map_marker_popup(address: str, lat: float, lng: float, 
                           source: str = "unknown") -> str:
    """Create standardized popup HTML for map markers"""
    
    source_info = {
        'gps': ('🛰️', 'GPS Location'),
        'map_click': ('📍', 'Map Selection'),
        'search': ('🔍', 'Search Result'),
        'unknown': ('❓', 'Unknown Source')
    }
    
    emoji, source_name = source_info.get(source, source_info['unknown'])
    
    popup_html = f"""
    <div style="font-family: Arial, sans-serif; max-width: 220px;">
        <h4 style="margin: 0 0 8px 0; color: #d32f2f;">{emoji} {source_name}</h4>
        <p style="margin: 4px 0; font-size: 13px;">
            <strong>📍 Alamat:</strong><br/>
            <span style="color: #333;">{address}</span>
        </p>
        <p style="margin: 4px 0; font-size: 12px;">
            <strong>🎯 Koordinat:</strong><br/>
            <code style="background: #f5f5f5; padding: 2px 4px; border-radius: 3px;">
                {lat:.6f}°, {lng:.6f}°
            </code>
        </p>
        <div style="margin: 8px 0 0 0; padding-top: 8px; border-top: 1px solid #eee;">
            <a href="https://www.google.com/maps?q={lat},{lng}" target="_blank" 
               style="color: #1976d2; text-decoration: none; font-size: 11px;">
                🗺️ Buka di Google Maps
            </a>
        </div>
    </div>
    """
    
    return popup_html 