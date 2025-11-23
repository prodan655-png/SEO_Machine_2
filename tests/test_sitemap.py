import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '../backend'))

from modules.sitemap_parser import parse_sitemap

def test_sitemap_parsing():
    # Test with a known sitemap (using a small one or a mock if possible, but real one is better for this)
    # Let's try a common one, or just handle the error gracefully if network fails
    url = "https://yoast.com/sitemap_index.xml" 
    print(f"Testing sitemap parsing for: {url}")
    
    try:
        urls = parse_sitemap(url)
        print(f"Found {len(urls)} URLs")
        for u in urls[:5]:
            print(f" - {u}")
            
        if len(urls) > 0:
            print("✅ Sitemap parsing successful")
        else:
            print("⚠️ No URLs found (might be empty or blocked)")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_sitemap_parsing()
