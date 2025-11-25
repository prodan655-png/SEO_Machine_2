import os
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent / 'backend'))

# Try loading .env
from dotenv import load_dotenv

env_file = Path('.env.development')
print(f"Looking for: {env_file.absolute()}")
print(f"Exists: {env_file.exists()}")

if env_file.exists():
    load_dotenv(env_file, override=True)
    print("\nLoaded .env.development")
    print(f"AI_ENABLED: {os.getenv('AI_ENABLED')}")
    print(f"GEMINI_API_KEY: {'SET' if os.getenv('GEMINI_API_KEY') else 'NOT SET'}")
    print(f"Key length: {len(os.getenv('GEMINI_API_KEY', ''))}")
    
    # Try importing backend config
    print("\n--- Importing backend config ---")
    try:
        from backend import config
        print(f"config.AI_ENABLED: {config.AI_ENABLED}")
        print(f"config.GEMINI_API_KEY: {'SET' if config.GEMINI_API_KEY else 'NOT SET'}")
        print(f"config.get_config('ai.enabled'): {config.get_config('ai.enabled')}")
        print(f"config.get_config('ai.gemini_api_key'): {'SET' if config.get_config('ai.gemini_api_key') else 'NOT SET'}")
    except Exception as e:
        print(f"Error importing config: {e}")
