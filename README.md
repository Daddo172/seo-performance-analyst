# 🚀 AI SEO & AEO Audit Dashboard

Dashboard interattiva sviluppata in **Streamlit** per il monitoraggio, l'analisi e l'ottimizzazione di siti web, progettata sia per i motori di ricerca tradizionali (SEO) che per i nuovi motori di risposta basati su Intelligenza Artificiale (AEO / GEO).

L'applicazione unisce i dati quantitativi di traffico alla diagnostica qualitativa sulla struttura delle pagine, offrendo suggerimenti di riscrittura automatizzati tramite intelligenza artificiale.

---

## 🛠️ Funzionalità Attuali

### 1. Data Ingestion & Monitoraggio
*   **GA4 AI Traffic Tracker:** Segmentazione automatica e filtraggio del traffico referral proveniente esclusivamente da Answer Engines (`chatgpt.com`, `perplexity.ai`, `gemini.google.com`, `copilot.microsoft.com`).
*   **GSC Performance Analyzer:** Estrazione delle metriche chiave di posizionamento (Keyword, Impression, Clic) con sanitizzazione e controllo del CTR per identificare le pagine con potenziale inespresso.

### 2. Diagnostica e Audit Tecnico (`src/aeo.py`)
*   **AI Crawlability Check:** Scansione dinamica del file `robots.txt` del dominio per verificare lo stato dei principali crawler di intelligenza artificiale (`GPTBot`, `Claude-Web`, `PerplexityBot`, `Google-Extended`).
*   **AEO Readiness Score:** Algoritmo proprietario che genera un punteggio da 0 a 100 pesato sulla presenza di segnali E-E-A-T, dati strutturati (`FAQPage`), scannabilità del testo (liste/tabelle) e frammenti di testo ottimizzati per il recupero semantico.

### 3. Ottimizzazione On-Page (AI Generative Engine)
*   **SEO Optimizer:** Generazione guidata di tag Title e Meta Description ottimizzati per incrementare drasticamente il CTR nei risultati organici.
*   **AEO FAQ Generator:** Creazione automatica di risposte brevi in stile conversazionale e del relativo blocco di markup `JSON-LD` pronto da copiare nel codice del sito.

---

## 🔮 Sviluppi Futuri & Roadmap

Sulla base dei più recenti studi accademici e di settore (tra cui il paper di riferimento *"GEO: Generative Engine Optimization"*), sono previste le seguenti estensioni del core applicativo:

### 1. Ottimizzazione Avanzata GEO & RAG
*   **Calibrazione Text-Length:** Implementazione di un analizzatore di testo per verificare se i blocchi informativi si attestano nella "zona d'oro" dei sistemi RAG (~130-170 parole), massimizzando le probabilità di citazione.
*   **Analisi della Densità Semantica (Entity Density):** Evoluzione del motore di crawling verso l'estrazione e la mappatura di entità semantiche correlate rispetto alla vecchia ripetizione delle singole keyword.

### 2. Strutturazione del Contenuto e Segnali di Autorevolezza
*   **Rilevamento del Pattern Domanda/Risposta:** Parsing euristico avanzato per premiare i testi strutturati con intestazioni (`H2`/`H3`) poste come domande reali dell'utente e seguite immediatamente da frasi definitorie dirette (es. *"X è..."*).
*   **Verifica E-E-A-T Estesa:** Implementazione di controlli automatizzati sulla presenza di metadati autore, date di ultimo aggiornamento del contenuto e citazioni a fonti esterne autorevoli.

### 3. Sandbox Sperimentale e Misurazione (Case Studies Tracker)
*   **Diario dei Test A/B AEO:** Sviluppo di un database locale (o tab dedicata) per registrare gli esperimenti sul campo: tracciamento dell'URL, tattica applicata, data della modifica e check-point dopo alcune settimane per misurare la variazione delle citazioni reali.
*   **AI Share of Voice Monitor:** Cruscotto di tracciamento per archiviare lo storico del posizionamento del brand all'interno dei motori generativi durante i test manuali su prompt specifici.

---

## 📦 Installazione e Avvio Rapido

1. **Clona la repository** ed entra nella cartella del progetto:
   ```bash
   git clone <url-repository>
   cd seo-aeo-dashboard
