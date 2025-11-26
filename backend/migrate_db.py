"""
Quick migration script to add missing columns to competitors table.
"""
import sqlite3

db_path = "seo_machine.db"

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Check if columns exist
cursor.execute("PRAGMA table_info(competitors)")
columns = [col[1] for col in cursor.fetchall()]

print(f"Existing columns: {columns}")

# Add missing columns
if 'snippet' not in columns:
    print("Adding column: snippet")
    cursor.execute("ALTER TABLE competitors ADD COLUMN snippet TEXT")
    
if 'favicon_url' not in columns:
    print("Adding column: favicon_url")
    cursor.execute("ALTER TABLE competitors ADD COLUMN favicon_url VARCHAR(500)")
    
if 'thumbnail_url' not in columns:
    print("Adding column: thumbnail_url")
    cursor.execute("ALTER TABLE competitors ADD COLUMN thumbnail_url VARCHAR(500)")

conn.commit()
conn.close()

print("✅ Migration completed!")
