"""
Semantic Analyzer Module.
Extracts important terms using TF-IDF + spaCy NLP.
"""

from typing import List, Dict, Any, Tuple
import re
from pathlib import Path
from collections import Counter
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from logger import setup_logger
from config import get_config

logger = setup_logger(__name__)


def load_stop_words(language: str) -> List[str]:
    """Load stop words for given language."""
    stop_words_path = Path(__file__).parent.parent / get_config('semantic_analyzer.stop_words_path', 'stop_words')
    file_path = stop_words_path / f"{language}.txt"
    
    if not file_path.exists():
        logger.warning(f"Stop words file not found: {file_path}")
        return []
    
    with open(file_path, 'r', encoding='utf-8') as f:
        return [line.strip() for line in f if line.strip()]


def get_language_pipeline(language: str):
    """
    Get spaCy language pipeline.
    
    Args:
        language: Language code (uk, en)
    
    Returns:
        spaCy nlp object
    """
    try:
        import spacy
        
        model_map = {
            'uk': 'uk_core_news_sm',
            'en': 'en_core_web_sm'
        }
        
        model_name = model_map.get(language, 'en_core_web_sm')
        
        try:
            nlp = spacy.load(model_name)
            logger.info(f"Loaded spaCy model: {model_name}")
            return nlp
        except OSError:
            logger.error(f"spaCy model {model_name} not found. Run: python -m spacy download {model_name}")
            return None
    
    except ImportError:
        logger.error("spaCy not installed. Install with: pip install spacy")
        return None


def compute_tfidf_terms(
    docs: List[str],
    language: str,
    config: Dict[str, Any]
) -> List[Tuple[str, float]]:
    """
    Compute TF-IDF terms from documents.
    
    Args:
        docs: List of document texts
        language: Language code
        config: Configuration dict
    
    Returns:
        List of (term, score) tuples
    """
    if not docs:
        return []
    
    # Load stop words
    stop_words = load_stop_words(language)
    
    # Get n-gram range from config
    ngrams = get_config('semantic_analyzer.ngrams', [1, 2, 3])
    min_ngram = min(ngrams)
    max_ngram = max(ngrams)
    
    # Create TF-IDF vectorizer
    vectorizer = TfidfVectorizer(
        ngram_range=(min_ngram, max_ngram),
        stop_words=stop_words,
        max_features=get_config('semantic_analyzer.top_terms_limit', 80) * 2,  # Get more, filter later
        lowercase=True,
        min_df=get_config('semantic_analyzer.min_docs_used_in', 3),
        token_pattern=r'(?u)\b[а-яА-ЯіІїЇєЄґҐa-zA-Z][а-яА-ЯіІїЇєЄґҐa-zA-Z\'-]+\b'
    )
    
    try:
        tfidf_matrix = vectorizer.fit_transform(docs)
        feature_names = vectorizer.get_feature_names_out()
        
        # Calculate average TF-IDF score for each term across all documents
        avg_scores = np.asarray(tfidf_matrix.mean(axis=0)).flatten()
        
        # Create term-score pairs
        term_scores = [(feature_names[i], avg_scores[i]) for i in range(len(feature_names))]
        
        # Sort by score descending
        term_scores.sort(key=lambda x: x[1], reverse=True)
        
        logger.info(f"TF-IDF extracted {len(term_scores)} terms from {len(docs)} documents")
        
        return term_scores
    
    except Exception as e:
        logger.error(f"TF-IDF computation failed: {str(e)}")
        return []


def extract_nlp_entities(
    docs: List[str],
    language: str
) -> List[Tuple[str, float]]:
    """
    Extract named entities using spaCy.
    
    Args:
        docs: List of document texts
        language: Language code
    
    Returns:
        List of (entity, salience) tuples
    """
    nlp = get_language_pipeline(language)
    
    if not nlp:
        logger.warning("spaCy not available, skipping entity extraction")
        return []
    
    entity_counter = Counter()
    total_docs = len(docs)
    
    for doc_text in docs:
        # Limit text length to avoid memory issues
        doc_text = doc_text[:100000]
        
        try:
            doc = nlp(doc_text)
            
            # Extract entities with high salience
            for ent in doc.ents:
                if ent.label_ in ['PERSON', 'ORG', 'PRODUCT', 'EVENT', 'GPE', 'LOC']:
                    # Normalize entity text
                    entity_text = ent.text.strip().lower()
                    
                    # Filter out generic words
                    if entity_text not in ['page', 'company', 'website', 'site', 'article']:
                        entity_counter[entity_text] += 1
        
        except Exception as e:
            logger.warning(f"Entity extraction failed for document: {str(e)}")
            continue
    
    # Calculate salience (frequency / total_docs)
    entities = [(entity, count / total_docs) for entity, count in entity_counter.items()]
    
    # Sort by salience
    entities.sort(key=lambda x: x[1], reverse=True)
    
    logger.info(f"Extracted {len(entities)} entities from {total_docs} documents")
    
    return entities


