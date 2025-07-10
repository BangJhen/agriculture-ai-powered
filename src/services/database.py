"""
Database Services for Agricultural Decision Support System
Contains MongoDB manager and database operations.

## MongoDB Document Structure (Clean Format)

### Main Document Fields:
- `interaction_id`: Unique 8-character identifier
- `user_session`: User session ID for data isolation
- `timestamp`: Analysis creation timestamp
- `sensor_data`: Complete sensor parameters and location data
- `ml_result`: Machine Learning analysis results
- `ai_result`: Clean AI/LLM analysis results (see structure below)
- `location_context`: Essential location context data
- `title`: Human-readable interaction title
- `suitability_score`: Overall suitability score (0.0-1.0)
- `confidence_level`: Analysis confidence (low/medium/high)
- `analysis_status`: Processing status (completed/pending/failed)
- `created_at`: Document creation timestamp
- `updated_at`: Last modification timestamp

### AI Result Structure (Clean Format):
```json
{
  "llm_analysis": "LLM-generated analysis text (max 1000 chars)",
  "recommendations": {
    "immediate_actions": ["action1", "action2", "action3"],  // Max 3 items
    "key_insights": ["insight1", "insight2"],              // Max 2 items  
    "fertilizer": "fertilizer recommendations if available"
  },
  "suitability_score": 0.85,
  "confidence_level": "high",
  "analysis_timestamp": "2024-01-01T12:00:00",
  "analysis_type": "comprehensive" | "basic" | "legacy"
}
```

### Removed Fields (Not Stored in Clean Format):
- `risk_assessment`: Too complex, not essential for storage
- `alternative_crops`: Computed dynamically, not stored
- `optimization_plan`: Heavy data, not essential
- `knowledge_base_insights`: Not essential for storage
- `evaluation_result`: Full evaluation object, too heavy

### Location Context Structure:
```json
{
  "region": "region_name",
  "climate_suitability": "high" | "medium" | "low", 
  "main_crops": ["crop1", "crop2", "crop3"]  // Max 3 items
}
```

### Benefits of Clean Format:
- 📦 Reduced document size by ~70%
- 🚀 Faster database operations
- 💾 Essential data only, no redundancy
- 🔄 Better backward compatibility
- 📊 Easier data analysis and reporting
"""

import streamlit as st
from datetime import datetime
from typing import Dict, List, Optional, Any
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError

# Import config and utilities
from ..utils.config import MONGODB_CONFIG, ERROR_MESSAGES, SUCCESS_MESSAGES
from ..utils.helpers import handle_error, show_success, clean_dict, sanitize_string

