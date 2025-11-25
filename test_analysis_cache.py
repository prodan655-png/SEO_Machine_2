"""
Test Analysis Caching End-to-End
"""
import requests
import time

BASE_URL = "http://localhost:8000"

print("=" * 60)
print("TESTING ANALYSIS CACHING")
print("=" * 60)

keyword = "cache test keyword"
data = {
    "keyword": keyword,
    "language": "en",
    "location": "United States",
    "device": "desktop"
}

# Test 1: First analysis (should process normally)
print("\n[TEST 1] First Analysis (should take 7-15s)...")
print("-" * 60)
start = time.time()

response1 = requests.post(f"{BASE_URL}/api/analysis/create", json=data)
duration1 = time.time() - start

print(f"Response: {response1.status_code}")
result1 = response1.json()
print(f"Status: {result1.get('status')}")
print(f"Analysis ID: {result1.get('id')}")
print(f"Duration: {duration1:.2f}s")

if result1.get('status') == 'processing':
    print("\nℹ️  Analysis started, waiting for completion...")
    
    # Wait for analysis to complete
    analysis_id = result1['id']
    max_wait = 60  # 60 seconds max
    start_wait = time.time()
    
    while time.time() - start_wait < max_wait:
        check_response = requests.get(f"{BASE_URL}/api/analysis/{analysis_id}")
        if check_response.ok:
            check_data = check_response.json()
            if check_data.get('status') == 'completed':
                print(f"✅ Analysis completed in {time.time() - start:.2f}s total")
                break
        time.sleep(2)
    else:
        print("⚠️ Analysis did not complete in time")

# Test 2: Second analysis with SAME keyword (should hit cache!)
print("\n[TEST 2] Second Analysis (should be instant!)...")
print("-" * 60)
start = time.time()

response2 = requests.post(f"{BASE_URL}/api/analysis/create", json=data)
duration2 = time.time() - start

print(f"Response: {response2.status_code}")
result2 = response2.json()
print(f"Status: {result2.get('status')}")
print(f"Analysis ID: {result2.get('id')}")
print(f"Duration: {duration2:.2f}s")

# Summary
print("\n" + "=" * 60)
print("RESULTS:")
print("=" * 60)
print(f"1st Call: {duration1:.2f}s (status: {result1.get('status')})")
print(f"2nd Call: {duration2:.2f}s (status: {result2.get('status')})")

if duration2 < 1.0 and result2.get('status') == 'completed':
    speedup = duration1 / duration2 if duration2 > 0 else 0
    print(f"\n✅ CACHE WORKS! Second call was {speedup:.0f}x faster!")
    print("   Analysis returned instantly from cache.")
else:
    print("\n⚠️ Cache might not be working:")
    print(f"   Expected: < 1s with status='completed'")
    print(f"   Got: {duration2:.2f}s with status='{result2.get('status')}'")

print("\nDone!")
