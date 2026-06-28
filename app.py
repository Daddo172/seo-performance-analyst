import streamlit as st
import pandas as pd
import plotly.express as px
from src.ai_seo import generate_seo_suggestions
from src.processor import add_seo_score, generate_seo_report, diagnose_page, get_actionable_insight , load_query, load_pages, load_date

# Configurazione Pagina
st.set_page_config(page_title="SEO Strategy Dashboard", layout="wide")
st.title("🚀 SEO Performance Analyzer")
st.markdown("Trasforma i dati di Search Console in strategie di crescita.")

# 1. Box di caricamento dinamico
st.sidebar.header("Carica i Dati")
uploaded_query = st.sidebar.file_uploader("Carica Query.csv", type=['csv'])
uploaded_pages = st.sidebar.file_uploader("Carica Pagine.csv", type=['csv'])
uploaded_grafico = st.sidebar.file_uploader("Carica Grafico.csv", type=['csv'])


# 2. Logica: se l'utente carica i file, usa quelli. Se no, usa quelli di default (se esistono)
if uploaded_query and uploaded_pages and uploaded_grafico:
    df = load_query(uploaded_query) # Nota: dobbiamo aggiornare load_query sotto
    df_pages = add_seo_score(load_pages(uploaded_pages))
    df_date = load_date(uploaded_grafico) 
    st.success("Dati caricati correttamente!")

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
    tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8 = st.tabs(["📊 Panoramica", "🎯 Strategia", "📈 Pagine", "⚖️ Salute SEO", "⏳ Trend", "📋 Piano d'Azione","🌍 Analisi per Paese" , "📱 Analisi per Dispositivo"])

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
        st.subheader("🤖 Assistente Strategico SEO")
    
        # 1. Inizializziamo lo stato della chat se non esiste
        if "messages" not in st.session_state:
            st.session_state.messages = []

        # 2. Mostriamo i messaggi passati
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
    
        # 3. Input dell'utente
        if prompt := st.chat_input("Chiedi all'IA un consiglio su una keyword..."):
            # Mostriamo il messaggio dell'utente
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)

        # 4. Risposta dell'IA
        with st.chat_message("assistant"):
            with st.spinner("Sto elaborando..."):
                # Qui richiamiamo la funzione che abbiamo creato
                response = generate_seo_suggestions(prompt, posizione=10, ctr=0.02) 
                st.markdown(response)
        
        # Salviamo la risposta
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

    with tab4:
        avg_score = df_pages['SEO_Score'].mean()
        st.metric("Salute SEO Globale", f"{avg_score:.1f}/100")
        if avg_score > 50: st.success("Il sito ha una buona salute SEO.")
        else: st.warning("Attenzione: Il sito necessita di ottimizzazione.")
        insight_seo = get_actionable_insight(df_pages, "Salute SEO")
        st.warning(f"🎯 **Consiglio per il cliente:** {insight_seo}")

    with tab5:
        st.subheader("📈 Analisi Temporale")
        fig_date = px.line(df_date, x='Data', y='Clic', title="Andamento Clic nel Tempo", markers=True)
        st.plotly_chart(fig_date, use_container_width=True)
        st.dataframe(df_date.tail(7), use_container_width=True)

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
    with tab7: # Analisi Geografica
        st.subheader("🌍 Analisi per Paese")
        df_paesi = load_countries(uploaded_paesi) # Aggiungi l'uploader nella sidebar!
        
        # Grafico a barre orizzontali (più leggibile per i nomi dei paesi)
        fig_p = px.bar(df_paesi.sort_values('Clic', ascending=True), 
                    x='Clic', y='Paese', orientation='h', title="Clic per Paese")
        st.plotly_chart(fig_p, use_container_width=True)

    with tab8: # Analisi Dispositivi
        st.subheader("📱 Analisi per Dispositivo")
        df_dev = load_devices(uploaded_dispositivi)
        
        # Grafico a torta per vedere il mix di traffico
        fig_d = px.pie(df_dev, names='Dispositivo', values='Clic', title="Distribuzione Clic per Dispositivo")
        st.plotly_chart(fig_d, use_container_width=True)
        
        st.dataframe(df_dev, use_container_width=True)
else:
    st.info("👋 Carica i file richiesti nella barra laterale per iniziare l'analisi.")
    st.stop() # Ferma l'esecuzione finché non ci sono i file

with st.sidebar:
    st.markdown("---")
    st.write("### Hai bisogno di una consulenza?")
    st.write("Se vuoi che ti aiuti a implementare queste strategie, contattami:")
    st.button("Invia Email a Davide") # Oppure metti il tuo link LinkedIn
