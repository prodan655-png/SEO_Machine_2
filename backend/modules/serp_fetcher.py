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
    
    # Real implementation
    from config import SERP_PROVIDER
    
    if SERP_PROVIDER == 'serper':
        return _fetch_serper_dev(keyword, language, location, device, count)
    else:
        return _fetch_serp_real(keyword, language, location, device, count)


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
                import time
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
                    print(f"🚫 Blocking site: {url} (matched {site})")
                    return True
                    
            return False
        except Exception as e:
            print(f"⚠️ Error checking URL {url}: {e}")
            return False
    
    print(f"🔍 SERP returned {len(organic_results)} results")
        
    for res in organic_results:
        print(f"  - {res.get('link', 'No link')}")

    filtered_results = [
        result for result in organic_results
        if not is_blocked(result.get('link', ''))
    ]
    
    print(f"✅ After filtering: {len(filtered_results)} results")
    
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
        
    logger.info(f"✓ Fetched {len(results)} SERP results via Serper.dev")
    
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
    
    # Retry logic
    max_retries = get_config('serp.retry_attempts', 3)
    retry_delay = get_config('serp.retry_delay', 2)
    timeout = get_config('serp.request_timeout', 30)
    
    for attempt in range(max_retries):
        try:
            response = requests.get(
                "https://serpapi.com/search",
                params=params,
                timeout=timeout
            )
            response.raise_for_status()
            data = response.json()
            
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
            
            # Check for single domain dominance
            if len(domains_seen) == 1 and len(results) > 5:
                logger.warning(f"Single domain dominance detected: {list(domains_seen)[0]}")
            
            logger.info(f"✓ Fetched {len(results)} SERP results ({len(domains_seen)} unique domains)")
            
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
            
        except requests.exceptions.Timeout:
            logger.warning(f"SERP API timeout (attempt {attempt + 1}/{max_retries})")
            if attempt < max_retries - 1:
                time.sleep(retry_delay)
            else:
                raise SerpAPIError("SERP API request timed out after retries")
        
        except requests.exceptions.RequestException as e:
            logger.error(f"SERP API request failed: {str(e)}")
            if "401" in str(e) or "403" in str(e):
                logger.warning("Invalid API key or unauthorized. Falling back to MOCK SERP.")
                from modules.mocks.serp_mock import mock_fetch_serp
                return mock_fetch_serp(keyword, language, location, device, count)
            
            if attempt < max_retries - 1:
                time.sleep(retry_delay)
            else:
                logger.error("All retries failed. Falling back to MOCK SERP.")
                from modules.mocks.serp_mock import mock_fetch_serp
                return mock_fetch_serp(keyword, language, location, device, count)


def _extract_domain(url: str) -> str:
    """Extract domain from URL."""
    from urllib.parse import urlparse
    parsed = urlparse(url)
    return parsed.netloc.replace("www.", "")


if __name__ == "__main__":
    # Test
    result = fetch_serp("keto diet", "en", "United States", "desktop", 10)
    print(f"Success: {result['success']}")
    print(f"Results: {len(result['results'])}")
    for r in result['results'][:3]:
        print(f"  {r['position']}. {r['title']} ({r['domain']})")
