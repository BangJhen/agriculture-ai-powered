"""
Knowledge Base Service Module for Agricultural Decision Support System
Handles Qdrant vector database integration and semantic search functionality.
"""

import os
from typing import Dict, List, Any, Optional, Tuple
import requests
import json
from datetime import datetime

# Optional imports for knowledge base functionality
try:
    from sentence_transformers import SentenceTransformer
    from qdrant_client import QdrantClient
    from qdrant_client.http import models
    from qdrant_client.models import Distance, VectorParams, PointStruct
    KNOWLEDGE_BASE_AVAILABLE = True
except ImportError as e:
    print(f"⚠️ Knowledge base dependencies not available: {e}")
    KNOWLEDGE_BASE_AVAILABLE = False
    SentenceTransformer = None
    QdrantClient = None
    models = None

# Import configuration
from ..utils.config import LLM_CONFIG
from ..utils.helpers import handle_error

# ==================== QDRANT CONFIGURATION ====================

QDRANT_CONFIG = {
    'url': 'http://localhost:6333',
    'collection_name': 'agricultural_knowledge',
    'vector_size': 384,  # all-MiniLM-L6-v2 dimension
    # 'distance_metric': Distance.COSINE,
    'model_name': 'all-MiniLM-L6-v2'
}

# ==================== KNOWLEDGE BASE SERVICE ====================

