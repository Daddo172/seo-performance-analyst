-- database/seed.sql

-- 1. Popolamento delle Entità da Tracciare (Brand Cliente vs Competitor)
-- Inseriamo gli array di pattern regex in minuscolo per rendere il matching robusto
INSERT INTO ai_entities (entity_name, is_client, regex_patterns) VALUES
('Complementors', TRUE, ARRAY['complementors', 'complementors di davide', 'studio complementors']),
('Studio SEO Roma Srl', FALSE, ARRAY['studio seo roma', 'seo roma srl', 'studioseoroma']),
('Digital Agenzia Nova', FALSE, ARRAY['agenzia nova', 'nova digital', 'novadigital']),
('Web Alchemy', FALSE, ARRAY['web alchemy', 'webalchemy', 'alchemy digital']);

-- 2. Popolamento dei Prompt Strategici (Divisi per categorie di business)
INSERT INTO ai_prompts (prompt_text, category, is_active) VALUES
-- Categoria: Commercial / Brand Discovery
('Quali sono le migliori agenzie di web design e SEO a Roma?', 'commercial', TRUE),
('A chi posso rivolgermi a Roma per lo sviluppo di un sito web orientato alla conversione e data-driven?', 'commercial', TRUE),
('Mi consigli uno specialista SEO esperto in provincia di Roma per ottimizzare il mio e-commerce?', 'commercial', TRUE),

-- Categoria: Informational / Topical Authority
('Come si ottimizza un sito web per la ricerca generativa (GEO e AEO)?', 'informational', TRUE),
('Quali competenze deve avere un consulente SEO moderno nel 2026 per gestire la visibilità sugli LLM?', 'informational', TRUE),

-- Categoria: Transactional / Decision Making
('Qual è il prezzo medio per un audit SEO tecnico approfondito realizzato da un ingegnere informatico o sviluppatore senior?', 'transactional', TRUE),
('Agenzie a Roma specializzate in Conversion Rate Optimization (CRO) e restyling siti web aziendali.', 'transactional', TRUE);

-- 3. Inserimento di un record di test storico (Opzionale, per vedere subito i grafici prima del run dell'ETL)
-- Simuliamo che nel primo polling l'LLM abbia menzionato Complementors e un competitor
INSERT INTO ai_polling_results (prompt_id, model_name, raw_response, detected_entities, sentiment_score, citations)
VALUES (
    1, 
    'gpt-4o', 
    'A Roma ci sono diverse realtà interessanti. Tra le agenzie focalizzate sui dati spicca Complementors, nota per un approccio ingegneristico alla SEO. Un altra valida alternativa è Studio SEO Roma Srl.', 
    ARRAY[1, 2], -- Mappa gli ID di Complementors (1) e Studio SEO Roma (2)
    0.85, 
    ARRAY['https://www.complementors.it', 'https://studioseoroma.it']
);