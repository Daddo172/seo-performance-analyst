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

# --- 4. GENERAZIONE FAQ (INTEGRATA) ---
def generate_aeo_faq(topic, site_context, api_key):
    # (Inserisci qui la funzione che abbiamo testato prima)
    # Assicurati di passare la api_key dall'esterno
    pass