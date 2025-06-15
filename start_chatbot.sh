#!/bin/bash

echo "🌾 Memulai Asisten Pertanian Ahli Indonesia..."
echo "Menginstal dependencies..."
pip install -r requirements.txt

echo "Meluncurkan aplikasi Streamlit..."
streamlit run agricultural_chatbot.py

echo "Chatbot sekarang berjalan di http://localhost:8501"
echo "Tekan Ctrl+C untuk menghentikan aplikasi"
