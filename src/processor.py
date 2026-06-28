import pandas as pd

def clean_gsc_common(df):
    """Funzione di pulizia base usata da tutti i caricamenti"""
    # Pulizia CTR: gestisce stringhe con %, virgole e converte in float
    if 'CTR' in df.columns:
        df['CTR'] = df['CTR'].astype(str).str.replace('%', '').str.replace(',', '.').astype(float) / 100
    
    # Conversione numerica sicura (coerente tra tutti i file)
    cols_to_numeric = ['Clic', 'Impressioni', 'Posizione']
    for col in cols_to_numeric:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
    
    # Assicuriamo che Clic e Impressioni siano interi
    if 'Clic' in df.columns: df['Clic'] = df['Clic'].astype(int)
    if 'Impressioni' in df.columns: df['Impressioni'] = df['Impressioni'].astype(int)
        
    return df

def load_query(filepath):
    # Se è un file caricato da Streamlit, dobbiamo resettare il puntatore all'inizio
    if hasattr(filepath, 'seek'):
        filepath.seek(0)
    # Se è un percorso (stringa), usa pd.read_csv. Se è un file caricato, lo legge direttamente
    if isinstance(filepath, str):
        df = pd.read_csv(filepath, quotechar='"', on_bad_lines='skip')
    else:
        df = pd.read_csv(filepath, quotechar='"', on_bad_lines='skip')
    df.columns = ['Query', 'Clic', 'Impressioni', 'CTR', 'Posizione']
    return clean_gsc_common(df)

def load_date(filepath):
    # Se è un file caricato da Streamlit, dobbiamo resettare il puntatore all'inizio
    if hasattr(filepath, 'seek'):
        filepath.seek(0)
    df = pd.read_csv(filepath, quotechar='"', on_bad_lines='skip')
    # Se il tuo file 'Grafico.csv' ha la colonna '0' come data, la rinominiamo qui
    df.columns = ['Data', 'Clic', 'Impressioni', 'CTR', 'Posizione']
    df['Data'] = pd.to_datetime(df['Data'], errors='coerce')
    return clean_gsc_common(df)

def load_pages(filepath):
    # Se è un file caricato da Streamlit, dobbiamo resettare il puntatore all'inizio
    if hasattr(filepath, 'seek'):
        filepath.seek(0)
    df = pd.read_csv(filepath, quotechar='"', on_bad_lines='skip')
    df.columns = ['Pagina', 'Clic', 'Impressioni', 'CTR', 'Posizione']
    return clean_gsc_common(df)

def load_countries(filepath):
    df = pd.read_csv(filepath, quotechar='"', on_bad_lines='skip')
    df.columns = ['Paese', 'Clic', 'Impressioni', 'CTR', 'Posizione']
    return clean_gsc_common(df)

def load_devices(filepath):
    df = pd.read_csv(filepath, quotechar='"', on_bad_lines='skip')
    df.columns = ['Dispositivo', 'Clic', 'Impressioni', 'CTR', 'Posizione']
    return clean_gsc_common(df)

def add_seo_score(df):
    # Gestione sicura per evitare divisioni per zero
    pos_clean = df['Posizione'].replace(0, 100) # Se posizione è 0, mettiamo un valore basso
    pos_factor = pos_clean.apply(lambda x: 10 if x <= 3 else (5 if x <= 10 else 1))
    ctr_factor = df['CTR'] * 100
    
    df['SEO_Score'] = (pos_factor * 6 + ctr_factor * 4).clip(0, 100)
    return df

def get_actionable_insight(df, tab_name):
    """Restituisce un messaggio strategico basato sui dati"""
    if tab_name == "Panoramica":
        if df['CTR'].mean() < 0.02:
            return "⚠️ CTR basso: I tuoi titoli (Meta Titles) potrebbero non essere abbastanza attrattivi."
        return "✅ CTR nella norma: Continua a monitorare il trend."
        
    elif tab_name == "Salute SEO":
        avg_score = df['SEO_Score'].mean()
        if avg_score < 50:
            return "🚨 Salute SEO critica: Focalizzati sulle pagine con SEO Score < 30."
        return "🌟 Salute SEO buona: Il sito è ben posizionato."
    
    return "Analisi in corso..."

def diagnose_page(row):
    if row['SEO_Score'] > 50:
        return "✅ Ottimo: Pagina sana e performante"
    elif row['Impressioni'] > 100 and row['SEO_Score'] < 30:
        return "🚨 Critica: Alto traffico ma bassa performance (Ottimizza subito!)"
    elif row['Posizione'] > 20:
        return "🔍 Invisibile: Pagina in fondo ai risultati (Rivedi la SEO)"
    else:
        return "⚖️ Standard: Monitorare"

def generate_seo_report(df):
    """Genera un riassunto testuale delle performance"""
    total_clicks = df['Clic'].sum()
    best_query = df.loc[df['Clic'].idxmax(), 'Query']
    quick_wins = df[(df['Posizione'] > 10) & (df['Posizione'] <= 20)]
    
    report = f"""
    --- REPORT SEO AUTOMATIZZATO ---
    Data Generazione: {pd.Timestamp.now().strftime('%Y-%m-%d')}
    
    RIEPILOGO PERFORMANCE:
    - Totale Clic generati: {total_clicks}
    - Keyword Top Performer: '{best_query}'
    
    OPPORTUNITA' IMMEDIATE:
    - Hai {len(quick_wins)} keyword in seconda pagina. 
      Ottimizzare queste pagine potrebbe portare un incremento di traffico stimato del 15-20%.
    
    AZIONI CONSIGLIATE:
    1. Revisione dei Meta Title per le keyword in Quick Wins.
    2. Analisi della User Intent per le pagine con basso CTR.
    --------------------------------
    """
    return report

def get_seo_opportunities(df):
    return df[(df['Posizione'] > 10) & (df['Posizione'] <= 20)].sort_values('Impressioni', ascending=False)