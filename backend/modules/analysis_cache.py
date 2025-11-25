"""
Analysis Cache Module
Caches complete analysis results to avoid re-scraping competitors
"""

import sqlite3
import json
import hashlib
from pathlib import Path
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
from logger import setup_logger

logger = setup_logger(__name__)

CACHE_DB_PATH = Path(__file__).parent.parent / 'analysis_cache.db'
CACHE_TTL_HOURS = 24  # Cache valid for 24 hours

def _init_cache():
    """Initialize analysis cache database."""
    with sqlite3.connect(CACHE_DB_PATH) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS analysis_cache (
                key TEXT PRIMARY KEY,
                keyword TEXT,
                language TEXT,
                data TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        # Create index for cleanup queries
        conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_created_at 
            ON analysis_cache(created_at)
        """)

def _get_cache_key(keyword: str, language: str, location: str) -> str:
    """Generate cache key for analysis."""
    raw = f"{keyword.lower().strip()}|{language}|{location}"
    return hashlib.md5(raw.encode()).hexdigest()

def get_cached_analysis(keyword: str, language: str, location: str) -> Optional[Dict[str, Any]]:
    """
    Retrieve cached analysis if exists and not expired.
    
    Args:
        keyword: Search keyword
        language: Language code
        location: Location
        
    Returns:
        Cached analysis data or None
    """
    try:
        key = _get_cache_key(keyword, language, location)
        
        with sqlite3.connect(CACHE_DB_PATH) as conn:
            cursor = conn.execute(
                """
                SELECT data, created_at 
                FROM analysis_cache 
                WHERE key = ?
                """,
                (key,)
            )
            row = cursor.fetchone()
            
            if not row:
                return None
                
            data, created_at = row
            
            # Check if expired
            created_time = datetime.fromisoformat(created_at)
            if datetime.now() - created_time > timedelta(hours=CACHE_TTL_HOURS):
                logger.info(f"Cache expired for '{keyword}' (age: {datetime.now() - created_time})")
                # Delete expired entry
                conn.execute("DELETE FROM analysis_cache WHERE key = ?", (key,))
                return None
            
            logger.info(f"✅ Analysis Cache HIT for '{keyword}' (age: {datetime.now() - created_time})")
            return json.loads(data)
            
    except Exception as e:
        logger.error(f"Cache read error: {e}")
        return None

def save_analysis_to_cache(
    keyword: str, 
    language: str, 
    location: str, 
    analysis_data: Dict[str, Any]
) -> None:
    """
    Save analysis results to cache.
    
    Args:
        keyword: Search keyword
        language: Language code
        location: Location
        analysis_data: Complete analysis result
    """
    try:
        key = _get_cache_key(keyword, language, location)
        
        with sqlite3.connect(CACHE_DB_PATH) as conn:
            conn.execute(
                """
                INSERT OR REPLACE INTO analysis_cache 
                (key, keyword, language, data, created_at) 
                VALUES (?, ?, ?, ?, ?)
                """,
                (key, keyword, language, json.dumps(analysis_data), datetime.now().isoformat())
            )
            
        logger.info(f"💾 Saved analysis to cache: '{keyword}'")
        
    except Exception as e:
        logger.error(f"Cache write error: {e}")

def cleanup_old_cache(days: int = 7) -> int:
    """
    Remove cache entries older than specified days.
    
    Args:
        days: Remove entries older than this many days
        
    Returns:
        Number of entries removed
    """
    try:
        cutoff = datetime.now() - timedelta(days=days)
        
        with sqlite3.connect(CACHE_DB_PATH) as conn:
            cursor = conn.execute(
                "DELETE FROM analysis_cache WHERE created_at < ?",
                (cutoff.isoformat(),)
            )
            deleted = cursor.rowcount
            
        if deleted > 0:
            logger.info(f"🧹 Cleaned up {deleted} old cache entries")
            
        return deleted
        
    except Exception as e:
        logger.error(f"Cache cleanup error: {e}")
        return 0

def get_cache_stats() -> Dict[str, Any]:
    """Get cache statistics."""
    try:
        with sqlite3.connect(CACHE_DB_PATH) as conn:
            cursor = conn.execute("SELECT COUNT(*) FROM analysis_cache")
            total = cursor.fetchone()[0]
            
            cursor = conn.execute(
                """
                SELECT COUNT(*) FROM analysis_cache 
                WHERE created_at > ?
                """,
                (datetime.now() - timedelta(hours=CACHE_TTL_HOURS),)
            )
            valid = cursor.fetchone()[0]
            
        return {
            "total_entries": total,
            "valid_entries": valid,
            "expired_entries": total - valid
        }
        
    except Exception as e:
        logger.error(f"Stats error: {e}")
        return {"total_entries": 0, "valid_entries": 0, "expired_entries": 0}

# Initialize cache on module load
try:
    _init_cache()
    logger.info("Analysis cache initialized")
except Exception as e:
    logger.error(f"Failed to init analysis cache: {e}")
