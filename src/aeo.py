import requests
from bs4 import BeautifulSoup
import re
import json


class AEOAnalyzer:
    def __init__(self, url):
        self.url = url
        self.soup = None
        self.robots_content = None

    def fetch_page(self):
        """Scarica il contenuto della pagina per l'analisi."""
        try:
            response = requests.get(self.url, timeout=10)
            self.soup = BeautifulSoup(response.content, 'html.parser')
            return True
        except Exception as e:
            print(f"Errore nel fetch della pagina: {e}")
            return False

    def check_robots_txt(self):
        """Analizza il robots.txt per verificare il blocco dei bot AI."""
        try:
            # Ricava l'URL del robots.txt
            base_url = "/".join(self.url.split("/")[:3])
            response = requests.get(f"{base_url}/robots.txt", timeout=5)
            self.robots_content = response.text
            
            ai_bots = ['GPTBot', 'ClaudeBot', 'PerplexityBot', 'Google-Extended']
            results = {bot: (bot not in self.robots_content) for bot in ai_bots}
            return results
        except:
            return "Impossibile recuperare robots.txt"

    def analyze_scannability(self):
        """Verifica la presenza di liste e tabelle."""
        if not self.soup: return 0
        lists = self.soup.find_all(['ul', 'ol'])
        tables = self.soup.find_all('table')
        # Logica semplificata: ritorna True se ci sono elementi di formattazione
        return len(lists) > 0 or len(tables) > 0

    def get_audit_report(self):
        """Restituisce un riepilogo dello score AEO."""
        if not self.fetch_page():
            return "Errore nell'analisi"
        
        robots_audit = self.check_robots_txt()
        scannable = self.analyze_scannability()
        
        # Placeholder per il calcolo dello score (0-100)
        score = 0
        if isinstance(robots_audit, dict) and all(robots_audit.values()): score += 20
        if scannable: score += 15
        
        return {
            "score": score,
            "robots_audit": robots_audit,
            "scannable": scannable
        }
# --- 1. AUDIT CRAWLABILITÀ ---
def audit_robots_txt(domain):
    """Verifica se i principali bot AI sono bloccati nel robots.txt."""
    bots = ["GPTBot", "Claude-Web", "PerplexityBot", "Google-Extended"]
    results = {bot: "✅ Consentito" for bot in bots}
    
    try:
        response = requests.get(f"{domain}/robots.txt", timeout=5)
        if response.status_code == 200:
            content = response.text
            for bot in bots:
                # Cerca direttive Disallow che menzionano il bot
                if re.search(f"User-agent: {bot}.*Disallow: /", content, re.IGNORECASE):
                    results[bot] = "❌ Bloccato"
    except:
        return {bot: "⚠️ Errore fetch" for bot in bots}
    return results

# --- 2. ANALISI E-E-A-T E SCANNABILITÀ ---
def analyze_page_aeo(url):
    """Analisi strutturale della pagina (E-E-A-T, Scannabilità, Pattern)."""
    try:
        response = requests.get(url, timeout=10)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Scannabilità: liste e tabelle
        lists = len(soup.find_all(['ul', 'ol']))
        tables = len(soup.find_all('table'))
        
        # E-E-A-T: ricerca meta author o data
        has_author = bool(soup.find("meta", {"name": "author"}) or soup.find(class_="author"))
        has_date = bool(soup.find("meta", {"property": "article:published_time"}))
        
        # Pattern Domanda/Risposta: ricerca h2/h3 seguite da p brevi
        patterns = 0
        for header in soup.find_all(['h2', 'h3']):
            next_p = header.find_next_sibling('p')
            if next_p and 20 < len(next_p.text.split()) < 70:
                patterns += 1

        # Check Schema
        schemas = [s.string for s in soup.find_all("script", type="application/ld+json")]
        has_faq = any("FAQPage" in s for s in schemas)
        
        return {
            "scannability_score": min(10, (lists * 2) + (tables * 3)),
            "eeat_signals": has_author + has_date,
            "pattern_qa": patterns,
            "has_faq_schema": has_faq
        }
    except Exception as e:
        return {"error": str(e)}

