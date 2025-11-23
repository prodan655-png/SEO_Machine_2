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
    count: int = 10
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
    
    payload = json.dumps({
        "q": keyword,
        "gl": language[:2],
        "hl": language,
        "location": location,
        "num": count
    })
    
    headers = {
        'X-API-KEY': SERPAPI_KEY,
        'Content-Type': 'application/json'
    }
    
    try:
        response = requests.request("POST", url, headers=headers, data=payload)
        response.raise_for_status()
        data = response.json()
        
        organic_results = data.get("organic", [])
        
        # Filter out Russian and Belarusian domains
        blocked_domains = ['.ru', '.by', '.su']
        filtered_results = [
            result for result in organic_results
            if not any(result.get('link', '').endswith(domain) or f"{domain}/" in result.get('link', '') 
                      for domain in blocked_domains)
        ]
        
        logger.info(f"Filtered {len(organic_results) - len(filtered_results)} Russian/Belarusian sites from {len(organic_results)} results")
        
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

    except Exception as e:
        logger.error(f"Serper.dev request failed: {str(e)}")
        if "401" in str(e) or "403" in str(e):
            logger.warning("Invalid API key. Falling back to MOCK SERP.")
            from modules.mocks.serp_mock import mock_fetch_serp
            return mock_fetch_serp(keyword, language, location, device, count)
        raise SerpAPIError(f"Serper.dev error: {str(e)}")


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
