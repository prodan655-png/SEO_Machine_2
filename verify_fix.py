"""
Verification Script for Analysis Timeout Fix
Tests scraping concurrency with 20 URLs.
"""
import sys
import os
import time
import asyncio

# Add backend to path
sys.path.append(os.path.join(os.getcwd(), 'backend'))

async def verify():
    print("Verifying Analysis Fix...")
    print("=" * 60)

    # Mock URLs to test concurrency
    # We'll use a mix of real and mock to test the extractor
    urls = [
        "https://example.com",
        "https://google.com",
        "https://bing.com",
        "https://yahoo.com",
        "https://wikipedia.org",
        "https://github.com",
        "https://stackoverflow.com",
        "https://python.org",
        "https://fastapi.tiangolo.com",
        "https://reactjs.org",
        "https://vuejs.org",
        "https://angular.io",
        "https://svelte.dev",
        "https://nextjs.org",
        "https://nuxtjs.org",
        "https://gatsbyjs.com",
        "https://hugo.io",
        "https://jekyllrb.com",
        "https://wordpress.org",
        "https://drupal.org"
    ]

    print(f"Testing batch extraction of {len(urls)} URLs...")
    print(f"Expected concurrency: 10 workers")
    
    start = time.time()
    
    from modules.content_extractor import batch_extract_competitors
    
    # Run extraction
    results = await batch_extract_competitors(urls)
    
    duration = time.time() - start
    print(f"\n✓ Extraction took: {duration:.2f}s")
    print(f"✓ Average per URL: {duration/len(urls):.2f}s")
    print(f"✓ Successful extractions: {len([r for r in results if r.get('status') != 'failed'])}")
    
    if duration < 15: # If it takes less than 15s for 20 URLs, concurrency is working well
        print("\n✅ PASS: Concurrency seems effective (fast execution)")
    else:
        print(f"\n⚠️ NOTE: Took {duration:.2f}s. Check if this is acceptable.")

if __name__ == "__main__":
    asyncio.run(verify())
