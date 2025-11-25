"""
Test Analysis Timing Breakdown
Shows which step takes the most time
"""
import sys
import os
import time

sys.path.append(os.path.join(os.getcwd(), 'backend'))

print("Testing Full Analysis Flow...")
print("=" * 60)

keyword = "test timing"
language = "en"
location = "United States"

# Step 1: SERP
print("\n[STEP 1] SERP Fetch...")
start = time.time()
from modules.serp_fetcher import fetch_serp
serp_result = fetch_serp(keyword, language, location, "desktop", count=10)
step1_time = time.time() - start
print(f"✓ Time: {step1_time:.2f}s")
print(f"✓ Results: {len(serp_result.get('results', []))}")

# Step 2: Extract competitors (this is SLOW!)
print("\n[STEP 2] Scraping Competitors...")
start = time.time()
from modules.content_extractor import batch_extract_competitors
import asyncio

urls = [r['url'] for r in serp_result['results'][:5]]  # Test only 5 for speed
print(f"Scraping {len(urls)} URLs...")

results = asyncio.run(batch_extract_competitors(urls))
step2_time = time.time() - start
print(f"✓ Time: {step2_time:.2f}s")
print(f"✓ Valid: {len([r for r in results if r.get('status') == 'valid'])}/{len(results)}")

# Step 3: Analyze terms
print("\n[STEP 3] Term Analysis...")
start = time.time()
from modules.semantic_analyzer import analyze_competitors

serp_weights = [1.0, 0.9, 0.8, 0.7, 0.6]
terms = analyze_competitors(results, language, serp_weights)
step3_time = time.time() - start
print(f"✓ Time: {step3_time:.2f}s")
print(f"✓ Terms: {len(terms)}")

# Summary
print("\n" + "=" * 60)
print("TIMING BREAKDOWN:")
print("=" * 60)
print(f"SERP Fetch:       {step1_time:>6.2f}s ({step1_time/(step1_time+step2_time+step3_time)*100:.1f}%)")
print(f"Scraping:         {step2_time:>6.2f}s ({step2_time/(step1_time+step2_time+step3_time)*100:.1f}%)")
print(f"Term Analysis:    {step3_time:>6.2f}s ({step3_time/(step1_time+step2_time+step3_time)*100:.1f}%)")
print("-" * 60)
print(f"TOTAL:            {step1_time+step2_time+step3_time:>6.2f}s")
print("\nℹ️  Most time is spent on SCRAPING, not SERP!")
