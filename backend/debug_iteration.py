import asyncio
import os
import sys
from modules.ai.content_iterator import improve_iteratively
from logger import setup_logger

# Setup logger to print to console
logger = setup_logger('debug_iteration')

async def main():
    print("🚀 Starting Iteration Debug")
    
    # Mock data
    content = """
    <h1>Delicious Cake Recipe</h1>
    <p>This is a simple cake recipe.</p>
    <h2>Ingredients</h2>
    <ul><li>Flour</li><li>Sugar</li></ul>
    """
    
    guidelines = {
        "word_count": {"min": 300, "optimal": 500},
        "headings": {"min": 3, "optimal": 5},
        "paragraphs": {"min": 3, "optimal": 5},
        "images": {"min": 1, "optimal": 2}
    }
    
    terms = [
        {"term": "chocolate", "importance": 10, "recommended_min": 2, "recommended_max": 5, "current": 0, "status": "low"},
        {"term": "baking", "importance": 8, "recommended_min": 1, "recommended_max": 3, "current": 0, "status": "low"}
    ]
    
    current_score = 20
    target_score = 80
    
    try:
        result = await improve_iteratively(
            content,
            guidelines,
            terms,
            current_score,
            target_score,
            max_iterations=3
        )
        
        print("\n✅ Iteration Result:")
        print(f"Success: {result['success']}")
        print(f"Final Score: {result['final_score']}")
        print(f"Iterations: {len(result['iterations'])}")
        
        for i, step in enumerate(result['iterations']):
            print(f"\nStep {i+1}:")
            print(f"  Action: {step['action']}")
            print(f"  Score Delta: {step['score_delta']}")
            print(f"  Success: {step['success']}")
            if not step['success']:
                print(f"  Reason: {step['reason']}")
                
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    sys.path.append(os.getcwd())
    asyncio.run(main())
