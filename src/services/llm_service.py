"""
LLM Service Module for Agricultural Decision Support System
Handles Ollama, OpenRouter, and LLM-based evaluation/recommendation services.
"""

import os
import requests
import json
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime

# Import configuration
from ..utils.config import LLM_CONFIG, ERROR_MESSAGES, SUCCESS_MESSAGES
from ..utils.helpers import handle_error, format_timestamp

# ==================== LLM CONNECTION CLASSES ====================

class OllamaService:
    """Service for interacting with Ollama local LLM"""
    
    def __init__(self):
        self.base_url = LLM_CONFIG['ollama']['base_url']
        self.default_model = LLM_CONFIG['ollama']['default_model']
        self.timeout = LLM_CONFIG['ollama']['timeout']
        self.is_available = False
        self.test_connection()
    
    def test_connection(self) -> bool:
        """Test connection to Ollama server"""
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            if response.status_code == 200:
                self.is_available = True
                print("✅ Ollama connection established")
                return True
        except Exception as e:
            print(f"⚠️ Ollama not available: {e}")
        
        self.is_available = False
        return False
    
    def call_model(self, model_name: str, prompt: str, system_prompt: str = None, 
                   temperature: float = 0.7, max_tokens: int = 2000) -> str:
        """Call Ollama model with given parameters"""
        
        if not self.is_available:
            return ""
        
        try:
            # Prepare the prompt
            full_prompt = prompt
            if system_prompt:
                full_prompt = f"{system_prompt}\n\n{prompt}"
            
            # Prepare request payload
            payload = {
                "model": model_name,
                "prompt": full_prompt,
                "options": {
                    "temperature": temperature,
                    "num_predict": max_tokens
                },
                "stream": False
            }
            
            # Make request
            response = requests.post(
                f"{self.base_url}/api/generate",
                json=payload,
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                result = response.json()
                return result.get('response', '')
            else:
                print(f"⚠️ Ollama API error: {response.status_code}")
                return ""
                
        except Exception as e:
            print(f"⚠️ Ollama call error: {e}")
            return ""
    
    def get_available_models(self) -> List[str]:
        """Get list of available models"""
        if not self.is_available:
            return []
        
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            if response.status_code == 200:
                data = response.json()
                return [model['name'] for model in data.get('models', [])]
        except Exception as e:
            print(f"⚠️ Error getting Ollama models: {e}")
        
        return []

class OpenRouterService:
    """Service for interacting with OpenRouter LLM API"""
    
    def __init__(self):
        self.base_url = LLM_CONFIG['openrouter']['base_url']
        self.api_key = LLM_CONFIG['openrouter']['api_key']
        self.default_model = LLM_CONFIG['openrouter']['default_model']
        self.timeout = LLM_CONFIG['openrouter']['timeout']
        self.is_available = False
        self.test_connection()
    
    def test_connection(self) -> bool:
        """Test connection to OpenRouter API"""
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            # Simple test call
            payload = {
                "model": self.default_model,
                "messages": [{"role": "user", "content": "Hello"}],
                "max_tokens": 10
            }
            
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                json=payload,
                timeout=10
            )
            
            if response.status_code == 200:
                self.is_available = True
                print("✅ OpenRouter connection established")
                return True
            elif response.status_code == 401:
                print("⚠️ OpenRouter API key invalid")
            elif response.status_code == 402:
                print("⚠️ OpenRouter insufficient credits")
            else:
                print(f"⚠️ OpenRouter API error: {response.status_code}")
                
        except Exception as e:
            print(f"⚠️ OpenRouter connection error: {e}")
        
        self.is_available = False
        return False
    
    def call_model(self, model_name: str, prompt: str, system_prompt: str = None,
                   temperature: float = 0.7, max_tokens: int = 2000) -> str:
        """Call OpenRouter model with given parameters"""
        
        if not self.is_available:
            return ""
        
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
                "HTTP-Referer": "https://agricultural-chatbot.streamlit.app",
                "X-Title": "Agricultural Decision Support System"
            }
            
            # Prepare messages
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})
            
            # Prepare payload
            payload = {
                "model": model_name,
                "messages": messages,
                "temperature": temperature,
                "max_tokens": max_tokens
            }
            
            # Make request
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                json=payload,
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                result = response.json()
                if 'choices' in result and len(result['choices']) > 0:
                    return result['choices'][0]['message']['content']
            else:
                print(f"⚠️ OpenRouter API error: {response.status_code}")
                
        except Exception as e:
            print(f"⚠️ OpenRouter call error: {e}")
        
        return ""

