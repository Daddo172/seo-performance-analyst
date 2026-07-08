"""
Modulo AEO — Answer Engine Optimization
=========================================

Cos'e' l'AEO e perche' e' diverso dalla SEO classica
-----------------------------------------------------
La SEO tradizionale ottimizza per un algoritmo di ranking che restituisce
una lista di link (la SERP). L'AEO ottimizza per un sistema che legge il
contenuto, lo sintetizza e restituisce UNA risposta diretta all'utente
(AI Overviews di Google, ChatGPT, Perplexity, Copilot, Gemini...).

Conseguenza pratica: non basta piu' "rankare", bisogna essere la fonte che
il modello sceglie di leggere, capire e citare. Questo modulo misura 5
categorie di segnali che la letteratura tecnica (documentazione ufficiale
di OpenAI/Google Search Central sugli AI crawler, linee guida schema.org,
e le best practice di E-E-A-T di Google) indica come rilevanti:

1. CRAWLABILITA' AI (peso 20/100) — GATE
   Se il robots.txt blocca i bot delle AI (GPTBot, PerplexityBot, ClaudeBot,
   Google-Extended, CCBot...), la pagina e' semplicemente invisibile a
   quell'answer engine, indipendentemente da quanto sia ben scritta.
   E' un requisito binario prima ancora che una questione di qualita'.

2. STRUTTURA DEI DATI / SCHEMA.ORG (peso 25/100)
   I markup FAQPage, HowTo, Article, Organization aiutano gli answer engine
   a disambiguare "cos'e' questo contenuto" senza dover inferire dal testo
   libero. E' il segnale piu' correlato empiricamente alla comparsa nei
   featured snippet e nelle AI Overview di Google.

3. FORMATO "RISPOSTA DIRETTA" (peso 25/100)
   I modelli estraggono piu' facilmente contenuto organizzato come
   domanda (H2/H3) seguita da una risposta diretta e concisa (idealmente
   40-60 parole) nel paragrafo immediatamente successivo, prima di
   eventuali approfondimenti. E' il pattern che rende un paragrafo
   "estraibile" come risposta autonoma.

4. SEGNALI E-E-A-T (peso 15/100)
   Autore dichiarato, data di pubblicazione/aggiornamento visibile.
   Gli answer engine, come Google, pesano l'affidabilita' percepita
   della fonte quando scelgono cosa citare.

5. SCANNABILITA' (peso 15/100)
   Liste puntate/numerate e tabelle sono piu' facili da segmentare e
   riutilizzare per un LLM rispetto a blocchi di prosa non strutturata.
"""
import re
import json
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse

# Domini dei principali "answer engine" — usati per segmentare il traffico GA4
AEO_REFERRAL_DOMAINS = {
    "chatgpt.com": "ChatGPT",
    "chat.openai.com": "ChatGPT",
    "perplexity.ai": "Perplexity",
    "copilot.microsoft.com": "Microsoft Copilot",
    "bing.com/chat": "Bing Copilot",
    "gemini.google.com": "Google Gemini",
    "claude.ai": "Claude",
    "you.com": "You.com",
}

# User-agent dei crawler usati dalle AI per addestramento/retrieval.
# Se il robots.txt li blocca, il sito e' invisibile a quell'ecosistema.
AI_CRAWLER_USER_AGENTS = {
    "GPTBot": "OpenAI (ChatGPT / training)",
    "OAI-SearchBot": "OpenAI (ricerca/citazioni in ChatGPT)",
    "ChatGPT-User": "OpenAI (browsing live durante la chat)",
    "PerplexityBot": "Perplexity",
    "ClaudeBot": "Anthropic (Claude)",
    "anthropic-ai": "Anthropic (training)",
    "Google-Extended": "Google (Gemini / AI Overviews)",
    "CCBot": "Common Crawl (usato per addestrare molti LLM)",
    "Bytespider": "ByteDance",
    "Applebot-Extended": "Apple Intelligence",
}

QUESTION_STARTERS = (
    "come", "cosa", "cos'", "quanto", "quanti", "quante", "perché", "perche",
    "quando", "dove", "chi", "quale", "quali", "che cos", "is ", "what",
    "how", "why", "when", "where", "who", "which",
)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}


