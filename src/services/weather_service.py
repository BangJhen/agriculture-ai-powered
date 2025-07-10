import requests
import streamlit as st
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List, Tuple
import logging

logger = logging.getLogger(__name__)

class WeatherService:
    """
    Service untuk mengintegrasikan API OpenMeteo untuk mendapatkan data cuaca
    termasuk suhu, kelembapan, curah hujan, suhu tanah, dan kelembapan tanah
    """
    
    def __init__(self):
        self.base_url = "https://api.open-meteo.com/v1/forecast"
        self.cache_duration = 3600  # 1 hour cache
        
    def get_current_weather(self, latitude: float, longitude: float) -> Dict[str, Any]:
        """
        Mengambil data cuaca terkini berdasarkan koordinat
        
        Args:
            latitude: Garis lintang
            longitude: Garis bujur
            
        Returns:
            Dictionary dengan data cuaca lengkap
        """
        try:
            # Check cache first
            cache_key = f"weather_{latitude}_{longitude}"
            cached_data = self._get_cached_weather(cache_key)
            if cached_data:
                return cached_data
            
            # Fetch fresh data from OpenMeteo API
            params = {
                'latitude': latitude,
                'longitude': longitude,
                'current': [
                    'temperature_2m',           # Suhu udara (2m)
                    'relative_humidity_2m',     # Kelembapan relatif (2m)
                    'precipitation',            # Curah hujan saat ini
                    'weather_code',             # Kode cuaca
                    'surface_pressure',         # Tekanan permukaan
                    'wind_speed_10m',          # Kecepatan angin (10m)
                    'wind_direction_10m'        # Arah angin (10m)
                ],
                'hourly': [
                    'temperature_2m',           # Suhu udara
                    'relative_humidity_2m',     # Kelembapan relatif
                    'precipitation',            # Curah hujan
                    'soil_temperature_0cm',     # Suhu tanah 0cm
                    'soil_temperature_6cm',     # Suhu tanah 6cm
                    'soil_temperature_18cm',    # Suhu tanah 18cm
                    'soil_temperature_54cm',    # Suhu tanah 54cm
                    'soil_moisture_0_1cm',      # Kelembapan tanah 0-1cm
                    'soil_moisture_1_3cm',      # Kelembapan tanah 1-3cm
                    'soil_moisture_3_9cm',      # Kelembapan tanah 3-9cm
                    'soil_moisture_9_27cm',     # Kelembapan tanah 9-27cm
                    'soil_moisture_27_81cm'     # Kelembapan tanah 27-81cm
                ],
                'daily': [
                    'temperature_2m_max',       # Suhu maksimum
                    'temperature_2m_min',       # Suhu minimum
                    'precipitation_sum',        # Total curah hujan
                    'precipitation_probability_max',  # Probabilitas hujan max
                    'sunshine_duration',        # Durasi sinar matahari
                    'et0_fao_evapotranspiration'  # Evapotranspirasi
                ],
                'timezone': 'Asia/Jakarta',
                'forecast_days': 7,
                'past_days': 1
            }
            
            response = requests.get(self.base_url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            processed_data = self._process_weather_data(data)
            
            # Cache the processed data
            self._cache_weather_data(cache_key, processed_data)
            
            return processed_data
            
        except requests.RequestException as e:
            logger.error(f"Error fetching weather data: {e}")
            return self._get_fallback_weather_data()
        except Exception as e:
            logger.error(f"Unexpected error in weather service: {e}")
            return self._get_fallback_weather_data()
    
    def _process_weather_data(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Memproses data mentah dari OpenMeteo API
        """
        try:
            current = raw_data.get('current', {})
            hourly = raw_data.get('hourly', {})
            daily = raw_data.get('daily', {})
            
            # Current weather
            current_weather = {
                'temperature': current.get('temperature_2m', 0),
                'humidity': current.get('relative_humidity_2m', 0),
                'precipitation': current.get('precipitation', 0),
                'weather_code': current.get('weather_code', 0),
                'pressure': current.get('surface_pressure', 0),
                'wind_speed': current.get('wind_speed_10m', 0),
                'wind_direction': current.get('wind_direction_10m', 0),
                'timestamp': current.get('time', '')
            }
            
            # Soil data (ambil rata-rata 24 jam terakhir)
            soil_data = self._calculate_soil_averages(hourly)
            
            # Daily forecast (7 hari ke depan)
            daily_forecast = self._process_daily_forecast(daily)
            
            # Weather description
            weather_description = self._get_weather_description(current.get('weather_code', 0))
            
            return {
                'status': 'success',
                'location': {
                    'latitude': raw_data.get('latitude'),
                    'longitude': raw_data.get('longitude'),
                    'elevation': raw_data.get('elevation', 0)
                },
                'current': current_weather,
                'soil': soil_data,
                'daily_forecast': daily_forecast,
                'weather_description': weather_description,
                'units': {
                    'temperature': '°C',
                    'humidity': '%',
                    'precipitation': 'mm',
                    'pressure': 'hPa',
                    'wind_speed': 'km/h',
                    'soil_temperature': '°C',
                    'soil_moisture': 'm³/m³'
                },
                'updated_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error processing weather data: {e}")
            return self._get_fallback_weather_data()
    
    def _calculate_soil_averages(self, hourly_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Menghitung rata-rata data tanah untuk 24 jam terakhir
        """
        try:
            # Ambil 24 data terakhir (24 jam)
            soil_temps = {
                'surface': hourly_data.get('soil_temperature_0cm', [])[-24:],
                'shallow': hourly_data.get('soil_temperature_6cm', [])[-24:],
                'medium': hourly_data.get('soil_temperature_18cm', [])[-24:],
                'deep': hourly_data.get('soil_temperature_54cm', [])[-24:]
            }
            
            soil_moisture = {
                'very_shallow': hourly_data.get('soil_moisture_0_1cm', [])[-24:],
                'shallow': hourly_data.get('soil_moisture_1_3cm', [])[-24:],
                'medium': hourly_data.get('soil_moisture_3_9cm', [])[-24:],
                'deep': hourly_data.get('soil_moisture_9_27cm', [])[-24:],
                'very_deep': hourly_data.get('soil_moisture_27_81cm', [])[-24:]
            }
            
            # Hitung rata-rata
            avg_soil_temp = {}
            for depth, temps in soil_temps.items():
                if temps and len(temps) > 0:
                    valid_temps = [t for t in temps if t is not None]
                    avg_soil_temp[depth] = round(sum(valid_temps) / len(valid_temps), 1) if valid_temps else 0
                else:
                    avg_soil_temp[depth] = 0
            
            avg_soil_moisture = {}
            for depth, moisture in soil_moisture.items():
                if moisture and len(moisture) > 0:
                    valid_moisture = [m for m in moisture if m is not None]
                    avg_soil_moisture[depth] = round(sum(valid_moisture) / len(valid_moisture), 3) if valid_moisture else 0
                else:
                    avg_soil_moisture[depth] = 0
            
            return {
                'temperature': avg_soil_temp,
                'moisture': avg_soil_moisture,
                'overall_avg_temp': round(sum(avg_soil_temp.values()) / len(avg_soil_temp), 1),
                'overall_avg_moisture': round(sum(avg_soil_moisture.values()) / len(avg_soil_moisture), 3)
            }
            
        except Exception as e:
            logger.error(f"Error calculating soil averages: {e}")
            return {
                'temperature': {'surface': 0, 'shallow': 0, 'medium': 0, 'deep': 0},
                'moisture': {'very_shallow': 0, 'shallow': 0, 'medium': 0, 'deep': 0, 'very_deep': 0},
                'overall_avg_temp': 0,
                'overall_avg_moisture': 0
            }
    
    def _process_daily_forecast(self, daily_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Memproses data ramalan harian
        """
        try:
            forecast = []
            times = daily_data.get('time', [])
            
            for i, date_str in enumerate(times[:7]):  # 7 hari forecast
                day_data = {
                    'date': date_str,
                    'temp_max': daily_data.get('temperature_2m_max', [])[i] if i < len(daily_data.get('temperature_2m_max', [])) else 0,
                    'temp_min': daily_data.get('temperature_2m_min', [])[i] if i < len(daily_data.get('temperature_2m_min', [])) else 0,
                    'precipitation': daily_data.get('precipitation_sum', [])[i] if i < len(daily_data.get('precipitation_sum', [])) else 0,
                    'precipitation_prob': daily_data.get('precipitation_probability_max', [])[i] if i < len(daily_data.get('precipitation_probability_max', [])) else 0,
                    'sunshine': daily_data.get('sunshine_duration', [])[i] if i < len(daily_data.get('sunshine_duration', [])) else 0,
                    'evapotranspiration': daily_data.get('et0_fao_evapotranspiration', [])[i] if i < len(daily_data.get('et0_fao_evapotranspiration', [])) else 0
                }
                forecast.append(day_data)
            
            return forecast
            
        except Exception as e:
            logger.error(f"Error processing daily forecast: {e}")
            return []
    
    def _get_weather_description(self, weather_code: int) -> str:
        """
        Mengkonversi kode cuaca WMO menjadi deskripsi dalam bahasa Indonesia
        """
        weather_codes = {
            0: "Cerah",
            1: "Sebagian Cerah",
            2: "Berawan Sebagian",
            3: "Berawan",
            45: "Berkabut",
            48: "Berkabut Tebal",
            51: "Gerimis Ringan",
            53: "Gerimis Sedang",
            55: "Gerimis Lebat",
            56: "Gerimis Beku Ringan",
            57: "Gerimis Beku Lebat",
            61: "Hujan Ringan",
            63: "Hujan Sedang",
            65: "Hujan Lebat",
            66: "Hujan Beku Ringan",
            67: "Hujan Beku Lebat",
            71: "Salju Ringan",
            73: "Salju Sedang",
            75: "Salju Lebat",
            77: "Butir Salju",
            80: "Hujan Deras Ringan",
            81: "Hujan Deras Sedang",
            82: "Hujan Deras Lebat",
            85: "Salju Deras Ringan",
            86: "Salju Deras Lebat",
            95: "Badai Petir",
            96: "Badai Petir dengan Hujan Es Ringan",
            99: "Badai Petir dengan Hujan Es Lebat"
        }
        
        return weather_codes.get(weather_code, "Tidak Diketahui")
    
    def _get_cached_weather(self, cache_key: str) -> Optional[Dict[str, Any]]:
        """
        Mengambil data cuaca dari cache session state
        """
        try:
            if f"weather_cache_{cache_key}" in st.session_state:
                cached_item = st.session_state[f"weather_cache_{cache_key}"]
                cache_time = datetime.fromisoformat(cached_item['timestamp'])
                
                if datetime.now() - cache_time < timedelta(seconds=self.cache_duration):
                    return cached_item['data']
            
            return None
        except Exception:
            return None
    
    def _cache_weather_data(self, cache_key: str, data: Dict[str, Any]) -> None:
        """
        Menyimpan data cuaca ke cache session state
        """
        try:
            st.session_state[f"weather_cache_{cache_key}"] = {
                'data': data,
                'timestamp': datetime.now().isoformat()
            }
        except Exception:
            pass  # Gagal cache tidak kritis
    
    def _get_fallback_weather_data(self) -> Dict[str, Any]:
        """
        Data cuaca fallback jika API tidak tersedia
        """
        return {
            'status': 'fallback',
            'location': {'latitude': 0, 'longitude': 0, 'elevation': 0},
            'current': {
                'temperature': 0,
                'humidity': 0,
                'precipitation': 0,
                'weather_code': 0,
                'pressure': 0,
                'wind_speed': 0,
                'wind_direction': 0,
                'timestamp': ''
            },
            'soil': {
                'temperature': {'surface': 0, 'shallow': 0, 'medium': 0, 'deep': 0},
                'moisture': {'very_shallow': 0, 'shallow': 0, 'medium': 0, 'deep': 0, 'very_deep': 0},
                'overall_avg_temp': 0,
                'overall_avg_moisture': 0
            },
            'daily_forecast': [],
            'weather_description': 'Data tidak tersedia',
            'units': {
                'temperature': '°C',
                'humidity': '%',
                'precipitation': 'mm',
                'pressure': 'hPa',
                'wind_speed': 'km/h',
                'soil_temperature': '°C',
                'soil_moisture': 'm³/m³'
            },
            'updated_at': datetime.now().isoformat(),
            'error': 'API cuaca tidak tersedia'
        }
    
    def get_agricultural_weather_summary(self, latitude: float, longitude: float) -> Dict[str, Any]:
        """
        Mendapatkan ringkasan cuaca yang relevan untuk pertanian
        """
        weather_data = self.get_current_weather(latitude, longitude)
        
        if weather_data['status'] == 'fallback':
            return weather_data
        
        # Analisis kondisi untuk pertanian
        current = weather_data['current']
        soil = weather_data['soil']
        
        # Evaluasi kondisi
        agricultural_conditions = {
            'temperature_status': self._evaluate_temperature(current['temperature']),
            'humidity_status': self._evaluate_humidity(current['humidity']),
            'soil_temp_status': self._evaluate_soil_temperature(soil['overall_avg_temp']),
            'soil_moisture_status': self._evaluate_soil_moisture(soil['overall_avg_moisture']),
            'precipitation_status': self._evaluate_precipitation(current['precipitation']),
            'overall_rating': 'baik'  # Akan dihitung berdasarkan kondisi
        }
        
        # Hitung rating keseluruhan
        ratings = [agricultural_conditions[key] for key in agricultural_conditions if key.endswith('_status')]
        good_ratings = sum(1 for rating in ratings if rating == 'baik')
        
        if good_ratings >= 4:
            agricultural_conditions['overall_rating'] = 'sangat_baik'
        elif good_ratings >= 3:
            agricultural_conditions['overall_rating'] = 'baik'
        elif good_ratings >= 2:
            agricultural_conditions['overall_rating'] = 'sedang'
        else:
            agricultural_conditions['overall_rating'] = 'kurang_baik'
        
        weather_data['agricultural_analysis'] = agricultural_conditions
        
        return weather_data
    
    def _evaluate_temperature(self, temp: float) -> str:
        """Evaluasi kondisi suhu untuk pertanian"""
        if 20 <= temp <= 30:
            return 'baik'
        elif 15 <= temp < 20 or 30 < temp <= 35:
            return 'sedang'
        else:
            return 'kurang_baik'
    
    def _evaluate_humidity(self, humidity: float) -> str:
        """Evaluasi kelembapan untuk pertanian"""
        if 50 <= humidity <= 70:
            return 'baik'
        elif 40 <= humidity < 50 or 70 < humidity <= 80:
            return 'sedang'
        else:
            return 'kurang_baik'
    
    def _evaluate_soil_temperature(self, soil_temp: float) -> str:
        """Evaluasi suhu tanah untuk pertanian"""
        if 18 <= soil_temp <= 25:
            return 'baik'
        elif 15 <= soil_temp < 18 or 25 < soil_temp <= 30:
            return 'sedang'
        else:
            return 'kurang_baik'
    
    def _evaluate_soil_moisture(self, soil_moisture: float) -> str:
        """Evaluasi kelembapan tanah untuk pertanian"""
        if 0.2 <= soil_moisture <= 0.4:
            return 'baik'
        elif 0.1 <= soil_moisture < 0.2 or 0.4 < soil_moisture <= 0.5:
            return 'sedang'
        else:
            return 'kurang_baik'
    
    def _evaluate_precipitation(self, precipitation: float) -> str:
        """Evaluasi curah hujan untuk pertanian"""
        if 0 <= precipitation <= 10:
            return 'baik'
        elif 10 < precipitation <= 20:
            return 'sedang'
        else:
            return 'kurang_baik'


# Global instance
weather_service = WeatherService() 