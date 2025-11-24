"""
Configuration module for SEO Analyzer.
Loads settings from environment variables and config.yaml.
"""

import os
from typing import Any, Dict
import yaml
from dotenv import load_dotenv
from pathlib import Path


# Determine environment and load appropriate .env file
ENV = os.getenv('ENV', 'development')

# Load environment-specific .env file
env_file = f'.env.{ENV}' if ENV in ['development', 'production'] else '.env'
env_path = Path(__file__).parent.parent / env_file

if env_path.exists():
    load_dotenv(env_path, override=True)
    print(f"[OK] Loaded environment from {env_file}")
    print(f"DEBUG: USE_MOCK_SERP = {os.getenv('USE_MOCK_SERP')}")
else:
    print(f"⚠ Warning: {env_file} not found, using system environment variables")


# Load YAML configuration
config_path = Path(__file__).parent / 'config.yaml'
with open(config_path, 'r', encoding='utf-8') as f:
    CONFIG: Dict[str, Any] = yaml.safe_load(f)


# Environment variables with validation
def get_env_var(name: str, required: bool = False, default: Any = None) -> Any:
    """Get environment variable with optional validation."""
    value = os.getenv(name, default)
    if required and not value:
        raise ValueError(f"Missing required environment variable: {name}")
    return value


# Core settings
DEBUG = get_env_var('DEBUG', default='false').lower() == 'true'
LOG_LEVEL = get_env_var('LOG_LEVEL', default='INFO')

# Database
DATABASE_URL = get_env_var('DATABASE_URL', required=True)

# SERP API
USE_MOCK_SERP = get_env_var('USE_MOCK_SERP', default='false').lower() == 'true'
SERP_PROVIDER = get_env_var('SERP_PROVIDER', default='serpapi')
SERPAPI_KEY = get_env_var('SERPAPI_KEY', required=not USE_MOCK_SERP)

# AI Configuration
AI_ENABLED = get_env_var('AI_ENABLED', default='false').lower() == 'true'
AI_PROVIDER = get_env_var('AI_PROVIDER', default='mock')
GEMINI_API_KEY = get_env_var('GEMINI_API_KEY')
OPENAI_API_KEY = get_env_var('OPENAI_API_KEY')

# CORS
ALLOWED_ORIGINS = get_env_var('ALLOWED_ORIGINS', default='http://localhost:8080,http://localhost:8081').split(',')

# Auth
ADMIN_TOKEN = get_env_var('ADMIN_TOKEN')

# Rate Limiting
# Rate Limiting
RATE_LIMIT_ENABLED = get_env_var('RATE_LIMIT_ENABLED', default='false').lower() == 'true'


# Update CONFIG with environment variables
if 'ai' not in CONFIG:
    CONFIG['ai'] = {}
CONFIG['ai']['enabled'] = AI_ENABLED
CONFIG['ai']['provider'] = AI_PROVIDER
CONFIG['ai']['gemini_api_key'] = GEMINI_API_KEY


# Helper functions to access nested config
def get_config(path: str, default: Any = None) -> Any:
    """
    Get configuration value using dot notation.
    Example: get_config('scoring.weights.terms') -> 60
    """
    keys = path.split('.')
    value = CONFIG
    for key in keys:
        if isinstance(value, dict):
            value = value.get(key)
        else:
            return default
        if value is None:
            return default
    return value


# Print configuration summary on import (in development)
if DEBUG:
    print("\n=== SEO Analyzer Configuration ===")
    print(f"Environment: {ENV}")
    print(f"Debug: {DEBUG}")
    print(f"Log Level: {LOG_LEVEL}")
    print(f"Database: {DATABASE_URL}")
    print(f"Mock SERP: {USE_MOCK_SERP}")
    print(f"AI Enabled: {AI_ENABLED}")
    print(f"AI Provider: {AI_PROVIDER}")
    print(f"Rate Limiting: {RATE_LIMIT_ENABLED}")
    print("==================================\n")
