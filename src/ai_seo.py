import google.generativeai as genai
import os
import requests
from google import genai
from google.genai import types
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
def generate_seo_suggestions(keyword, current_title, current_desc, posizione, ctr):
    """
    Genera proposte SEO effettuando una chiamata HTTP diretta alle API di Gemini.
    Perfettamente compatibile con chiavi API che iniziano per AQ e AIzaSy.
    """
    
    # --- 🛠️ BLOCCO DI SICUREZZA PER IL CTR ---
    try:
        if isinstance(ctr, str):
            ctr = ctr.replace('%', '').strip()
        ctr_num = float(ctr)
        if ctr_num > 1.0:
            ctr_num = ctr_num / 100
        ctr_visualizzato = f"{ctr_num:.2%}"
    except (ValueError, TypeError):
        ctr_visualizzato = str(ctr)

    # --- 🔑 RECUPERO API KEY ---
    api_key = st.secrets.get("GEMINI_API_KEY") or os.getenv("GEMINI_API_KEY")
    if not api_key:
        return "⚠️ Errore: Configura la tua 'GEMINI_API_KEY' nei Secrets di Streamlit."
        
    # --- 🧠 COSTRUZIONE DEL PROMPT ---
    prompt = f"""
    Agisci come un esperto SEO Copywriter Senior specializzato nell'aumentare il CTR (Click-Through Rate) nei risultati di ricerca di Google.
    Un sito web di una PMI ha una pagina con le seguenti performance attuali:
    - Keyword principale: '{keyword}'
    - Posizione media: {posizione}
    - CTR attuale: {ctr_visualizzato}
    
    I tag HTML attuali sono:
    - TITOLO ATTUALE: {current_title}
    - META DESCRIPTION ATTUALE: {current_desc}
    
    Riscrivi il Tag Title (max 60 caratteri) e la Meta Description (max 150 caratteri) per aumentare drasticamente i clic, mantenendo la keyword principale.
    Fornisci esattamente 3 varianti in italiano, formattate chiaramente con titoli (Variante 1, 2, 3). Vai dritto al punto.
    """

    # --- 🌐 CHIAMATA REST DIRETTA ---
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={api_key}"
    headers = {"Content-Type": "application/json"}
    payload = {
        "contents": [
            {
                "parts": [{"text": prompt}]
            }
        ]
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=15)
        response_json = response.json()
        
        if response.status_code != 200:
            error_details = response_json.get("error", {}).get("message", "Errore sconosciuto")
            return f"❌ Errore API Gemini ({response.status_code}): {error_details}"
            
        return response_json['candidates'][0]['content']['parts'][0]['text']
    except Exception as e:
        return f"❌ Errore di connessione durante la richiesta a Gemini: {str(e)}"


def get_search_intent(keyword):
    """
    Funzione di fallback per calcolare l'intento di ricerca della keyword,
    evitando il NameError / ImportError all'avvio di app.py.
    """
    # Puoi espandere questa logica in futuro se serve alla dashboard,
    # per ora restituisce un valore sicuro per non bloccare l'app.
    kw_lower = str(keyword).lower()
    if any(w in kw_lower for w in ["comprare", "prezzo", "costo", "bistrot", "ristorante", "shop"]):
        return "Commerciale / Transazionale"
    return "Informativo"
