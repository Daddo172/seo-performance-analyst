import requests

def check_ssl(url):
    """Controlla se il sito usa HTTPS"""
    if not url.startswith("https://"):
        return "❌ No HTTPS"
    
    try:
        # Proviamo a connetterci
        response = requests.get(url, timeout=5)
        return "✅ HTTPS Attivo"
    except requests.exceptions.SSLError:
        return "❌ Errore SSL"
    except Exception:
        return "⚠️ Irraggiungibile"