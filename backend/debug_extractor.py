import asyncio
import os
import sys
from modules.content_extractor import fetch_page_content, extract_main_content
from logger import setup_logger

# Setup logger to print to console
logger = setup_logger('debug_extractor')

def main():
    urls = [
        "https://rud.ua/consumer/recipe/tortu/",
        "https://klopotenko.com/torty/"
    ]
    
    print(f"🔍 Testing extraction for {len(urls)} URLs")
    
    for url in urls:
        print(f"\nProcessing: {url}")
        try:
            html = fetch_page_content(url)
            print(f"  ✓ Fetched HTML ({len(html)} chars)")
            
            data = extract_main_content(html, url)
            print(f"  Title: {data['title']}")
            print(f"  Word count: {data['word_count']}")
            print(f"  Status: {data['status']}")
            
            if data['status'] != 'valid':
                print(f"  ❌ INVALID: {data['status']}")
            else:
                print(f"  ✅ VALID")
                
        except Exception as e:
            print(f"  ❌ Error: {e}")

if __name__ == "__main__":
    # Ensure we can import modules
    sys.path.append(os.getcwd())
    main()
