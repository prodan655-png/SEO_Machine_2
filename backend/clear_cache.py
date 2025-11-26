import sqlite3
import os

cache_db = "analysis_cache.db"

if os.path.exists(cache_db):
    conn = sqlite3.connect(cache_db)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM analysis_cache")
    conn.commit()
    count = cursor.rowcount
    conn.close()
    print(f"✅ Cleared {count} entries from analysis cache")
else:
    print("⚠️ Cache database not found")
