import sqlite3
import sys

db_path = sys.argv[1] if len(sys.argv) > 1 else 'backend/dev_seo_analyzer.db'
analysis_id = sys.argv[2] if len(sys.argv) > 2 else 'e4f15f46-18e2-4421-b657-89f22169097d'

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

print(f"\n=== Checking Analysis: {analysis_id} ===\n")

# Check analysis status
cursor.execute("SELECT status, error_message FROM analyses WHERE id = ?", ( analysis_id,))
result = cursor.fetchone()
if result:
    print(f"Status: {result[0]}")
    if result[1]:
        print(f"Error: {result[1]}")
else:
    print("Analysis not found!")
    sys.exit(1)

# Check terms count
cursor.execute("SELECT COUNT(*) FROM terms WHERE analysis_id = ?", (analysis_id,))
terms_count = cursor.fetchone()[0]
print(f"\nTerms count: {terms_count}")

# Show first 5 terms if any
if terms_count > 0:
    cursor.execute("""
        SELECT term, type, min_recommended, max_recommended 
        FROM terms 
        WHERE analysis_id = ? 
        LIMIT 5
    """, (analysis_id,))
    
    print("\nFirst 5 terms:")
    for row in cursor.fetchall():
        print(f"  - {row[0]} ({row[1]}): {row[2]}-{row[3]}")
else:
    print("  No terms found!")

conn.close()
