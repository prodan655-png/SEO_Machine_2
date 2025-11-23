"""
Mock implementation of SERP fetcher for development.
Returns pre-defined SERP results without calling external APIs.
"""

from typing import List, Dict, Any
from logger import setup_logger

logger = setup_logger(__name__)


def mock_fetch_serp(
    keyword: str,
    language: str,
    location: str,
    device: str,
    count: int = 10
) -> Dict[str, Any]:
    """
    Mock SERP fetcher that returns fake but realistic results.
    
    Args:
        keyword: Search keyword
        language: Language code (uk, en)
        location: Location for search
        device: desktop or mobile
        count: Number of results to return
    
    Returns:
        Dict with success status, results list, and metadata
    """
    logger.info(f"[MOCK] Fetching SERP for keyword='{keyword}', location={location}, count={count}")
    
    # Generate mock results
    results = []
    domains = [
        "healthline.com", "medicalnewstoday.com", "webmd.com",
        "nhs.uk", "mayoclinic.org", "verywellhealth.com",
        "wikipedia.org", "eatthis.com", "diet doctor.com", "ruled.me"
    ]
    
    for i in range(min(count, len(domains))):
        results.append({
            "position": i + 1,
            "url": f"mock://{domains[i]}/article/{keyword.replace(' ', '-').lower()}",
            "title": f"{keyword.title()}: Complete Guide from {domains[i].split('.')[0].title()}",
            "snippet": f"Learn everything about {keyword}. Discover benefits, risks, and practical tips from experts...",
            "domain": domains[i]
        })
    
    response = {
        "success": True,
        "results": results,
        "metadata": {
            "total_results": len(results),
            "unique_domains": len(set(r["domain"] for r in results)),
            "query_time": "2025-11-22T13:09:34Z",
            "mock": True
        }
    }
    
    logger.info(f"[MOCK] Returned {len(results)} SERP results with mock:// URLs")
    return response


def mock_fetch_serp_with_duplicates(keyword: str, **kwargs) -> Dict[str, Any]:
    """Mock SERP with duplicate domains (for testing single-domain warning)."""
    results = []
    for i in range(10):
        results.append({
            "position": i + 1,
            "url": f"https://example.com/article-{i}",
            "title": f"Example Article {i}",
            "snippet": f"This is article {i}",
            "domain": "example.com"
        })
    
    return {
        "success": True,
        "results": results,
        "metadata": {
            "total_results": 10,
            "unique_domains": 1,
            "mock": True
        }
    }
