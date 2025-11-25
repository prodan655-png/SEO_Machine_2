"""
Pytest configuration and fixtures
"""
import os
import sys
import pytest

# Set test environment variables before importing modules
os.environ['DATABASE_URL'] = 'sqlite:///:memory:'  # In-memory DB for tests
os.environ['GEMINI_API_KEY'] = 'test_key'
os.environ['SERP_API_KEY'] = 'test_key'
os.environ['ENVIRONMENT'] = 'test'

# Add backend to path
sys.path.insert(0, os.path.dirname(__file__))
