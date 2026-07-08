import pandas as pd
import requests
import os
from bs4 import BeautifulSoup
import google.generativeai as genai
import streamlit as st

def find_quick_wins(df, min_impressions=500, max_ctr=0.03):
    """
    Isola le pagine con alto potenziale (buone impression) ma basso CTR.
    Filtra le keyword posizionate nelle prime 15 posizioni.
    """
    if df.empty:
        return pd.DataFrame()
    
    # Filtriamo: posizioni rilevanti, buone impression, ma CTR basso
    quick_wins = df[
        (df['position'] <= 15) & 
        (df['impressions'] >= min_impressions) & 
        (df['ctr'] < max_ctr)
    ].copy()
    
    # Ordiniamo per opportunità (chi ha più impression ma pochi clic viene prima)
    quick_wins = quick_wins.sort_values(by='impressions', ascending=False)
    return quick_wins

def scrape_current_tags(url):
    """
    Effettua il web scraping della pagina per estrarre il Title e la Meta Description attuali.
    """
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    try:
        response = requests.get(url, headers=headers, timeout=5)
        if response.status_code != 200:
            return "Non accessibile", "Non accessibile"
            
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Estrazione del Titolo
        title = soup.find('title').text.strip() if soup.find('title') else "Nessun Titolo Trovato"
        
        # Estrazione della Meta Description
        meta_desc = "Nessuna Meta Description Trovata"
        meta_tag = soup.find('meta', attrs={'name': 'description'}) or soup.find('meta', attrs={'property': 'og:description'})
        if meta_tag and meta_tag.get('content'):
            meta_desc = meta_tag['content'].strip()
            
        return title, meta_desc
    except Exception as e:
        return f"Errore: {str(e)}", "Errore"

def generate_seo_suggestions(keyword, current_title, current_desc):
    """
    Interroga l'API di Gemini per generare proposte di ottimizzazione del CTR.
    """
    # Recupera la chiave API da Streamlit Secrets o variabili d'ambiente
    api_key = st.secrets.get("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
    if not api_key:
        return ["Configura la tua GOOGLE_API_KEY per ricevere suggerimenti."]
        
    genai.configure(api_key=api_key)
    
    # Usiamo il modello stabile e veloce per elaborazione testi
    model = genai.GenerativeModel('gemini-1.5-flash')
    
    prompt = f"""
    Agisci come un esperto SEO Copywriter Senior specializzato nell'aumentare il CTR (Click-Through Rate) nei risultati di ricerca di Google.
    Un sito web ha una pagina che si posiziona per la keyword: '{keyword}'.
    
    I tag HTML attuali di questa pagina sono:
    - TITOLO ATTUALE: {current_title}
    - META DESCRIPTION ATTUALE: {current_desc}
    
    Il tuo compito è riscrivere questi tag per renderli irresistibili da cliccare, mantenendo la keyword principale all'inizio o comunque dentro i testi, rispettando i limiti di lunghezza di Google (Title: max 60 caratteri, Description: max 150 caratteri).
    
    Fornisci esattamente 3 varianti diverse (es. una basata sulla curiosità, una sui benefici, una numerica/emozionale).
    Rispondi esclusivamente in italiano formattando l'output in modo pulito ed elegante.
    """
    
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Errore nella generazione AI: {str(e)}"