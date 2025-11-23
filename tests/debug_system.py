import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '../backend'))

from database import SessionLocal, Analysis
from modules.ai.ai_client import get_ai_client
import asyncio

def check_db():
    print("Checking Database...")
    db = SessionLocal()
    try:
        analyses = db.query(Analysis).all()
        print(f"Found {len(analyses)} analyses.")
        for a in analyses:
            print(f" - ID: {a.id}, Keyword: {a.keyword}, Status: {a.status}")
    finally:
        db.close()

async def check_ai():
    print("\nChecking AI Client...")
    try:
        client = get_ai_client()
        print(f"AI Client initialized.")
        
        response = await client.generate_content("Say 'Hello' in Ukrainian.")
        print(f"AI Response: {response}")
    except Exception as e:
        print(f"AI Error: {e}")

if __name__ == "__main__":
    check_db()
    asyncio.run(check_ai())
