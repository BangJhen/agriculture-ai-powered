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
                    box-shadow: 0 1px 6px rgba(0,0,0,0.05);
                ">
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
                
                # Non-clickable card
                st.markdown(card_html, unsafe_allow_html=True)
            
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