"""
SEO Analyzer - FastAPI Application
Provides REST API endpoints for SEO content analysis.
"""

import os
import sys
from typing import Optional, Dict, Any
from datetime import datetime
import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, BackgroundTasks, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

# Add backend to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import DATABASE_URL, ALLOWED_ORIGINS
from database import Base, Analysis, Competitor, Term, Guideline
from logger import setup_logger
from modules.serp_fetcher import fetch_serp
from modules.content_extractor import batch_extract_competitors
from modules.semantic_analyzer import analyze_competitors
from modules.guidelines_generator import generate_guidelines
from modules.content_scorer import compute_content_score

# Setup
logger = setup_logger('api')
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)

# Create tables
Base.metadata.create_all(bind=engine)


# Lifespan context manager
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events."""
    logger.info("Starting SEO Analyzer API")
    yield
    logger.info("Shutting down SEO Analyzer API")


# FastAPI app
app = FastAPI(
    title="SEO Analyzer API",
    description="Content analysis and optimization for SEO",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Pydantic models
class AnalysisCreateRequest(BaseModel):
    keyword: str = Field(..., min_length=1, max_length=200)
    language: str = Field(default="en", pattern="^(en|uk)$")
    location: str = Field(default="US", max_length=100)
    device: str = Field(default="desktop", pattern="^(desktop|mobile)$")


class AnalysisCreateResponse(BaseModel):
    analysis_id: str
    status: str


class ScoreDraftRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=50000)
    format: str = Field(default="html", pattern="^(html|markdown)$")


class ToggleCompetitorRequest(BaseModel):
    competitor_url: str
    enabled: bool


class HealthResponse(BaseModel):
    status: str
    timestamp: str


# Background task function
def process_analysis_task(analysis_id: str):
    """
    Background task to process SEO analysis.
    Fetches SERP, extracts content, analyzes competitors, generates guidelines.
    """
    db: Session = SessionLocal()
    
    try:
        # Get analysis from database
        analysis = db.query(Analysis).filter(Analysis.id == analysis_id).first()
        if not analysis:
            logger.error(f"Analysis {analysis_id} not found")
            return
        
        logger.info(f"Processing analysis {analysis_id} for keyword '{analysis.keyword}'")
        
        # Step 1: Fetch SERP results
        serp_data = fetch_serp(analysis.keyword, analysis.language)
        
        if 'error' in serp_data:
            analysis.status = 'failed'
            analysis.error_message = serp_data['error']
            db.commit()
            logger.error(f"SERP fetch failed for {analysis_id}: {serp_data['error']}")
            return
        
        # Step 2: Extract competitor content in batch
        competitor_urls = [result['url'] for result in serp_data['results']]
        extracted_data = batch_extract_competitors(competitor_urls)
        
        # Step 3: Save competitors to database
        for i, comp_data in enumerate(extracted_data):
            competitor = Competitor(
                analysis_id=analysis_id,
                url=comp_data['url'],
                position=i + 1,
                title=comp_data.get('title', ''),
                word_count=comp_data.get('word_count', 0),
                status=comp_data.get('status', 'FAILED'),
                extracted_data={
                    'main_text': comp_data.get('main_text', ''),
                    'headings': comp_data.get('headings', []),
                    'language': comp_data.get('language')
                },
                image_count=comp_data.get('image_count', 0),
                headings_count=len(comp_data.get('headings', []))
            )
            db.add(competitor)
        
        db.commit()
        
        # Step 4: Semantic analysis (extract terms)
        position_weights = [1.0, 0.9, 0.8, 0.7, 0.6, 0.5, 0.4, 0.3, 0.2, 0.1]
        terms_data = analyze_competitors(extracted_data, analysis.language, position_weights)
        
        # Step 5: Save terms to database
        for term_info in terms_data.get('terms', []):
            term = Term(
                analysis_id=analysis_id,
                term=term_info['term'],
                term_normalized=term_info['term'].lower(),
                type='phrase',
                min_recommended=term_info['range']['min'],
                max_recommended=term_info['range']['max'],
                avg_in_competitors=term_info['range'].get('avg', term_info['range']['median']),
                median_in_competitors=term_info['range']['median'],
                docs_used_in=term_info.get('docs_used_in', 3)
            )
            db.add(term)
        
        db.commit()
        
        # Step 6: Generate guidelines
        guidelines_data = generate_guidelines(extracted_data, position_weights)
        
        # Step 7: Save guidelines to database
        guideline = Guideline(
            analysis_id=analysis_id,
            word_count_min=guidelines_data['word_count']['min'],
            word_count_max=guidelines_data['word_count']['max'],
            word_count_median=guidelines_data['word_count']['median'],
            word_count_confidence=guidelines_data.get('confidence', 1.0),
            headings_min=guidelines_data['headings_count']['min'],
            headings_max=guidelines_data['headings_count']['max'],
            headings_median=guidelines_data['headings_count']['median'],
            headings_confidence=guidelines_data.get('confidence', 1.0),
            images_min=guidelines_data['images']['min'],
            images_max=guidelines_data['images']['max'],
            images_median=guidelines_data['images']['median'],
            images_confidence=guidelines_data.get('confidence', 1.0),
            suggested_outline=guidelines_data.get('suggested_outline', []),
            warnings=guidelines_data.get('warnings', []),
            competitors_analyzed=len([c for c in extracted_data if c.get('status') == 'valid'])
        )
        db.add(guideline)
        
        # Update analysis status
        analysis.status = 'COMPLETED'
        
        db.commit()
        logger.info(f"Analysis {analysis_id} completed successfully")
        
    except Exception as e:
        logger.error(f"Error processing analysis {analysis_id}: {str(e)}", exc_info=True)
        analysis.status = 'FAILED'
        analysis.error_message = str(e)
        db.commit()
        
    finally:
        db.close()


# API Endpoints

@app.post("/api/analysis/create", response_model=AnalysisCreateResponse, status_code=status.HTTP_201_CREATED)
async def create_analysis(
    request: AnalysisCreateRequest,
    background_tasks: BackgroundTasks
):
    """
    Create a new SEO analysis for a keyword.
    Triggers background task to fetch SERP and analyze competitors.
    """
    db: Session = SessionLocal()
    
    try:
        # Create analysis record
        import uuid
        analysis = Analysis(
            id=str(uuid.uuid4()),
            keyword=request.keyword,
            language=request.language,
            location=request.location,
            device=request.device,
            status='PROCESSING'
        )
        
        db.add(analysis)
        db.commit()
        db.refresh(analysis)
        
        analysis_id = str(analysis.id)
        
        # Trigger background task
        background_tasks.add_task(process_analysis_task, analysis_id)
        
        logger.info(f"Created analysis {analysis_id} for keyword '{request.keyword}'")
        
        return AnalysisCreateResponse(
            analysis_id=analysis_id,
            status='processing'
        )
        
    except Exception as e:
        logger.error(f"Error creating analysis: {str(e)}", exc_info=True)
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create analysis: {str(e)}"
        )
    finally:
        db.close()


@app.get("/api/analysis/{analysis_id}")
async def get_analysis(analysis_id: str):
    """
    Retrieve analysis results by ID.
    Returns full analysis data including terms, guidelines, and competitors.
    """
    db: Session = SessionLocal()
    
    try:
        # Get analysis
        analysis = db.query(Analysis).filter(Analysis.id == analysis_id).first()
        
        if not analysis:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Analysis {analysis_id} not found"
            )
        
        # Build response
        response = {
            "id": str(analysis.id),
            "keyword": analysis.keyword,
            "language": analysis.language,
            "status": analysis.status.value if hasattr(analysis.status, 'value') else str(analysis.status),
            "created_at": analysis.created_at.isoformat() if analysis.created_at else None,
            "updated_at": analysis.updated_at.isoformat() if analysis.updated_at else None,
            "error_message": analysis.error_message
        }
        
        # If completed, include full data
        status_str = analysis.status.value if hasattr(analysis.status, 'value') else str(analysis.status)
        if status_str == 'COMPLETED':
            # Get terms
            terms = db.query(Term).filter(Term.analysis_id == analysis_id).all()
            response['terms'] = [
                {
                    "term": t.term,
                    "range": {
                        "min": t.min_recommended,
                        "max": t.max_recommended,
                        "median": t.median_in_competitors
                    },
                    "score": t.median_in_competitors
                }
                for t in terms
            ]
            
            # Get guidelines
            guideline = db.query(Guideline).filter(Guideline.analysis_id == analysis_id).first()
            if guideline:
                response['guidelines'] = {
                    "word_count": {
                        "min": guideline.word_count_min,
                        "max": guideline.word_count_max,
                        "median": guideline.word_count_median
                    },
                    "headings_count": {
                        "min": guideline.headings_min,
                        "max": guideline.headings_max,
                        "median": guideline.headings_median
                    },
                    "images": {
                        "min": guideline.images_min,
                        "max": guideline.images_max,
                        "median": guideline.images_median
                    },
                    "suggested_outline": guideline.suggested_outline,
                    "confidence": guideline.word_count_confidence,
                    "warnings": guideline.warnings
                }
            
            # Get competitors
            competitors = db.query(Competitor).filter(Competitor.analysis_id == analysis_id).all()
            response['competitors'] = [
                {
                    "url": c.url,
                    "position": c.position,
                    "title": c.title,
                    "word_count": c.word_count,
                    "status": c.status,
                    "enabled": c.is_enabled
                }
                for c in competitors
            ]
        
        return response
        
    finally:
        db.close()


@app.post("/api/analysis/{analysis_id}/score")
async def score_draft(analysis_id: str, request: ScoreDraftRequest):
    """
    Score user's draft content against analysis guidelines.
    Returns score breakdown by terms, structure, and headings.
    """
    db: Session = SessionLocal()
    
    try:
        # Get analysis
        analysis = db.query(Analysis).filter(Analysis.id == analysis_id).first()
        
        if not analysis:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Analysis {analysis_id} not found"
            )
        
        if analysis.status != 'completed':
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Analysis is not completed yet (status: {analysis.status})"
            )
        
        # Get terms and guidelines
        terms = db.query(Term).filter(Term.analysis_id == analysis_id).all()
        guideline = db.query(Guideline).filter(Guideline.analysis_id == analysis_id).first()
        
        if not terms or not guideline:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Analysis data is incomplete"
            )
        
        # Format data for scorer
        terms_data = [
            {
                "term": t.term,
                "range": {"min": t.min_recommended, "max": t.max_recommended, "median": t.median_in_competitors}
            }
            for t in terms
        ]
        
        guidelines_data = {
            "word_count": {
                "min": guideline.word_count_min,
                "max": guideline.word_count_max,
                "median": guideline.word_count_median
            },
            "headings_count": {
                "min": guideline.headings_min,
                "max": guideline.headings_max,
                "median": guideline.headings_median
            },
            "images": {
                "min": guideline.images_min,
                "max": guideline.images_max,
                "median": guideline.images_median
            }
        }
        
        # Compute score
        score_result = compute_content_score(
            request.text,
            guidelines_data,
            terms_data,
            request.format
        )
        
        return score_result
        
    finally:
        db.close()


@app.put("/api/analysis/{analysis_id}/competitors")
async def toggle_competitor(analysis_id: str, request: ToggleCompetitorRequest):
    """
    Enable or disable a competitor from analysis.
    """
    db: Session = SessionLocal()
    
    try:
        # Get competitor
        competitor = db.query(Competitor).filter(
            Competitor.analysis_id == analysis_id,
            Competitor.url == request.competitor_url
        ).first()
        
        if not competitor:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Competitor not found"
            )
        
        # Update enabled status
        competitor.is_enabled = request.enabled
        db.commit()
        
        logger.info(f"Toggled competitor {request.competitor_url} to {request.enabled}")
        
        return {
            "url": competitor.url,
            "enabled": competitor.is_enabled,
            "message": f"Competitor {'enabled' if request.enabled else 'disabled'}"
        }
        
    finally:
        db.close()


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    return HealthResponse(
        status="healthy",
        timestamp=datetime.utcnow().isoformat()
    )



# Error handlers
from fastapi.responses import JSONResponse

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Handle HTTP exceptions."""
    logger.warning(f"HTTP {exc.status_code}: {exc.detail}")
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.detail}
    )


@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """Handle general exceptions."""
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"error": "Internal server error"}
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
