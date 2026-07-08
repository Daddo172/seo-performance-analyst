import streamlit as st
from datetime import datetime, timedelta
import pandas as pd
from src.seo_optimizer import find_quick_wins, scrape_current_tags
from src.google_api_connector import get_merged_seo_data, fetch_ga4_traffic_sources
import plotly.express as px
from src.ai_seo import get_search_intent, generate_seo_suggestions, generate_aeo_faq
from src.processor import get_competitor_gap, analyze_content_decay, calculate_keyword_difficulty, perform_technical_audit, analyze_crawl_efficiency, add_seo_score, generate_seo_report, diagnose_page, get_actionable_insight, load_query, load_pages, load_date, load_devices, load_countries
from src.broken_links import check_broken_links
from src.technical_audit import check_ssl
from src.forecasting import train_and_forecast, perform_backtest
from src.aeo import audit_page_aeo, classify_ai_referrals, parse_qa_text, generate_faq_schema

# Configurazione Pagina
st.set_page_config(page_title="SEO Strategy Dashboard", layout="wide")
st.title("🚀 SEO Performance Analyzer")
st.markdown("Trasforma i dati di Search Console in strategie di crescita.")

# 1. Box di caricamento dinamico
st.sidebar.title("Configurazione Sorgente Dati")
source_type = st.sidebar.radio("Scegli come inserire i dati:", ["Connessione API (Raccomandato)", "Carica file CSV"])

if source_type == "Connessione API (Raccomandato)":
    st.subheader("Dati Estratti in Tempo Reale via API")
    
    # Input di configurazione (in produzione leggerai questi dati da un file di configurazione dell'utente)
    site_url = st.sidebar.text_input("GSC Site URL", value="https://www.esempio.com/")
    property_id = st.sidebar.text_input("GA4 Property ID", value="123456789")
    
    # Selettore di date spazioso ed elegante
    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input("Data Inizio", datetime.now() - timedelta(days=30))
    with col2:
        end_date = st.date_input("Data Fine", datetime.now())
        
    if st.button("Calcola Performance e Genera Soluzioni"):
        with st.spinner("Estrazione e incrocio dati in corso..."):
            # Chiamata alla funzione di Data Science
            df_final = get_merged_seo_data(
                site_url, 
                property_id, 
                start_date.strftime("%Y-%m-%d"), 
                end_date.strftime("%Y-%m-%d")
            )
            
            if not df_final.empty:
                st.success("Dati caricati e uniti con successo!")
                st.dataframe(df_final.head(10))
                
                # QUI SALVIAMO IL DATAFRAME IN SESSION_STATE PER I MODULI SUCCESSIVI
                st.session_state['seo_data'] = df_final
                st.session_state['ga4_property_id'] = property_id
                st.session_state['gsc_site_url'] = site_url
                st.session_state['api_start_date'] = start_date
                st.session_state['api_end_date'] = end_date
            else:
                st.error("Nessun dato trovato per le credenziali o le date inserite.")
    # Sotto il caricamento dei dati in app.py...
