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


def get_search_intent(query):
    model = genai.GenerativeModel('gemini-1.5-flash')
    
    prompt = f"""
    Sei un esperto SEO. Classifica la keyword fornita in UNA di queste categorie: "Informativa", "Transazionale", "Navigazionale".
    
    Esempi:
    - "ristorante roma" -> Transazionale
    - "come cucinare la pasta" -> Informativa
    - "sito ufficiale volpe pasini" -> Navigazionale
    
    Keyword da classificare: "{query}"
    Rispondi SOLTANTO con la categoria, nessuna spiegazione.
    """
    
    try:
        response = model.generate_content(prompt)
        result = response.text.strip()
        # Pulizia: se l'IA aggiunge punti o spazi
        return result.replace('.', '').strip()
    except:
        return "Errore IA"