# ---------------------------------------------------------------------------
# 1. CRAWLABILITA' AI — analisi robots.txt
# ---------------------------------------------------------------------------
def check_ai_crawlability(base_url, timeout=8):
    """
    Scarica robots.txt e verifica se i crawler delle principali AI sono bloccati.
    Ritorna un dict {user_agent: bool_bloccato} + lista leggibile dei blocchi.
    """
    parsed = urlparse(base_url)
    robots_url = f"{parsed.scheme}://{parsed.netloc}/robots.txt"

    try:
        resp = requests.get(robots_url, headers=HEADERS, timeout=timeout)
        if resp.status_code != 200:
            # Nessun robots.txt = nessun blocco esplicito ai bot AI
            return {"robots_found": False, "blocked_bots": [], "raw_status": resp.status_code}

        content = resp.text
        # Parsing semplice: individua i blocchi User-agent e i Disallow: / associati
        current_agents = []
        disallow_all = set()
        for line in content.splitlines():
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if line.lower().startswith("user-agent:"):
                agent = line.split(":", 1)[1].strip()
                current_agents = [agent]
            elif line.lower().startswith("disallow:"):
                path = line.split(":", 1)[1].strip()
                if path == "/":
                    disallow_all.update(current_agents)

        blocked_known_bots = [
            {"bot": bot, "owner": owner}
            for bot, owner in AI_CRAWLER_USER_AGENTS.items()
            if bot in disallow_all or "*" in disallow_all
        ]

        return {
            "robots_found": True,
            "blocked_bots": blocked_known_bots,
            "raw_status": resp.status_code,
        }
    except requests.exceptions.RequestException:
        return {"robots_found": None, "blocked_bots": [], "raw_status": "unreachable"}


# ---------------------------------------------------------------------------
# 2-5. SCRAPING ON-PAGE per struttura dati, formato risposta, E-E-A-T, scannabilita'
# ---------------------------------------------------------------------------
def scrape_page_for_aeo(url, timeout=8):
    """Estrae dal codice HTML della pagina tutti i segnali AEO grezzi."""
    try:
        resp = requests.get(url, headers=HEADERS, timeout=timeout)
        if resp.status_code != 200:
            return {"error": f"Pagina non raggiungibile (status {resp.status_code})"}
        soup = BeautifulSoup(resp.text, "html.parser")
    except requests.exceptions.RequestException as e:
        return {"error": f"Errore di connessione: {e}"}

    signals = {}

    # --- Schema.org (JSON-LD) ---
    schema_types = []
    for tag in soup.find_all("script", attrs={"type": "application/ld+json"}):
        try:
            data = json.loads(tag.string or "{}")
            items = data if isinstance(data, list) else [data]
            for item in items:
                t = item.get("@type")
                if t:
                    schema_types.extend(t if isinstance(t, list) else [t])
        except (json.JSONDecodeError, AttributeError, TypeError):
            continue
    signals["schema_types"] = list(set(schema_types))
    signals["has_faq_schema"] = any(t in schema_types for t in ("FAQPage",))
    signals["has_howto_schema"] = any(t in schema_types for t in ("HowTo",))
    signals["has_article_schema"] = any(t in schema_types for t in ("Article", "BlogPosting", "NewsArticle"))

    # --- Formato "risposta diretta": header a domanda + paragrafo conciso subito dopo ---
    question_headers = []
    headers_tags = soup.find_all(["h2", "h3"])
    for h in headers_tags:
        text = h.get_text(strip=True)
        text_lower = text.lower()
        is_question = text.endswith("?") or text_lower.startswith(QUESTION_STARTERS)
        if is_question:
            # cerca il primo <p> dopo l'header
            next_p = h.find_next("p")
            answer_words = len(next_p.get_text(strip=True).split()) if next_p else 0
            question_headers.append({
                "header": text,
                "answer_word_count": answer_words,
                "direct_answer": 15 <= answer_words <= 60,
            })
    signals["question_headers"] = question_headers
    signals["direct_answer_blocks"] = sum(1 for q in question_headers if q["direct_answer"])

    # --- E-E-A-T: autore e data ---
    author_found = bool(
        soup.find(attrs={"class": re.compile("author|byline", re.I)})
        or soup.find("meta", attrs={"name": "author"})
        or soup.find(attrs={"rel": "author"})
    )
    date_found = bool(
        soup.find("time")
        or soup.find("meta", attrs={"property": "article:published_time"})
        or soup.find("meta", attrs={"property": "article:modified_time"})
    )
    signals["has_author"] = author_found
    signals["has_date"] = date_found

    # --- Scannabilita' ---
    signals["list_count"] = len(soup.find_all(["ul", "ol"]))
    signals["table_count"] = len(soup.find_all("table"))

    # --- Title/H1 per completezza del report ---
    signals["title"] = soup.find("title").get_text(strip=True) if soup.find("title") else ""
    h1 = soup.find("h1")
    signals["h1"] = h1.get_text(strip=True) if h1 else ""

    return signals


