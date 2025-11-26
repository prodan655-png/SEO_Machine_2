import requests
import json
import os
import sys

# Load config from .env.development manually or just hardcode for testing
# I'll try to read from the file to be safe
def load_env():
    env_path = os.path.join(os.getcwd(), '.env.development')
    config = {}
    if os.path.exists(env_path):
        with open(env_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    config[key] = value
    return config

config = load_env()
SERPAPI_KEY = config.get('SERPAPI_KEY')

print(f"Loaded API Key: {SERPAPI_KEY[:5]}...")

def debug_serp(keyword, location="Ukraine", language="uk"):
    url = "https://google.serper.dev/search"
    
    payload = json.dumps({
        "q": keyword,
        "gl": language[:2],
        "hl": language,
        "location": location,
        "num": 20
    })
    
    headers = {
        'X-API-KEY': SERPAPI_KEY,
        'Content-Type': 'application/json'
    }
    
    print(f"\nFetching '{keyword}' from Serper.dev...")
    try:
        response = requests.request("POST", url, headers=headers, data=payload)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code != 200:
            print(f"Error: {response.text}")
            return

        data = response.json()
        organic = data.get("organic", [])
        print(f"Raw Results Found: {len(organic)}")
        
        # Replicate filtering logic
        blocked_domains = ['.ru', '.by', '.su', '.рф']
        blocked_sites = [
            'russianfood.com', 'say7.info', 'vkusnyblog.com', 'povar.ru', 
            'eda.ru', 'gotovim-doma.ru', 'iamcook.ru', 'koolinar.ru', 'nyam.ru',
            'youtube.com', 'facebook.com', 'instagram.com', 'pinterest.com', 
            'twitter.com', 'tiktok.com', 'linkedin.com', 'vimeo.com',
            'cookpad.com'
        ]
        
        allowed_count = 0
        for res in organic:
            link = res.get('link', '')
            title = res.get('title', '')
            
            is_blocked = False
            from urllib.parse import urlparse
            try:
                parsed = urlparse(link)
                domain = parsed.netloc.lower()
                
                for tld in blocked_domains:
                    if domain.endswith(tld) or f"{tld}." in domain:
                        is_blocked = True
                        print(f"❌ BLOCKED (TLD): {link}")
                        break
                
                if not is_blocked:
                    for site in blocked_sites:
                        if site in domain:
                            is_blocked = True
                            print(f"❌ BLOCKED (Site): {link}")
                            break
            except:
                pass
            
            if not is_blocked:
                print(f"✅ ALLOWED: {link} - {title}")
                allowed_count += 1
                
        print(f"\nSummary: {allowed_count} allowed out of {len(organic)} raw results.")
        
    except Exception as e:
        print(f"Exception: {e}")

if __name__ == "__main__":
    debug_serp("тест")
    debug_serp("секс")