# ==================== MONGODB MANAGER CLASS ====================

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
            # Use configuration from config.py
            connection_string = MONGODB_CONFIG['connection_string']
            database_name = MONGODB_CONFIG['database']
            collection_name = MONGODB_CONFIG['collection']
            
            # Check if using custom or default configuration
            is_custom = any([
                connection_string != MONGODB_CONFIG['connection_string'],
                database_name != MONGODB_CONFIG['database'],
                collection_name != MONGODB_CONFIG['collection']
            ])
            
            if is_custom:
                print("🔗 Using custom MongoDB from environment variables")
            else:
                print("🔗 Using provided MongoDB Atlas connection")
            
            # Create MongoDB client with timeout
            self.client = MongoClient(connection_string, serverSelectionTimeoutMS=5000)
            
            # Test connection
            self.client.admin.command('ping')
            
            # Get database and collection
            self.db = self.client[database_name]
            self.collection = self.db[collection_name]
            
            # Create indexes for better performance
            try:
                self.collection.create_index("interaction_id", unique=True)
                self.collection.create_index("timestamp")
                self.collection.create_index("user_session")
            except Exception as index_error:
                print(f"⚠️ Index creation warning: {index_error}")
            
            self.connected = True
            print(f"✅ MongoDB Atlas connection established successfully to {database_name}")
            return True
            
        except ConnectionFailure:
            self.connected = False
            handle_error('mongodb_connection', 'Connection failed - check network or credentials', show_streamlit=False)
            return False
        except ServerSelectionTimeoutError:
            self.connected = False
            handle_error('mongodb_connection', 'Connection timeout - check network connectivity', show_streamlit=False)
            return False
        except Exception as e:
            self.connected = False
            handle_error('mongodb_connection', f"MongoDB error: {str(e)}", show_streamlit=False)
            return False
    
    def is_connected(self) -> bool:
        """Check if connected to MongoDB"""
        return self.connected
    
    def reconnect(self) -> bool:
        """Attempt to reconnect to MongoDB"""
        self.connected = False
        return self._connect()
    
    def save_interaction(self, interaction_data: Dict) -> bool:
        """Save interaction to MongoDB with detailed debugging and clean document structure"""
        if not self.connected:
            print("⚠️ MongoDB not connected - skipping database save")
            print("🔧 Interaction will be saved to session history only")
            return False
            
        try:
            # Clean and validate interaction data
            cleaned_data = clean_dict(interaction_data)
            
            # Debug: Print AI analysis data being saved
            ai_result = cleaned_data.get("ai_result", {})
            if ai_result:
                print(f"🤖 AI Analysis being saved:")
                print(f"  📝 LLM Analysis: {len(ai_result.get('llm_analysis', ''))} chars")
                print(f"  💡 Recommendations: {list(ai_result.get('recommendations', {}).keys())}")
                print(f"  📊 Suitability Score: {ai_result.get('suitability_score', 0):.2f}")
                print(f"  🎯 Analysis Type: {ai_result.get('analysis_type', 'unknown')}")
            
            # Debug: Print location and coordinates data before saving
            sensor_data = cleaned_data.get("sensor_data", {})
            coordinates = sensor_data.get("coordinates")
            location = sensor_data.get("location")
            location_source = sensor_data.get("location_source", "N/A")
            
            print(f"🔍 Saving interaction to MongoDB with:")
            print(f"  📍 Location: {location}")
            print(f"  🌍 Coordinates: {coordinates}")
            print(f"  📊 Location Source: {location_source}")
            
            # Get user session with fallback
            user_session = st.session_state.get('session_id', MONGODB_CONFIG['user_session'])
            
            # ✅ IMPROVED: Clean document structure for MongoDB
            document = {
                "interaction_id": cleaned_data["id"],
                "user_session": user_session,
                "timestamp": cleaned_data["timestamp"],  # MongoDB handles Python datetime
                "sensor_data": cleaned_data["sensor_data"],
                "ml_result": cleaned_data.get("ml_result"),
                "ai_result": cleaned_data.get("ai_result"),  # ✅ Clean AI results
                "location_context": cleaned_data.get("location_context"),  # ✅ Essential location data
                "title": cleaned_data.get("title"),
                "suitability_score": cleaned_data.get("suitability_score", 0.0),
                "confidence_level": cleaned_data.get("confidence_level", "medium"),
                "analysis_status": cleaned_data.get("analysis_status", "completed"),
                "created_at": datetime.now(),
                "updated_at": datetime.now()
            }
            
            # ✅ REMOVED: Don't save heavy/unnecessary fields like evaluation_result, location_advice, risk_level
            
            # Upsert (update if exists, insert if not)
            result = self.collection.replace_one(
                {"interaction_id": cleaned_data["id"]},
                document,
                upsert=True
            )
            
            if result.acknowledged:
                print(f"✅ Interaction successfully saved to MongoDB: {cleaned_data['id']}")
                if coordinates:
                    print(f"  🌍 GPS coordinates confirmed saved: {coordinates}")
                
                # Debug: Confirm what was saved
                crop_name = sensor_data.get('selected_crop_display', 'Unknown')
                location_name = location.split(',')[0] if location else 'Unknown'
                analysis_type = ai_result.get('analysis_type', 'unknown')
                print(f"  📊 Saved: {crop_name} {analysis_type} analysis for {location_name}")
                return True
            else:
                print("❌ Failed to save interaction to MongoDB - result not acknowledged")
                return False
            
        except Exception as e:
            handle_error('database_save_failed', f"Could not save to database: {str(e)}", show_streamlit=False)
            return False
    
    def load_interactions(self, limit: int = 50) -> List[Dict]:
        """Load recent interactions from MongoDB with debugging and backward compatibility"""
        if not self.connected:
            print("⚠️ MongoDB not connected - cannot load from database")
            return []
            
        try:
            user_session = st.session_state.get('session_id', MONGODB_CONFIG['user_session'])
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
                
                # ✅ IMPROVED: Handle both old and new document structures
                ai_result = doc.get("ai_result", {})
                
                # Backward compatibility: Convert old ai_result format to new format
                if ai_result and not ai_result.get('analysis_type'):
                    # Old format detected, convert to new format
                    old_llm_analysis = ai_result.get('llm_analysis', '')
                    old_recommendations = ai_result.get('recommendations', {})
                    
                    # Convert to new clean format
                    ai_result = {
                        'llm_analysis': old_llm_analysis[:1000] if old_llm_analysis else '',
                        'recommendations': {
                            'immediate_actions': old_recommendations.get('immediate_actions', [])[:3] if old_recommendations else []
                        },
                        'suitability_score': ai_result.get('suitability_score', 0.0),
                        'confidence_level': ai_result.get('confidence_level', 'medium'),
                        'analysis_timestamp': doc.get("timestamp", datetime.now()).isoformat(),
                        'analysis_type': 'legacy'  # Mark as converted from old format
                    }
                    print(f"🔄 Converted legacy document format: {doc['interaction_id']}")
                
                interaction = {
                    "id": doc["interaction_id"],
                    "timestamp": doc["timestamp"],
                    "sensor_data": doc["sensor_data"],
                    "ml_result": doc.get("ml_result"),
                    "ai_result": ai_result,  # ✅ Clean AI results (converted if needed)
                    "location_context": doc.get("location_context"),  # ✅ New field
                    "title": title,
                    "suitability_score": doc.get("suitability_score", 0.0),
                    "confidence_level": doc.get("confidence_level", "medium"),
                    "analysis_status": doc.get("analysis_status", "completed")
                }
                interactions.append(interaction)
            
            print(f"📊 Found {len(interactions)} interactions in MongoDB")
            if len(interactions) > 0:
                latest = interactions[0]['timestamp']
                latest_analysis_type = interactions[0].get('ai_result', {}).get('analysis_type', 'unknown')
                print(f"📅 Latest interaction: {latest} (Type: {latest_analysis_type})")
            
            return interactions
            
        except Exception as e:
            handle_error('database_load_failed', f"Could not load from database: {str(e)}", show_streamlit=False)
            return []
    
    def get_interaction_by_id(self, interaction_id: str) -> Optional[Dict]:
        """Get specific interaction by ID"""
        if not self.connected:
            return None
            
        try:
            user_session = st.session_state.get('session_id', MONGODB_CONFIG['user_session'])
            doc = self.collection.find_one({
                "interaction_id": interaction_id,
                "user_session": user_session
            })
            
            if doc:
                # Create title if it doesn't exist (backward compatibility)
                title = doc.get("title")
                if not title:
                    sensor_data = doc.get("sensor_data", {})
                    crop = sensor_data.get("selected_crop", "Unknown")
                    location = sensor_data.get("location", "Unknown")
                    title = f"{crop.title()} - {location}"
                
                return {
                    "id": doc["interaction_id"],
                    "timestamp": doc["timestamp"],
                    "sensor_data": doc["sensor_data"],
                    "ml_result": doc.get("ml_result"),
                    "ai_result": doc.get("ai_result"),
                    "title": title
                }
            
            return None
            
        except Exception as e:
            handle_error('database_get_failed', f"Could not get interaction: {str(e)}", show_streamlit=False)
            return None
    
    def delete_interaction(self, interaction_id: str) -> bool:
        """Delete specific interaction from MongoDB"""
        if not self.connected:
            return False
            
        try:
            user_session = st.session_state.get('session_id', MONGODB_CONFIG['user_session'])
            result = self.collection.delete_one({
                "interaction_id": interaction_id,
                "user_session": user_session
            })
            
            success = result.deleted_count > 0
            if success:
                print(f"✅ Deleted interaction: {interaction_id}")
            else:
                print(f"⚠️ Interaction not found: {interaction_id}")
            
            return success
            
        except Exception as e:
            handle_error('database_delete_failed', f"Could not delete from database: {str(e)}", show_streamlit=False)
            return False
    
    def clear_all_interactions(self) -> bool:
        """Clear all interactions for current user"""
        if not self.connected:
            return False
            
        try:
            user_session = st.session_state.get('session_id', MONGODB_CONFIG['user_session'])
            result = self.collection.delete_many({"user_session": user_session})
            
            print(f"✅ Cleared {result.deleted_count} interactions for user: {user_session}")
            return True
            
        except Exception as e:
            handle_error('database_clear_failed', f"Could not clear database: {str(e)}", show_streamlit=False)
            return False
    
    def update_interaction_results(self, interaction_id: str, ml_result=None, ai_result=None) -> bool:
        """Update interaction with ML/AI results"""
        if not self.connected:
            return False
            
        try:
            user_session = st.session_state.get('session_id', MONGODB_CONFIG['user_session'])
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
            
            success = result.modified_count > 0
            if success:
                print(f"✅ Updated interaction results: {interaction_id}")
            
            return success
            
        except Exception as e:
            handle_error('database_update_failed', f"Error updating MongoDB: {str(e)}", show_streamlit=False)
            return False
    
    def get_user_statistics(self) -> Dict[str, Any]:
        """Get user interaction statistics"""
        if not self.connected:
            return {}
            
        try:
            user_session = st.session_state.get('session_id', MONGODB_CONFIG['user_session'])
            
            # Count total interactions
            total_count = self.collection.count_documents({"user_session": user_session})
            
            # Get date range
            if total_count > 0:
                oldest = self.collection.find({"user_session": user_session}).sort("timestamp", 1).limit(1)
                newest = self.collection.find({"user_session": user_session}).sort("timestamp", -1).limit(1)
                
                oldest_doc = list(oldest)[0] if oldest else None
                newest_doc = list(newest)[0] if newest else None
                
                return {
                    'total_interactions': total_count,
                    'oldest_date': oldest_doc['timestamp'] if oldest_doc else None,
                    'newest_date': newest_doc['timestamp'] if newest_doc else None
                }
            else:
                return {'total_interactions': 0}
                
        except Exception as e:
            print(f"⚠️ Error getting statistics: {str(e)}")
            return {}