# ---------------------------------------------------------------------------
# SCORING — combina crawlabilita' + segnali on-page in un punteggio 0-100
# ---------------------------------------------------------------------------
def compute_aeo_score(crawl_signals, page_signals):
    """
    Calcola l'AEO Score (0-100) e la lista di raccomandazioni prioritizzate.
    Pesi: Crawlabilita' 20 | Schema 25 | Risposta diretta 25 | E-E-A-T 15 | Scannabilita' 15
    """
    if page_signals.get("error"):
        return {"score": None, "error": page_signals["error"], "breakdown": {}, "recommendations": []}

    breakdown = {}
    recommendations = []

    # 1. Crawlabilita' (20 pt) — se un bot AI e' bloccato, penalita' pesante
    blocked = crawl_signals.get("blocked_bots", [])
    crawl_score = 20 if not blocked else max(0, 20 - len(blocked) * 7)
    breakdown["Crawlabilità AI"] = crawl_score
    if blocked:
        nomi = ", ".join(b["owner"] for b in blocked)
        recommendations.append(
            f"🚨 PRIORITÀ MASSIMA: il robots.txt blocca crawler AI ({nomi}). "
            f"La pagina è invisibile a quegli answer engine finché non rimuovi il blocco."
        )

    # 2. Schema.org (25 pt)
    schema_score = 0
    if page_signals.get("has_faq_schema"):
        schema_score += 12
    if page_signals.get("has_howto_schema"):
        schema_score += 8
    if page_signals.get("has_article_schema"):
        schema_score += 5
    breakdown["Structured Data"] = min(schema_score, 25)
    if not page_signals.get("has_faq_schema") and page_signals.get("question_headers"):
        recommendations.append(
            "📋 Hai già contenuto in formato domanda/risposta ma manca il markup FAQPage: "
            "aggiungilo per rendere il contenuto esplicito per gli answer engine."
        )
    elif schema_score == 0:
        recommendations.append(
            "📋 Nessuno schema.org rilevato. Aggiungi almeno Article/FAQPage per dare "
            "contesto strutturato al contenuto."
        )

    # 3. Risposta diretta (25 pt)
    n_questions = len(page_signals.get("question_headers", []))
    n_direct = page_signals.get("direct_answer_blocks", 0)
    if n_questions == 0:
        direct_score = 0
        recommendations.append(
            "❓ Nessun header in formato domanda trovato. Trasforma almeno 2-3 H2 in "
            "domande reali che il tuo pubblico cerca, seguite da una risposta diretta "
            "di 40-60 parole nel primo paragrafo."
        )
    else:
        ratio = n_direct / n_questions
        direct_score = round(ratio * 25)
        if ratio < 0.5:
            recommendations.append(
                f"✂️ {n_questions - n_direct} dei tuoi header a domanda non hanno una risposta "
                f"diretta e concisa nel paragrafo successivo (target: 40-60 parole prima di "
                f"eventuali approfondimenti)."
            )
    breakdown["Formato Risposta Diretta"] = direct_score

    # 4. E-E-A-T (15 pt)
    eeat_score = (7 if page_signals.get("has_author") else 0) + (8 if page_signals.get("has_date") else 0)
    breakdown["Segnali E-E-A-T"] = eeat_score
    if not page_signals.get("has_author"):
        recommendations.append("👤 Manca un autore dichiarato: aggiungi una byline visibile.")
    if not page_signals.get("has_date"):
        recommendations.append("📅 Manca una data di pubblicazione/aggiornamento visibile.")

    # 5. Scannabilita' (15 pt)
    lists = page_signals.get("list_count", 0)
    tables = page_signals.get("table_count", 0)
    scan_score = min(15, lists * 4 + tables * 5)
    breakdown["Scannabilità"] = scan_score
    if lists == 0 and tables == 0:
        recommendations.append(
            "📃 Nessuna lista o tabella nella pagina: converti dove possibile la prosa in "
            "elenchi puntati/numerati, molto più facili da estrarre per un LLM."
        )

    total = sum(breakdown.values())
    return {
        "score": total,
        "breakdown": breakdown,
        "recommendations": recommendations,
        "raw_signals": page_signals,
        "crawl_signals": crawl_signals,
    }


