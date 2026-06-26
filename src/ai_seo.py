import google.generativeai as genai
import os
import streamlit as st # Importa streamlit per leggere i segreti

# Configura l'API (usa una variabile d'ambiente per sicurezza!)
try:
    api_key = os.getenv("GOOGLE_API_KEY") 
except:
    # 2. Se non siamo su Cloud, carica dal file .env locale
    from dotenv import load_dotenv
    load_dotenv()
    api_key = os.getenv("GOOGLE_API_KEY")
    
genai.configure(api_key=api_key)
def generate_seo_suggestions(query, posizione, ctr):
    model = genai.GenerativeModel('gemini-2.5-flash')
    prompt = f"""
    Sei un esperto SEO. Analizza questa keyword: '{query}'.
    Posizione attuale: {posizione}, CTR attuale: {ctr:.2%}.
    Scrivi:
    1. Un titolo (Meta Title) ottimizzato di 60 caratteri.
    2. Un consiglio rapido per migliorare il posizionamento.
    Sii breve e strategico.
    """
    
    response = model.generate_content(prompt)
    return response.text
