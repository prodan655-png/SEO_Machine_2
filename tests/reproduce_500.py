import requests
import json

url = "http://localhost:8000/api/ai/generate"

payload = {
    "brief": {
        "topic": "Test Topic",
        "keywords": ["test"],
        "target_audience": "General",
        "tone": "professional"
    },
    "tone": "professional",
    "language": "uk",
    "coach_actions": "Make it better"
}

try:
    response = requests.post(url, json=payload)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text}")
except Exception as e:
    print(f"Error: {e}")
