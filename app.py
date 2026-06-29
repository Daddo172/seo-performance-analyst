import streamlit as st
import pandas as pd
import plotly.express as px
from src.ai_seo import get_search_intent,generate_seo_suggestions
from src.processor import get_competitor_gap ,analyze_content_decay,calculate_keyword_difficulty,perform_technical_audit, analyze_crawl_efficiency ,perform_technical_audit,add_seo_score, generate_seo_report, diagnose_page, get_actionable_insight , load_query, load_pages, load_date , load_devices , load_countries
from src.broken_links import check_broken_links
from src.technical_audit import check_ssl

# Configurazione Pagina
st.set_page_config(page_title="SEO Strategy Dashboard", layout="wide")
st.title("🚀 SEO Performance Analyzer")
st.markdown("Trasforma i dati di Search Console in strategie di crescita.")

# 1. Box di caricamento dinamico
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
    tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8, tab9,tab10 , tab11 = st.tabs(["📊 Panoramica", "🎯 Strategia", "📈 Pagine", "⚖️ Salute SEO", "⏳ Trend", "📋 Piano d'Azione","🌍 Analisi per Paese" , "📱 Analisi per Dispositivo","🛠 Technical SEO Audit","🔗 Controllo Integrità & Sicurezza","⚔️ Analisi Competitiva (Gap Analysis)"])

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



else:
    st.info("👋 Carica i file richiesti nella barra laterale per iniziare l'analisi.")
    st.stop() # Ferma l'esecuzione finché non ci sono i file

with st.sidebar:
    st.markdown("---")
    st.write("### Hai bisogno di una consulenza?")
    st.write("Se vuoi che ti aiuti a implementare queste strategie, contattami:")
    st.button("Invia Email a Davide") # Oppure metti il tuo link LinkedIn