# ==================== LLM MANAGER CLASS ====================

class LLMManager:
    """Central LLM management class"""
    
    def __init__(self):
        self.ollama = OllamaService()
        self.openrouter = OpenRouterService()
        self.preferred_service = self._determine_preferred_service()
        
        print(f"🤖 LLM Services Status:")
        print(f"   Ollama: {'✅ Available' if self.ollama.is_available else '❌ Not Available'}")
        print(f"   OpenRouter: {'✅ Available' if self.openrouter.is_available else '❌ Not Available'}")
        print(f"   Preferred: {self.preferred_service}")
    
    def _determine_preferred_service(self) -> str:
        """Determine which LLM service to use as primary"""
        if self.openrouter.is_available:
            return "openrouter"
        elif self.ollama.is_available:
            return "ollama"
        else:
            return "none"
    
    def call_llm(self, prompt: str, system_prompt: str = None, 
                 temperature: float = 0.7, max_tokens: int = 2000,
                 prefer_service: str = None) -> str:
        """Call LLM with fallback mechanism"""
        
        # Determine which service to use
        service_to_use = prefer_service or self.preferred_service
        
        # Try OpenRouter first if available
        if service_to_use == "openrouter" and self.openrouter.is_available:
            result = self.openrouter.call_model(
                self.openrouter.default_model, prompt, system_prompt, 
                temperature, max_tokens
            )
            if result:
                return result
        
        # Fallback to Ollama
        if self.ollama.is_available:
            result = self.ollama.call_model(
                self.ollama.default_model, prompt, system_prompt,
                temperature, max_tokens
            )
            if result:
                return result
        
        # No LLM available
        return ""
    
    def is_available(self) -> bool:
        """Check if any LLM service is available"""
        return self.ollama.is_available or self.openrouter.is_available
    
    def get_status(self) -> Dict[str, Any]:
        """Get comprehensive status of all LLM services"""
        return {
            "ollama": {
                "available": self.ollama.is_available,
                "models": self.ollama.get_available_models() if self.ollama.is_available else []
            },
            "openrouter": {
                "available": self.openrouter.is_available,
                "model": self.openrouter.default_model
            },
            "preferred": self.preferred_service
        }

# ==================== AGRICULTURAL LLM SERVICES ====================

