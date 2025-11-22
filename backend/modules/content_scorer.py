"""
Content Scorer Module.
Scores draft content against guidelines and terms (0-100).
"""

from typing import Dict, List, Any
import re
from bs4 import BeautifulSoup
import markdown
from logger import setup_logger
from config import get_config

logger = setup_logger(__name__)


def parse_draft_content(text: str, format: str = "html") -> Dict[str, Any]:
    """
    Parse draft text to extract metrics.
    
    Args:
        text: Draft content
        format: 'html' or 'markdown'
    
    Returns:
        Dict with extracted metrics
    """
    if format == "markdown":
        # Convert markdown to HTML first
        html = markdown.markdown(text)
    else:
        html = text
    
    soup = BeautifulSoup(html, 'lxml')
    
    # Extract headings
    headings = []
    for tag in ['h1', 'h2', 'h3']:
        for heading in soup.find_all(tag):
            headings.append({
                'level': tag,
                'text': heading.get_text(strip=True)
            })
    
    # Get plain text
    plain_text = soup.get_text(separator=' ', strip=True)
    plain_text = re.sub(r'\s+', ' ', plain_text)
    
    # Count metrics
    words = plain_text.split()
    word_count = len(words)
    
    paragraphs = soup.find_all('p')
    paragraph_count = len([p for p in paragraphs if p.get_text(strip=True)])
    
    images = soup.find_all('img')
    image_count = len(images)
    
    return {
        'plain_text': plain_text,
        'word_count': word_count,
        'paragraph_count': paragraph_count,
        'image_count': image_count,
        'headings': headings,
        'has_h1': any(h['level'] == 'h1' for h in headings),
        'h2_h3_count': len([h for h in headings if h['level'] in ['h2', 'h3']])
    }


