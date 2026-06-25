# SEO Performance Analyst

## 🎯 Obiettivo
Analisi multidimensionale delle performance organiche di un sito web tramite dati Google Search Console. L'obiettivo è trasformare dati grezzi in insight strategici, identificando opportunità di crescita e inefficienze di posizionamento.

## 🛠 Tech Stack
- **Data Analysis:** Python (Pandas, NumPy)
- **Data Visualization:** Plotly, Streamlit
- **Pipeline:** ETL (Extract, Transform, Load) da file CSV a dashboard interattiva.

 Pipeline & Roadmap di Sviluppo
🤖 Automazione (CI/CD Pipeline)
Il sistema è progettato per garantire continuità operativa attraverso processi automatizzati:
Data Ingestion Automatizzata: Implementazione di workflow tramite GitHub Actions per l'aggiornamento schedulato dei dati.
Integrazione Continua (CI): Ogni modifica al codice viene validata automaticamente, garantendo l'integrità dell'analisi.
🔮 Roadmap & Evoluzioni Future

SaaS Self-Service: Implementazione di un modulo di caricamento file tramite interfaccia web, permettendo agli utenti di analizzare i propri dataset in tempo reale.

Generative SEO Assistant: Integrazione di modelli di linguaggio (LLM) per generare suggerimenti di copywriting ottimizzati direttamente dalla dashboard.

Data Fusion Avanzata: Espansione del modello di analisi incrociando i dati di Query.csv con Pagine.csv e Dispositivi.csv per una visione a 360° dell'utente.

Containerizzazione: Packaging dell'intera applicazione tramite Docker per facilitare il deploy in ambienti cloud scalabili.

## 📂 Struttura Dati
Il progetto analizza principalmente il file `Query.csv` estratto da Google Search Console, focalizzandosi su:
- **Impressioni:** Visibilità del sito.
- **Clic:** Engagement degli utenti.
- **Posizione:** Ranking organico.
