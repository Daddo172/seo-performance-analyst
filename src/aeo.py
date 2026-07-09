import requests
from bs4 import BeautifulSoup
import re

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