def audit_page_aeo(url):
    """Funzione di alto livello: esegue l'intero audit AEO di una singola pagina."""
    crawl_signals = check_ai_crawlability(url)
    page_signals = scrape_page_for_aeo(url)
    return compute_aeo_score(crawl_signals, page_signals)


# ---------------------------------------------------------------------------
# TRAFFICO — segmentazione delle sessioni GA4 provenienti da answer engine
# ---------------------------------------------------------------------------
def classify_ai_referrals(df_sources):
    """
    Prende il dataframe restituito da fetch_ga4_traffic_sources (colonna 'source')
    e isola le sessioni che arrivano da answer engine noti.
    Ritorna (df_filtrato_con_engine, riepilogo_per_engine).
    """
    import pandas as pd

    if df_sources is None or df_sources.empty:
        return pd.DataFrame(), pd.DataFrame()

    def match_engine(source):
        source_l = str(source).lower()
        for domain, name in AEO_REFERRAL_DOMAINS.items():
            if domain in source_l:
                return name
        return None

    df = df_sources.copy()
    df["ai_engine"] = df["source"].apply(match_engine)
    df_ai = df[df["ai_engine"].notna()].copy()

    if df_ai.empty:
        return df_ai, pd.DataFrame()

    summary = (
        df_ai.groupby("ai_engine")
        .agg(sessioni=("sessions", "sum"), conversioni=("conversions", "sum"))
        .reset_index()
        .sort_values("sessioni", ascending=False)
    )
    return df_ai, summary


# ---------------------------------------------------------------------------
# UTILITY — genera lo snippet JSON-LD FAQPage pronto da incollare nel sito
# ---------------------------------------------------------------------------
def parse_qa_text(raw_text):
    """
    Estrae coppie (domanda, risposta) da un testo nel formato:
        D: ...
        R: ...
    (come generato da ai_seo.generate_aeo_faq). Tollerante a spazi/maiuscole.
    """
    pairs = []
    current_q, current_r = None, []

    for line in raw_text.splitlines():
        stripped = line.strip()
        m_q = re.match(r"^\**\s*D\s*[:\.]\s*(.+)", stripped, re.IGNORECASE)
        m_r = re.match(r"^\**\s*R\s*[:\.]\s*(.+)", stripped, re.IGNORECASE)
        if m_q:
            if current_q and current_r:
                pairs.append((current_q, " ".join(current_r).strip()))
            current_q = m_q.group(1).strip()
            current_r = []
        elif m_r:
            current_r.append(m_r.group(1).strip())
        elif current_q and stripped:
            current_r.append(stripped)

    if current_q and current_r:
        pairs.append((current_q, " ".join(current_r).strip()))

    return pairs


def generate_faq_schema(qa_pairs):
    """
    qa_pairs: lista di tuple (domanda, risposta)
    Ritorna una stringa JSON-LD pronta da incollare in un tag <script type="application/ld+json">.
    """
    payload = {
        "@context": "https://schema.org",
        "@type": "FAQPage",
        "mainEntity": [
            {
                "@type": "Question",
                "name": q,
                "acceptedAnswer": {"@type": "Answer", "text": a},
            }
            for q, a in qa_pairs
        ],
    }
    return json.dumps(payload, ensure_ascii=False, indent=2)
