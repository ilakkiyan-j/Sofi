# tools/web_tools.py
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlencode, quote_plus, urljoin
import re
import time
import html
import textwrap
from collections import Counter, defaultdict
import heapq

USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120 Safari/537.36"
HEADERS = {"User-Agent": USER_AGENT}
DEFAULT_TIMEOUT = 8.0


# -------------------------
#  Intent detection
# -------------------------
def detect_query_type(query: str) -> str:
    q = query.lower()
    if any(w in q for w in ["news", "latest", "breaking", "today", "headlines", "trending"]):
        return "news"
    if any(w in q for w in ["buy", "price", "under", "best", "deal", "cheap", "cost", "how much", "store"]):
        return "shopping"
    if any(w in q for w in ["code", "example", "snippet", "stack overflow", "stackoverflow", "github"]):
        return "code"
    if any(w in q for w in ["how to", "tutorial", "guide", "steps", "install", "setup"]):
        return "tutorial"
    if any(w in q for w in ["youtube", "video", "watch"]):
        return "youtube"
    if any(w in q for w in ["price of", "new iphone", "iphone price", "iphone 15", "iphone 16"]):
        # shopping-ish but explicit
        return "shopping"
    return "general"


def enhance_query(query: str, qtype: str) -> str:
    q = query.strip()
    if qtype == "news":
        return f"{q} latest news"
    if qtype == "shopping":
        return f"{q} price review buy"
    if qtype == "code":
        return f"{q} stackoverflow example github"
    if qtype == "tutorial":
        return f"how to {q} step by step"
    if qtype == "youtube":
        return f"{q} site:youtube.com"
    return q


# -------------------------
#  Utilities
# -------------------------
def safe_get(url, method="get", **kwargs):
    try:
        func = requests.get if method.lower() == "get" else requests.post
        r = func(url, headers=HEADERS, timeout=DEFAULT_TIMEOUT, **kwargs)
        return r
    except Exception as e:
        return None


def is_captcha(html_text: str) -> bool:
    low = html_text.lower()
    if "captcha" in low or "verify you are human" in low or "detected unusual traffic" in low:
        return True
    return False


def clean_text(s: str) -> str:
    if not s:
        return ""
    # unescape html entities and collapse whitespace
    t = html.unescape(s)
    t = re.sub(r"\s+", " ", t).strip()
    # strip tracking params from common urls (not perfect)
    return t


def dedupe_results(results):
    seen = set()
    out = []
    for r in results:
        key = (r.get("title","").lower(), r.get("url",""))
        if key in seen:
            continue
        seen.add(key)
        out.append(r)
    return out


# -------------------------
#  Parsers / Extractors
# -------------------------
def parse_ddg(html_text: str):
    soup = BeautifulSoup(html_text, "html.parser")
    results = []

    # DuckDuckGo old-style search result titles
    for res in soup.select("div.result"):
        a = res.select_one("a.result__a")
        snippet = res.select_one(".result__snippet")
        url = a["href"] if a else None
        title = a.get_text(strip=True) if a else None
        if title and url:
            results.append({
                "title": clean_text(title),
                "url": url,
                "snippet": clean_text(snippet.get_text(" ", strip=True)) if snippet else ""
            })

    # fallback: link blocks (.result__body etc)
    if not results:
        for a in soup.select("a"):
            txt = a.get_text(" ", strip=True)
            href = a.get("href")
            if txt and href and len(txt) > 10:
                results.append({"title": clean_text(txt[:200]), "url": href, "snippet": ""})

    return dedupe_results(results)


def parse_bing(html_text: str):
    soup = BeautifulSoup(html_text, "html.parser")
    results = []
    for li in soup.select("li.b_algo"):
        a = li.select_one("h2 > a")
        snippet = li.select_one(".b_caption p")
        if a:
            title = a.get_text(strip=True)
            url = a.get("href")
            results.append({
                "title": clean_text(title),
                "url": url,
                "snippet": clean_text(snippet.get_text(" ", strip=True)) if snippet else ""
            })
    return dedupe_results(results)


def parse_brave(html_text: str):
    # Brave has similar structure to DDG/Bing in many cases
    soup = BeautifulSoup(html_text, "html.parser")
    results = []
    for card in soup.select("article"):
        a = card.select_one("a")
        snippet = card.get_text(" ", strip=True)
        if a and card and snippet:
            url = a.get("href")
            title = a.get_text(" ", strip=True)[:200]
            results.append({"title": clean_text(title), "url": url, "snippet": ""})
    return dedupe_results(results)


