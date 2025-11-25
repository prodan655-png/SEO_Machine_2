"""
Simple Golden Test Suite for Scoring (No pytest required)
Validates scoring algorithm against known scenarios
"""
import sys
import os

# Setup environment
os.environ['DATABASE_URL'] = 'sqlite:///:memory:'
os.environ['GEMINI_API_KEY'] = 'test'
os.environ['SERP_API_KEY'] = 'test'

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from modules.content_scorer import compute_content_score

# Test configuration
GUIDELINES = {
    'word_count': {'min': 1000, 'max': 2000, 'median': 1500},
    'headings': {'min': 5, 'max': 10, 'median': 7},
    'images': {'min': 2, 'max': 5, 'median': 3}
}

TERMS = [
    {'term': 'SEO', 'term_normalized': 'seo', 'min_recommended': 8, 'max_recommended': 15},
    {'term': 'content', 'term_normalized': 'content', 'min_recommended': 10, 'max_recommended': 20},
    {'term': 'optimization', 'term_normalized': 'optimization', 'min_recommended': 5, 'max_recommended': 10},
]

def test(name, article, expected_min, expected_max):
    """Run a single test"""
    print(f"\n[TEST] {name}")
    result = compute_content_score(article, GUIDELINES, TERMS, 'html')
    score = result['total_score']
    version = result.get('scoring_version', 'N/A')
    
    passed = expected_min <= score <= expected_max
    status = "✅ PASS" if passed else "❌ FAIL"
    
    print(f"  Score: {score}/100 (version {version})")
    print(f"  Expected: {expected_min}-{expected_max}")
    print(f"  {status}")
    
    return passed

# Run tests
print("=" * 60)
print("GOLDEN TEST SUITE - Scoring Validation")
print("=" * 60)

results = []

# Test 1: Perfect article
perfect = """
<h1>SEO Content Optimization</h1>
<p>SEO content optimization techniques. """ + " SEO content optimization " * 50 + """ optimization SEO content.</p>
<h2>Content Strategy</h2>
<p>Content SEO optimization strategies. """ + " content SEO optimization " * 40 + """</p>
<img src="img1.jpg"><img src="img2.jpg"><img src="img3.jpg">
<h2>SEO Techniques</h2>
<p>SEO optimization content techniques. """ + " SEO content optimization " * 40 + """</p>
<h2>Optimization Methods</h2>
<p>Content optimization methods. """ + " optimization content SEO " * 40 + """</p>
<h2>Advanced SEO</h2>
<p>Advanced content optimization. """ + " SEO content optimization " * 40 + """</p>
<h2>Best Practices</h2>
<p>SEO content best practices. """ + " optimization content SEO " * 40 + """</p>
"""
results.append(test("Perfect Article", perfect, 80, 100))

# Test 2: Missing terms
missing_terms = """
<h1>General Guide</h1>
""" + "<p>Generic filler text. " * 200 + "</p>" + """
<h2>Section One</h2>
<p>More generic content here.</p>
<h2>Section Two</h2>
<p>Additional generic information.</p>
<img src="img.jpg"><img src="img2.jpg">
"""
results.append(test("Missing Terms", missing_terms, 30, 60))

# Test 3: Short content
short = """
<h1>SEO Guide</h1>
<p>SEO content optimization. Content SEO optimization techniques.</p>
<h2>Introduction</h2>
<p>SEO and content optimization basics.</p>
<img src="img.jpg">
"""
results.append(test("Short Content", short, 20, 50))

# Summary
print("\n" + "=" * 60)
print("SUMMARY")
print("=" * 60)
passed = sum(results)
total = len(results)
print(f"Tests passed: {passed}/{total}")

if passed == total:
    print("✅ All golden tests passed!")
    sys.exit(0)
else:
    print("⚠️ Some tests failed - review scoring logic")
    sys.exit(1)
