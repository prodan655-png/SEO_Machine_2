import requests
import json
import os
from dotenv import load_dotenv

# Load env
load_dotenv('.env.development')

api_key = os.getenv('SERPAPI_KEY')
print(f"Loaded API Key: {api_key[:5]}...{api_key[-5:] if api_key else 'None'}")

url = "https://google.serper.dev/search"
payload = json.dumps({
    "q": "seo optimization",
    "gl": "us",
    "hl": "en",
    "num": 10
})
headers = {
    'X-API-KEY': api_key,
    'Content-Type': 'application/json'
}

try:
    print(f"Sending request to {url}...")
    response = requests.request("POST", url, headers=headers, data=payload)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.text[:500]}")
    response.raise_for_status()
    print("✅ API Request Successful")
except Exception as e:
    print(f"❌ API Request Failed: {e}")
