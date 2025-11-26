import sys
import os

# Add backend to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from modules.serp_fetcher import fetch_serp

print("Testing fetch_serp logging...")
try:
    fetch_serp("test_log_keyword", count=1)
except Exception as e:
    print(f"Caught expected exception (or unexpected): {e}")

if os.path.exists("debug_serp.log"):
    print("✅ debug_serp.log created successfully.")
    with open("debug_serp.log", "r", encoding="utf-8") as f:
        print(f"Log content:\n{f.read()}")
else:
    print("❌ debug_serp.log NOT found.")
