import google.generativeai as genai
import os
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
    Interroga l'API di Gemini per generare proposte di ottimizzazione del CTR.
    Gestisce in totale sicurezza i dati numerici ed evita i crash di formattazione stringa.
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
        
    # --- 🚀 INIZIALIZZAZIONE CON IL NUOVO CLIENT ---
    try:
        # Il nuovo client accetta nativamente le chiavi AQ
        client = genai.Client(api_key=api_key)
        model = genai.GenerativeModel('gemini-2.0-flash-latest')
        
        # --- 🧠 COSTRUZIONE DEL PROMPT AVANZATO ---
        prompt = f"""
        Agisci come un esperto SEO Copywriter Senior specializzato nell'aumentare il CTR (Click-Through Rate) nei risultati di ricerca di Google.
        Un sito web di una PMI ha una pagina con le seguenti performance attuali:
        - Keyword principale per cui si posiziona: '{keyword}'
        - Posizione media su Google: {posizione}
        - CTR attuale: {ctr_visualizzato}
        
        I tag HTML attualmente caricati sulla pagina sono:
        - TITOLO ATTUALE: {current_title}
        - META DESCRIPTION ATTUALE: {current_desc}
        
        Il tuo compito è riscrivere il Tag Title e la Meta Description per renderli irresistibili da cliccare rispetto alla concorrenza, stimolando la curiosità, l'urgenza o l'esclusività, ma mantenendo obbligatoriamente la keyword principale (essenziale per non perdere il posizionamento acquisito).
        
        Rispetta rigidamente i limiti di pixel/caratteri di Google:
        - Tag Title: Massimo 60 caratteri.
        - Meta Description: Massimo 150 caratteri.
        
        Fornisci esattamente 3 varianti diverse (es. una basata sui benefici diretti, una numerica/lista, una emozionale o a domanda), formattate chiaramente in questo modo:
        
        ### 🎯 Variante 1: [Tipo di approccio]
        **Title:** [Nuovo Titolo Ottimizzato]
        **Meta Description:** [Nuova Meta Description Ottimizzata]
        
        ### 🎯 Variante 2: [Tipo di approccio]
        **Title:** [Nuovo Titolo Ottimizzato]
        **Meta Description:** [Nuova Meta Description Ottimizzata]
        
        ### 🎯 Variante 3: [Tipo di approccio]
        **Title:** [Nuovo Titolo Ottimizzato]
        **Meta Description:** [Nuova Meta Description Ottimizzata]
        
        Rispondi esclusivamente in italiano. Vai dritto al punto senza preamboli, introduzioni o saluti.
        """
        
        # --- 🚀 ESECUZIONE CHIAMATA API ---
        # Chiamata con il nuovo SDK e modello consigliato
        response = client.models.generate_content(
            model='gemini-2.0-flash',
            contents=prompt,
        )
        return response.text
    except Exception as e:
        return f"❌ Errore con il nuovo client Gemini: {str(e)}"
def get_search_intent(query):
    model = genai.GenerativeModel('gemini-2-0-flash-latest')
    
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