if 'seo_data' in st.session_state:
    df_final = st.session_state['seo_data']
    
    # Creiamo tre tab nella dashboard per organizzare il lavoro
    tab1, tab2, tab3 = st.tabs(["📊 Panoramica Dati", "🚀 Modulo: Vincite Facili (Ottimizzazione CTR)", "🤖 AEO Readiness"])
    
    with tab1:
        st.subheader("I tuoi dati SEO uniti")
        st.dataframe(df_final)
        
    with tab2:
        st.subheader("Pagine ad alto potenziale ma basso Click-Through Rate")
        st.write("Queste pagine compaiono spesso su Google (alte Impression) ma gli utenti non le cliccano. Ottimizza il titolo e la descrizione per attirare traffico!")
        
        # Eseguiamo l'algoritmo di Data Science per trovare i Quick Wins
        df_wins = find_quick_wins(df_final)
        
        if df_wins.empty:
            st.info("Congratulazioni! Non ci sono pagine con un CTR criticamente basso sotto la posizione 15.")
        else:
            # Mostriamo la tabella delle opportunità semplificata per la PMI
            st.dataframe(
                df_wins[['page', 'keyword', 'impressions', 'clicks', 'ctr', 'position']].head(10),
                column_config={
                    "page": "URL Pagina",
                    "keyword": "Keyword Principale",
                    "impressions": "Visualizzazioni",
                    "clicks": "Clic Ricevuti",
                    "ctr": st.column_config.NumberColumn("CTR attuale", format="%.2f%%"),
                    "position": "Posizione Media"
                }
            )
            
            st.markdown("---")
            st.subheader("🧠 Ottimizzatore Intelligente Singola Pagina")
            
            # Creiamo un selettore per permettere alla PMI di scegliere quale keyword/pagina ottimizzare
            opportunity_list = [f"{row['keyword']} -> {row['page']}" for _, row in df_wins.head(10).iterrows()]
            selected_opt = st.selectbox("Seleziona quale opportunità vuoi analizzare:", opportunity_list)
            
            if selected_opt:
                # Estraiamo la keyword e l'URL selezionati dalla stringa del selectbox
                selected_keyword = selected_opt.split(" -> ")[0]
                selected_url = selected_opt.split(" -> ")[1]
                
                # 💡 IL TRUCCO: Recuperiamo l'intera riga del DataFrame associata a questa specifica pagina
                riga_selezionata = df_wins[df_wins['page'] == selected_url].iloc[0]
                
                if st.button("Analizza Pagina e Genera Nuovi Tag con AI"):
                    with st.spinner("Scansione della pagina web in corso..."):
                        current_title, current_desc = scrape_current_tags(selected_url)
                        
                        col_left, col_right = st.columns(2)
                        with col_left:
                            st.info(f"**Titolo Rilevato sul Sito:**\n{current_title}")
                        with col_right:
                            st.info(f"**Meta Description Rilevata:**\n{current_desc}")
                            
                    with st.spinner("Gemini sta elaborando le varianti di copywriting ad alto CTR..."):
                        # ✨ CHIAMATA AGGIORNATA: Ora passiamo tutti e 5 i parametri richiesti dalla funzione
                        ai_suggestions = generate_seo_suggestions(
                            keyword=selected_keyword,
                            current_title=current_title,
                            current_desc=current_desc,
                            posizione=riga_selezionata['position'],  # o 'posizione' se hai rinominato la colonna
                            ctr=riga_selezionata['ctr']
                        )
                        
                        st.success("✨ Ecco le proposte di ottimizzazione generate dall'Intelligenza Artificiale:")
                        st.markdown(ai_suggestions)

    with tab3:
        st.subheader("🤖 AEO Readiness")
        with st.expander("❓ Cos'è l'AEO"):
            st.write("""
            L'AEO (Answer Engine Optimization) ottimizza il contenuto per essere letto,
            sintetizzato e citato da ChatGPT, Perplexity, Copilot, Gemini e le AI Overview
            di Google — non solo per rankare in una SERP classica. Il punteggio sotto pesa:
            crawlabilità per i bot AI (20 pt), structured data/schema.org (25 pt), formato
            risposta diretta (25 pt), segnali E-E-A-T come autore e data (15 pt),
            scannabilità con liste/tabelle (15 pt).
            """)

        st.markdown("#### Audit AEO di una pagina")
        default_url = df_final['page'].iloc[0] if not df_final.empty and 'page' in df_final.columns else st.session_state.get('gsc_site_url', 'https://www.tuosito.it/')
        aeo_url_api = st.text_input("URL da analizzare", value=default_url, key="aeo_url_api")

        if st.button("🔍 Calcola AEO Score", key="aeo_score_api_btn"):
            with st.spinner("Scansione robots.txt e contenuto della pagina..."):
                result = audit_page_aeo(aeo_url_api)

            if result.get("error"):
                st.error(f"Impossibile completare l'audit: {result['error']}")
            else:
                score = result["score"]
                col_s1, col_s2 = st.columns([1, 2])
                with col_s1:
                    st.metric("AEO Score", f"{score}/100")
                with col_s2:
                    breakdown_df = pd.DataFrame(
                        [{"Categoria": k, "Punti": v} for k, v in result["breakdown"].items()]
                    )
                    fig_aeo = px.bar(breakdown_df, x="Punti", y="Categoria", orientation="h",
                                      range_x=[0, 25], title="Dettaglio punteggio")
                    st.plotly_chart(fig_aeo, use_container_width=True)

                st.markdown("#### 🎯 Raccomandazioni prioritarie")
                for rec in result["recommendations"]:
                    st.write(f"- {rec}")

        st.markdown("---")
        st.markdown("#### Traffico da AI Answer Engine")
        st.write("Isola le sessioni GA4 in arrivo da ChatGPT, Perplexity, Gemini, Copilot.")
        saved_property_id = st.session_state.get('ga4_property_id', '')
        saved_start = st.session_state.get('api_start_date', datetime.now() - timedelta(days=30))
        saved_end = st.session_state.get('api_end_date', datetime.now())
        col_t1, col_t2, col_t3 = st.columns(3)
        with col_t1:
            traffic_property_id = st.text_input("GA4 Property ID", value=saved_property_id, key="aeo_traffic_prop")
        with col_t2:
            traffic_start = st.date_input("Da", saved_start, key="aeo_traffic_start")
        with col_t3:
            traffic_end = st.date_input("A", saved_end, key="aeo_traffic_end")

        if st.button("📊 Analizza traffico AI", key="aeo_traffic_api_btn"):
            if not traffic_property_id:
                st.warning("Inserisci un GA4 Property ID valido.")
            else:
                with st.spinner("Estrazione sorgenti di traffico da GA4..."):
                    try:
                        df_sources = fetch_ga4_traffic_sources(
                            traffic_property_id,
                            traffic_start.strftime("%Y-%m-%d"),
                            traffic_end.strftime("%Y-%m-%d"),
                        )
                        df_ai, summary = classify_ai_referrals(df_sources)
                    except Exception as e:
                        st.error(f"Errore nel recupero dati GA4: {e}")
                        df_ai, summary = pd.DataFrame(), pd.DataFrame()

                if summary.empty:
                    st.info("Nessuna sessione rilevata da answer engine noti nel periodo selezionato.")
                else:
                    st.success(f"Trovate {int(df_ai['sessions'].sum())} sessioni da AI answer engine!")
                    fig_ref = px.bar(summary, x="ai_engine", y="sessioni", color="ai_engine",
                                      title="Sessioni per Answer Engine")
                    st.plotly_chart(fig_ref, use_container_width=True)
                    st.dataframe(summary, use_container_width=True)

