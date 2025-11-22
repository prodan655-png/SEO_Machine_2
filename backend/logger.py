"""
Logging configuration for SEO Analyzer.
Implements structured logging with secret redaction.
"""

import logging
import re
import os
from pathlib import Path
from typing import Optional


class SanitizingFormatter(logging.Formatter):
    """Formatter that redacts sensitive information from logs."""
    
    PATTERNS = [
        (r'(api[_-]?key["\']?\s*[:=]\s*["\']?)([^"\'\s]+)', r'\1***REDACTED***'),
        (r'(token["\']?\s*[:=]\s*["\']?)([^"\'\s]+)', r'\1***REDACTED***'),
        (r'(password["\']?\s*[:=]\s*["\']?)([^"\'\s]+)', r'\1***REDACTED***'),
        (r'(secret["\']?\s*[:=]\s*["\']?)([^"\'\s]+)', r'\1***REDACTED***'),
    ]
    
    def format(self, record):
        msg = super().format(record)
        
        # Redact sensitive data using patterns
        for pattern, replacement in self.PATTERNS:
            msg = re.sub(pattern, replacement, msg, flags=re.IGNORECASE)
        
        return msg


def setup_logger(
    name: str,
    level: Optional[str] = None,
    log_file: Optional[str] = None
) -> logging.Logger:
    """
    Set up a logger with console and optional file handlers.
    
    Args:
        name: Logger name (usually __name__)
        level: Log level (DEBUG, INFO, WARNING, ERROR)
        log_file: Optional log file path
    
    Returns:
        Configured logger instance
    """
    from config import LOG_LEVEL
    
    logger = logging.getLogger(name)
    
    # Set level from parameter or config
    log_level = getattr(logging, (level or LOG_LEVEL).upper(), logging.INFO)
    logger.setLevel(log_level)
    
    # Remove existing handlers to avoid duplicates
    logger.handlers = []
    
    # Create formatter
    formatter = SanitizingFormatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # File handler (optional)
    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    # Don't propagate to root logger
    logger.propagate = False
    
    return logger


# Create main application logger
logger = setup_logger('seo_analyzer')
