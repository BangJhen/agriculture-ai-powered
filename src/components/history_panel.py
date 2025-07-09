"""
History Panel Component for Agricultural Decision Support System
Manages interaction history display and new interaction forms in the sidebar.
Extracted from agricultural_chatbot.py to maintain original functionality.
"""

import streamlit as st
from datetime import datetime
from typing import Dict, List, Any, Optional

def display_interaction_history():
    """Display interaction history in sidebar - matches original implementation"""
    with st.sidebar:
        
        if not st.session_state.interaction_history:
            st.info("Belum ada interaksi tersimpan")
            st.markdown("*Gunakan **➕ New** untuk membuat preset atau input manual*")
            return
        
        # Show total count with summary
        total = len(st.session_state.interaction_history)
        if total == 1:
            st.caption(f"Total: {total} interaction")
        else:
            st.caption(f"Total: {total} interactions")
        
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
            if interaction.get('ml_result') and interaction['ml_result'].get('confidence'):
                confidence = interaction['ml_result']['confidence'] * 100
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
    """Display form for creating new interaction in sidebar - matches original implementation"""
    with st.sidebar:
        st.markdown("### ➕ New Interaction")
        
        with st.form("sidebar_new_interaction", clear_on_submit=False):
            st.markdown("**Quick Setup**")
            
            # Quick presets
            preset = st.selectbox("📋 Preset", [
                "Custom", "Rice - Tropis", "Maize - Musim Kering", 
                "Cotton - Komersial", "Banana - Lembab"
            ])
            
            # Show preset info
            if preset != "Custom":
                if preset == "Rice - Tropis":
                    st.info("🌾 Padi untuk iklim tropis dengan kelembaban tinggi")
                elif preset == "Maize - Musim Kering":
                    st.info("🌽 Jagung untuk musim kemarau dengan curah hujan sedang")
                elif preset == "Cotton - Komersial":
                    st.info("🏭 Kapas komersial dengan nutrisi tinggi")
                elif preset == "Banana - Lembab":
                    st.info("🍌 Pisang untuk daerah lembab")
            
            # Submit button (always visible - fixed unconditional)
            submitted = st.form_submit_button("📝 Use Main Form", type="primary" if preset != "Custom" else "secondary")
            
            # Handle submission
            if submitted:
                if preset != "Custom":
                    # Define preset data (don't save as interaction yet)
                    preset_data = {}
                    if preset == "Rice - Tropis":
                        preset_data = {
                            'N': 80, 'P': 40, 'K': 40, 'temperature': 26,
                            'humidity': 80, 'ph': 6.0, 'rainfall': 280,  # Fixed: within max 298.6
                            'field_size': 2.0, 'selected_crop': 'rice', 'location': 'Jawa Barat'
                        }
                    elif preset == "Maize - Musim Kering":
                        preset_data = {
                            'N': 90, 'P': 50, 'K': 30, 'temperature': 28,
                            'humidity': 55, 'ph': 6.8, 'rainfall': 120,  # Fixed: within max 298.6 
                            'field_size': 3.0, 'selected_crop': 'maize', 'location': 'Jawa Tengah'
                        }
                    elif preset == "Cotton - Komersial":
                        preset_data = {
                            'N': 120, 'P': 70, 'K': 150, 'temperature': 30,
                            'humidity': 45, 'ph': 7.2, 'rainfall': 80,   # Fixed: within max 298.6
                            'field_size': 5.0, 'selected_crop': 'cotton', 'location': 'Sulawesi'
                        }
                    elif preset == "Pisang - Lembab":
                        preset_data = {
                            'N': 100, 'P': 60, 'K': 180, 'temperature': 27,
                            'humidity': 85, 'ph': 6.0, 'rainfall': 250,  # Fixed: within max 298.6
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
                    # Import here to avoid circular imports
                    from src.services.database import get_mongodb_manager
                    
                    # Clear session state
                    st.session_state.interaction_history = []
                    st.session_state.current_interaction_id = None
                    st.session_state.preset_data = None
                    st.session_state.preset_name = None
                    
                    # Clear MongoDB
                    mongo_manager = get_mongodb_manager()
                    if mongo_manager.is_connected():
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
        
        # If it's from GPS, also restore to GPS session state
        if location_source == 'gps':
            # Extract GPS-specific data if available
            gps_accuracy = sensor_data.get('gps_accuracy', 10)  # Default accuracy
            st.session_state.gps_location_data = {
                'lat': coordinates['lat'],
                'lng': coordinates['lng'],
                'address': location,
                'accuracy': gps_accuracy,
                'timestamp': datetime.now().isoformat()  # Current timestamp for restored data
            }
            st.session_state.gps_permission_requested = True  # Mark as GPS already used
            print(f"✅ GPS location data restored with accuracy: {gps_accuracy}m")
        
        print(f"✅ Location restored successfully from {location_source}")
    else:
        print(f"⚠️ Incomplete location data - coordinates: {bool(coordinates)}, location: {bool(location)}")


def load_interaction(interaction_id):
    """Load interaction from history"""
    for interaction in st.session_state.interaction_history:
        if interaction['id'] == interaction_id:
            return interaction
    return None


def get_current_interaction_data():
    """Get current interaction data if any"""
    if st.session_state.current_interaction_id:
        return load_interaction(st.session_state.current_interaction_id)
    return None


def update_interaction_results(interaction_id, ml_result=None, ai_result=None):
    """Update interaction with ML and AI results in both session state and MongoDB"""
    # Import here to avoid circular imports
    from src.services.database import get_mongodb_manager
    
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
    if mongo_manager.is_connected():
        mongo_manager.update_interaction_results(interaction_id, ml_result, ai_result) 