import sys
import os
import logging
import argparse

# Add backend to path
backend_path = os.path.join(os.getcwd(), 'backend')
if backend_path not in sys.path:
    sys.path.append(backend_path)

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

try:
    from config import SERPAPI_KEY, SERP_PROVIDER
    from modules.serp_fetcher import _fetch_serper_dev
except ImportError:
    # Try alternate path if running from tools dir
    sys.path.append(os.path.join(os.getcwd(), '..', 'backend'))
    from config import SERPAPI_KEY, SERP_PROVIDER
    from modules.serp_fetcher import _fetch_serper_dev

def test_serp(keyword, language, location):
    print(f"\n=== SERP API DIAGNOSTIC TOOL ===")
    print(f"🔑 API Key: {SERPAPI_KEY[:5]}...{SERPAPI_KEY[-5:] if SERPAPI_KEY else 'None'}")
    print(f"🌐 Provider: {SERP_PROVIDER}")
    print(f"🔍 Query: '{keyword}'")
    print(f"🌍 Settings: {location} ({language})")
    print("================================\n")

    if not SERPAPI_KEY or "your_new" in SERPAPI_KEY:
        print("❌ ERROR: Invalid API Key in .env.development")
        return

    try:
        print("⏳ Sending request to API...")
        # Call the internal function directly to see raw results
        results = _fetch_serper_dev(keyword, language, location, "desktop", 20)
        
        print(f"\n✅ API SUCCESS! Received response.")
        print(f"📊 Total Raw Results: {len(results.get('results', []))}")
        
        print("\n📋 Top 5 Results:")
        for res in results.get('results', [])[:5]:
            print(f"  - [{res.get('position')}] {res.get('domain')} - {res.get('title')[:60]}...")
            
        # Check for blocked sites (simulation)
        blocked_domains = ['.ru', '.by', '.su', '.рф']
        blocked_sites = ['youtube.com', 'facebook.com', 'vk.com', 'ok.ru']
        
        blocked_count = 0
        for res in results.get('results', []):
            domain = res.get('domain', '').lower()
            if any(domain.endswith(ext) for ext in blocked_domains) or \
               any(site in domain for site in blocked_sites):
                blocked_count += 1
                
        print(f"\n🛡️  Filtering Simulation:")
        print(f"   - Blocked: {blocked_count}")
        print(f"   - Valid: {len(results.get('results', [])) - blocked_count}")
        
        if len(results.get('results', [])) - blocked_count == 0:
            print("\n⚠️  WARNING: All results would be filtered out by the application!")
            print("   Try changing the location or language.")

    except Exception as e:
        print(f"\n❌ API ERROR: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Test SERP API')
    parser.add_argument('--keyword', type=str, default='що таке дріжджі', help='Keyword to search')
    parser.add_argument('--lang', type=str, default='uk', help='Language code (uk, en)')
    parser.add_argument('--loc', type=str, default='Ukraine', help='Location (Ukraine, United States)')
    
    args = parser.parse_args()
    
    test_serp(args.keyword, args.lang, args.loc)
