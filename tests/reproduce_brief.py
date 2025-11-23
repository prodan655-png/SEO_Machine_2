import requests
import json

url = "http://localhost:8000/api/ai/brief"

payload = {
    "analysis_id": "3ba006ea-b616-4ed2-8f1b-374fdc607829",  # Valid UUID from DB
    "tone": "professional"
}

# We need to make sure we have an analysis ID. 
# If this fails with 404 Analysis not found, we know the endpoint is reachable but data is missing.
# If it fails with 500, it's the AI or backend logic.

try:
    print(f"Testing {url}...")
    response = requests.post(url, json=payload)
    print(f"Status: {response.status_code}")
    # print(f"Response: {response.text}")
except Exception as e:
    print(f"Error: {e}")