# --- 3. CALCOLO SCORE ---
def calculate_aeo_score(audit_data, robots_data):
    """Calcola score 0-100 pesato."""
    score = 0
    # Peso robots (30%)
    score += (sum(1 for v in robots_data.values() if v == "✅ Consentito") / len(robots_data)) * 30
    # Peso schema (30%)
    if audit_data.get("has_faq_schema"): score += 30
    # Peso E-E-A-T (20%)
    score += min(20, audit_data.get("eeat_signals", 0) * 10)
    # Peso Scannabilità (20%)
    score += min(20, audit_data.get("scannability_score", 0))
    
    return int(score)

# --- 2. ANALIZZATORE EURISTICO GEO & RAG ---
def analyze_page_geo_features(url):
    """
    Analizza l'HTML della pagina per estrarre le feature qualitative
    richieste dalle strategie d'ottimizzazione GEO e dai vincoli RAG.
    """
    try:
        response = requests.get(url, timeout=10)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Estrazione del testo pulito dai paragrafi
        paragraphs = [p.text.strip() for p in soup.find_all('p') if len(p.text.strip()) > 10]
        full_text = " ".join(paragraphs)
        words = full_text.split()
        total_words = len(words)
        
        if total_words == 0:
            return {"error": "Nessun testo rilevabile nei paragrafi."}

        # 1. Rilevamento Statistiche (Numeri, percentuali, dati) -> Impatto: Altissimo
        # Cerca cifre numeriche seguite da % o numeri isolati (es. 20%, 150.000, 2026)
        stats_count = len(re.findall(r'\b\d+(?:[\.,]\d+)?%?|\b\d+\b', full_text))
        has_statistics = stats_count > (total_words / 200) # Almeno una statistica ogni 200 parole
        
        # 2. Rilevamento Virgolettati / Citazioni Esperti -> Impatto: Altissimo
        # Cerca virgolette o verbi di dichiarazione (es. "ha dichiarato", "secondo l'esperto")
        quotes_count = len(re.findall(r'["\'«“].*?["\'»”]', full_text))
        declaration_verbs = len(re.findall(r'\b(ha affermato|ha dichiarato|secondo|sostiene|ha evidenziato)\b', full_text, re.IGNORECASE))
        has_quotations = quotes_count > 0 or declaration_verbs > 1
        
        # 3. Citazione Fonti Esterne -> Impatto: Alto
        # Cerca parole chiave come "studio", "report", "ricerca", "paper", "fonte"
        sources_count = len(re.findall(r'\b(studio|report|ricerca|paper|fonte|pubblicazione|dati ufficiali)\b', full_text, re.IGNORECASE))
        cite_sources = sources_count > 1
        
        # 4. Tono Assertivo / Autorevole -> Impatto: Alto (fondamentale su Scienza/Medicina)
        # Semplificato: presenza di frasi definitorie dirette ("è", "sono", "rappresenta", "certamente")
        authoritative_patterns = len(re.findall(r'\b(è certamente|dimostra che|è scientificamente|i dati confermano)\b', full_text, re.IGNORECASE))
        authoritative_tone = authoritative_patterns > 0

        # 5. Struttura RAG Calibrazione Lunghezza Testo (~130-170 parole per blocco informativo)
        # Analizziamo la lunghezza media dei paragrafi per vedere se si allineano alla zona d'oro RAG
        rag_compliant_blocks = 0
        for p in paragraphs:
            p_len = len(p.split())
            if 100 <= p_len <= 180: # Finestra ottimale per il recupero dei chunk nei sistemi RAG
                rag_compliant_blocks += 1

        # 6. Presenza Dati Strutturati FAQ
        schemas = [s.string for s in soup.find_all("script", type="application/ld+json") if s.string]
        has_faq_schema = any("FAQPage" in s for s in schemas)
        
        # 7. Scannabilità (Presenza di Liste o Tabelle)
        lists_and_tables = len(soup.find_all(['ul', 'ol', 'table']))
        scannability_score = min(10, lists_and_tables * 2)

        return {
            "has_statistics": has_statistics,
            "has_quotations": has_quotations,
            "cite_sources": cite_sources,
            "authoritative_tone": authoritative_tone,
            "rag_compliant_blocks": rag_compliant_blocks,
            "has_faq_schema": has_faq_schema,
            "scannability_score": scannability_score,
            "total_words": total_words
        }
    except Exception as e:
        return {"error": str(e)}

