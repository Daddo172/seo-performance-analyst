import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

def check_broken_links(base_url):
    broken_links = []
    try:
        response = requests.get(base_url)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Trova tutti i tag <a>
        links = soup.find_all('a', href=True)
        
        for link in links:
            href = link['href']
            full_url = urljoin(base_url, href)
            
            # Controlla solo i link interni
            if base_url in full_url:
                try:
                    r = requests.head(full_url, timeout=2)
                    if r.status_code == 404:
                        broken_links.append(full_url)
                except:
                    continue
                    
    except Exception as e:
        print(f"Errore durante il crawl: {e}")
        
    return broken_links