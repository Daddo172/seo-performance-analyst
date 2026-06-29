🚀 SEO Performance Analyzer: End-to-End Suite
🎯 Panoramica del Progetto
Questo progetto è una suite completa di Data Engineering, Analytics e AI sviluppata per trasformare i dati grezzi di Google Search Console in una strategia SEO professionale. L'applicazione non si limita a visualizzare grafici, ma funge da vero consulente virtuale, identificando opportunità di crescita e ottimizzando i contenuti tramite Intelligenza Artificiale.
⚙️ Architettura del Sistema
Il sistema è costruito attorno a una pipeline modulare:
Data Ingestion & Cleaning (processor.py): Modulo dedicato alla pulizia dati, normalizzazione metrica (CTR/Posizione) e integrazione multi-file.
Persistence Layer: Utilizzo di SQLAlchemy e SQLite per la gestione centralizzata dei dati (Master Data Structure).
Intelligence Engine (ai_seo.py): Integrazione delle API di Google Gemini (LLM) per la classificazione dell'intento di ricerca e la generazione di copy ottimizzato.
Dashboarding (app.py): Interfaccia web interattiva realizzata con Streamlit e Plotly per il monitoraggio in tempo reale.
🛠 Funzionalità Implementate
Multi-File Processing: Supporto per il caricamento dinamico e l'unione di file Query, Pagine, Date e Competitor.
Diagnostic Audit: Calcolo automatico di un SEO Score sintetico per la valutazione della salute delle pagine.
Strategia SEO: Analisi dei "Quick Wins" (keyword ad alto potenziale in seconda pagina) con calcolo del traffico mancante.
Search Intent AI: Classificazione automatizzata delle keyword in Informativa, Transazionale o Navigazionale.
Crawl Efficiency: Modulo di monitoraggio della struttura dei link interni e controllo dell'integrità (Broken Links / HTTPS).
Automazione: Pipeline di CI/CD tramite GitHub Actions per l'integrazione e il deployment continuo.
📈 Roadmap & Sviluppi Futuri

Pipeline di Automazione: Pipeline automatizzata su GitHub Actions per il workflow di aggiornamento.

Data Fusion: Integrazione file per analisi segmentata (Device/Paesi).

Predizione: Implementazione di modelli di Machine Learning per la previsione del traffico futuro.

SaaS Deployment: Espansione del tool per permettere l'analisi in modalità multi-utente in cloud.
💻 Tech Stack
Languages: Python
Libraries: Streamlit, Pandas, Plotly, SQLAlchemy, Google GenAI, BeautifulSoup.
Cloud: Streamlit Cloud, GitHub Actions.
