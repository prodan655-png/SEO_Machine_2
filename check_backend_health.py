import requests
import sys

def check_backend():
    url = "http://localhost:8000/health"
    print(f"Checking {url}...")
    try:
        response = requests.get(url, timeout=5)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        if response.status_code == 200:
            print("✅ Backend is accessible via localhost")
        else:
            print("❌ Backend returned error")
    except Exception as e:
        print(f"❌ Failed to connect to localhost: {e}")

    url_ip = "http://127.0.0.1:8000/health"
    print(f"\nChecking {url_ip}...")
    try:
        response = requests.get(url_ip, timeout=5)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        if response.status_code == 200:
            print("✅ Backend is accessible via 127.0.0.1")
        else:
            print("❌ Backend returned error")
    except Exception as e:
        print(f"❌ Failed to connect to 127.0.0.1: {e}")

if __name__ == "__main__":
    check_backend()
