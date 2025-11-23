
import os
import sys
import asyncio
from dotenv import load_dotenv

# Add backend to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../backend')))

from modules.ai.ai_client import GeminiClient
from config import get_config

async def test_ai_connection():
    print("Testing AI Connection...")
    
    # Load env
    load_dotenv('.env.development')
    
    api_key = os.getenv('GEMINI_API_KEY')
    print(f"API Key present: {bool(api_key)}")
    
    try:
        client = GeminiClient(api_key=api_key)
        print(f"Client initialized with model: {client.model_name}")
        
        response = await client.generate_content("Hello, are you working?")
        print(f"Response received: {response}")
        print("✅ AI Client is working!")
        
    except Exception as e:
        print(f"❌ AI Client failed: {e}")

if __name__ == "__main__":
    asyncio.run(test_ai_connection())
