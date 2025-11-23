import asyncio
import sys
import os
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'backend'))

from modules.ai.coach import get_seo_coaching
from config import get_config

async def test_coach():
    print("Testing SEO Coach...")
    
    # Check config
    print(f"AI Enabled: {get_config('ai.enabled')}")
    print(f"Gemini Key Present: {bool(get_config('ai.gemini_api_key'))}")
    
    # Mock data
    current_score = 45
    target_score = 85
    
    breakdown = {
        "terms": {"score": 25, "max": 60},
        "structure": {"score": 10, "max": 20},
        "headings": {"score": 10, "max": 20}
    }
    
    term_details = [
        {
            "term": "seo optimization",
            "current": 2,
            "recommended_min": 5,
            "recommended_max": 10,
            "status": "low"
        },
        {
            "term": "keywords",
            "current": 15,
            "recommended_min": 3,
            "recommended_max": 8,
            "status": "high"
        }
    ]
    
    structure_details = {
        "word_count": {
            "current": 500,
            "recommended_min": 1000,
            "recommended_max": 2000
        }
    }
    
    headings_details = {
        "has_h1": True,
        "h2_count": 2,
        "recommended_h2": 5
    }
    
    try:
        result = await get_seo_coaching(
            current_score,
            target_score,
            breakdown,
            term_details,
            structure_details,
            headings_details
        )
        
        print("\nSUCCESS! Result:")
        import json
        print(json.dumps(result, indent=2, ensure_ascii=False))
        
    except Exception as e:
        print(f"\nFAILED: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_coach())