# ==================== DATABASE MANAGER INSTANCE ====================

# Global database manager instance
_mongodb_manager = None

@st.cache_resource
def get_mongodb_manager() -> MongoDBManager:
    """Get MongoDB manager instance (cached)"""
    global _mongodb_manager
    if _mongodb_manager is None:
        _mongodb_manager = MongoDBManager()
    return _mongodb_manager

def reset_mongodb_manager():
    """Reset MongoDB manager (for testing/debugging)"""
    global _mongodb_manager
    if _mongodb_manager:
        try:
            _mongodb_manager.client.close()
        except:
            pass
    _mongodb_manager = None
    # Clear streamlit cache
    st.cache_resource.clear()

# ==================== HELPER FUNCTIONS ====================

def save_interaction_to_db(interaction_data: Dict) -> bool:
    """Convenient function to save interaction"""
    db_manager = get_mongodb_manager()
    return db_manager.save_interaction(interaction_data)

def load_interactions_from_db(limit: int = 50) -> List[Dict]:
    """Convenient function to load interactions"""
    db_manager = get_mongodb_manager()
    return db_manager.load_interactions(limit)

def get_interaction_from_db(interaction_id: str) -> Optional[Dict]:
    """Convenient function to get interaction by ID"""
    db_manager = get_mongodb_manager()
    return db_manager.get_interaction_by_id(interaction_id)

