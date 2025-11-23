import asyncio
import os
import sys
from modules.serp_fetcher import fetch_serp
from logger import setup_logger

# Setup logger to print to console
logger = setup_logger('debug_serp')

def main():
    keyword = "торт рецепт"
    print(f"🔍 Testing SERP fetch for: {keyword}")
    
    try:
        results = fetch_serp(keyword, "uk", "Ukraine")
        print(f"✅ Success! Got {len(results['organic'])} results")
        for i, res in enumerate(results['organic'][:5]):
            print(f"  {i+1}. {res.get('link')} - {res.get('title')}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    # Ensure we can import modules
    sys.path.append(os.getcwd())
    main()
