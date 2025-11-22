"""
Guidelines Generator Module.
Generates content guidelines based on competitor analysis.
"""

from typing import List, Dict, Any, Tuple
import numpy as np
from logger import setup_logger
from config import get_config

logger = setup_logger(__name__)


def calculate_metric_ranges(
    values: List[float],
    serp_weights: List[float],
    remove_outliers: bool = True
) -> Dict[str, Any]:
    """
    Calculate min/max ranges for a metric with outlier detection.
    
    Args:
        values: List of metric values from competitors
        serp_weights: SERP position weights
        remove_outliers: Whether to remove outliers using IQR
    
    Returns:
        Dict with min, max, median, confidence
    """
    if not values:
        return {'min': 0, 'max': 0, 'median': 0, 'confidence': 0.0}
    
    # Apply SERP weights
    if len(serp_weights) >= len(values):
        weights = serp_weights[:len(values)]
    else:
        weights = serp_weights + [0.1] * (len(values) - len(serp_weights))
    
    weighted_values = [values[i] * weights[i] for i in range(len(values))]
    
    if remove_outliers and len(weighted_values) > 3:
        # Calculate IQR
        q1 = np.percentile(weighted_values, 25)
        q3 = np.percentile(weighted_values, 75)
        iqr = q3 - q1
        
        # Remove outliers
        multiplier = get_config('outlier_detection.word_count_iqr_multiplier', 1.5)
        lower_bound = q1 - multiplier * iqr
        upper_bound = q3 + multiplier * iqr
        
        filtered = [v for v in weighted_values if lower_bound <= v <= upper_bound]
        
        if filtered:
            weighted_values = filtered
    
    # Calculate statistics
    median_val = int(np.median(weighted_values))
    min_val = max(1, int(np.percentile(weighted_values, 25)))
    max_val = max(min_val + 1, int(np.percentile(weighted_values, 75)))
    
    # Calculate confidence based on data quality
    confidence = min(1.0, len(values) / 10.0)  # Full confidence with 10+ competitors
    
    return {
        'min': min_val,
        'max': max_val,
        'median': median_val,
        'confidence': round(confidence, 2)
    }


def extract_common_headings(
    competitors_data: List[Dict[str, Any]],
    serp_weights: List[float]
) -> List[Dict[str, Any]]:
    """
    Extract common H2/H3 headings from competitors.
    
    Args:
        competitors_data: List of competitor data with headings
        serp_weights: SERP position weights
    
    Returns:
        List of common headings with frequency and position
    """
    heading_counter = {}
    
    for i, competitor in enumerate(competitors_data):
        headings = competitor.get('headings', [])
        weight = serp_weights[i] if i < len(serp_weights) else 0.1
        
        for heading in headings:
            if heading['level'] in ['h2', 'h3']:
                text = heading['text'].lower().strip()
                
                # Skip very short headings
                if len(text) < 5:
                    continue
                
                if text not in heading_counter:
                    heading_counter[text] = {
                        'heading': heading['text'],  # Original case
                        'frequency': 0,
                        'weighted_positions': []
                    }
                
                heading_counter[text]['frequency'] += 1
                heading_counter[text]['weighted_positions'].append(i * weight)
    
    # Calculate average position for each heading
    common_headings = []
    for data in heading_counter.values():
        if data['frequency'] >= 2:  # Appears in at least 2 competitors
            avg_position = np.mean(data['weighted_positions']) if data['weighted_positions'] else 0
            common_headings.append({
                'heading': data['heading'],
                'frequency': data['frequency'],
                'avg_position': round(avg_position, 2)
            })
    
    # Sort by frequency (descending), then by average position (ascending)
    common_headings.sort(key=lambda x: (-x['frequency'], x['avg_position']))
    
    logger.info(f"Extracted {len(common_headings)} common headings")
    
    return common_headings


