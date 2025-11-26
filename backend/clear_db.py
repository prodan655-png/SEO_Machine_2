import sqlite3

# Clear all analyses from database
conn = sqlite3.connect('seo_machine.db')
cursor = conn.cursor()

# Delete all data
cursor.execute("DELETE FROM analyses")
cursor.execute("DELETE FROM competitors")
cursor.execute("DELETE FROM terms")
cursor.execute("DELETE FROM guidelines")
cursor.execute("DELETE FROM drafts")

conn.commit()
print(f"✅ Очищено всі дані з бази даних")
conn.close()