def merge_and_rank_terms(
    tfidf_terms: List[Tuple[str, float]],
    entities: List[Tuple[str, float]],
    config: Dict[str, Any]
) -> List[Dict[str, Any]]:
    """
    Merge TF-IDF terms and entities, rank and filter.
    
    Args:
        tfidf_terms: TF-IDF terms with scores
        entities: NLP entities with salience
        config: Configuration dict
    
    Returns:
        List of term dicts with metadata
    """
    top_limit = get_config('semantic_analyzer.top_terms_limit', 80)
    
    # Combine terms
    all_terms = {}
    
    # Add TF-IDF terms
    for term, score in tfidf_terms:
        all_terms[term] = {
            'term': term,
            'term_normalized': term.lower(),
            'type': 'phrase',
            'score': score
        }
    
    # Add entities (boost their scores slightly)
    for entity, salience in entities:
        if entity in all_terms:
            all_terms[entity]['score'] += salience * 0.5  # Boost existing terms
            all_terms[entity]['type'] = 'entity'
        else:
            all_terms[entity] = {
                'term': entity,
                'term_normalized': entity.lower(),
                'type': 'entity',
                'score': salience
            }
    
    # Sort by score
    ranked_terms = sorted(all_terms.values(), key=lambda x: x['score'], reverse=True)
    
    # Take top N
    top_terms = ranked_terms[:top_limit]
    
    logger.info(f"Merged and ranked {len(top_terms)} terms")
    
    return top_terms


def calculate_term_ranges(
    terms: List[Dict[str, Any]],
    competitor_texts: List[str],
    serp_weights: List[float]
) -> List[Dict[str, Any]]:
    """
    Calculate min/max recommended usage for each term.
    
    Args:
        terms: List of term dicts
        competitor_texts: List of competitor text content
        serp_weights: SERP position weights
    
    Returns:
        List of terms with min/max recommendations
    """
    results = []
    
    for term_dict in terms:
        term = term_dict['term_normalized']
        
        # Count occurrences in each competitor
        occurrences = []
        for i, text in enumerate(competitor_texts):
            # Case-insensitive search
            pattern = re.compile(re.escape(term), re.IGNORECASE)
            count = len(pattern.findall(text))
            occurrences.append(count)
        
        # Skip terms that don't appear in enough documents
        min_docs = get_config('semantic_analyzer.min_docs_used_in', 3)
        docs_used_in = len([c for c in occurrences if c > 0])
        
        if docs_used_in < min_docs:
            continue
        
        # Apply SERP position weights
        if len(serp_weights) >= len(occurrences):
            weights = serp_weights[:len(occurrences)]
        else:
            # Pad with lower weights if needed
            weights = serp_weights + [0.1] * (len(occurrences) - len(serp_weights))
        
        weighted_occurrences = [occurrences[i] * weights[i] for i in range(len(occurrences))]
        
        # Calculate statistics
        if weighted_occurrences:
            # Use weighted median and IQR
            sorted_weighted = sorted([o for o in weighted_occurrences if o > 0])
            
            if len(sorted_weighted) == 0:
                continue
            
            median = np.median(sorted_weighted)
            q1 = np.percentile(sorted_weighted, 25)
            q3 = np.percentile(sorted_weighted, 75)
            iqr = q3 - q1
            
            # Remove outliers (values > Q3 + 2*IQR)
            outlier_threshold = q3 + 2 * iqr
            filtered = [o for o in sorted_weighted if o <= outlier_threshold]
            
            if filtered:
                min_recommended = max(1, int(np.percentile(filtered, 25)))
                max_recommended = max(min_recommended + 1, int(np.percentile(filtered, 75)))
                avg_in_competitors = float(np.mean(filtered))
                median_val = float(np.median(filtered))
            else:
                continue
            
            results.append({
                'term': term_dict['term'],
                'term_normalized': term,
                'type': term_dict['type'],
                'min_recommended': min_recommended,
                'max_recommended': max_recommended,
                'avg_in_competitors': round(avg_in_competitors, 2),
                'median_in_competitors': round(median_val, 2),
                'docs_used_in': docs_used_in,
                'occurrences_by_position': occurrences
            })
    
    logger.info(f"Calculated ranges for {len(results)} terms")
    
    return results


def analyze_competitors(
    competitors_data: List[Dict[str, Any]],
    language: str,
    serp_weights: List[float]
) -> List[Dict[str, Any]]:
    """
    Main function to analyze competitors and extract terms.
    
    Args:
        competitors_data: List of competitor extraction results
        language: Language code
        serp_weights: SERP position weights
    
    Returns:
        List of terms with recommendations
    """
    # Filter valid competitors
    valid_competitors = [c for c in competitors_data if c.get('status') == 'valid']
    
    if not valid_competitors:
        logger.warning("No valid competitors to analyze")
        return []
    
    logger.info(f"Analyzing {len(valid_competitors)} valid competitors")
    
    # Extract texts
    texts = [c['main_text'] for c in valid_competitors]
    
    # Compute TF-IDF terms
    tfidf_terms = compute_tfidf_terms(texts, language, {})
    
    # Extract NLP entities
    entities = extract_nlp_entities(texts, language)
    
    # Merge and rank
    top_terms = merge_and_rank_terms(tfidf_terms, entities, {})
    
    # Calculate ranges
    terms_with_ranges = calculate_term_ranges(top_terms, texts, serp_weights)
    
    return terms_with_ranges


if __name__ == "__main__":
    # Simple test
    test_docs = [
        "Кето дієта це низьковуглеводна дієта. Кето дієта допомагає схуднути.",
        "Схуднення на кето дієті. Низьковуглеводна дієта для здоров'я.",
        "Кето дієта rules: низьковуглеводна їжа, жири, білки."
    ]
    
    tfidf = compute_tfidf_terms(test_docs, 'uk', {})
    print(f"TF-IDF terms: {tfidf[:5]}")
