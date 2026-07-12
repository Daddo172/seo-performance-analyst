import os
import re
import json
import psycopg2
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

class AIEngineTracker:
    def __init__(self):
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.conn = psycopg2.connect(os.getenv("DATABASE_URL"))
        self.cur = self.conn.cursor()

    def fetch_active_prompts(self):
        self.cur.execute("SELECT prompt_id, prompt_text FROM ai_prompts WHERE is_active = TRUE;")
        return self.cur.fetchall()

    def fetch_entities(self):
        self.cur.execute("SELECT entity_id, entity_name, regex_patterns FROM ai_entities;")
        return self.cur.fetchall()

    def analyze_sentiment_and_citations(self, text, brand_name):
        """
        Sfrutta un modello economico (gpt-4o-mini) per estrarre in modo deterministico 
        il sentiment e verificare le citazioni formattate in JSON.
        """
        system_prompt = (
            "Sei un analista dati SEO esperto. Analizza il testo fornito dall'utente e restituisci "
            "esclusivamente un oggetto JSON con le seguenti chiavi:\n"
            f"- 'sentiment': un float tra -1.00 e 1.00 che indica l'attitudine del testo verso il brand '{brand_name}'.\n"
            "- 'urls': una lista di tutti gli URL/link espliciti citati nel testo.\n"
            "Non aggiungere introduzioni o formattazione markdown al di fuori del puro JSON."
        )
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": text}
                ],
                temperature=0.0,
                response_format={"type": "json_object"}
            )
            data = json.loads(response.choices[0].message.content)
            return data.get("sentiment", 0.0), data.get("urls", [])
        except Exception:
            # Fallback in caso di errore di parsing o API
            urls = re.findall(r'https?://[^\s\)]+', text)
            return 0.0, urls

    def run_polling(self, model="gpt-4o"):
        prompts = self.fetch_active_prompts()
        entities = self.fetch_entities()
        
        # Identifica il brand del cliente per l'analisi del sentiment
        self.cur.execute("SELECT entity_name FROM ai_entities WHERE is_client = TRUE LIMIT 1;")
        client_brand = self.cur.fetchone()
        client_brand_name = client_brand[0] if client_brand else "Client"

        for prompt_id, prompt_text in prompts:
            try:
                # 1. Interrogazione del Modello Target
                response = self.client.chat.completions.create(
                    model=model,
                    messages=[{"role": "user", "content": prompt_text}],
                    temperature=0.2
                )
                raw_response = response.choices[0].message.content
                raw_lower = raw_response.lower()

                # 2. Entity Matching tramite Regex
                detected_entities = []
                for entity_id, name, patterns in entities:
                    for pattern in patterns:
                        if re.search(r'\b' + re.escape(pattern.lower()) + r'\b', raw_lower):
                            detected_entities.append(entity_id)
                            break

                # 3. Sentiment & Citations Parsing
                sentiment, citations = self.analyze_sentiment_and_citations(raw_response, client_brand_name)

                # 4. Inserimento a Database
                self.cur.execute("""
                    INSERT INTO ai_polling_results 
                    (prompt_id, model_name, raw_response, detected_entities, sentiment_score, citations)
                    VALUES (%s, %s, %s, %s, %s, %s);
                """, (prompt_id, model, raw_response, detected_entities, sentiment, citations))
                
                self.conn.commit()
                print(f"[SUCCESS] Polling completato per prompt_id: {prompt_id}")

            except Exception as e:
                self.conn.rollback()
                print(f"[ERROR] Fallimento sul prompt_id {prompt_id}: {str(e)}")

    def close(self):
        self.cur.close()
        self.conn.close()

if __name__ == "__main__":
    tracker = AIEngineTracker()
    tracker.run_polling(model="gpt-4o")
    tracker.close()