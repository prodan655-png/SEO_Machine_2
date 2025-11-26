import sys
import os
import logging

# Add backend to path
sys.path.append(os.path.join(os.getcwd(), 'backend'))

# Setup logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

from backend.modules.serp_fetcher import _fetch_serper_dev, SERPAPI_KEY

print(f"🔑 Using API Key: {SERPAPI_KEY[:5]}...{SERPAPI_KEY[-5:]}")

keyword = "що таке дріжджі"
# Testing with default parameters (likely what happened)
language = "en" 
location = "United States"

print(f"\n🔍 Fetching results for: '{keyword}' ({location}, {language})")

try:
    # Call the internal function directly to see raw results
    results = _fetch_serper_dev(keyword, language, location, "desktop", 10)
    
    print(f"\n✅ Success! Found {len(results['results'])} results.")
    
    print("\n📋 Top 5 Results:")
    for res in results['results'][:5]:
        print(f"  - [{res['position']}] {res['domain']} - {res['title']}")

except Exception as e:
    print(f"\n❌ Error: {e}")