def calculate_term_coverage_score(
    draft_text: str,
    terms: List[Dict[str, Any]],
    config: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Calculate term coverage score (0-60 points).
    
    Args:
        draft_text: Plain text of draft
        terms: List of term dicts with min/max recommendations
        config: Configuration dict
    
    Returns:
        Dict with score and term details
    """
    max_score = get_config('scoring.weights.terms', 60)
    
    if not terms:
        return {
            'score': 0,
            'max': max_score,
            'term_details': []
        }
    
    draft_lower = draft_text.lower()
    term_details = []
    total_term_score = 0.0
    
    over_optimization_multiplier = get_config('scoring.term_coverage.over_optimization_multiplier', 1.5)
    
    for term_dict in terms:
        term = term_dict['term_normalized']
        min_rec = term_dict['min_recommended']
        max_rec = term_dict['max_recommended']
        
        # Count occurrences
        pattern = re.compile(re.escape(term), re.IGNORECASE)
        matches = pattern.findall(draft_text)
        current_count = len(matches)
        
        # Find positions
        positions = [m.start() for m in pattern.finditer(draft_text)]
        
        # Calculate term score
        if current_count >= min_rec and current_count <= max_rec:
            # Perfect - full points for this term
            term_score = 1.0
            status = "ok"
        elif current_count < min_rec:
            # Under-optimized - proportional score
            term_score = current_count / min_rec if min_rec > 0 else 0
            status = "low"
        elif current_count > max_rec * over_optimization_multiplier:
            # Over-optimized - penalty
            term_score = 0.0
            status = "high"
        else:
            # Slightly over - reduced score
            over_amount = current_count - max_rec
            penalty = over_amount / max_rec
            term_score = max(0.5, 1.0 - penalty)
            status = "high"
        
        total_term_score += term_score
        
        term_details.append({
            'term': term_dict['term'],
            'recommended_min': min_rec,
            'recommended_max': max_rec,
            'current': current_count,
            'status': status,
            'term_score': round(term_score, 3),
            'positions': positions[:10]  # Limit to first 10
        })
    
    # Calculate final score
    if terms:
        avg_term_score = total_term_score / len(terms)
        final_score = int(avg_term_score * max_score)
    else:
        final_score = 0
    
    return {
        'score': final_score,
        'max': max_score,
        'term_details': term_details
    }


def calculate_structure_score(
    draft_metrics: Dict[str, Any],
    guidelines: Dict[str, Any],
    config: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Calculate structure score (0-20 points).
    
    Args:
        draft_metrics: Metrics from parse_draft_content
        guidelines: Guidelines dict
        config: Configuration dict
    
    Returns:
        Dict with score and details
    """
    max_score = get_config('scoring.weights.structure', 20)
    word_count_weight = get_config('scoring.structure.word_count_weight', 10)
    images_weight = get_config('scoring.structure.images_weight', 5)
    paragraphs_weight = get_config('scoring.structure.paragraphs_weight', 5)
    
    # Word count sub-score
    wc = draft_metrics['word_count']
    wc_min = guidelines['word_count']['min']
    wc_max = guidelines['word_count']['max']
    
    if wc >= wc_min and wc <= wc_max:
        wc_score = word_count_weight
    elif wc < wc_min:
        # Linear decrease
        wc_score = (wc / wc_min) * word_count_weight if wc_min > 0 else 0
    else:
        # Plateau above max (not penalized much)
        wc_score = word_count_weight * 0.9
    
    # Images sub-score
    img = draft_metrics['image_count']
    img_min = guidelines['images']['min']
    img_max = guidelines['images']['max']
    
    if img >= img_min and img <= img_max:
        img_score = images_weight
    elif img < img_min:
        img_score = (img / img_min) * images_weight if img_min > 0 else 0
    else:
        img_score = images_weight * 0.8  # Slight penalty for too many
    
    # Paragraphs sub-score (reasonable paragraph count)
    para = draft_metrics['paragraph_count']
    expected_paragraphs = wc / 100  # Rough estimate: 100 words per paragraph
    
    if para >= expected_paragraphs * 0.5:
        para_score = paragraphs_weight
    else:
        para_score = (para / expected_paragraphs) * paragraphs_weight if expected_paragraphs > 0 else 0
    
    total_score = int(wc_score + img_score + para_score)
    
    return {
        'score': min(total_score, max_score),
        'max': max_score,
        'word_count': {
            'current': wc,
            'recommended': f"{wc_min}-{wc_max}",
            'score': int(wc_score)
        },
        'images': {
            'current': img,
            'recommended': f"{img_min}-{img_max}",
            'score': int(img_score)
        },
        'paragraphs': {
            'current': para,
            'score': int(para_score)
        }
    }


def calculate_headings_score(
    draft_headings: List[Dict[str, str]],
    guidelines: Dict[str, Any],
    terms: List[Dict[str, Any]],
    config: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Calculate headings score (0-20 points).
    
    Args:
        draft_headings: List of heading dicts
        guidelines: Guidelines dict
        terms: List of terms
        config: Configuration dict
    
    Returns:
        Dict with score and details
    """
    max_score = get_config('scoring.weights.headings', 20)
    h1_weight = get_config('scoring.headings.h1_weight', 5)
    h2_h3_count_weight = get_config('scoring.headings.h2_h3_count_weight', 10)
    terms_in_headings_weight = get_config('scoring.headings.terms_in_headings_weight', 5)
    
    # H1 presence and relevance
    h1_list = [h for h in draft_headings if h['level'] == 'h1']
    
    if h1_list:
        h1_score = h1_weight
        h1_present = True
    else:
        h1_score = 0
        h1_present = False
    
    # H2/H3 count
    h2_h3_list = [h for h in draft_headings if h['level'] in ['h2', 'h3']]
    h2_h3_count = len(h2_h3_list)
    
    h_min = guidelines['headings']['min']
    h_max = guidelines['headings']['max']
    
    if h2_h3_count >= h_min and h2_h3_count <= h_max:
        h_count_score = h2_h3_count_weight
    elif h2_h3_count < h_min:
        h_count_score = (h2_h3_count / h_min) * h2_h3_count_weight if h_min > 0 else 0
    else:
        h_count_score = h2_h3_count_weight * 0.8
    
    # Terms in headings bonus
    heading_texts = ' '.join([h['text'].lower() for h in draft_headings])
    terms_in_headings = 0
    
    for term_dict in terms[:10]:  # Check top 10 terms
        term = term_dict['term_normalized']
        if term in heading_texts:
            terms_in_headings += 1
    
    terms_score = min(terms_in_headings * 1.5, terms_in_headings_weight)
    
    total_score = int(h1_score + h_count_score + terms_score)
    
    return {
        'score': min(total_score, max_score),
        'max': max_score,
        'h1_present': h1_present,
        'h1_score': int(h1_score),
        'h2_h3_count': {
            'current': h2_h3_count,
            'recommended': f"{h_min}-{h_max}",
            'score': int(h_count_score)
        },
        'terms_in_headings': terms_in_headings,
        'terms_in_headings_score': int(terms_score)
    }


def compute_content_score(
    draft_text: str,
    guidelines: Dict[str, Any],
    terms: List[Dict[str, Any]],
    format: str = "html"
) -> Dict[str, Any]:
    """
    Main scoring function. Computes overall content score (0-100).
    
    Args:
        draft_text: Draft content text
        guidelines: Guidelines from generator
        terms: Terms from semantic analyzer
        format: 'html' or 'markdown'
    
    Returns:
        Complete score breakdown
    """
    # Parse draft
    draft_metrics = parse_draft_content(draft_text, format)
    
    # Calculate sub-scores
    term_coverage = calculate_term_coverage_score(
        draft_metrics['plain_text'],
        terms,
        {}
    )
    
    structure = calculate_structure_score(
        draft_metrics,
        guidelines,
        {}
    )
    
    headings = calculate_headings_score(
        draft_metrics['headings'],
        guidelines,
        terms,
        {}
    )
    
    # Total score
    total_score = term_coverage['score'] + structure['score'] + headings['score']
    
    result = {
        'total_score': total_score,
        'breakdown': {
            'term_coverage': {
                'score': term_coverage['score'],
                'max': term_coverage['max']
            },
            'structure': {
                'score': structure['score'],
                'max': structure['max']
            },
            'headings': {
                'score': headings['score'],
                'max': headings['max']
            }
        },
        'term_details': term_coverage['term_details'],
        'structure_details': structure,
        'headings_details': headings
    }
    
    logger.info(f"Content score: {total_score}/100 (terms={term_coverage['score']}, structure={structure['score']}, headings={headings['score']})")
    
    return result


if __name__ == "__main__":
    # Test with simple example
    test_draft = """
    <h1>Кето дієта: повний гід</h1>
    <p>Кето дієта - це низьковуглеводна дієта для схуднення.</p>
    <h2>Що таке кето дієта</h2>
    <p>Кето дієта базується на низьковуглеводному харчуванні.</p>
    """
    
    test_guidelines = {
        'word_count': {'min': 20, 'max': 50, 'median': 30},
        'headings': {'min': 2, 'max': 5, 'median': 3},
        'images': {'min': 0, 'max': 2, 'median': 1}
    }
    
    test_terms = [
        {'term': 'кето дієта', 'term_normalized': 'кето дієта', 'min_recommended': 2, 'max_recommended': 4},
        {'term': 'низьковуглеводна', 'term_normalized': 'низьковуглеводна', 'min_recommended': 1, 'max_recommended': 3}
    ]
    
    score = compute_content_score(test_draft, test_guidelines, test_terms, 'html')
    print(f"Total score: {score['total_score']}")
    print(f"Breakdown: {score['breakdown']}")
