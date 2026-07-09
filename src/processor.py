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

def analyze_content_decay(df_current, df_previous):
    """
    df_current: dati dell'ultimo mese
    df_previous: dati del mese precedente
    """
    # Uniamo i due dataframe sulla colonna 'Pagina'
    df_merged = pd.merge(df_current, df_previous, on='Pagina', suffixes=('_curr', '_prev'))
    
    # Calcoliamo il calo di clic
    df_merged['Variazione_Clic'] = df_merged['Clic_curr'] - df_merged['Clic_prev']
    df_merged['Perc_Decay'] = (df_merged['Variazione_Clic'] / df_merged['Clic_prev']) * 100
    
    # Filtriamo solo chi ha perso più del 20% di traffico
    decaying_pages = df_merged[df_merged['Perc_Decay'] < -20].sort_values('Perc_Decay')
    return decaying_pages

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
def perform_technical_audit(df_pages):
    """Diagnostica lo stato tecnico delle pagine"""
    audit = []
    for _, row in df_pages.iterrows():
        issues = []
        # Controllo Criticità
        if row['CTR'] < 0.01: issues.append("CTR molto basso (<1%)")
        if row['Posizione'] > 30: issues.append("Posizione critica (>30)")
        if row['Impressioni'] > 1000 and row['Posizione'] > 10: issues.append("Alta visibilità, basso ranking")
        
        audit.append({
            'Pagina': row['Pagina'],
            'Problemi': ", ".join(issues) if issues else "Nessun problema rilevato",
            'Stato': "🚨" if issues else "✅"
        })
    return pd.DataFrame(audit)

def get_competitor_gap(df_cliente, df_competitor):
    """Trova le keyword del competitor che il cliente non ha"""
    # Prendiamo le query del competitor che non sono presenti nelle query del cliente
    query_cliente = set(df_cliente['Query'].str.lower())
    gap = df_competitor[~df_competitor['Query'].str.lower().isin(query_cliente)]
    return gap.sort_values('Impressioni', ascending=False)

def analyze_crawl_efficiency(df_pages):
    """Calcola quanto è profonda una pagina nella struttura del sito"""
    # Profondità basata sul numero di slash (es. /a/b/c/d/ = 4 livelli)
    df_pages['Crawl_Depth'] = df_pages['Pagina'].str.count('/') - 2
    df_pages['Crawl_Depth'] = df_pages['Crawl_Depth'].clip(lower=0)
    return df_pages

def calculate_keyword_difficulty(df):
    """
    Stima la difficoltà di una keyword (0-100)
    Formula basata su: Impressioni (Volume), Posizione (Competizione), CTR
    """
    # 1. Normalizziamo i fattori
    # Più impressioni = più competizione (logaritmico)
    vol_factor = (df['Impressioni'] / df['Impressioni'].max()) * 50
    # Più la posizione è alta (es. 20), più è difficile scalare
    pos_factor = (df['Posizione'] / df['Posizione'].max()) * 30
    # Più il CTR è basso, più la competizione è agguerrita
    ctr_factor = (1 - df['CTR']) * 20
    
    df['Keyword_Difficulty'] = (vol_factor + pos_factor + ctr_factor).clip(0, 100)
    return df
    
def get_seo_opportunities(df):
    return df[(df['Posizione'] > 10) & (df['Posizione'] <= 20)].sort_values('Impressioni', ascending=False)