def parse_google_lite(html_text: str):
    soup = BeautifulSoup(html_text, "html.parser")
    results = []
    # Google lite pages vary; look for divs with an <a> and a snippet
    for g in soup.select("div"):
        a = g.select_one("a")
        text = g.get_text(" ", strip=True)
        if a and text and len(text) > 50:
            url = a.get("href")
            title = a.get_text(" ", strip=True)[:200]
            results.append({"title": clean_text(title), "url": url, "snippet": ""})
    return dedupe_results(results)


def parse_youtube_search(html_text: str):
    soup = BeautifulSoup(html_text, "html.parser")
    results = []
    # YouTube search page is JS-heavy; but HTML fallback includes links to /watch
    for a in soup.select("a"):
        href = a.get("href", "")
        if "/watch" in href:
            title = a.get("title") or a.get_text(" ", strip=True)
            url = urljoin("https://www.youtube.com", href)
            if title:
                results.append({"title": clean_text(title), "url": url, "snippet": ""})
    return dedupe_results(results)


# -------------------------
#  Site searchers (engines)
# -------------------------
def search_duckduckgo(query: str, max_results=6):
    # Use the HTML endpoint
    payload = {"q": query}
    r = safe_get("https://duckduckgo.com/html/?" + urlencode(payload))
    if not r or r.status_code != 200:
        return {"ok": False, "captcha": False, "results": []}
    if is_captcha(r.text):
        return {"ok": False, "captcha": True, "results": []}
    return {"ok": True, "captcha": False, "results": parse_ddg(r.text)[:max_results]}


def search_bing(query: str, max_results=6):
    q = quote_plus(query)
    url = f"https://www.bing.com/search?q={q}"
    r = safe_get(url)
    if not r or r.status_code != 200:
        return {"ok": False, "captcha": False, "results": []}
    if is_captcha(r.text):
        return {"ok": False, "captcha": True, "results": []}
    return {"ok": True, "captcha": False, "results": parse_bing(r.text)[:max_results]}


def search_brave(query: str, max_results=6):
    q = quote_plus(query)
    url = f"https://search.brave.com/search?q={q}"
    r = safe_get(url)
    if not r or r.status_code != 200:
        return {"ok": False, "captcha": False, "results": []}
    if is_captcha(r.text):
        return {"ok": False, "captcha": True, "results": []}
    return {"ok": True, "captcha": False, "results": parse_brave(r.text)[:max_results]}


def search_google_lite(query: str, max_results=6):
    # Try google "lite" by adding &btnI or using textise dot iitty; use basic query page
    q = quote_plus(query)
    url = f"https://www.google.com/search?q={q}&hl=en&gl=us"
    r = safe_get(url)
    if not r or r.status_code != 200:
        return {"ok": False, "captcha": False, "results": []}
    if is_captcha(r.text):
        return {"ok": False, "captcha": True, "results": []}
    return {"ok": True, "captcha": False, "results": parse_google_lite(r.text)[:max_results]}


def search_youtube(query: str, max_results=6):
    q = quote_plus(query)
    url = f"https://www.youtube.com/results?search_query={q}"
    r = safe_get(url)
    if not r or r.status_code != 200:
        return {"ok": False, "captcha": False, "results": []}
    if is_captcha(r.text):
        return {"ok": False, "captcha": True, "results": []}
    return {"ok": True, "captcha": False, "results": parse_youtube_search(r.text)[:max_results]}


# -------------------------
#  Extractive summarizer (simple, fast)
# -------------------------
def summarize_texts(results, max_sentences=3):
    # Build a small corpus from snippets + titles
    corpus = []
    for r in results:
        if r.get("snippet"):
            corpus.append(r["snippet"])
        if r.get("title"):
            corpus.append(r["title"])
    full = " ".join(corpus)
    if not full:
        return ""

    # Basic sentence tokenizer and scoring by word frequency
    sentences = re.split(r'(?<=[.!?])\s+', full)
    words = re.findall(r'\w+', full.lower())
    if not words:
        return ""

    freq = Counter(w for w in words if len(w) > 2)
    sentence_scores = []
    for s in sentences:
        s_words = re.findall(r'\w+', s.lower())
        score = sum(freq.get(w, 0) for w in s_words)
        sentence_scores.append((score, s))

    # pick top sentences
    top = heapq.nlargest(max_sentences, sentence_scores, key=lambda x: x[0])
    top_sentences = [t[1].strip() for t in top if t[0] > 0]
    return " ".join(top_sentences)


