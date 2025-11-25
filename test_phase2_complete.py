"""
Phase 2 Testing Script
Tests: SERP Caching, Playwright, Semantic Similarity
"""
import sys
import os
import time

sys.path.append(os.path.join(os.getcwd(), 'backend'))

print("=" * 60)
print("PHASE 2 TESTING")
print("=" * 60)

# Test 1: SERP Cache
print("\n[TEST 1] SERP Caching...")
print("-" * 60)

from modules.serp_fetcher import fetch_serp
from config import SERP_CACHE_ENABLED

print(f"Cache Enabled: {SERP_CACHE_ENABLED}")

keyword = "test cache phase2"
print(f"Testing keyword: '{keyword}'")

# First fetch
print("\n1st Fetch (should be slow, API call)...")
start = time.time()
try:
    result1 = fetch_serp(keyword, language="en", location="United States", device="desktop", count=10)
    duration1 = time.time() - start
    print(f"   ✓ Duration: {duration1:.2f}s")
    print(f"   ✓ Results: {len(result1.get('results', []))}")
except Exception as e:
    print(f"   ✗ Error: {e}")
    duration1 = -1

# Second fetch (should hit cache)
print("\n2nd Fetch (should be instant, < 0.1s)...")
start = time.time()
try:
    result2 = fetch_serp(keyword, language="en", location="United States", device="desktop", count=10)
    duration2 = time.time() - start
    print(f"   ✓ Duration: {duration2:.2f}s")
    print(f"   ✓ Results: {len(result2.get('results', []))}")
    
    if duration2 < 0.1:
        print("   ✅ CACHE HIT! (Instant response)")
    else:
        print(f"   ⚠️ CACHE MISS or SLOW (expected < 0.1s, got {duration2:.2f}s)")
        
except Exception as e:
    print(f"   ✗ Error: {e}")
    duration2 = -1

# Test 2: Check cache DB
print("\n[TEST 2] Cache Database...")
print("-" * 60)
import sqlite3
from pathlib import Path

cache_db = Path(__file__).parent / 'backend' / 'serp_cache.db'
if cache_db.exists():
    print(f"✓ Cache DB exists: {cache_db}")
    try:
        conn = sqlite3.connect(cache_db)
        cursor = conn.execute("SELECT COUNT(*) FROM serp_cache")
        count = cursor.fetchone()[0]
        print(f"✓ Cache entries: {count}")
        conn.close()
    except Exception as e:
        print(f"✗ DB Error: {e}")
else:
    print(f"✗ Cache DB not found at: {cache_db}")

# Test 3: Playwright
print("\n[TEST 3] Playwright Extraction...")
print("-" * 60)

try:
    from modules.content_extractor import PlaywrightExtractor
    
    extractor = PlaywrightExtractor()
    print("Testing on example.com...")
    
    start = time.time()
    content = extractor.fetch_content("https://example.com", timeout=10000)
    duration = time.time() - start
    
    print(f"✓ Fetched {len(content)} bytes in {duration:.2f}s")
    if "Example Domain" in content:
        print("✅ Playwright works! Content verified.")
    else:
        print("⚠️ Content verification failed")
        
except Exception as e:
    print(f"✗ Playwright Error: {e}")

# Test 4: Semantic Similarity
print("\n[TEST 4] Semantic Similarity...")
print("-" * 60)

try:
    from modules.semantic_analyzer import SemanticAnalyzer
    
    analyzer = SemanticAnalyzer()
    
    text1 = "How to lose weight with keto diet"
    text2 = "Losing weight using ketogenic low-carb nutrition"
    
    similarity = analyzer.calculate_similarity(text1, text2)
    
    print(f"Text 1: {text1}")
    print(f"Text 2: {text2}")
    print(f"Similarity: {similarity:.3f}")
    
    if similarity > 0.5:
        print("✅ Semantic analysis works! Texts are semantically similar.")
    else:
        print("⚠️ Low similarity (might be using fallback method)")
        
except Exception as e:
    print(f"✗ Semantic Error: {e}")

# Summary
print("\n" + "=" * 60)
print("SUMMARY")
print("=" * 60)

if duration1 > 0 and duration2 > 0:
    speedup = duration1 / duration2 if duration2 > 0 else 0
    print(f"SERP 1st call: {duration1:.2f}s")
    print(f"SERP 2nd call: {duration2:.2f}s")
    print(f"Speedup: {speedup:.1f}x")
    
    if duration2 < 0.5:
        print("✅ Caching works!")
    else:
        print("⚠️ Caching might not be working properly")
        print("   Check: SERP_CACHE_ENABLED in .env.development")

print("\nDone!")
