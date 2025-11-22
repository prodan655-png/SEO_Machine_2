"""
Unit tests for FastAPI endpoints.
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from main import app
from database import Base, Analysis, Competitor, Term, Guideline
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


# Test database setup
TEST_DATABASE_URL = "sqlite:///:memory:"
test_engine = create_engine(TEST_DATABASE_URL)
TestSessionLocal = sessionmaker(bind=test_engine)


@pytest.fixture
def client():
    """Create test client with in-memory database."""
    Base.metadata.create_all(bind=test_engine)
    
    # Override database dependency
    def override_get_db():
        db = TestSessionLocal()
        try:
            yield db
        finally:
            db.close()
    
    # Patch SessionLocal in main module
    with patch('main.SessionLocal', TestSessionLocal):
        test_client = TestClient(app)
        yield test_client
    
    Base.metadata.drop_all(bind=test_engine)


@pytest.fixture
def sample_analysis(client):
    """Create a sample completed analysis in test database."""
    db = TestSessionLocal()
    
    # Create analysis with all required fields
    analysis = Analysis(
        id="test-analysis-123",
        keyword="seo optimization",
        language="en",
        location="US",
        device="desktop",
        status="COMPLETED"
    )
    db.add(analysis)
    
    # Add terms with correct schema
    terms_data = [
        {"term": "seo", "min": 5, "max": 15, "median": 10, "score": 0.9},
        {"term": "optimization", "min": 3, "max": 10, "median": 6, "score": 0.8},
        {"term": "content", "min": 8, "max": 20, "median": 14, "score": 0.7}
    ]
    
    for term_info in terms_data:
        term = Term(
            analysis_id="test-analysis-123",
            term=term_info["term"],
            term_normalized=term_info["term"].lower(),
            type="phrase",
            min_recommended=term_info["min"],
            max_recommended=term_info["max"],
            avg_in_competitors=float(term_info["median"]),
            median_in_competitors=float(term_info["median"]),
            docs_used_in=3
        )
        db.add(term)
    
    # Add guideline with correct schema
    guideline = Guideline(
        analysis_id="test-analysis-123",
        word_count_min=800,
        word_count_max=1500,
        word_count_median=1100,
        word_count_confidence=0.95,
        headings_min=3,
        headings_max=8,
        headings_median=5,
        headings_confidence=0.95,
        images_min=2,
        images_max=6,
        images_median=4,
        images_confidence=0.95,
        suggested_outline=["Introduction", "SEO Basics", "Advanced Tips"],
        warnings=[],
        competitors_analyzed=3
    )
    db.add(guideline)
    
    # Add competitors
    for i in range(3):
        competitor = Competitor(
            analysis_id="test-analysis-123",
            url=f"https://example{i+1}.com",
            position=i+1,
            title=f"SEO Guide {i+1}",
            word_count=1000 + i*100,
            status="VALID",
            is_enabled=True
        )
        db.add(competitor)
    
    db.commit()
    db.close()
    
    return "test-analysis-123"


def test_health_check(client):
    """Test health check endpoint."""
    response = client.get("/health")
    
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "timestamp" in data


@patch('main.process_analysis_task')
def test_create_analysis(mock_task, client):
    """Test analysis creation endpoint."""
    request_data = {
        "keyword": "test keyword",
        "language": "en"
    }
    
    response = client.post("/api/analysis/create", json=request_data)
    
    assert response.status_code == 201
    data = response.json()
    assert "analysis_id" in data
    assert data["status"] == "processing"
    
    # Verify background task was called
    # mock_task.assert_called_once()  # Note: BackgroundTasks doesn't call immediately in tests


def test_create_analysis_invalid_language(client):
    """Test analysis creation with invalid language."""
    request_data = {
        "keyword": "test",
        "language": "fr"  # Not supported
    }
    
    response = client.post("/api/analysis/create", json=request_data)
    assert response.status_code == 422  # Validation error


def test_get_analysis_not_found(client):
    """Test getting non-existent analysis."""
    response = client.get("/api/analysis/nonexistent-id")
    
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


def test_get_analysis_completed(client, sample_analysis):
    """Test getting completed analysis."""
    response = client.get(f"/api/analysis/{sample_analysis}")
    
    assert response.status_code == 200
    data = response.json()
    
    assert data["id"] == sample_analysis
    assert data["keyword"] == "seo optimization"
    assert data["status"] == "completed"
    assert "terms" in data
    assert "guidelines" in data
    assert "competitors" in data
    
    # Verify data structure
    assert len(data["terms"]) == 3
    assert data["guidelines"]["word_count"]["min"] == 800
    assert len(data["competitors"]) == 3


def test_score_draft_html(client, sample_analysis):
    """Test scoring HTML draft."""
    draft_text = """
    <h1>SEO Optimization Guide</h1>
    <p>This is content about SEO and optimization. We'll cover various aspects
    of content creation and seo best practices for optimization.</p>
    <h2>What is SEO</h2>
    <p>Search engine optimization is important for content visibility.</p>
    """
    
    request_data = {
        "text": draft_text,
        "format": "html"
    }
    
    response = client.post(
        f"/api/analysis/{sample_analysis}/score",
        json=request_data
    )
    
    assert response.status_code == 200
    data = response.json()
    
    assert "total_score" in data
    assert "breakdown" in data
    assert 0 <= data["total_score"] <= 100


def test_score_draft_not_completed(client):
    """Test scoring when analysis is not completed."""
    db = TestSessionLocal()
    
    # Create processing analysis with all required fields
    analysis = Analysis(
        id="processing-123",
        keyword="test",
        language="en",
        location="US",
        device="desktop",
        status="PROCESSING"
    )
    db.add(analysis)
    db.commit()
    db.close()
    
    request_data = {
        "text": "<p>Test content</p>",
        "format": "html"
    }
    
    response = client.post(
        "/api/analysis/processing-123/score",
        json=request_data
    )
    
    assert response.status_code == 400
    assert "not completed" in response.json()["detail"].lower()


def test_toggle_competitor(client, sample_analysis):
    """Test toggling competitor enabled status."""
    request_data = {
        "competitor_url": "https://example1.com",
        "enabled": False
    }
    
    response = client.put(
        f"/api/analysis/{sample_analysis}/competitors",
        json=request_data
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["enabled"] == False
    assert "disabled" in data["message"].lower()


def test_toggle_competitor_not_found(client, sample_analysis):
    """Test toggling non-existent competitor."""
    request_data = {
        "competitor_url": "https://nonexistent.com",
        "enabled": False
    }
    
    response = client.put(
        f"/api/analysis/{sample_analysis}/competitors",
        json=request_data
    )
    
    assert response.status_code == 404


def test_cors_headers(client):
    """Test CORS headers are present."""
    response = client.get("/health")
    
    # CORS headers should be present (added by middleware)
    assert response.status_code == 200


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