else:
    st.sidebar.header("Carica i Dati")
    uploaded_query = st.sidebar.file_uploader("Carica Query.csv", type=['csv'])
    uploaded_pages = st.sidebar.file_uploader("Carica Pagine.csv", type=['csv'])
    uploaded_grafico = st.sidebar.file_uploader("Carica Grafico.csv", type=['csv'])
    uploaded_paesi = st.sidebar.file_uploader("Carica paesi.csv", type=['csv'])
    uploaded_dispositivi = st.sidebar.file_uploader("Carica dispositivi.csv", type=['csv'])


# 2. Logica: se l'utente carica i file, usa quelli. Se no, usa quelli di default (se esistono)
    if uploaded_query and uploaded_pages and uploaded_grafico and uploaded_paesi and uploaded_dispositivi:
        df = load_query(uploaded_query) # Nota: dobbiamo aggiornare load_query sotto
        df_pages = add_seo_score(load_pages(uploaded_pages))
        df_date = load_date(uploaded_grafico) 
        df_paesi = load_countries(uploaded_paesi)
        df_dev = load_devices(uploaded_dispositivi)
        st.success("Dati caricati correttamente!")
        total_pages = len(df_pages)
        healthy_pages = len(df_pages[df_pages['SEO_Score'] > 50])
        global_health = (healthy_pages / total_pages) * 100

        st.sidebar.metric("Salute Globale Sito", f"{global_health:.1f}%")
        # --- LOGICA DI BUSINESS ---
        def classify_keyword(row):
            if row['Posizione'] <= 3: return 'Campioni (Top 3)'
            elif row['Posizione'] <= 10: return 'Primi Posti'
            elif row['Posizione'] <= 20: return 'Quick Wins (2a Pagina)'
            else: return 'Long-tail / Da migliorare'

        df['Categoria'] = df.apply(classify_keyword, axis=1)
        df['Traffico_Potenziale'] = (df['Impressioni'] * 0.20).astype(int)
        df['Traffico_Mancante'] = (df['Traffico_Potenziale'] - df['Clic']).clip(lower=0)

        # --- LAYOUT DASHBOARD ---
        tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8, tab9, tab10, tab11, tab12 = st.tabs(["📊 Panoramica", "🎯 Strategia", "📈 Pagine", "⚖️ Salute SEO", "⏳ Trend", "📋 Piano d'Azione", "🌍 Analisi per Paese", "📱 Analisi per Dispositivo", "🛠 Technical SEO Audit", "🔗 Controllo Integrità & Sicurezza", "⚔️ Analisi Competitiva (Gap Analysis)", "🤖 AEO Readiness"])

        with tab1:
            col1, col2, col3 = st.columns(3)
            col1.metric("Totale Query", len(df))
            col2.metric("Posizione Media", f"{df['Posizione'].mean():.1f}")
            col3.metric("CTR Medio", f"{df['CTR'].mean():.2%}")
            
            fig = px.scatter(df, x="Posizione", y="Impressioni", size="Clic", color="Categoria",
                            hover_name="Query", title="Performance Keyword")
            st.plotly_chart(fig, use_container_width=True)
            insight = get_actionable_insight(df, "Panoramica")
            st.info(f"💡 **Analisi Strategica:** {insight}")

        with tab2:
            st.subheader("📋 Lista Priorità d'Azione (Quick Wins)")
            quick_wins = df[df['Categoria'] == 'Quick Wins (2a Pagina)'].sort_values('Traffico_Mancante', ascending=False)
            st.dataframe(quick_wins[['Query', 'Posizione', 'Impressioni', 'Traffico_Mancante']], use_container_width=True)
            st.subheader("📊 Analisi Difficoltà Keyword")
            df = calculate_keyword_difficulty(df)
            
            with st.expander("❓ Cosa significa la Difficoltà Keyword?"):
                st.write("""
                Il punteggio di **Difficoltà (0-100)** è un indice proprietario che stima quanto è complesso posizionarsi in prima pagina per una determinata query:
                
                *   **0-30 (Facile):** Poca competizione. Ottimo per siti nuovi o piccoli.
                *   **31-60 (Media):** Richiede contenuti di qualità e una strategia di backlink mirata.
                *   **61-100 (Difficile):** Parole chiave 'corpo' (es. "ristorante Roma"). Competizione altissima, serve autorità di dominio elevata.
                
                **Strategia:** Focalizzati sulle keyword con **Bassa Difficoltà e Alte Impressioni** per ottenere risultati rapidi.
                """)

            # Visualizziamo una tabella che mostra quali keyword sono "Easy Win" (Bassa Difficoltà, Alto Traffico)
            df_sorted = df.sort_values('Keyword_Difficulty')
            
            st.dataframe(
                df_sorted[['Query', 'Impressioni', 'Keyword_Difficulty']],
                column_config={
                    "Keyword_Difficulty": st.column_config.ProgressColumn(
                        "Difficoltà (0-100)",
                        format="%.0f",
                        min_value=0,
                        max_value=100,
                    ),
                },
                use_container_width=True
            )
            st.subheader("🤖 Analisi Intento di Ricerca (AI-Powered)")
            
            with st.expander("❓ Come funziona l'IA di analisi intenti?"):
                st.write("""
                Questa funzione utilizza modelli di Intelligenza Artificiale Generativa (LLM) per analizzare il **linguaggio naturale** delle tue parole chiave:
                
                *   **Informativa:** L'utente sta cercando risposte o guide (es. 'come fare pasta fresca'). Sono keyword ottime per il blog.
                *   **Transazionale:** L'utente ha il portafoglio in mano (es. 'prenota tavolo Roma'). Queste sono le tue priorità assolute per vendere.
                *   **Navigazionale:** L'utente cerca già il tuo brand specifico.
                
                **Perché lo facciamo?** Perché non tutti i clic valgono lo stesso. Puntare sulle keyword *Transazionali* significa aumentare direttamente le conversioni del tuo business.
                """)
            
            if st.button("🔍 Analizza Search Intent per le Quick Wins"):
                with st.spinner("L'IA sta analizzando l'intento delle keyword..."):
                    # Applichiamo la funzione solo alle Quick Wins
                    quick_wins = df[df['Categoria'] == 'Quick Wins (2a Pagina)'].head(10).copy()
                    quick_wins['Intent'] = quick_wins['Query'].apply(get_search_intent)
                    
                    st.write("### Keyword Classificate per Intento")
                    st.dataframe(quick_wins[['Query', 'Intent', 'Impressioni']])
            
                # Esempio grafico di distribuzione
                intent_counts = quick_wins['Intent'].value_counts().reset_index()
                fig_intent = px.pie(intent_counts, values='count', names='Intent', title="Distribuzione degli Intenti nelle Quick Wins")
                st.plotly_chart(fig_intent, use_container_width=True)
            st.subheader("🤖 Assistente Strategico SEO")
        
            # 1. Inizializza la cronologia della chat
            if "messages" not in st.session_state:
                st.session_state.messages = []

            # 2. Mostra i messaggi passati
            for message in st.session_state.messages:
                with st.chat_message(message["role"]):
                    st.markdown(message["content"])

            # 3. L'input dell'utente (è questo che "sblocca" l'IA, non un bottone automatico)
            if prompt := st.chat_input("Chiedi consiglio su una keyword (es: 'volpe pasini bistro')"):
                
                # Aggiungi il messaggio dell'utente alla cronologia
                st.session_state.messages.append({"role": "user", "content": prompt})
                with st.chat_message("user"):
                    st.markdown(prompt)

                # 4. Risposta dell'IA
                with st.chat_message("assistant"):
                    with st.spinner("L'IA sta analizzando..."):
                        # Qui richiami l'IA passando il prompt dell'utente
                        # Assicurati che generate_seo_suggestions prenda il prompt
                        response = generate_seo_suggestions(prompt, 0, 0) # Posizione e CTR di default
                        st.markdown(response)
                
                # Aggiungi la risposta alla cronologia
                st.session_state.messages.append({"role": "assistant", "content": response})
                
        with tab3:
            st.subheader("Audit Automatico delle Pagine")
            
            # Applichiamo la diagnosi
            df_pages['Stato'] = df_pages.apply(diagnose_page, axis=1)
            
            # Arrotondiamo per estetica
            df_pages['SEO_Score'] = df_pages['SEO_Score'].round(2)
            
            # Creiamo un selettore per filtrare per diagnosi
            diagnosi_selezionata = st.multiselect("Filtra per Stato:", df_pages['Stato'].unique())
            
            if diagnosi_selezionata:
                df_pages = df_pages[df_pages['Stato'].isin(diagnosi_selezionata)]
            
            st.dataframe(
                df_pages[['Pagina', 'Stato', 'SEO_Score', 'Posizione', 'Clic']],
                column_config={
                    "SEO_Score": st.column_config.ProgressColumn("Salute", format="%.2f", min_value=0, max_value=100),
                },
                use_container_width=True
            )
            st.subheader("🔗 Controllo Link Rotti (Broken Links)")
            target_url = st.text_input("Inserisci URL del sito da scansionare", "https://www.volpepasinibistroitaliano.it/")
            
            if st.button("Avvia Scansione"):
                with st.spinner("Scansionando il sito..."):
                    broken = check_broken_links(target_url)
                    if broken:
                        st.error(f"Trovati {len(broken)} link rotti!")
                        st.write(broken)
                    else:
                        st.success("Tutti i link funzionano correttamente!")

        with tab4:
            avg_score = df_pages['SEO_Score'].mean()
            st.metric("Salute SEO Globale", f"{avg_score:.1f}/100")
            if avg_score > 50: st.success("Il sito ha una buona salute SEO.")
            else: st.warning("Attenzione: Il sito necessita di ottimizzazione.")
            insight_seo = get_actionable_insight(df_pages, "Salute SEO")
            st.warning(f"🎯 **Consiglio per il cliente:** {insight_seo}")
            st.subheader("🛠 Technical SEO Audit & Crawl Budget")
        
            # 1. Analisi Profondità
            df_pages = analyze_crawl_efficiency(df_pages)
            
            # 2. Audit Diagnostico
            audit_df = perform_technical_audit(df_pages)
            
            # 3. Visualizzazione KPI
            col1, col2 = st.columns(2)
            deep_pages = df_pages[df_pages['Crawl_Depth'] > 3]
            col1.metric("Pagine scansionate", len(df_pages))
            col2.metric("Pagine a rischio 'profondità'", len(deep_pages))
            
            # 4. Tabella Audit
            st.write("### Dettaglio Audit Tecnico")
            show_only_issues = st.checkbox("Mostra solo pagine con criticità", key="audit_check")
            if show_only_issues:
                audit_df = audit_df[audit_df['Stato'] == "🚨"]
                
            st.dataframe(audit_df, use_container_width=True)
            
            st.info("💡 Una 'Crawl Depth' > 3 indica pagine difficili da raggiungere per i bot di Google.")
        with tab5:
            st.subheader("📈 Analisi Temporale")
            fig_date = px.line(df_date, x='Data', y='Clic', title="Andamento Clic nel Tempo", markers=True)
            st.plotly_chart(fig_date, use_container_width=True)
            st.dataframe(df_date.tail(7), use_container_width=True)
            st.subheader("🧪 Backtesting: Validazione del Modello")
        
            if st.button("Valida Modello (Backtest ultimi 30 giorni)"):
                mape, forecast = perform_backtest(df_date)
                
                # Mostriamo l'errore (più basso è, meglio è!)
                st.metric("Errore Medio (MAPE)", f"{mape:.2%}")
                
                if mape < 0.2:
                    st.success("Il modello è molto preciso!")
                else:
                    st.warning("Il modello ha margini di miglioramento.")
                    
                st.write("Confronto Previsione vs Reale:")
                # Grafico che confronta la previsione con il dato reale
                st.line_chart(forecast.set_index('ds')[['yhat']])
            st.subheader("🔮 Previsione Traffico (Prossimi 7 giorni)")
            
            if st.button("Genera Previsione IA"):
                with st.spinner("Addestramento modello in corso..."):
                    forecast = train_and_forecast(df_date)
                    
                    # Grafico
                    fig = px.line(forecast, x='ds', y='yhat', title="Previsione Clic futuri")
                    # Aggiungiamo l'area di incertezza (intervallo di confidenza)
                    fig.add_scatter(x=forecast['ds'], y=forecast['yhat_upper'], line=dict(width=0), showlegend=False)
                    fig.add_scatter(x=forecast['ds'], y=forecast['yhat_lower'], fill='tonexty', line=dict(width=0), showlegend=False)
                    
                    st.plotly_chart(fig, use_container_width=True)
                    st.success("Previsione completata con modello Prophet.")
            st.subheader("📉 Content Decay Alert")
        
            # Carichiamo due dataset (es. ultimo mese e mese prima)
            # Nota: L'utente dovrà caricare due file CSV distinti per questo confronto
            if st.checkbox("Analizza decadimento contenuti"):
                file_curr = st.file_uploader("CSV Periodo Recente", type=['csv'], key="curr")
                file_prev = st.file_uploader("CSV Periodo Precedente", type=['csv'], key="prev")
                
                if file_curr and file_prev:
                    df_curr = load_pages(file_curr)
                    df_prev = load_pages(file_prev)
                    
                    decay = analyze_content_decay(df_curr, df_prev)
                    
                    st.warning("🚨 Pagine in calo di traffico (>20%):")
                    st.dataframe(decay[['Pagina', 'Clic_curr', 'Clic_prev', 'Perc_Decay']])
        with tab6:
            st.subheader("📋 Piano d'Azione Prioritario")
            st.write("Segui questi step per incrementare il traffico organico del tuo sito:")
            
            # Calcolo logiche per il piano
            quick_wins = df[df['Categoria'] == 'Quick Wins (2a Pagina)']
            low_ctr = df[df['CTR'] < 0.015] # CTR sotto l'1.5%
            
            # 1. Priorità: Quick Wins
            if not quick_wins.empty:
                st.success("✅ 1. Ottimizzazione 'Quick Wins'")
                st.write(f"Hai **{len(quick_wins)} keyword** in 2a pagina. Ottimizza i meta-titoli di queste pagine per portarle in Top 10.")
                st.dataframe(quick_wins[['Query', 'Posizione', 'Impressioni']].head(5))
            
            # 2. Priorità: CTR Basso
            if not low_ctr.empty:
                st.warning("⚠️ 2. Miglioramento Copywriting (CTR Basso)")
                st.write("Le seguenti query hanno molte impressioni ma pochi clic. Riscrivi le meta-description per renderle più invitanti.")
                st.dataframe(low_ctr[['Query', 'CTR', 'Impressioni']].sort_values('Impressioni', ascending=False).head(5))
            
            # 3. Priorità: Focus Pagine
            st.info("🚀 3. Content Audit")
            st.write("Analizza le pagine con il SEO Score più basso (visibili nella Tab 3) e aggiorna i contenuti con informazioni più recenti o approfondite.")

            # Bottone di export per il cliente
            st.subheader("📥 Esporta Report Strategico")
        
            # Generiamo il report
            report_text = generate_seo_report(df)
            
            # Mostriamo un'anteprima
            st.text_area("Anteprima Report", value=report_text, height=300)
            
            # Bottone di download
            st.download_button(
                label="Scarica Report come .txt",
                data=report_text,
                file_name="Report_SEO_Strategico.txt",
                mime="text/plain"
            )
            # Calcoli per il tuo template
            tot_pagine = len(df_pages)
            problemi_rilevati = len(df_pages[df_pages['SEO_Score'] < 70]) # Esempio soglia
            critiche_alte = len(df_pages[df_pages['SEO_Score'] < 30])
            punteggio_seo = round(df_pages['SEO_Score'].mean(), 1)
            
            # Mostra i numeri da copiare
            st.info("Copia questi valori nel tuo template grafico:")
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("Pagine Analizzate", tot_pagine)
            col2.metric("Problemi Rilevati", problemi_rilevati)
            col3.metric("Criticità Alte", critiche_alte)
            col4.metric("Punteggio SEO", f"{punteggio_seo}/100")
            st.write("---")
            st.write("### 🚨 Top 5 Problemi da inserire nel Report:")
            
            # 1. Reset dell'indice per avere numeri da 1 a 5 puliti
            top_problemi = df_pages.sort_values('SEO_Score').head(5).reset_index(drop=True)
            
            # 2. Ciclo for migliorato
            for i, row in top_problemi.iterrows():
                # Usiamo st.markdown per rendere il link cliccabile se è un URL
                st.markdown(f"**{i+1}.** [{row['Pagina'][:40]}...]({row['Pagina']}) - Score: **{row['SEO_Score']}**")
        with tab7: # Analisi Geografica
            st.subheader("🌍 Analisi per Paese")

            # --- FILTRO DINAMICO ---
            min_clic = st.sidebar.slider("Numero minimo di clic per mostrare il paese", 
                                        min_value=0, 
                                        max_value=int(df_paesi['Clic'].max()), 
                                        value=10) # Default a 10 clic
            
            # Filtriamo il dataframe
            df_filtered = df_paesi[df_paesi['Clic'] >= min_clic]
            
            # Grafico pulito
            fig_p = px.bar(df_filtered.sort_values('Clic', ascending=True), 
                        x='Clic', y='Paese', orientation='h', 
                        title=f"Paesi con almeno {min_clic} clic",
                        color='Clic', 
                        color_continuous_scale='Blues')
            st.plotly_chart(fig_p, use_container_width=True)
            st.write(f"Stai visualizzando {len(df_filtered)} paesi su un totale di {len(df_paesi)}. I paesi con meno di {min_clic} clic sono stati esclusi dall'analisi.")
        with tab8: # Analisi Dispositivi
            st.subheader("📱 Analisi per Dispositivo")
            
            # Grafico a torta per vedere il mix di traffico
            fig_d = px.pie(df_dev, names='Dispositivo', values='Clic', title="Distribuzione Clic per Dispositivo")
            st.plotly_chart(fig_d, use_container_width=True)
            
            st.dataframe(df_dev, use_container_width=True)
        with tab9: # Tab Salute SEO / Audit
            st.subheader("🛠 Technical SEO Audit")
            
            audit_df = perform_technical_audit(df_pages)
            
            # Filtro rapido per vedere solo le pagine problematiche
            show_only_issues = st.checkbox("Mostra solo pagine con criticità")
            if show_only_issues:
                audit_df = audit_df[audit_df['Stato'] == "🚨"]
                
            st.table(audit_df)
            
            st.info("💡 Questo Audit scansiona le pagine identificando dove il motore di ricerca incontra difficoltà.")
        with tab10:
            st.subheader("🔗 Controllo Integrità & Sicurezza")
            target_url = st.text_input("Inserisci URL del sito", "https://www.volpepasinibistroitaliano.it/")
            
            if st.button("Avvia Audit Tecnico"):
                with st.spinner("Analisi in corso..."):
                    # Controllo SSL
                    status_ssl = check_ssl(target_url)
                    st.metric("Stato Sicurezza", status_ssl)
                    
                    # Controllo Broken Links
                    broken = check_broken_links(target_url)
                    if broken:
                        st.error(f"Trovati {len(broken)} link rotti!")
                        st.write(broken)
                    else:
                        st.success("Tutti i link funzionano!")
        with tab11: # Tab Analisi Competitiva
            st.subheader("⚔️ Analisi Competitiva (Gap Analysis)")
            # --- ESPANDER STRATEGICO ---
            with st.expander("💡 Perché l'analisi competitiva è cruciale?"):
                st.write("""
                Il confronto con i competitor non serve a copiare, ma a **trovare il tuo spazio di mercato**. 
                Attraverso questa analisi identifichiamo il **Content Gap**:
                1. **Keyword Opportunità:** Parole chiave per cui il concorrente è posizionato ma tu no.
                2. **Validazione di Mercato:** Se un concorrente riceve traffico su una specifica query, significa che c'è una domanda reale che puoi intercettare.
                3. **Focus Strategico:** Non sprecare tempo su parole chiave troppo difficili (High Difficulty), concentrati su quelle dove il concorrente ha una posizione debole (11-20).
                """)
            #Per testare la tua dashboard e mostrare che funziona, devi simulare il comportamento.
            #Prendi un sito concorrente.
            #Vai su uno strumento di analisi SEO gratuito (es. la versione free di Ubersuggest, Ahrefs Free Keyword Generator o SEOZoom).
            #Inserisci il dominio del concorrente.
            #Questi siti ti daranno una lista di "Top Keyword" del concorrente. Esporta quella lista in CSV.
            #Ora hai il file Competitor.csv da caricare nella tua dashboard
            col_c1, col_c2 = st.columns(2)
            with col_c1:
                file_cliente = st.file_uploader("Carica CSV Cliente", type=['csv'], key="cliente")
            with col_c2:
                file_comp = st.file_uploader("Carica CSV Competitor", type=['csv'], key="competitor")
                
            if file_cliente and file_comp:
                df_c = load_query(file_cliente)
                df_comp = load_query(file_comp)
                
                # Gap Analysis
                gap = get_competitor_gap(df_c, df_comp)
                
                st.write("### 🚩 Keyword dove il concorrente ti sta superando:")
                st.dataframe(gap[['Query', 'Impressioni', 'Posizione']], use_container_width=True)
                
                st.info("💡 Consiglio: Crea contenuti specifici per queste keyword. Sono il motivo per cui il tuo concorrente sta catturando traffico che potrebbe essere tuo.")

        with tab12:  # AEO Readiness
            st.subheader("🤖 AEO Readiness — Sei pronto per ChatGPT, Perplexity e le AI Overview?")

            with st.expander("❓ Cos'è l'AEO e perché la dashboard la misura separatamente dalla SEO"):
                st.write("""
                La **SEO classica** ottimizza per un algoritmo che restituisce una lista di link.
                L'**AEO (Answer Engine Optimization)** ottimizza per un sistema che *legge* il tuo
                contenuto e ne estrae una risposta diretta (ChatGPT, Perplexity, Copilot, Gemini,
                AI Overview di Google). Non basta più rankare: bisogna essere la fonte che il
                modello sceglie di citare.

                Il punteggio che vedi sotto pesa 5 categorie di segnali:
                - **Crawlabilità AI (20 pt)**: se il tuo `robots.txt` blocca bot come GPTBot o
                  ClaudeBot, la pagina è invisibile a quell'ecosistema, punto. È un requisito binario.
                - **Structured Data / Schema.org (25 pt)**: markup FAQPage/HowTo/Article che
                  disambiguano il contenuto per la macchina.
                - **Formato "Risposta Diretta" (25 pt)**: header a domanda seguiti da una risposta
                  autosufficiente di 40-60 parole, il pattern più facile da estrarre.
                - **Segnali E-E-A-T (15 pt)**: autore e data, usati per valutare l'affidabilità della fonte.
                - **Scannabilità (15 pt)**: liste e tabelle, più facili da segmentare per un LLM.
                """)

            st.markdown("#### 1. Audit AEO di una pagina")
            aeo_url = st.text_input(
                "URL da analizzare",
                value=df_pages['Pagina'].iloc[0] if not df_pages.empty else "https://www.tuosito.it/",
                key="aeo_url_input"
            )

            if st.button("🔍 Calcola AEO Score"):
                with st.spinner("Scansione robots.txt e contenuto della pagina in corso..."):
                    result = audit_page_aeo(aeo_url)

                if result.get("error"):
                    st.error(f"Impossibile completare l'audit: {result['error']}")
                else:
                    score = result["score"]
                    col_s1, col_s2 = st.columns([1, 2])
                    with col_s1:
                        st.metric("AEO Score", f"{score}/100")
                        if score >= 75:
                            st.success("Ottima leggibilità per gli answer engine.")
                        elif score >= 45:
                            st.warning("Base discreta, ma ci sono margini chiari di miglioramento.")
                        else:
                            st.error("Bassa probabilità di essere citato dagli answer engine.")
                    with col_s2:
                        breakdown_df = pd.DataFrame(
                            [{"Categoria": k, "Punti": v} for k, v in result["breakdown"].items()]
                        )
                        fig_aeo = px.bar(breakdown_df, x="Punti", y="Categoria", orientation="h",
                                          range_x=[0, 25], title="Dettaglio punteggio per categoria")
                        st.plotly_chart(fig_aeo, use_container_width=True)

                    st.markdown("#### 🎯 Raccomandazioni prioritarie")
                    if result["recommendations"]:
                        for rec in result["recommendations"]:
                            st.write(f"- {rec}")
                    else:
                        st.success("Nessuna criticità rilevata su questa pagina.")

                    with st.expander("🔬 Segnali grezzi rilevati (debug/dettaglio)"):
                        st.json({
                            "schema_types": result["raw_signals"].get("schema_types"),
                            "question_headers": result["raw_signals"].get("question_headers"),
                            "has_author": result["raw_signals"].get("has_author"),
                            "has_date": result["raw_signals"].get("has_date"),
                            "bot_bloccati": result["crawl_signals"].get("blocked_bots"),
                        })

                    st.session_state["aeo_last_url"] = aeo_url

            st.markdown("---")
            st.markdown("#### 2. Genera FAQ ottimizzate per AEO (con AI)")
            st.write(
                "Genera coppie domanda/risposta in formato 'risposta diretta', pronte per "
                "essere pubblicate e marcate con schema FAQPage."
            )
            col_f1, col_f2 = st.columns(2)
            with col_f1:
                aeo_topic = st.text_input("Argomento della pagina", key="aeo_topic")
            with col_f2:
                aeo_keywords = st.text_input("Keyword target (opzionale)", key="aeo_kw")

            if st.button("✨ Genera FAQ con AI"):
                if not aeo_topic:
                    st.warning("Inserisci l'argomento della pagina.")
                else:
                    with st.spinner("Generazione FAQ in corso..."):
                        faq_text = generate_aeo_faq(aeo_topic, aeo_keywords)
                    st.session_state["aeo_faq_text"] = faq_text
                    st.markdown(faq_text)

            if st.session_state.get("aeo_faq_text"):
                if st.button("📐 Converti in schema JSON-LD (FAQPage)"):
                    qa_pairs = parse_qa_text(st.session_state["aeo_faq_text"])
                    if not qa_pairs:
                        st.error("Non sono riuscito a interpretare le coppie D/R generate. Riprova la generazione.")
                    else:
                        schema_code = generate_faq_schema(qa_pairs)
                        st.code(f'<script type="application/ld+json">\n{schema_code}\n</script>', language="html")
                        st.download_button(
                            "📥 Scarica schema.html",
                            data=f'<script type="application/ld+json">\n{schema_code}\n</script>',
                            file_name="faq_schema.html",
                            mime="text/html",
                        )

            st.markdown("---")
            st.markdown("#### 3. Traffico da AI Answer Engine (richiede GA4)")
            st.write(
                "Isola le sessioni che arrivano da chatgpt.com, perplexity.ai, gemini.google.com, "
                "copilot.microsoft.com — il segnale più diretto che il tuo contenuto viene già "
                "citato dagli answer engine. Richiede un GA4 Property ID valido con le stesse "
                "credenziali configurate per la connessione API."
            )
            col_g1, col_g2, col_g3 = st.columns(3)
            with col_g1:
                aeo_property_id = st.text_input("GA4 Property ID", key="aeo_property_id")
            with col_g2:
                aeo_start = st.date_input("Da", datetime.now() - timedelta(days=30), key="aeo_start")
            with col_g3:
                aeo_end = st.date_input("A", datetime.now(), key="aeo_end")

            if st.button("📊 Analizza traffico da ChatGPT/Perplexity/Gemini/Copilot"):
                if not aeo_property_id:
                    st.warning("Inserisci un GA4 Property ID valido.")
                else:
                    with st.spinner("Estrazione sorgenti di traffico da GA4..."):
                        try:
                            df_sources = fetch_ga4_traffic_sources(
                                aeo_property_id,
                                aeo_start.strftime("%Y-%m-%d"),
                                aeo_end.strftime("%Y-%m-%d"),
                            )
                            df_ai, summary = classify_ai_referrals(df_sources)
                        except Exception as e:
                            st.error(f"Errore nel recupero dati GA4: {e}")
                            df_ai, summary = pd.DataFrame(), pd.DataFrame()

                    if summary.empty:
                        st.info("Nessuna sessione rilevata da answer engine noti nel periodo selezionato.")
                    else:
                        st.success(f"Trovate {int(df_ai['sessions'].sum())} sessioni da AI answer engine!")
                        fig_ref = px.bar(summary, x="ai_engine", y="sessioni", color="ai_engine",
                                          title="Sessioni per Answer Engine")
                        st.plotly_chart(fig_ref, use_container_width=True)
                        st.dataframe(summary, use_container_width=True)
                        st.write("**Pagine di atterraggio più citate dagli answer engine:**")
                        st.dataframe(
                            df_ai.groupby("landing_page").agg(sessioni=("sessions", "sum")).reset_index()
                            .sort_values("sessioni", ascending=False).head(10),
                            use_container_width=True,
                        )

    else:
        st.info("👋 Carica i file richiesti nella barra laterale per iniziare l'analisi.")
        st.stop() # Ferma l'esecuzione finché non ci sono i file

    with st.sidebar:
        st.markdown("---")
        st.write("### Hai bisogno di una consulenza?")
        st.write("Se vuoi che ti aiuti a implementare queste strategie, contattami:")
        st.button("Invia Email a Davide") # Oppure metti il tuo link LinkedIn