class KnowledgeBaseService:
    """Service for managing agricultural knowledge base using Qdrant and SentenceTransformers"""
    
    def __init__(self):
        self.is_available = KNOWLEDGE_BASE_AVAILABLE
        self.client = None
        self.embedding_model = None
        self.collection_name = QDRANT_CONFIG['collection_name']
        
        if self.is_available:
            self._initialize_services()
    
    def _initialize_services(self):
        """Initialize Qdrant client and SentenceTransformer model"""
        try:
            # Initialize Qdrant client
            self.client = QdrantClient(url=QDRANT_CONFIG['url'])
            
            # Test connection
            if self._test_qdrant_connection():
                print("✅ Qdrant connection established")
            else:
                print("❌ Qdrant connection failed")
                self.is_available = False
                return
            
            # Initialize embedding model
            self.embedding_model = SentenceTransformer(QDRANT_CONFIG['model_name'])
            print(f"✅ SentenceTransformer model loaded: {QDRANT_CONFIG['model_name']}")
            
            # Ensure collection exists
            self._ensure_collection_exists()
            
        except Exception as e:
            print(f"❌ Failed to initialize knowledge base: {e}")
            self.is_available = False
    
    def _test_qdrant_connection(self) -> bool:
        """Test connection to Qdrant server"""
        try:
            # Test with a simple request
            response = requests.get(f"{QDRANT_CONFIG['url']}/", timeout=5)
            return response.status_code == 200
        except Exception as e:
            print(f"⚠️ Qdrant connection test failed: {e}")
            return False
    
    def _ensure_collection_exists(self):
        """Ensure the agricultural knowledge collection exists"""
        try:
            collections = self.client.get_collections()
            collection_names = [col.name for col in collections.collections]
            
            if self.collection_name not in collection_names:
                print(f"📋 Creating collection: {self.collection_name}")
                self.client.create_collection(
                    collection_name=self.collection_name,
                    vectors_config=VectorParams(
                        size=QDRANT_CONFIG['vector_size'],
                        distance=QDRANT_CONFIG['distance_metric']
                    )
                )
                
                # Add initial knowledge base
                self._populate_initial_knowledge()
            else:
                print(f"✅ Collection exists: {self.collection_name}")
                
        except Exception as e:
            print(f"❌ Error ensuring collection: {e}")
    
    def _populate_initial_knowledge(self):
        """Populate the knowledge base with initial agricultural knowledge"""
        
        initial_knowledge = [
            {
                "id": "rice_cultivation_indonesia",
                "content": "Padi adalah tanaman pangan utama di Indonesia. Budidaya padi memerlukan kondisi lahan yang tergenang air dengan pH tanah 6.0-7.0. Suhu optimal untuk pertumbuhan padi adalah 22-32°C dengan kelembaban tinggi 80-90%. Kebutuhan nitrogen untuk padi adalah 90-150 kg/ha, fosfor 60-90 kg/ha, dan kalium 60-120 kg/ha. Musim tanam padi di Indonesia biasanya pada awal musim hujan.",
                "category": "tanaman_pangan",
                "crop_type": "padi",
                "location": "Indonesia"
            },
            {
                "id": "corn_cultivation_tropical",
                "content": "Jagung cocok ditanam di daerah tropis dengan suhu 21-34°C. Jagung membutuhkan tanah dengan pH 5.8-8.0 dan drainase yang baik. Kebutuhan nutrisi jagung meliputi nitrogen 200-300 kg/ha, fosfor 90-120 kg/ha, dan kalium 60-120 kg/ha. Jagung dapat ditanam 2-3 kali dalam setahun dengan periode tanam 90-120 hari.",
                "category": "tanaman_pangan",
                "crop_type": "jagung",
                "location": "tropis"
            },
            {
                "id": "soybean_cultivation",
                "content": "Kedelai adalah tanaman legum yang dapat menambat nitrogen dari udara. Cocok ditanam pada pH tanah 6.0-7.0 dengan suhu optimal 20-25°C. Kedelai membutuhkan sedikit nitrogen tambahan karena kemampuan fiksasi nitrogen, tetapi memerlukan fosfor 30-60 kg/ha dan kalium 50-100 kg/ha. Waktu tanam yang baik adalah awal musim kemarau.",
                "category": "tanaman_pangan",
                "crop_type": "kedelai",
                "location": "Indonesia"
            },
            {
                "id": "banana_cultivation_humid",
                "content": "Pisang tumbuh optimal di daerah lembab dengan suhu 26-30°C dan kelembaban 75-85%. Membutuhkan tanah dengan pH 5.5-7.0 dan drainase baik. Kebutuhan nutrisi pisang tinggi: nitrogen 200-400 kg/ha, fosfor 50-100 kg/ha, dan kalium 500-800 kg/ha. Pisang dapat dipanen setelah 9-12 bulan setelah tanam.",
                "category": "buah_buahan",
                "crop_type": "pisang",
                "location": "lembab"
            },
            {
                "id": "coffee_cultivation_mountain",
                "content": "Kopi arabika tumbuh baik di dataran tinggi 800-2000 meter dengan suhu 18-24°C. Membutuhkan tanah dengan pH 6.0-7.0 dan curah hujan 1500-2000 mm/tahun. Kopi memerlukan nitrogen 150-250 kg/ha, fosfor 30-60 kg/ha, dan kalium 150-300 kg/ha. Waktu panen kopi biasanya sekali dalam setahun.",
                "category": "tanaman_perkebunan",
                "crop_type": "kopi",
                "location": "dataran_tinggi"
            },
            {
                "id": "chili_cultivation",
                "content": "Cabai membutuhkan suhu 20-30°C dan kelembaban 60-80%. Cocok ditanam pada pH tanah 6.0-7.0 dengan drainase yang baik. Kebutuhan nutrisi cabai: nitrogen 150-200 kg/ha, fosfor 75-100 kg/ha, dan kalium 150-200 kg/ha. Cabai dapat dipanen setelah 2.5-3 bulan setelah tanam.",
                "category": "sayuran",
                "crop_type": "cabai",
                "location": "tropis"
            },
            {
                "id": "potato_cultivation",
                "content": "Kentang tumbuh baik di dataran tinggi dengan suhu 15-25°C. Membutuhkan tanah dengan pH 5.0-6.5 dan drainase yang sangat baik. Kebutuhan nutrisi kentang: nitrogen 120-180 kg/ha, fosfor 60-90 kg/ha, dan kalium 150-250 kg/ha. Kentang dapat dipanen setelah 90-120 hari setelah tanam.",
                "category": "umbi_umbian",
                "crop_type": "kentang",
                "location": "dataran_tinggi"
            },
            {
                "id": "coconut_cultivation",
                "content": "Kelapa tumbuh optimal di daerah pesisir dengan suhu 27-32°C dan kelembaban tinggi. Toleran terhadap tanah berpasir dan pH 5.5-8.0. Kebutuhan nutrisi kelapa: nitrogen 100-200 kg/ha, fosfor 50-100 kg/ha, dan kalium 200-400 kg/ha. Kelapa mulai berbuah setelah 5-6 tahun setelah tanam.",
                "category": "tanaman_perkebunan",
                "crop_type": "kelapa",
                "location": "pesisir"
            },
            {
                "id": "mango_cultivation",
                "content": "Mangga tumbuh baik di daerah tropis dengan suhu 24-30°C. Membutuhkan tanah dengan pH 5.5-7.5 dan drainase yang baik. Kebutuhan nutrisi mangga: nitrogen 100-200 kg/ha, fosfor 50-100 kg/ha, dan kalium 100-200 kg/ha. Mangga mulai berbuah setelah 3-5 tahun setelah tanam.",
                "category": "buah_buahan",
                "crop_type": "mangga",
                "location": "tropis"
            },
            {
                "id": "soil_ph_management",
                "content": "Pengelolaan pH tanah sangat penting untuk pertanian. Tanah asam (pH < 5.5) dapat diperbaiki dengan pengapuran menggunakan kapur pertanian. Tanah basa (pH > 8.0) dapat diperbaiki dengan penambahan bahan organik dan sulfur. pH optimal untuk kebanyakan tanaman adalah 6.0-7.0.",
                "category": "manajemen_tanah",
                "crop_type": "umum",
                "location": "Indonesia"
            },
            {
                "id": "organic_fertilizer_benefits",
                "content": "Pupuk organik memberikan banyak manfaat untuk tanah dan tanaman. Pupuk kompos meningkatkan struktur tanah, kapasitas menahan air, dan aktivitas mikroorganisme. Pupuk kandang memberikan nutrisi lengkap dan meningkatkan kesuburan tanah jangka panjang. Kombinasi pupuk organik dan anorganik memberikan hasil terbaik.",
                "category": "pemupukan",
                "crop_type": "umum",
                "location": "Indonesia"
            },
            {
                "id": "water_management_rice",
                "content": "Pengelolaan air pada budidaya padi sangat krusial. Fase vegetatif membutuhkan genangan air 2-5 cm. Fase generatif membutuhkan genangan air 3-7 cm. Pada fase pematangan, air dikurangi hingga panen. Sistem irigasi bergilir dapat menghemat air hingga 30-40%.",
                "category": "irigasi",
                "crop_type": "padi",
                "location": "Indonesia"
            },
            {
                "id": "pest_management_integrated",
                "content": "Pengendalian hama terpadu (PHT) mengkombinasikan berbagai metode: pencegahan, monitoring, pengendalian biologis, dan pestisida sebagai opsi terakhir. Penanaman tanaman perangkap, rotasi tanaman, dan penggunaan musuh alami sangat efektif. Penggunaan pestisida harus sesuai dosis dan waktu yang tepat.",
                "category": "pengendalian_hama",
                "crop_type": "umum",
                "location": "Indonesia"
            },
            {
                "id": "climate_adaptation_farming",
                "content": "Adaptasi pertanian terhadap perubahan iklim meliputi: pemilihan varietas tahan kekeringan, sistem irigasi hemat air, diversifikasi tanaman, dan jadwal tanam yang fleksibel. Teknologi greenhouse dan mulsa plastik membantu mengendalikan kondisi mikro iklim.",
                "category": "adaptasi_iklim",
                "crop_type": "umum",
                "location": "Indonesia"
            },
            {
                "id": "harvest_timing_optimization",
                "content": "Waktu panen yang tepat menentukan kualitas dan kuantitas hasil. Padi dipanen saat 80-90% bulir menguning. Jagung dipanen saat kadar air biji 20-25%. Sayuran dipanen saat mencapai ukuran optimal dan sebelum overripe. Buah dipanen saat matang fisiologis untuk transportasi jarak jauh.",
                "category": "panen",
                "crop_type": "umum",
                "location": "Indonesia"
            }
        ]
        
        try:
            # Convert knowledge to embeddings and store
            points = []
            for idx, knowledge in enumerate(initial_knowledge):
                # Create embedding for the content
                embedding = self.embedding_model.encode(knowledge['content']).tolist()
                
                # Create point for Qdrant
                point = PointStruct(
                    id=idx,
                    vector=embedding,
                    payload=knowledge
                )
                points.append(point)
            
            # Insert points to Qdrant
            self.client.upsert(
                collection_name=self.collection_name,
                points=points
            )
            
            print(f"✅ Added {len(points)} knowledge entries to the knowledge base")
            
        except Exception as e:
            print(f"❌ Error populating knowledge base: {e}")
    
    def search_knowledge(self, query: str, top_k: int = 5, 
                        category_filter: str = None) -> List[Dict[str, Any]]:
        """Search for relevant knowledge using semantic similarity"""
        
        if not self.is_available:
            return []
        
        try:
            # Create embedding for the query
            query_embedding = self.embedding_model.encode(query).tolist()
            
            # Prepare search filter
            search_filter = None
            if category_filter:
                search_filter = models.Filter(
                    must=[
                        models.FieldCondition(
                            key="category",
                            match=models.MatchValue(value=category_filter)
                        )
                    ]
                )
            
            # Search in Qdrant
            search_results = self.client.search(
                collection_name=self.collection_name,
                query_vector=query_embedding,
                query_filter=search_filter,
                limit=top_k
            )
            
            # Format results
            results = []
            for result in search_results:
                results.append({
                    "content": result.payload.get("content", ""),
                    "category": result.payload.get("category", ""),
                    "crop_type": result.payload.get("crop_type", ""),
                    "location": result.payload.get("location", ""),
                    "similarity_score": result.score,
                    "id": result.payload.get("id", "")
                })
            
            return results
            
        except Exception as e:
            print(f"❌ Error searching knowledge base: {e}")
            return []
    
    def add_knowledge(self, content: str, category: str, crop_type: str = "umum", 
                     location: str = "Indonesia", knowledge_id: str = None) -> bool:
        """Add new knowledge to the knowledge base"""
        
        if not self.is_available:
            return False
        
        try:
            # Create embedding
            embedding = self.embedding_model.encode(content).tolist()
            
            # Generate ID if not provided
            if not knowledge_id:
                knowledge_id = f"custom_{int(datetime.now().timestamp())}"
            
            # Create knowledge entry
            knowledge = {
                "id": knowledge_id,
                "content": content,
                "category": category,
                "crop_type": crop_type,
                "location": location
            }
            
            # Get collection info to determine next ID
            collection_info = self.client.get_collection(self.collection_name)
            next_id = collection_info.points_count
            
            # Create point
            point = PointStruct(
                id=next_id,
                vector=embedding,
                payload=knowledge
            )
            
            # Insert to Qdrant
            self.client.upsert(
                collection_name=self.collection_name,
                points=[point]
            )
            
            print(f"✅ Added knowledge: {knowledge_id}")
            return True
            
        except Exception as e:
            print(f"❌ Error adding knowledge: {e}")
            return False
    
    def get_knowledge_categories(self) -> List[str]:
        """Get all available knowledge categories"""
        
        if not self.is_available:
            return []
        
        try:
            # This is a simplified version - in real implementation,
            # you might want to aggregate from all documents
            categories = [
                "tanaman_pangan",
                "buah_buahan", 
                "sayuran",
                "umbi_umbian",
                "tanaman_perkebunan",
                "manajemen_tanah",
                "pemupukan",
                "irigasi",
                "pengendalian_hama",
                "adaptasi_iklim",
                "panen"
            ]
            return categories
            
        except Exception as e:
            print(f"❌ Error getting categories: {e}")
            return []
    
    def get_status(self) -> Dict[str, Any]:
        """Get knowledge base status"""
        
        status = {
            "available": self.is_available,
            "qdrant_connected": False,
            "model_loaded": False,
            "collection_exists": False,
            "knowledge_count": 0
        }
        
        if not self.is_available:
            return status
        
        try:
            # Check Qdrant connection
            status["qdrant_connected"] = self._test_qdrant_connection()
            
            # Check model
            status["model_loaded"] = self.embedding_model is not None
            
            # Check collection and count
            if self.client:
                collections = self.client.get_collections()
                collection_names = [col.name for col in collections.collections]
                status["collection_exists"] = self.collection_name in collection_names
                
                if status["collection_exists"]:
                    collection_info = self.client.get_collection(self.collection_name)
                    status["knowledge_count"] = collection_info.points_count
            
        except Exception as e:
            print(f"❌ Error getting status: {e}")
        
        return status

# ==================== GLOBAL INSTANCE ====================

# Global instance for easy access
knowledge_base = KnowledgeBaseService() 