def generate_guidelines(
    competitors_data: List[Dict[str, Any]],
    serp_weights: List[float]
) -> Dict[str, Any]:
    """
    Generate content guidelines from competitor analysis.
    
    Args:
        competitors_data: List of competitor extraction results
        serp_weights: SERP position weights
    
    Returns:
        Guidelines dict with ranges and suggestions
    """
    # Filter valid competitors
    valid_competitors = [c for c in competitors_data if c.get('status') == 'valid']
    
    competitors_count = len(valid_competitors)
    min_competitors = get_config('guidelines.min_competitors', 3)
    
    warnings = []
    is_thin_serp = competitors_count < min_competitors
    
    if is_thin_serp:
        warnings.append(f"Thin SERP: only {competitors_count} valid competitors (min {min_competitors} recommended)")
        logger.warning(f"Thin SERP detected: {competitors_count} competitors")
    
    if competitors_count == 0:
        logger.error("No valid competitors for guidelines generation")
        return {
            'word_count': {'min': 500, 'max': 1500, 'median': 1000, 'confidence': 0.0},
            'headings': {'min': 3, 'max': 8, 'median': 5, 'confidence': 0.0},
            'images': {'min': 1, 'max': 5, 'median': 2, 'confidence': 0.0},
            'suggested_outline': [],
            'warnings': ['No valid competitors found'],
            'competitors_analyzed': 0
        }
    
    # Extract metrics
    word_counts = [c['word_count'] for c in valid_competitors]
    heading_counts = [len(c.get('headings', [])) for c in valid_competitors]
    image_counts = [c.get('image_count', 0) for c in valid_competitors]
    
    # Calculate ranges
    word_count_range = calculate_metric_ranges(word_counts, serp_weights, remove_outliers=True)
    headings_range = calculate_metric_ranges(heading_counts, serp_weights, remove_outliers=False)
    images_range = calculate_metric_ranges(image_counts, serp_weights, remove_outliers=False)
    
    # Adjust ranges for thin SERP
    if is_thin_serp:
        multiplier = get_config('guidelines.thin_serp_range_multiplier', 1.3)
        
        word_count_range['min'] = int(word_count_range['min'] / multiplier)
        word_count_range['max'] = int(word_count_range['max'] * multiplier)
        
        headings_range['min'] = max(1, int(headings_range['min'] / multiplier))
        headings_range['max'] = int(headings_range['max'] * multiplier)
        
        # Lower confidence for thin SERP
        word_count_range['confidence'] *= 0.7
        headings_range['confidence'] *= 0.7
        images_range['confidence'] *= 0.7
    
    # Extract common headings
    common_headings = extract_common_headings(valid_competitors, serp_weights)
    suggested_outline = [h['heading'] for h in common_headings[:10]]  # Top 10
    
    guidelines = {
        'word_count': word_count_range,
        'headings': headings_range,
        'images': images_range,
        'suggested_outline': suggested_outline,
        'warnings': warnings,
        'competitors_analyzed': competitors_count
    }
    
    logger.info(f"Generated guidelines from {competitors_count} competitors")
    logger.info(f"  Word count: {word_count_range['min']}-{word_count_range['max']}")
    logger.info(f"  Headings: {headings_range['min']}-{headings_range['max']}")
    logger.info(f"  Images: {images_range['min']}-{images_range['max']}")
    
    return guidelines


if __name__ == "__main__":
    # Test with synthetic data
    test_competitors = [
        {'status': 'valid', 'word_count': 1500, 'headings': [{'level': 'h1', 'text': 'Title'}, {'level': 'h2', 'text': 'Section 1'}], 'image_count': 3},
        {'status': 'valid', 'word_count': 1800, 'headings': [{'level': 'h1', 'text': 'Title'}, {'level': 'h2', 'text': 'Section 1'}, {'level': 'h2', 'text': 'Section 2'}], 'image_count': 4},
        {'status': 'valid', 'word_count': 1600, 'headings': [{'level': 'h2', 'text': 'Section 1'}], 'image_count': 2},
    ]
    
    weights = [1.0, 0.9, 0.8]
    
    guidelines = generate_guidelines(test_competitors, weights)
    print(f"Word count: {guidelines['word_count']}")
    print(f"Headings: {guidelines['headings']}")
    print(f"Warnings: {guidelines['warnings']}")
