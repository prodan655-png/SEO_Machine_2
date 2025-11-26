import requests
import json
import time

url = "http://localhost:8001/api/analysis/create"
payload = {
    "keyword": "хліб рецепт",
    "language": "uk",
    "location": "Ukraine",
    "device": "desktop"
}
headers = {
    "Content-Type": "application/json"
}

try:
    print(f"Sending POST to {url}...")
    response = requests.post(url, json=payload)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.text}")
    
    if response.status_code == 201:
        data = response.json()
        analysis_id = data.get("id")
        print(f"Analysis created with ID: {analysis_id}")
        
        # Poll for status
        for i in range(10):
            time.sleep(2)
            status_url = f"http://localhost:8001/api/analysis/{analysis_id}"
            res = requests.get(status_url)
            status_data = res.json()
            status = status_data.get("status")
            print(f"[{i+1}] Status: {status}")
            
            if status in ["completed", "failed"]:
                if status == "failed":
                    print(f"Error: {status_data.get('error_message')}")
                
                print(f"Exit code: {0 if status == 'completed' else 1}")
                
                # Dump full JSON for inspection
                with open("analysis_debug.json", "w", encoding="utf-8") as f:
                    json.dump(status_data, f, indent=2, ensure_ascii=False)
                print("Full analysis saved to analysis_debug.json")
                
                break
except Exception as e:
    print(f"Error: {e}")