class AgriculturalLLMService:
    """Specialized LLM service for agricultural domain"""
    
    def __init__(self):
        self.llm_manager = LLMManager()
        self.agricultural_context = self._load_agricultural_context()
    
    def _load_agricultural_context(self) -> str:
        """Load agricultural domain context for LLM"""
        return """
        Anda adalah ahli pertanian dan konsultan agrikultur yang berpengalaman di Indonesia.
        Anda memiliki pengetahuan mendalam tentang:
        - Kondisi iklim dan cuaca Indonesia
        - Jenis tanaman yang cocok untuk berbagai daerah
        - Teknik budidaya dan pemeliharaan tanaman
        - Analisis kondisi tanah dan nutrisi
        - Penanganan hama dan penyakit tanaman
        - Optimasi hasil panen
        - Praktik pertanian berkelanjutan
        
        Berikan saran yang praktis, relevan dengan kondisi Indonesia, dan mudah dipahami petani.
        Gunakan bahasa Indonesia yang jelas dan ramah.
        """
    
    def generate_crop_evaluation(self, sensor_data: Dict[str, Any], 
                                location_data: Dict[str, Any] = None,
                                ml_prediction: Dict[str, Any] = None) -> str:
        """Generate comprehensive crop evaluation using LLM"""
        
        if not self.llm_manager.is_available():
            return "⚠️ LLM service tidak tersedia untuk evaluasi tanaman"
        
        # Prepare context
        context = f"""
        **Data Sensor Lahan:**
        - Nitrogen: {sensor_data.get('nitrogen', 'N/A')} kg/ha
        - Fosfor: {sensor_data.get('phosphorus', 'N/A')} kg/ha
        - Kalium: {sensor_data.get('potassium', 'N/A')} kg/ha
        - Suhu: {sensor_data.get('temperature', 'N/A')}°C
        - Kelembaban: {sensor_data.get('humidity', 'N/A')}%
        - pH Tanah: {sensor_data.get('ph', 'N/A')}
        - Curah Hujan: {sensor_data.get('rainfall', 'N/A')} mm
        - Luas Lahan: {sensor_data.get('land_area', 'N/A')} ha
        """
        
        if location_data:
            context += f"""
            
            **Informasi Lokasi:**
            - Lokasi: {location_data.get('address', 'N/A')}
            - Koordinat: {location_data.get('lat', 'N/A')}, {location_data.get('lng', 'N/A')}
            """
        
        if ml_prediction:
            context += f"""
            
            **Prediksi Model ML:**
            - Tanaman Terpilih: {ml_prediction.get('crop', 'N/A')}
            - Tingkat Kesesuaian: {ml_prediction.get('confidence', 0)*100:.1f}%
            """
        
        prompt = f"""
        Berdasarkan data berikut, berikan evaluasi mendalam tentang kondisi lahan pertanian:
        
        {context}
        
        Harap berikan:
        1. 🎯 **Evaluasi Kondisi Lahan** - Analisis kualitas tanah dan kondisi lingkungan
        2. 🌱 **Rekomendasi Tanaman** - Tanaman yang paling cocok untuk kondisi ini
        3. 💡 **Saran Perbaikan** - Langkah-langkah untuk mengoptimalkan kondisi lahan
        4. ⚠️ **Peringatan** - Potensi masalah dan cara mengatasinya
        5. 📅 **Waktu Tanam** - Kapan waktu terbaik untuk menanam
        
        Berikan jawaban yang praktis dan dapat diterapkan langsung oleh petani.
        """
        
        return self.llm_manager.call_llm(
            prompt=prompt,
            system_prompt=self.agricultural_context,
            temperature=0.7,
            max_tokens=2000
        )
    
    def generate_location_specific_advice(self, location_data: Dict[str, Any],
                                         sensor_data: Dict[str, Any] = None) -> str:
        """Generate location-specific agricultural advice"""
        
        if not self.llm_manager.is_available():
            return "⚠️ LLM service tidak tersedia untuk saran lokasi"
        
        context = f"""
        **Informasi Lokasi:**
        - Alamat: {location_data.get('address', 'N/A')}
        - Koordinat: {location_data.get('lat', 'N/A')}, {location_data.get('lng', 'N/A')}
        """
        
        if sensor_data:
            context += f"""
            
            **Data Kondisi Lahan:**
            - Suhu: {sensor_data.get('temperature', 'N/A')}°C
            - Kelembaban: {sensor_data.get('humidity', 'N/A')}%
            - Curah Hujan: {sensor_data.get('rainfall', 'N/A')} mm
            """
        
        prompt = f"""
        Berdasarkan lokasi berikut, berikan saran pertanian yang spesifik:
        
        {context}
        
        Harap berikan:
        1. 🗺️ **Karakteristik Wilayah** - Kondisi iklim dan geografis daerah ini
        2. 🌾 **Tanaman Unggulan** - Tanaman yang populer dan cocok di daerah ini
        3. 🌤️ **Pola Musim** - Musim tanam dan panen yang optimal
        4. 🏞️ **Kondisi Tanah** - Jenis tanah yang umum di daerah ini
        5. 💧 **Manajemen Air** - Sistem irigasi dan pengelolaan air yang efektif
        6. 🏘️ **Akses Pasar** - Peluang pasar dan distribusi hasil panen
        
        Berikan saran yang relevan dengan kondisi lokal dan praktik pertanian setempat.
        """
        
        return self.llm_manager.call_llm(
            prompt=prompt,
            system_prompt=self.agricultural_context,
            temperature=0.7,
            max_tokens=2000
        )
    
    def generate_optimization_suggestions(self, current_data: Dict[str, Any],
                                        target_crop: str = None) -> str:
        """Generate optimization suggestions for current conditions"""
        
        if not self.llm_manager.is_available():
            return "⚠️ LLM service tidak tersedia untuk saran optimasi"
        
        context = f"""
        **Kondisi Saat Ini:**
        - Nitrogen: {current_data.get('nitrogen', 'N/A')} kg/ha
        - Fosfor: {current_data.get('phosphorus', 'N/A')} kg/ha  
        - Kalium: {current_data.get('potassium', 'N/A')} kg/ha
        - Suhu: {current_data.get('temperature', 'N/A')}°C
        - Kelembaban: {current_data.get('humidity', 'N/A')}%
        - pH: {current_data.get('ph', 'N/A')}
        - Curah Hujan: {current_data.get('rainfall', 'N/A')} mm
        """
        
        if target_crop:
            context += f"\n**Tanaman Target:** {target_crop}"
        
        prompt = f"""
        Berdasarkan kondisi lahan saat ini, berikan saran optimasi:
        
        {context}
        
        Harap berikan:
        1. 📊 **Analisis Defisiensi** - Parameter yang perlu diperbaiki
        2. 🧪 **Rekomendasi Pupuk** - Jenis dan dosis pupuk yang tepat
        3. 💧 **Manajemen Air** - Pengaturan irigasi yang optimal
        4. 🌡️ **Kontrol Iklim** - Cara mengelola suhu dan kelembaban
        5. 🔄 **Langkah Bertahap** - Rencana perbaikan step-by-step
        6. 💰 **Estimasi Biaya** - Perkiraan biaya untuk optimasi
        
        Berikan saran yang praktis dan ekonomis untuk petani.
        """
        
        return self.llm_manager.call_llm(
            prompt=prompt,
            system_prompt=self.agricultural_context,
            temperature=0.7,
            max_tokens=2000
        )
    
    def generate_seasonal_recommendations(self, location_data: Dict[str, Any],
                                        current_month: int = None) -> str:
        """Generate seasonal agricultural recommendations"""
        
        if not self.llm_manager.is_available():
            return "⚠️ LLM service tidak tersedia untuk rekomendasi musiman"
        
        current_month = current_month or datetime.now().month
        month_names = [
            "", "Januari", "Februari", "Maret", "April", "Mei", "Juni",
            "Juli", "Agustus", "September", "Oktober", "November", "Desember"
        ]
        
        context = f"""
        **Informasi Lokasi:**
        - Lokasi: {location_data.get('address', 'N/A')}
        - Koordinat: {location_data.get('lat', 'N/A')}, {location_data.get('lng', 'N/A')}
        - Bulan Saat Ini: {month_names[current_month]}
        """
        
        prompt = f"""
        Berdasarkan lokasi dan waktu saat ini, berikan rekomendasi musiman:
        
        {context}
        
        Harap berikan:
        1. 🌤️ **Kondisi Musim** - Karakteristik musim saat ini di daerah tersebut
        2. 🌱 **Tanaman Musiman** - Tanaman yang tepat ditanam bulan ini
        3. 🌾 **Aktivitas Pertanian** - Kegiatan yang harus dilakukan saat ini
        4. 📅 **Kalender Tanam** - Jadwal tanam dan panen untuk 3 bulan ke depan
        5. ⚠️ **Antisipasi Cuaca** - Persiapan menghadapi perubahan cuaca
        6. 🏪 **Peluang Pasar** - Komoditas yang sedang bagus di pasar
        
        Berikan saran yang sesuai dengan pola musim dan iklim Indonesia.
        """
        
        return self.llm_manager.call_llm(
            prompt=prompt,
            system_prompt=self.agricultural_context,
            temperature=0.7,
            max_tokens=2000
        )
    
    def get_service_status(self) -> Dict[str, Any]:
        """Get status of LLM services"""
        return self.llm_manager.get_status()

# ==================== GLOBAL INSTANCE ====================

# Global instance for easy access
agricultural_llm = AgriculturalLLMService() 