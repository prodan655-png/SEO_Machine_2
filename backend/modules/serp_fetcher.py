"""
SERP Fetcher Module.
Fetches Google search results using SerpAPI or mock data in development.
"""

from typing import List, Dict, Any, Optional
import time
from logger import setup_logger
from config import USE_MOCK_SERP, SERPAPI_KEY

logger = setup_logger(__name__)


class NoSerpResultsError(Exception):
    """Raised when SERP API returns no results."""
    pass


class SerpAPIError(Exception):
    """Raised when SERP API encounters an error."""
    pass


def fetch_serp(
    keyword: str,
    language: str = "en",
    location: str = "United States",
    device: str = "desktop",
    count: int = 50
) -> Dict[str, Any]:
    """
    Fetch Google SERP results.
    
    Args:
        keyword: Search keyword
        language: Language code (en, uk)
        location: Location for search results
        device: desktop or mobile
        count: Number of results to fetch (10 or 20)
    
    Returns:
        Dict containing success status, results list, and metadata
    
    Raises:
        NoSerpResultsError: If no results returned
        SerpAPIError: If API request fails
    """
    # Use mock in development
    if USE_MOCK_SERP:
        from modules.mocks.serp_mock import mock_fetch_serp
        return mock_fetch_serp(keyword, language, location, device, count)
    
    # Check Cache
    from config import SERP_CACHE_ENABLED
    if SERP_CACHE_ENABLED:
        cache_key = _get_cache_key(keyword, language, location, device)
        cached_data = _get_from_cache(cache_key)
        if cached_data:
            logger.info(f"SERP Cache Hit for '{keyword}'")
            return cached_data

    # Real implementation
    from config import SERP_PROVIDER
    
    result = None
    if SERP_PROVIDER == 'serper':
        result = _fetch_serper_dev(keyword, language, location, device, count)
    else:
        result = _fetch_serp_real(keyword, language, location, device, count)
        
    # Save to cache
    if SERP_CACHE_ENABLED and result and result.get('success'):
        _save_to_cache(cache_key, result)
        
    return result


def _fetch_serper_dev(
    keyword: str,
    language: str,
    location: str,
    device: str,
    count: int
) -> Dict[str, Any]:
    """
    Fetch SERP results using Serper.dev API.
    """
    import requests
    import json
    from config import get_config
    
    logger.info(f"Fetching SERP (Serper.dev) for '{keyword}' ({language}, {location}, {device})")
    
    url = "https://google.serper.dev/search"
    
    all_results = []
    start = 0
    
    headers = {
        'X-API-KEY': SERPAPI_KEY,
        'Content-Type': 'application/json'
    }
    
    while len(all_results) < count:
        # Calculate remaining
        remaining = count - len(all_results)
        # Google usually returns 10 per page
        num_to_fetch = min(remaining, 100)
        
        payload = json.dumps({
            "q": keyword,
            "gl": language[:2],
            "hl": language,
            "location": location,
            "num": num_to_fetch,
            "start": start
        })
        
        logger.info(f"Fetching SERP page start={start}, num={num_to_fetch}")
        
        try:
            response = requests.request("POST", url, headers=headers, data=payload)
            response.raise_for_status()
            data = response.json()
            
            organic = data.get("organic", [])
            if not organic:
                break
                
            all_results.extend(organic)
            start += len(organic)
            
            # If we got fewer than requested, we probably reached the end
            if len(organic) < num_to_fetch and len(organic) < 10:
                break
                
            # Avoid rate limits
            if len(all_results) < count:
                time.sleep(0.5)
                
        except Exception as e:
            logger.error(f"Error fetching SERP page: {e}")
            break
            
    # Construct final response format
    # Use all_results instead of organic_results
    organic_results = all_results
        
    # Filter out Russian/Belarusian sites AND Social Media
    # Include both TLDs and known Russian domains on .com/.info
    blocked_domains = ['.ru', '.by', '.su', '.рф']
    blocked_sites = [
        # Russian sites
        'russianfood.com', 'say7.info', 'vkusnyblog.com', 'povar.ru', 
        'eda.ru', 'gotovim-doma.ru', 'iamcook.ru', 'koolinar.ru', 'nyam.ru',
        # Social Media & Video (not articles)
        'youtube.com', 'facebook.com', 'instagram.com', 'pinterest.com', 
        'twitter.com', 'tiktok.com', 'linkedin.com', 'vimeo.com',
        'cookpad.com'  # Often just recipes without much text or user generated
    ]
    
    def is_blocked(url):
        try:
            from urllib.parse import urlparse
            parsed = urlparse(url)
            domain = parsed.netloc.lower()
            
            # Check TLDs (must be at end of domain)
            for tld in blocked_domains:
                if domain.endswith(tld) or f"{tld}." in domain:
                    return True
                    
            # Check specific blocked sites
            for site in blocked_sites:
                if site in domain:
                    print(f"[BLOCK] Blocking site: {url} (matched {site})")
                    return True
                    
            return False
        except Exception as e:
            print(f"[WARN] Error checking URL {url}: {e}")
            return False
    
    print(f"[SEARCH] SERP returned {len(organic_results)} results")
        
    for res in organic_results:
        print(f"  - {res.get('link', 'No link')}")

    filtered_results = [
        result for result in organic_results
        if not is_blocked(result.get('link', ''))
    ]
    
    print(f"[OK] After filtering: {len(filtered_results)} results")
    
    # If we filtered too many, log warning
    if len(filtered_results) < 3:
        logger.warning(f"Aggressive filtering! Original: {len(organic_results)}, Filtered: {len(filtered_results)}")
    
    if not filtered_results:
        raise NoSerpResultsError(f"No SERP results for keyword '{keyword}'")
        
    results = []
    domains_seen = set()
    
    for idx, result in enumerate(filtered_results[:count]):
        url = result.get("link")
        domain = _extract_domain(url)
        domains_seen.add(domain)
        
        results.append({
            "position": result.get("position", idx + 1),
            "url": url,
            "title": result.get("title", ""),
            "snippet": result.get("snippet", ""),
            "domain": domain
        })
        
    logger.info(f"[OK] Fetched {len(results)} SERP results via Serper.dev")
    
    return {
        "success": True,
        "results": results,
        "metadata": {
            "total_results": len(results),
            "unique_domains": len(domains_seen),
            "query_time": time.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "mock": False,
            "provider": "serper"
        }
    }




