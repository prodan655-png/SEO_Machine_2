"""
Integration Test for Iterative Coach System.
Tests the complete flow: content → iteration → improved content.
"""

import asyncio
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from modules.ai.content_iterator import improve_iteratively
from modules.content_scorer import compute_content_score
from database import SessionLocal
from database import Analysis, Term, Guideline


async def test_iterative_improvement():
    """Test the iterative improvement system."""
    
    print("=" * 60)
    print("INTEGRATION TEST: Iterative Coach System")
    print("=" * 60)
    
    # Get a real analysis from DB
    db = SessionLocal()
    try:
        # Find a completed analysis
        analysis = db.query(Analysis).filter(
            Analysis.status == 'COMPLETED'
        ).first()
        
        if not analysis:
            print("❌ No completed analysis found in database")
            return
        
        print(f"\n✅ Using analysis: {analysis.keyword}")
        print(f"   Analysis ID: {analysis.id}")
        
        # Get terms and guidelines
        terms = db.query(Term).filter(Term.analysis_id == analysis.id).all()
        guideline = db.query(Guideline).filter(Guideline.analysis_id == analysis.id).first()
        
        if not guideline:
            print("❌ No guidelines found")
            return
        
        print(f"   Terms: {len(terms)}")
        print(f"   Guidelines: word_count={guideline.word_count_min}-{guideline.word_count_max}")
        
        # Format data
        terms_data = [{
            'term': t.term,
            'term_normalized': t.term_normalized,
            'min_recommended': t.min_recommended,
            'max_recommended': t.max_recommended
        } for t in terms]
        
        guidelines_data = {
            'word_count': {
                'min': guideline.word_count_min,
                'max': guideline.word_count_max,
                'median': guideline.word_count_median
            },
            'headings': {
                'min': guideline.headings_min,
                'max': guideline.headings_max,
                'median': guideline.headings_median
            },
            'images': {
                'min': guideline.images_min,
                'max': guideline.images_max,
                'median': guideline.images_median
            }
        }
        
        # Create test content (intentionally poor)
        test_content = f"""
<h1>{analysis.keyword}</h1>
<p>Це тестова стаття про {analysis.keyword}. Вона дуже коротка і не містить достатньо інформації.</p>
<p>Ще один абзац тексту.</p>
"""
        
        print("\n" + "=" * 60)
        print("INITIAL CONTENT")
        print("=" * 60)
        print(test_content[:200] + "...")
        
        # Calculate initial score
        initial_score_result = compute_content_score(
            test_content,
            guidelines_data,
            terms_data,
            format='html'
        )
        initial_score = initial_score_result['total_score']
        
        print(f"\n📊 Initial Score: {initial_score}/100")
        print(f"   Terms: {initial_score_result['breakdown']['term_coverage']['score']}/60")
        print(f"   Structure: {initial_score_result['breakdown']['structure']['score']}/20")
        print(f"   Headings: {initial_score_result['breakdown']['headings']['score']}/20")
        
        # Run iterative improvement
        print("\n" + "=" * 60)
        print("STARTING ITERATIVE IMPROVEMENT")
        print("=" * 60)
        
        result = await improve_iteratively(
            test_content,
            guidelines_data,
            terms_data,
            initial_score,
            target_score=85,
            max_iterations=5
        )
        
        # Display results
        print("\n" + "=" * 60)
        print("ITERATION RESULTS")
        print("=" * 60)
        
        print(f"\n📈 Score Progress: {result['initial_score']} → {result['final_score']}")
        print(f"🎯 Target: {result['target_score']}")
        print(f"✅ Success: {result['success']}")
        print(f"🔄 Improvements Made: {result['improvements_made']}/{len(result['iterations'])}")
        
        print("\n📋 Iteration Steps:")
        for iteration in result['iterations']:
            status_icon = "✅" if iteration['success'] else "❌"
            delta_sign = "+" if iteration['score_delta'] > 0 else ""
            print(f"\n  {status_icon} Step {iteration['step']}: {iteration['old_score']} → {iteration['new_score']} ({delta_sign}{iteration['score_delta']})")
            print(f"     Action: {iteration['action']}")
            if not iteration['success']:
                print(f"     Reason: {iteration.get('reason', 'Unknown')}")
        
        print("\n" + "=" * 60)
        print("FINAL CONTENT (first 500 chars)")
        print("=" * 60)
        print(result['final_content'][:500] + "...")
        
        # Verify final score
        final_score_result = compute_content_score(
            result['final_content'],
            guidelines_data,
            terms_data,
            format='html'
        )
        
        print("\n📊 Final Score Breakdown:")
        print(f"   Terms: {final_score_result['breakdown']['term_coverage']['score']}/60")
        print(f"   Structure: {final_score_result['breakdown']['structure']['score']}/20")
        print(f"   Headings: {final_score_result['breakdown']['headings']['score']}/20")
        print(f"   TOTAL: {final_score_result['total_score']}/100")
        
        # Validation
        print("\n" + "=" * 60)
        print("VALIDATION")
        print("=" * 60)
        
        if result['final_score'] > result['initial_score']:
            print("✅ Score improved!")
        else:
            print("❌ Score did not improve")
        
        if result['success']:
            print("✅ Target score reached!")
        else:
            print(f"⚠️  Target not reached (got {result['final_score']}, target {result['target_score']})")
        
        if result['improvements_made'] > 0:
            print(f"✅ Made {result['improvements_made']} successful improvements")
        else:
            print("❌ No successful improvements made")
        
        print("\n" + "=" * 60)
        print("TEST COMPLETE")
        print("=" * 60)
        
    finally:
        db.close()


if __name__ == "__main__":
    asyncio.run(test_iterative_improvement())
