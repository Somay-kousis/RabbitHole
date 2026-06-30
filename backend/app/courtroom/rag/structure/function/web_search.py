import os
import re
import requests
from urllib.parse import urlparse
from concurrent.futures import ThreadPoolExecutor, as_completed

def get_source_tag(url: str) -> str:
    """
    Parses a URL and returns a clean, formatted source tag.
    Examples:
      - https://twitter.com/rajat_x/status/123 -> <@rajat_x_post>
      - https://timesofindia.indiatimes.com/india/news -> <TimesOfIndia>
      - https://barandbench.com/news -> <BarAndBench>
    """
    try:
        parsed = urlparse(url)
        netloc = parsed.netloc.lower()
        path = parsed.path
        
        # 1. Handle Twitter/X posts
        if "twitter.com" in netloc or "x.com" in netloc:
            # Extract first folder in path (the username)
            parts = [p for p in path.split("/") if p]
            if parts:
                username = parts[0]
                # Clean username from any extra characters
                username = re.sub(r'[^a-zA-Z0-9_]', '', username)
                return f"<@{username}_x_post>"
            return "<TwitterPost>"
            
        # 2. Handle standard websites
        # Remove www. and subdomains if present (e.g. indiatimes.com instead of timesofindia.indiatimes.com)
        parts = netloc.split(".")
        if len(parts) >= 2:
            # If www is first, discard it
            if parts[0] == "www":
                parts = parts[1:]
            # Get main domain name (e.g., indiatimes, barandbench, livelaw)
            domain = parts[0]
            # Special case for double domains like timesofindia.indiatimes.com -> extract timesofindia
            if len(parts) >= 3 and parts[-1] in ("com", "org", "co", "in") and parts[-2] in ("co", "gov", "nic"):
                domain = parts[0]
            elif "timesofindia" in netloc:
                domain = "timesofindia"
            
            # Capitalize each word segment or clean it up
            # Convert barandbench to BarAndBench, livelaw to LiveLaw, etc.
            domain_clean = "".join([w.capitalize() for w in re.split(r'[-_]', domain)])
            # Handle common Indian legal source capitalizations
            corrections = {
                "barandbench": "BarAndBench",
                "livelaw": "LiveLaw",
                "indiankanoon": "IndianKanoon",
                "supremecourtofindia": "SupremeCourtOfIndia",
                "timesofindia": "TimesOfIndia"
            }
            domain_lower = domain_clean.lower()
            for key, val in corrections.items():
                if key in domain_lower:
                    return f"<{val}>"
                    
            return f"<{domain_clean}>"
            
        return f"<{netloc}>"
    except Exception:
        return "<WebSource>"

def single_query_search(query: str, jina_api_key: str) -> list[dict]:
    """
    Executes a single search query against Jina Search API.
    Returns a list of structured result dicts.
    """
    url = f"https://s.jina.ai/{query}"
    headers = {
        "Authorization": f"Bearer {jina_api_key}",
        "Accept": "application/json"
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            data = response.json().get("data", [])
            results = []
            for item in data:
                url_str = item.get("url", "")
                results.append({
                    "title": item.get("title", "Untitled"),
                    "url": url_str,
                    "source_tag": get_source_tag(url_str),
                    "content": item.get("content", "")
                })
            return results
    except Exception as e:
        print(f"Jina search failed for query '{query}': {e}")
    return []

def web_search(queries: list[str]) -> list[dict]:
    """
    Executes web search for multiple queries in parallel.
    Consolidates and deduplicates results by URL.
    """
    jina_key = os.environ.get("JINA_API_KEY")
    if not jina_key:
        print("Warning: JINA_API_KEY is not set. Web search will return empty results.")
        return []
        
    all_results = []
    seen_urls = set()
    
    # Run searches in parallel to minimize latency (up to 10 queries)
    with ThreadPoolExecutor(max_workers=min(len(queries), 5)) as executor:
        futures = {executor.submit(single_query_search, q, jina_key): q for q in queries}
        
        for future in as_completed(futures):
            results = future.result()
            for item in results:
                url = item["url"]
                if url not in seen_urls:
                    seen_urls.add(url)
                    all_results.append(item)
                    
    return all_results