def delete_interaction_from_db(interaction_id: str) -> bool:
    """Convenient function to delete interaction"""
    db_manager = get_mongodb_manager()
    return db_manager.delete_interaction(interaction_id)

def clear_all_interactions_from_db() -> bool:
    """Convenient function to clear all interactions"""
    db_manager = get_mongodb_manager()
    return db_manager.clear_all_interactions()

def update_interaction_results_in_db(interaction_id: str, ml_result=None, ai_result=None) -> bool:
    """Convenient function to update interaction results"""
    db_manager = get_mongodb_manager()
    return db_manager.update_interaction_results(interaction_id, ml_result, ai_result)

def check_database_connection() -> bool:
    """Check database connection status"""
    db_manager = get_mongodb_manager()
    return db_manager.is_connected()

def get_database_statistics() -> Dict[str, Any]:
    """Get database statistics"""
    db_manager = get_mongodb_manager()
    return db_manager.get_user_statistics()

# ==================== SESSION INTEGRATION ====================

def init_database_session():
    """Initialize database-related session state"""
    
    # Set default session ID if not exists
    if 'session_id' not in st.session_state:
        st.session_state.session_id = MONGODB_CONFIG['user_session']
    
    # Load interaction history from database
    if 'interaction_history' not in st.session_state:
        st.session_state.interaction_history = load_interactions_from_db()

def sync_session_with_database():
    """Sync session state with database"""
    
    try:
        # Load latest interactions from database
        db_interactions = load_interactions_from_db()
        
        # Update session state
        st.session_state.interaction_history = db_interactions
        
        print(f"🔄 Synced {len(db_interactions)} interactions from database")
        return True
        
    except Exception as e:
        print(f"⚠️ Error syncing with database: {str(e)}")
        return False 