# --- 3. CALCOLO SCORE PESATO SECONDO IL PAPER GEO (KDD 2024) ---
def calculate_scientific_geo_score(page_features, robots_data, intent_type="scientific_medical"):
    """
    Calcola un punteggio da 0 a 100 pesando le feature in base all'impatto 
    scoperto nel paper GEO (2024) e all'intento di ricerca selezionato.
    """
    if "error" in page_features:
        return 0, ["Impossibile calcolare lo score: errore di scansione della pagina."]
        
    score = 0
    recommendations = []
    
    # 🛑 CRITICITÀ 1: Crawlabilità (Se i bot sono bloccati, l'ottimizzazione è inutile)
    allowed_bots = sum(1 for v in robots_data.values() if v == "✅ Consentito")
    crawl_ratio = allowed_bots / len(robots_data)
    score += crawl_ratio * 20  # Max 20 punti
    if crawl_ratio < 1.0:
        recommendations.append("⚠️ Alcuni bot AI sono bloccati nel robots.txt. Sblocca l'accesso per GPTBot e PerplexityBot.")

    # 📈 STRATEGIA 1: Aggiunta Statistiche (Impatto Altissimo: +30/40% di Impression Score)
    if page_features["has_statistics"]:
        score += 25
    else:
        recommendations.append("🔴 FONDAMENTALE: Integra dati numerici, percentuali e statistiche precise a supporto delle tue tesi (+30/40% visibilità AI).")

    # 💬 STRATEGIA 2: Aggiunta Virgolettati (Impatto Altissimo)
    if page_features["has_quotations"]:
        score += 20
    else:
        recommendations.append("🔴 FONDAMENTALE: Includi citazioni testuali o virgolettati provenienti da esperti o figure autorevoli del settore.")

    # 📚 STRATEGIA 3: Citazione Fonti
    if page_features["cite_sources"]:
        score += 15
    else:
        recommendations.append("🟡 CONSIGLIATO: Inserisci riferimenti espliciti a studi, report o pubblicazioni scientifiche esterne.")

    # 🎯 STRATEGIA SPECIFICA PER DOMINIO / INTENTO DI RICERCA
    if intent_type == "scientific_medical":
        # Richiede tono assertivo e fonti solide
        if page_features["authoritative_tone"]:
            score += 10
        else:
            recommendations.append("🔵 OTTIMIZZAZIONE DOMINIO: Adotta un registro linguistico più sicuro, assertivo e focalizzato sulla certezza dei fatti.")
    else:
        # Intento commerciale/lifestyle: favorisce scannabilità e fluidità
        if page_features["scannability_score"] >= 6:
            score += 10
        else:
            recommendations.append("🔵 OTTIMIZZAZIONE DOMINIO: Incrementa la scannabilità del testo inserendo più liste puntate o tabelle comparative.")

    # 🧠 STRATEGIA RAG: Chunking e Lunghezza Paragrafi
    if page_features["rag_compliant_blocks"] >= 2:
        score += 10
    else:
        recommendations.append("🟢 STRUTTURA RAG: Rimodula alcuni paragrafi per creare blocchi informativi autosufficienti di circa 130-170 parole.")

    return int(score), recommendations