def _fetch_serp_real(
    keyword: str,
    language: str,
    location: str,
    device: str,
    count: int
) -> Dict[str, Any]:
    """
    Real SERP fetching implementation using SerpAPI.
    """
    import requests
    from config import get_config
    
    logger.info(f"Fetching SERP (SerpApi) for '{keyword}' ({language}, {location}, {device})")
    
    # SerpAPI parameters
    params = {
        "q": keyword,
        "location": location,
        "hl": language,
        "gl": language[:2],  # Country code
        "google_domain": "google.com",
        "device": device,
        "num": count,
        "api_key": SERPAPI_KEY
    }
    
    # Retry logic using tenacity
    from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
    
    max_retries = get_config('serp.retry_attempts', 3)
    
    @retry(
        stop=stop_after_attempt(max_retries),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type(requests.exceptions.RequestException),
        reraise=True
    )
    def make_request():
        response = requests.get(
            "https://serpapi.com/search",
            params=params,
            timeout=get_config('serp.request_timeout', 30)
        )
        response.raise_for_status()
        return response.json()

    try:
        data = make_request()
        
        # Extract organic results
        organic_results = data.get("organic_results", [])
        
        if not organic_results:
            raise NoSerpResultsError(f"No SERP results for keyword '{keyword}'")
        
        # Format results
        results = []
        domains_seen = set()
        
        for idx, result in enumerate(organic_results[:count]):
            url = result.get("link")
            domain = _extract_domain(url)
            
            # Track unique domains
            domains_seen.add(domain)
            
            results.append({
                "position": idx + 1,
                "url": url,
                "title": result.get("title", ""),
                "snippet": result.get("snippet", ""),
                "domain": domain
            })
        
        logger.info(f"[OK] Fetched {len(results)} SERP results ({len(domains_seen)} unique domains)")
        
        return {
            "success": True,
            "results": results,
            "metadata": {
                "total_results": len(results),
                "unique_domains": len(domains_seen),
                "query_time": time.strftime("%Y-%m-%dT%H:%M:%SZ"),
                "mock": False,
                "provider": "serpapi"
            }
        }
        
    except Exception as e:
        logger.error(f"SERP API request failed after retries: {str(e)}")
        if "401" in str(e) or "403" in str(e):
            logger.warning("Invalid API key or unauthorized. Falling back to MOCK SERP.")
            from modules.mocks.serp_mock import mock_fetch_serp
            return mock_fetch_serp(keyword, language, location, device, count)
        raise SerpAPIError(f"SERP failed: {e}")


def _extract_domain(url: str) -> str:
    """Extract domain from URL."""
    from urllib.parse import urlparse
    try:
        parsed = urlparse(url)
        return parsed.netloc.replace("www.", "")
    except:
        return ""


# --- Caching Implementation ---
import sqlite3
import json
import hashlib
from pathlib import Path

CACHE_DB_PATH = Path(__file__).parent.parent / 'serp_cache.db'

def _init_cache():
    """Initialize cache database."""
    with sqlite3.connect(CACHE_DB_PATH) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS serp_cache (
                key TEXT PRIMARY KEY,
                data TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

def _get_cache_key(keyword, language, location, device):
    """Generate unique cache key."""
    raw = f"{keyword}|{language}|{location}|{device}"
    return hashlib.md5(raw.encode()).hexdigest()

def _get_from_cache(key):
    """Retrieve from cache."""
    try:
        with sqlite3.connect(CACHE_DB_PATH) as conn:
            cursor = conn.execute("SELECT data FROM serp_cache WHERE key = ?", (key,))
            row = cursor.fetchone()
            if row:
                return json.loads(row[0])
    except Exception as e:
        logger.warning(f"Cache read error: {e}")
    return None

def _save_to_cache(key, data):
    """Save to cache."""
    try:
        with sqlite3.connect(CACHE_DB_PATH) as conn:
            conn.execute(
                "INSERT OR REPLACE INTO serp_cache (key, data) VALUES (?, ?)",
                (key, json.dumps(data))
            )
    except Exception as e:
        logger.warning(f"Cache write error: {e}")

# Initialize cache on module load
try:
    _init_cache()
except Exception as e:
    logger.error(f"Failed to init SERP cache: {e}")


if __name__ == "__main__":
    # Test
    result = fetch_serp("keto diet", "en", "United States", "desktop", 10)
    print(f"Success: {result['success']}")
    print(f"Results: {len(result['results'])}")

