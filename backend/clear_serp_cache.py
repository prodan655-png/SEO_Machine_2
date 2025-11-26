import sqlite3

# Clear SERP cache
conn = sqlite3.connect('serp_cache.db')
cursor = conn.cursor()
cursor.execute("DELETE FROM serp_cache")
conn.commit()
rows = cursor.rowcount
conn.close()
print(f"✅ Очищено {rows} записів з SERP кешу")
