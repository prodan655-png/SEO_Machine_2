
import os
import sys
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import uuid

# Add backend to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../backend')))

from main import app
from database import Base, Analysis, Term, Guideline, AnalysisStatus, get_db
from config import CONFIG

# Setup test DB
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_debug.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

# Create tables
Base.metadata.create_all(bind=engine)

client = TestClient(app)

def test_coach_endpoint():
    print("\n--- Starting Coach Endpoint Debug ---")
    
    # 1. Create dummy analysis
    db = TestingSessionLocal()
    analysis_id = str(uuid.uuid4())
    
    analysis = Analysis(
        id=analysis_id,
        keyword="test seo",
        language="uk",
        location="Ukraine",
        device="desktop",
        status=AnalysisStatus.COMPLETED
    )
    db.add(analysis)
    
    # Add some terms
    term = Term(
        analysis_id=analysis_id,
        term="seo",
        term_normalized="seo",
        type="phrase",
        min_recommended=2,
        max_recommended=5,
        avg_in_competitors=3.0,
        median_in_competitors=3.0,
        docs_used_in=5
    )
    db.add(term)
    
    # Add guideline
    guideline = Guideline(
        analysis_id=analysis_id,
        word_count_min=500,
        word_count_max=1000,
        word_count_median=750,
        headings_min=2,
        headings_max=5,
        headings_median=3,
        images_min=1,
        images_max=3,
        images_median=2,
        competitors_analyzed=5
    )
    db.add(guideline)
    db.commit()
    
    print(f"Created analysis {analysis_id} with status {analysis.status}")
    
    # 2. Call API
    payload = {
        "analysis_id": analysis_id,
        "current_score": 50,
        "target_score": 85
    }
    
    print(f"Sending payload: {payload}")
    
    try:
        response = client.post("/api/ai/coach", json=payload)
        print(f"Response Status: {response.status_code}")
        print(f"Response Body: {response.text}")
        
        if response.status_code == 200:
            print("✅ Success!")
        else:
            print("❌ Failed!")
            
    except Exception as e:
        print(f"❌ Exception: {e}")
    
    # Cleanup
    db.close()
    os.remove("./test_debug.db")

if __name__ == "__main__":
    # Force AI enabled
    os.environ["AI_ENABLED"] = "true"
    CONFIG['ai']['enabled'] = True
    
    test_coach_endpoint()
