from fastapi.testclient import TestClient
from unittest.mock import MagicMock, patch
import sys
import os
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'backend'))

from main import app
from database import Analysis, AnalysisStatus, Term, Guideline

client = TestClient(app)

@patch('main.SessionLocal')
@patch('modules.ai.coach.get_seo_coaching')
def test_coach_endpoint(mock_get_coaching, mock_session_cls):
    print("Testing Coach API Endpoint...")
    
    # Mock DB session
    mock_session = MagicMock()
    mock_session_cls.return_value = mock_session
    
    # Mock Analysis
    mock_analysis = MagicMock(spec=Analysis)
    mock_analysis.id = "test-id"
    mock_analysis.status = AnalysisStatus.COMPLETED
    # Ensure status.value is accessible if it's an enum, or just string
    # In main.py logic: status_str = analysis.status.value if hasattr(analysis.status, 'value') else str(analysis.status)
    
    # Mock Terms
    mock_term = MagicMock(spec=Term)
    mock_term.term = "test term"
    mock_term.min_recommended = 5
    mock_term.max_recommended = 10
    
    # Mock Guideline
    mock_guideline = MagicMock(spec=Guideline)
    mock_guideline.word_count_min = 1000
    mock_guideline.word_count_max = 2000
    mock_guideline.word_count_median = 1500
    mock_guideline.headings_min = 5
    mock_guideline.headings_max = 10
    mock_guideline.headings_median = 7
    mock_guideline.images_min = 2
    mock_guideline.images_max = 5
    mock_guideline.images_median = 3
    
    # Setup queries
    # query(Analysis).filter(...).first()
    mock_session.query.return_value.filter.return_value.first.side_effect = [
        mock_analysis, # Analysis query
        mock_guideline # Guideline query
    ]
    # query(Term).filter(...).all()
    mock_session.query.return_value.filter.return_value.all.return_value = [mock_term]
    
    # Mock AI response
    mock_get_coaching.return_value = {"priority_actions": []}
    
    # Make request
    response = client.post(
        "/api/ai/coach",
        json={
            "analysis_id": "test-id",
            "current_score": 50,
            "target_score": 90
        }
    )
    
    print(f"Status Code: {response.status_code}")
    if response.status_code != 200:
        print(f"Response: {response.json()}")
    else:
        print("SUCCESS")

if __name__ == "__main__":
    test_coach_endpoint()