# -------------------------
#  Main orchestrator
# -------------------------
def merge_results(list_of_results):
    merged = []
    for r in list_of_results:
        if not r:
            continue
        for item in r.get("results", []):
            merged.append(item)
    return dedupe_results(merged)


def search_with_fallback(query: str, mode: str):
    """
    Attempts engines in order and returns the first meaningful result set.
    For shopping/news we try to be broader.
    """
    engines = [
        ("duckduckgo", search_duckduckgo),
        ("bing", search_bing),
        ("brave", search_brave),
        ("google", search_google_lite)
    ]

    # For youtube mode prefer youtube search first
    if mode == "youtube":
        primary = search_youtube(query)
        if primary["ok"] and primary["results"]:
            return {"engine": "youtube", "results": primary["results"], "captcha": primary["captcha"]}
        # fallback to others
    # Try each engine until we get results
    accumulated = []
    for name, fn in engines:
        try:
            res = fn(query)
        except Exception:
            res = {"ok": False, "captcha": False, "results": []}
        # if engine returned results
        if res.get("ok") and res.get("results"):
            return {"engine": name, "results": res["results"], "captcha": res.get("captcha", False)}
        # if captcha, abort and let caller know
        if res.get("captcha"):
            return {"engine": name, "results": [], "captcha": True}
        # keep accumulating as fallback
        accumulated.append(res)
        # small pause to reduce risk of blocks
        time.sleep(0.2)
    # last resort merge accumulated
    merged = merge_results(accumulated)
    return {"engine": "merged", "results": merged, "captcha": False}


def format_result_struct(mode, query, engine, results, summary):
    return {
        "mode": mode,
        "query": query,
        "engine": engine,
        "summary": summary,
        "results": results
    }


def search_web(query: str):
    """
    Full blown search function:
    - detects mode, enhances query
    - tries multiple search engines
    - extracts clean structured results
    - returns dict { mode, query, engine, summary, results }
    """
    try:
        mode = detect_query_type(query)
        enhanced = enhance_query(query, mode)

        # Primary search attempt
        search_out = search_with_fallback(enhanced, mode)
        if search_out.get("captcha"):
            return format_result_struct(mode, query, search_out.get("engine"), [], "Search blocked by CAPTCHA. Try again later.")

        results = search_out.get("results", [])
        if not results:
            # If nothing found, try relaxing query (remove mode-enhancement)
            fallback_out = search_with_fallback(query, mode)
            results = fallback_out.get("results", [])
            engine_used = fallback_out.get("engine")
        else:
            engine_used = search_out.get("engine")

        # If still nothing, return helpful message
        if not results:
            return format_result_struct(mode, query, engine_used or "none", [], "No results found. Try altering your query or being more specific (e.g., include brand, 'price', or 'review').")

        # Summarize
        summary = summarize_texts(results, max_sentences=3)

        return format_result_struct(mode, query, engine_used, results, summary)

    except Exception as e:
        return format_result_struct("general", query, "error", [], f"Search failed: {e}")


# -------------------------
#  Pretty text formatter
# -------------------------
def format_search_response(resp: dict, max_links: int = 5) -> str:
    """
    Convert the dict output into a friendly multi-line text reply
    that Sofi can speak. Keep it compact.
    """
    mode = resp.get("mode", "general").capitalize()
    summary = resp.get("summary") or ""
    results = resp.get("results", [])[:max_links]

    out_lines = []
    out_lines.append(f"🔎 Mode: {mode}")
    if summary:
        out_lines.append("")
        out_lines.append(textwrap.fill(summary, width=100))
    out_lines.append("")

    if not results:
        out_lines.append("No results found.")
        return "\n".join(out_lines)

    out_lines.append("Top results:")
    for i, r in enumerate(results, 1):
        title = r.get("title", "")[:120]
        url = r.get("url", "")
        snippet = r.get("snippet", "")
        line = f"{i}. {title}"
        if snippet:
            line += f" — {snippet[:200]}"
        line += f"\n   {url}"
        out_lines.append(line)

    return "\n\n".join(out_lines)
