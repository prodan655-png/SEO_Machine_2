import requests
import time
import json
import sys

BASE_URL = "http://127.0.0.1:8000"

def reproduce_error():
    print("1. Creating analysis...")
    try:
        resp = requests.post(f"{BASE_URL}/api/analysis/create", json={
            "keyword": "test keyword",
            "language": "uk",
            "location": "Ukraine",
            "device": "desktop"
        })
        resp.raise_for_status()
        data = resp.json()
        analysis_id = data["analysis_id"]
        print(f"Analysis created: {analysis_id}")
        
        # Wait a bit for background tasks
        print("Waiting 2 seconds...")
        time.sleep(2)
        
        print("2. Triggering Brief Generation (expecting 500)...")
        brief_resp = requests.post(f"{BASE_URL}/api/ai/brief", json={
            "analysis_id": analysis_id,
            "tone": "professional"
        })
        
        print(f"Status Code: {brief_resp.status_code}")
        print(f"Response: {brief_resp.text}")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    # Wait for server to be ready
    print("Waiting for server to be ready...")
    for _ in range(10):
        try:
            requests.get(f"{BASE_URL}/health")
            print("Server is ready!")
            break
        except:
            time.sleep(1)
    else:
        print("Server did not start in time.")
        sys.exit(1)

    reproduce_error()
