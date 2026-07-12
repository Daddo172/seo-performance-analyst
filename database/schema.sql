-- Estensione del database per il modulo GEO/AEO

-- Tabella dei prompt target
CREATE TABLE IF NOT EXISTS ai_prompts (
    prompt_id SERIAL PRIMARY KEY,
    prompt_text TEXT NOT NULL UNIQUE,
    category VARCHAR(50) DEFAULT 'informational', -- informational, commercial, transactional
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabella delle entità tracciate (il brand del cliente e i competitor principali)
CREATE TABLE IF NOT EXISTS ai_entities (
    entity_id SERIAL PRIMARY KEY,
    entity_name VARCHAR(100) NOT NULL UNIQUE,
    is_client BOOLEAN DEFAULT FALSE,
    regex_patterns TEXT[] NOT NULL -- Pattern per il matching (es. {'complementors', 'studio complementors'})
);

-- Tabella storica delle interrogazioni (Polling Data)
CREATE TABLE IF NOT EXISTS ai_polling_results (
    result_id SERIAL PRIMARY KEY,
    prompt_id INT REFERENCES ai_prompts(prompt_id) ON DELETE CASCADE,
    model_name VARCHAR(50) NOT NULL, -- gpt-4o, claude-3-5-sonnet, etc.
    raw_response TEXT NOT NULL,
    detected_entities INT[], -- Array di entity_id trovati
    sentiment_score NUMERIC(3,2) DEFAULT 0.00, -- Range -1.00 a 1.00
    citations TEXT[], -- Array di URL citati come fonti
    polled_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);