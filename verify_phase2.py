import sys
import os
import time

# Add backend to path
sys.path.append(os.path.join(os.getcwd(), 'backend'))

from modules.serp_fetcher import fetch_serp
from modules.content_extractor import PlaywrightExtractor, extract_single
from config import SERP_CACHE_ENABLED

def test_serp_cache():
    print("\n--- Testing SERP Cache ---")
    keyword = "test cache"
    
    # 1. First fetch (should miss cache)
    start = time.time()
    try:
        res1 = fetch_serp(keyword, count=10)
        print(f"First fetch took: {time.time() - start:.2f}s")
    except Exception as e:
        print(f"First fetch failed: {e}")
        return

    # 2. Second fetch (should hit cache)
    start = time.time()
    try:
        res2 = fetch_serp(keyword, count=10)
        duration = time.time() - start
        print(f"Second fetch took: {duration:.2f}s")
        
        if duration < 0.1:
            print("✅ Cache HIT confirmed (fast response)")
        else:
            print("⚠️ Cache MISS or slow (check implementation)")
            
    except Exception as e:
        print(f"Second fetch failed: {e}")

def test_playwright():
    print("\n--- Testing Playwright Extractor ---")
    url = "https://example.com" # Simple test
    
    try:
        extractor = PlaywrightExtractor()
        content = extractor.fetch_content(url)
        print(f"✅ Playwright fetched {len(content)} bytes from {url}")
        
        if "Example Domain" in content:
            print("✅ Content verification passed")
        else:
            print("⚠️ Content verification failed")
            
    except Exception as e:
        print(f"❌ Playwright failed: {e}")
        print("Did you run 'playwright install'?")

if __name__ == "__main__":
    test_serp_cache()
    test_playwright()
