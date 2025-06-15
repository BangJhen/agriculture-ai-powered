#!/usr/bin/env python3
"""
Test script untuk Asisten Pertanian Indonesia
Mendemonstrasikan format respons terstruktur khusus Indonesia
"""

from agricultural_chatbot import initialize_openai_client, get_ai_response

def test_indonesian_responses():
    """Test format respons terstruktur dengan skenario Indonesia"""
    
    client = initialize_openai_client()
    
    test_scenarios = [
        {
            "role": "Petani",
            "location": "Jawa Barat",
            "question": "Sawah padi saya terkena serangan wereng minggu lalu. Berapa lama waktu pemulihan yang dibutuhkan?"
        },
        {
            "role": "Peternak", 
            "location": "Jawa Timur",
            "question": "Beberapa sapi saya menunjukkan gejala penyakit pernapasan. Bagaimana timeline pemulihannya?"
        },
        {
            "role": "Insinyur Pertanian",
            "location": "Sumatera Utara",
            "question": "Sistem irigasi teknis gagal saat musim kemarau. Apa strategi pemulihan terbaik?"
        }
    ]
    
    print("🌾 Testing Asisten Pertanian Indonesia - Format Respons Terstruktur")
    print("=" * 80)
    
    for i, scenario in enumerate(test_scenarios, 1):
        print(f"\n🧪 TEST {i}: {scenario['role']} - {scenario['location']}")
        print(f"📝 Pertanyaan: {scenario['question']}")
        print("-" * 80)
        
        try:
            response = get_ai_response(client, scenario['role'], scenario['question'], scenario['location'])
            print(response)
        except Exception as e:
            print(f"❌ Error: {e}")
        
        print("=" * 80)

if __name__ == "__main__":
    test_indonesian_responses()
